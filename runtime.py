"""Manifest and checkpoint verification."""

from contextlib import contextmanager
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def complete(root, run_id):
    out = root / "checkpoints" / run_id
    if not (out / "complete.json").exists():
        return False
    done, meta = load(out / "complete.json"), load(out / "1000/metadata.json")
    manifest = load(root / "manifest.json")
    run = manifest["runs"][run_id]
    expected_done = dict(
        version=1,
        run_id=run_id,
        seed=run["seed"],
        tasks=run["tasks"],
        optimizer_updates=1000,
        snapshots=[1000],
    )
    if any(done.get(key) != value for key, value in expected_done.items()):
        raise ValueError(f"Run completion record changed: {run_id}")
    expected_meta = dict(
        run_id=run_id,
        step=1000,
        optimizer_updates=1000,
        seed=run["seed"],
        tasks=run["tasks"],
        effective_batch=manifest["effective_batch"],
        full_parameter_finetune=True,
        lora=False,
    )
    for key, value in expected_meta.items():
        if meta.get(key) != value:
            raise ValueError(f"Run metadata changed: {run_id}: {key}")
    if not (out / "1000/params/_METADATA").is_file():
        raise ValueError("Missing full weights")
    return True


@contextmanager
def lock(path):
    import fcntl

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
