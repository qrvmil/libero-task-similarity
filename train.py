"""Full-parameter single-task fine-tuning from pi05_libero."""

from __future__ import annotations

import argparse
import dataclasses
from dataclasses import replace
from functools import cache
import json
import math
from pathlib import Path
import random
from unittest.mock import patch

from flax import nnx, traverse_util
import jax
import jax.numpy as jnp
import numpy as np
import optax
import orbax.checkpoint as ocp
import torch

from openpi.training import config, data_loader, weight_loaders
from scripts import train

EXPECTED_PI05_PARAMETER_COUNT = 3_353_433_872


def load_json(path: Path):
    return json.loads(path.read_text())


def _source_dataset(source: dict, open_dataset):
    dataset = Path(source["dataset"]).resolve()
    episodes = [json.loads(line) for line in (dataset / "meta/episodes.jsonl").read_text().splitlines()]
    raw_sources = load_json(dataset / "meta/source_episodes.json")
    episode = int(source["episode"])
    if not 0 <= episode < len(episodes) or len(episodes) != len(raw_sources):
        raise ValueError(f"Invalid episode metadata for {dataset}")
    expected_offset = sum(int(item["length"]) for item in episodes[:episode])
    actual = episodes[episode]
    raw = raw_sources[episode]
    if expected_offset != int(source["offset"]):
        raise ValueError(f"Frame offset changed for {dataset} episode {episode}")
    if int(actual["length"]) != int(source["length"]):
        raise ValueError(f"Episode length changed for {dataset} episode {episode}")
    if int(raw["demo_index"]) != int(source["demo"]) or raw["bddl"] != source["bddl"]:
        raise ValueError(f"Source demonstration changed for {dataset} episode {episode}")

    frames, data_config = open_dataset(dataset)
    if len(frames) != int(source["dataset_frames"]):
        raise ValueError(f"Dataset frame count changed for {dataset}")
    subset = torch.utils.data.Subset(
        frames,
        range(expected_offset, expected_offset + int(source["length"])),
    )
    return subset, data_config


def fixed_loader(manifest: dict, run: dict, cfg, *, sharding, shuffle):
    del shuffle
    (task,) = run["tasks"]

    @cache
    def open_dataset(path):
        data_config = replace(cfg.data, repo_id=str(path)).create(cfg.assets_dirs, cfg.model)
        frames = data_loader.create_torch_dataset(data_config, cfg.model.action_horizon, cfg.model)
        return data_loader.transform_dataset(frames, data_config), data_config

    demo_count = int(manifest["training_demo_count"])
    sources = manifest["tasks"][str(task)]["sources"]
    if len(sources) != demo_count or {int(s["demo"]) for s in sources} != set(range(demo_count)):
        raise ValueError(f"Task {task} must contain every configured demonstration exactly once")
    if len({s["dataset"] for s in sources}) != 1:
        raise ValueError(f"Task {task} must use a single dataset")
    subsets = []
    spans = []
    offset = 0
    for source in sources:
        subset, data_config = _source_dataset(source, open_dataset)
        subsets.append(subset)
        spans.append((offset, len(subset)))
        offset += len(subset)

    dataset = torch.utils.data.ConcatDataset(subsets)
    effective_batch = int(manifest["effective_batch"])
    indices = []
    rng = random.Random(int(run["seed"]))
    for _ in range(int(manifest["steps"]) + 4):
        for _ in range(effective_batch):
            start, length = spans[rng.randrange(demo_count)]
            indices.append(start + rng.randrange(length))

    class FixedSampler(torch.utils.data.Sampler):
        def __iter__(self):
            return iter(indices)

        def __len__(self):
            return len(indices)

    loader = data_loader.TorchDataLoader(
        dataset,
        effective_batch,
        sharding=sharding,
        sampler=FixedSampler(),
        num_workers=0,
        seed=int(run["seed"]),
    )
    return data_loader.DataLoaderImpl(data_config, loader)


def _batch_slice(tree, start, size):
    return jax.tree.map(lambda value: jax.lax.dynamic_slice_in_dim(value, start, size, axis=0), tree)


