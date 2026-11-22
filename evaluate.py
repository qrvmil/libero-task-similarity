import json
from pathlib import Path
import socket
import subprocess
import time
import urllib.request

import runtime

SCRIPTS = Path(__file__).resolve().parent


def collect(out, starts, ids):
    rows = []
    for shard in range(2):
        rows.extend(
            json.loads(line)
            for line in (out / f"shard{shard}" / "episodes.jsonl").read_text().splitlines()
        )
    expected = {(task, index) for task in ids for index in starts["tasks"][str(task)]["indices"]}
    actual = {(row["task_id"], row["state_index"]) for row in rows}
    if len(rows) != len(expected) or actual != expected:
        raise ValueError("Evaluation outcomes differ from the frozen episode set")
    rows.sort(key=lambda row: (row["task_id"], row["state_index"]))
    summary = {
        str(task): dict(
            episodes=50, successes=sum(bool(row["success"]) for row in rows if row["task_id"] == task)
        )
        for task in ids
    }
    return rows, summary


def paired_rollouts(out, checkpoint, starts_path, manifest_path, run_id, seed, ids, port=19397):
    starts = runtime.load(starts_path)
    if starts["seed"] != seed or starts["suite"] != "libero_90" or starts["trials"] != 50:
        raise ValueError("Evaluation protocol differs from the requested seed or suite")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "complete.json").exists():
        rows, summary = collect(out, starts, ids)
        if runtime.load(out / "complete.json") != summary:
            raise ValueError("Evaluation summary differs from episode outcomes")
        return
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", port))
    common = [
        "simenv/bin/python",
        "-u",
        str(SCRIPTS / "rollout.py"),
        "--suite",
        starts["suite"],
        "--ids",
        *map(str, ids),
        "--manifest",
        str(starts_path),
        "--port",
        str(port),
        "--seed",
        str(seed),
    ]
    with (out / "server.log").open("a") as log:
        server = subprocess.Popen(
            [
                "dart/.venv/bin/python",
                "-u",
                str(SCRIPTS / "serve.py"),
                "--manifest",
                str(manifest_path),
                "--run-id",
                run_id,
                "--checkpoint",
                str(checkpoint),
                "--port",
                str(port),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        clients, handles = [], []
        try:
            for _ in range(600):
                if server.poll() is not None:
                    raise RuntimeError("Policy server failed")
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{port}/healthz", timeout=2
                    ) as response:
                        if response.status == 200:
                            break
                except OSError:
                    pass
                time.sleep(1)
            else:
                raise TimeoutError("Policy server readiness timeout")
            for shard in range(2):
                folder = out / f"shard{shard}"
                folder.mkdir(exist_ok=True)
                handle = (folder / "client.log").open("a")
                handles.append(handle)
                clients.append(
                    subprocess.Popen(
                        [*common, "--out", str(folder), "--offset", str(shard * 25), "--count", "25"],
                        stdout=handle,
                        stderr=subprocess.STDOUT,
                    )
                )
            codes = [client.wait() for client in clients]
            if any(codes):
                raise RuntimeError(f"Evaluation clients failed: {codes}")
        finally:
            for process in [*clients, server]:
                if process.poll() is None:
                    process.terminate()
            for process in [*clients, server]:
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            for handle in handles:
                handle.close()
    rows, summary = collect(out, starts, ids)
    (out / "episodes.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
    runtime.save(out / "complete.json", summary)


def evaluate(manifest, root):
    root = Path(root)
    ids = [int(key) for key in manifest["tasks"]]
    for seed in manifest["evaluation"]["seeds"]:
        starts = root / f"starts-seed{seed}.json"
        out = root / "evaluations" / f"seed{seed}"
        subprocess.run(
            [
                "simenv/bin/python",
                str(SCRIPTS / "rollout.py"),
                "--prepare-only",
                "--suite",
                manifest["suite"],
                "--ids",
                *map(str, ids),
                "--trials",
                str(manifest["evaluation"]["trials"]),
                "--seed",
                str(seed),
                "--manifest",
                str(starts),
                "--out",
                str(out),
            ],
            check=True,
        )
        tasks = runtime.load(starts)["tasks"]
        for task, spec in manifest["tasks"].items():
            if tasks[task]["name"] != spec["bddl"] or tasks[task]["prompt"] != spec["prompt"]:
                raise ValueError(f"LIBERO task {task} differs between training and evaluation")
        for run_id in ("base", *manifest["runs"]):
            checkpoint = Path(manifest["checkpoint"])
            if run_id != "base":
                if not runtime.complete(root, run_id):
                    raise ValueError(f"Missing final checkpoint for {run_id}")
                checkpoint = root / "checkpoints" / run_id / str(manifest["steps"])
            paired_rollouts(out / run_id, checkpoint, starts, root / "manifest.json", run_id, seed, ids)
