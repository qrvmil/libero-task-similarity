import argparse
import logging
from pathlib import Path

import jax
from openpi.policies import policy_config
from openpi.serving.websocket_policy_server import WebsocketPolicyServer
from openpi.training import checkpoints
from openpi.training.config import get_config

import runtime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--port", type=int, default=19397)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    manifest = runtime.load(args.manifest)
    if manifest["version"] != 1 or (args.run_id != "base" and args.run_id not in manifest["runs"]):
        raise ValueError("Unknown experiment or policy run")
    base = Path(manifest["checkpoint"]).resolve()
    norm_assets = Path(manifest["norm_assets"]).resolve()
    if base.name != "pi05_libero" or norm_assets != (base / "assets").resolve():
        raise ValueError("Expected the pinned pi05_libero base and normalization")
    if not (base / "params/_METADATA").is_file() or not norm_assets.is_dir():
        raise FileNotFoundError("Base checkpoint or normalization assets are missing")
    if args.run_id == "base":
        if args.checkpoint.resolve() != base:
            raise ValueError("Baseline uses different weights")
    else:
        metadata = runtime.load(args.checkpoint / "metadata.json")
        run = manifest["runs"][args.run_id]
        expected = dict(
            run_id=args.run_id,
            seed=run["seed"],
            tasks=run["tasks"],
            step=manifest["steps"],
            full_parameter_finetune=True,
            lora=False,
        )
        if any(metadata.get(key) != value for key, value in expected.items()):
            raise ValueError("Checkpoint differs from the requested full-SFT run")
    if not (args.checkpoint / "params/_METADATA").is_file():
        raise FileNotFoundError("Incomplete parameter checkpoint")
    config = get_config("pi05_libero")
    data_config = config.data.create(config.assets_dirs, config.model)
    norm_stats = checkpoints.load_norm_stats(norm_assets, data_config.asset_id)
    policy = policy_config.create_trained_policy(config, args.checkpoint, norm_stats=norm_stats)
    print("WEIGHT SOURCE", args.checkpoint.resolve(), "RUN", args.run_id, flush=True)

    class PairedPolicy:
        def infer(self, observation):
            observation = dict(observation)
            policy._rng = jax.random.key(int(observation.pop("pilot_seed")))
            return policy.infer(observation)

    WebsocketPolicyServer(
        policy=PairedPolicy(), host="127.0.0.1", port=args.port, metadata=policy.metadata
    ).serve_forever()


if __name__ == "__main__":
    main()
