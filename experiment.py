import argparse
from pathlib import Path
import subprocess
import sys

import runtime

CODE = Path(__file__).resolve().parent
CONFIG = CODE / "configs" / "five_task_sft.json"
ROOT = Path("results/pi05-libero/five-task-sft-50demo-v1")


def prepare(config):
    from data_prep import capture_split, check_or_create, features, validate_raw_demos

    manifest = dict(config, version=1, norm_assets=str(Path(config["checkpoint"]) / "assets"))
    suite, seed = config["suite"], config["training_seed"]
    demo_ids = list(range(config["training_demo_count"]))
    feature_spec = features()
    tasks, runs = {}, {}
    for group in config["groups"].values():
        for task in group:
            task_id, prompt = task["id"], task["prompt"]
            name = f"{task['scene']}_{prompt.replace(' ', '_')}"
            raw = Path("data") / suite / f"{name}_demo.hdf5"
            validate_raw_demos(raw, suite, task_id, name, demo_ids)
            dataset = ROOT / "datasets" / f"task{task_id}"
            sources = capture_split(dataset, suite, task_id, name, prompt, raw, demo_ids, feature_spec)
            tasks[str(task_id)] = {"bddl": name, "prompt": prompt, "sources": sources}
            runs[f"s{seed}-t{task_id}-only"] = {"seed": seed, "tasks": [task_id]}
    manifest.update(tasks=tasks, runs=runs, seeds=[seed], exports=[config["steps"]])
    check_or_create(ROOT / "manifest.json", manifest)


def train(manifest):
    for run_id in manifest["runs"]:
        with runtime.lock(ROOT / "locks" / f"{run_id}.lock"):
            if not runtime.complete(ROOT, run_id):
                subprocess.run(
                    [
                        sys.executable,
                        "-u",
                        str(CODE / "train.py"),
                        "--manifest",
                        str(ROOT / "manifest.json"),
                        "--run-id",
                        run_id,
                        "--out",
                        str(ROOT / "checkpoints" / run_id),
                        "--fsdp-devices",
                        "1",
                    ],
                    check=True,
                )
                if not runtime.complete(ROOT, run_id):
                    raise RuntimeError(f"Missing final checkpoint for {run_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("prepare", "train", "eval"))
    stage = parser.parse_args().stage
    if stage == "prepare":
        with runtime.lock(ROOT / "locks" / "prepare.lock"):
            prepare(runtime.load(CONFIG))
        return
    manifest = runtime.load(ROOT / "manifest.json")
    if any(manifest.get(key) != value for key, value in runtime.load(CONFIG).items()):
        raise ValueError("Configuration differs from the prepared experiment")
    if stage == "train":
        train(manifest)
    else:
        from evaluate import evaluate

        with runtime.lock(ROOT / "locks" / "eval.lock"):
            evaluate(manifest, ROOT)


if __name__ == "__main__":
    main()