def accumulated_train_step(config_, rng, state, batch, *, microbatch: int):
    """Average microbatch gradients, then apply clipping and one AdamW update."""
    effective_batch = int(config_.batch_size)
    if effective_batch % microbatch:
        raise ValueError("Effective batch must be divisible by microbatch")
    accumulation = effective_batch // microbatch
    observation, actions = batch
    base_rng = jax.random.fold_in(rng, state.step)
    full_flat = traverse_util.flatten_dict(state.params.to_pure_dict())
    trainable_flat = traverse_util.flatten_dict(
        state.params.filter(config_.trainable_filter).to_pure_dict()
    )
    if full_flat.keys() != trainable_flat.keys():
        raise ValueError("Full fine-tuning requires every model parameter to be trainable")

    def gradient(index):
        obs = _batch_slice(observation, index * microbatch, microbatch)
        act = jax.lax.dynamic_slice_in_dim(actions, index * microbatch, microbatch, axis=0)

        # Raw jax.value_and_grad keeps the NNX state pure inside the sequential
        # lax loop.  nnx.value_and_grad cannot be nested in lax.fori_loop.
        def loss_fn(current_params):
            current_model = nnx.merge(state.model_def, current_params)
            current_model.train()
            loss = current_model.compute_loss(jax.random.fold_in(base_rng, index), obs, act, train=True)
            return jnp.mean(loss)

        return jax.value_and_grad(loss_fn)(state.params)

    total_loss, total_grads = gradient(jnp.asarray(0, dtype=jnp.int32))

    def accumulate(index, carry):
        loss_sum, grad_sum = carry
        loss, grads = gradient(index)
        return loss_sum + loss, jax.tree.map(jnp.add, grad_sum, grads)

    total_loss, total_grads = jax.lax.fori_loop(1, accumulation, accumulate, (total_loss, total_grads))
    loss = total_loss / accumulation
    grads = jax.tree.map(lambda value: value / accumulation, total_grads)

    params = state.params.filter(config_.trainable_filter)
    updates, new_opt_state = state.tx.update(grads, state.opt_state, params)
    new_trainable = optax.apply_updates(params, updates)
    model = nnx.merge(state.model_def, state.params)
    nnx.update(model, new_trainable)
    new_params = nnx.state(model)
    new_state = dataclasses.replace(
        state,
        step=state.step + 1,
        params=new_params,
        opt_state=new_opt_state,
    )
    if state.ema_decay is not None:
        new_state = dataclasses.replace(
            new_state,
            ema_params=jax.tree.map(
                lambda old, new: state.ema_decay * old + (1 - state.ema_decay) * new,
                state.ema_params,
                new_params,
            ),
        )
    return new_state, {
        "loss": loss,
        "grad_norm": optax.global_norm(grads),
        "param_norm": optax.global_norm(params),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--microbatch", type=int)
    parser.add_argument("--fsdp-devices", type=int, required=True)
    parser.add_argument(
        "--check-data",
        action="store_true",
        help="Validate the frozen sampler and one batch without initializing the model",
    )
    args = parser.parse_args()
    args.out = args.out.resolve()

    manifest = load_json(args.manifest)
    if manifest.get("version") != 1:
        raise ValueError("Expected full-FT manifest version 1")
    if args.run_id not in manifest["runs"]:
        raise ValueError(f"Unknown run: {args.run_id}")
    run = manifest["runs"][args.run_id]
    if int(run["seed"]) not in [int(seed) for seed in manifest["seeds"]]:
        raise ValueError("Run seed is outside the frozen seed list")
    if int(manifest["steps"]) != 1000 or int(manifest["effective_batch"]) != 64:
        raise ValueError("This experiment requires 1000 updates and effective batch 64")
    exports = [int(step) for step in manifest.get("exports", [1000])]
    if exports != [int(manifest["steps"])]:
        raise ValueError("Export the final optimizer step")
    microbatch = int(args.microbatch or manifest["microbatch"])
    if microbatch <= 0 or 64 % microbatch:
        raise ValueError("Microbatch must be a positive divisor of 64")
    if microbatch % jax.device_count():
        raise ValueError("Global microbatch must be divisible by the JAX device count")
    if args.fsdp_devices <= 0 or jax.device_count() % args.fsdp_devices:
        raise ValueError("FSDP device count must divide the JAX device count")

    base = Path(manifest["checkpoint"]).resolve()
    norm_assets = Path(manifest["norm_assets"]).resolve()
    if base.name != "pi05_libero" or norm_assets != (base / "assets").resolve():
        raise ValueError("The frozen base must be pi05_libero with its own normalization assets")
    if not (base / "params" / "_METADATA").is_file() or not norm_assets.is_dir():
        raise FileNotFoundError("Frozen pi05_libero checkpoint or normalization assets are missing")
    for step in exports:
        if (args.out / str(step)).exists() or (args.out / f".{step}.tmp").exists():
            raise FileExistsError(f"Refusing to overwrite existing snapshot state for step {step}")
    if (args.out / "complete.json").exists() or (args.out / ".complete.tmp").exists():
        raise FileExistsError(f"Run is already complete: {args.out}")
    args.out.mkdir(parents=True, exist_ok=True)

    first_source = manifest["tasks"][str(run["tasks"][0])]["sources"][0]
    template = config.get_config("pi05_libero_oneshotft")
    train_config = replace(
        template,
        data=replace(
            template.data,
            repo_id=str(Path(first_source["dataset"]).resolve()),
            camera_view="original",
            assets=replace(template.data.assets, assets_dir=str(norm_assets)),
        ),
        weight_loader=weight_loaders.CheckpointWeightLoader(str(base / "params")),
        freeze_filter=nnx.Nothing(),
        ema_decay=None,
        exp_name=args.run_id,
        seed=int(run["seed"]),
        checkpoint_base_dir=str((args.out / "_trainer").resolve()),
        batch_size=64,
        num_train_steps=1000,
        num_workers=0,
        log_interval=20,
        save_interval=int(manifest["steps"]),
        keep_period=None,
        fsdp_devices=args.fsdp_devices,
        wandb_enabled=False,
    )
    if "lora" in repr(train_config.model).lower() or "Nothing" not in repr(train_config.freeze_filter):
        raise AssertionError("Full fine-tuning requires a non-LoRA model and no frozen parameters")
    snapshots = []

    def export_params(manager, state, loader, step):
        del manager, loader, step
        count = int(np.asarray(jax.device_get(state.step)))
        if count not in exports:
            return
        destination = args.out / str(count)
        temporary = args.out / f".{count}.tmp"
        if destination.exists() or temporary.exists():
            raise FileExistsError(f"Refusing to overwrite {destination} or {temporary}")
        temporary.mkdir(parents=True)
        params = state.ema_params if state.ema_params is not None else state.params
        pure_params = params.to_pure_dict()
        flat = traverse_util.flatten_dict(pure_params)
        trainable = traverse_util.flatten_dict(
            params.filter(train_config.trainable_filter).to_pure_dict()
        )
        if flat.keys() != trainable.keys():
            raise ValueError("Some parameters were frozen in a full-FT run")
        if any("lora" in part.lower() for key in flat for part in key):
            raise ValueError("LoRA parameters appeared in a full-FT checkpoint")
        if not flat or not all(jnp.issubdtype(value.dtype, jnp.floating) for value in flat.values()):
            raise ValueError("Unexpected parameter tree")
        parameter_count = sum(math.prod(value.shape) for value in flat.values())
        if parameter_count != EXPECTED_PI05_PARAMETER_COUNT:
            raise ValueError(
                f"pi05_libero schema changed: {parameter_count} != {EXPECTED_PI05_PARAMETER_COUNT}"
            )
        finite = jax.tree.reduce(
            jnp.logical_and,
            jax.tree.map(lambda value: jnp.all(jnp.isfinite(value)), pure_params),
            initializer=jnp.asarray(True),
        )
        if not bool(np.asarray(jax.device_get(finite))):
            raise ValueError("Non-finite value in full-FT parameters")
        jax.block_until_ready(params)
        with ocp.PyTreeCheckpointer() as checkpointer:
            checkpointer.save(temporary / "params", {"params": pure_params})
        dtype_counts = {}
        for value in flat.values():
            dtype_counts[str(value.dtype)] = dtype_counts.get(str(value.dtype), 0) + math.prod(
                value.shape
            )
        metadata = {
            "version": 1,
            "run_id": args.run_id,
            "step": count,
            "optimizer_updates": count,
            "seed": int(run["seed"]),
            "tasks": [int(task) for task in run["tasks"]],
            "checkpoint": str(base),
            "norm_assets": str(norm_assets),
            "effective_batch": 64,
            "microbatch": microbatch,
            "gradient_accumulation": 64 // microbatch,
            "fsdp_devices": args.fsdp_devices,
            "parameter_leaves": len(flat),
            "parameter_count": parameter_count,
            "dtype_parameter_counts": dtype_counts,
            "full_parameter_finetune": True,
            "lora": False,
        }
        (temporary / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        temporary.rename(destination)
        snapshots.append(count)
        print(f"Exported full parameters after {count} optimizer updates to {destination}", flush=True)

    def patched_step(config_, rng, state, batch):
        return accumulated_train_step(config_, rng, state, batch, microbatch=microbatch)

    def factory(cfg, *, sharding, shuffle):
        return fixed_loader(manifest, run, cfg, sharding=sharding, shuffle=shuffle)

    if args.check_data:
        observation, actions = next(iter(factory(train_config, sharding=None, shuffle=True)))
        image_shapes = {name: tuple(value.shape) for name, value in observation.images.items()}
        if actions.shape[0] != 64 or any(shape[0] != 64 for shape in image_shapes.values()):
            raise ValueError("Frozen sampler did not produce a global batch of 64")
        print(
            json.dumps(
                {
                    "run_id": args.run_id,
                    "seed": int(run["seed"]),
                    "tasks": [int(task) for task in run["tasks"]],
                    "images": image_shapes,
                    "actions": tuple(actions.shape),
                    "effective_batch": 64,
                    "microbatch": microbatch,
                    "gradient_accumulation": 64 // microbatch,
                    "full_parameter_finetune": True,
                    "lora": False,
                },
                default=list,
            ),
            flush=True,
        )
        return
    with (
        patch.object(data_loader, "create_data_loader", factory),
        patch.object(train, "train_step", patched_step),
        patch.object(train._checkpoints, "save_state", export_params),
    ):
        train.main(train_config)

    if snapshots != exports:
        raise RuntimeError(f"Expected snapshots {exports}, got {snapshots}")
    complete = {
        "version": 1,
        "run_id": args.run_id,
        "seed": int(run["seed"]),
        "tasks": [int(task) for task in run["tasks"]],
        "optimizer_updates": 1000,
        "snapshots": snapshots,
    }
    complete_tmp = args.out / ".complete.tmp"
    complete_tmp.write_text(json.dumps(complete, indent=2) + "\n")
    complete_tmp.rename(args.out / "complete.json")


if __name__ == "__main__":
    main()
