import argparse
from collections import deque
import json
from pathlib import Path
import runpy

import h5py
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    parser.add_argument("--ids", type=int, nargs="+", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--trials", type=int, default=50)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=19397)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int)
    args = parser.parse_args()
    if args.suite != "libero_90" or args.trials != 50 or len(set(args.ids)) != len(args.ids):
        raise ValueError("Expected distinct LIBERO-90 tasks and 50 starts")
    api = runpy.run_path("dart/examples/libero-view/main.py")
    suite = api["benchmark"].get_benchmark_dict()[args.suite]()
    tasks = {}
    for task_id in args.ids:
        task = suite.get_task(task_id)
        states = np.asarray(suite.get_task_init_states(task_id))
        raw_path = Path("data") / args.suite / (task.name + "_demo.hdf5")
        with h5py.File(raw_path) as raw:
            starts = [np.asarray(demo["states"][0]) for demo in raw["data"].values()]
        excluded = [
            i
            for i, state in enumerate(states)
            if any(
                state.shape == start.shape and np.allclose(state[1:], start[1:], rtol=0, atol=1e-6)
                for start in starts
            )
        ]
        indices = [i for i in range(len(states)) if i not in excluded][: args.trials]
        if len(indices) != args.trials:
            raise ValueError("Insufficient starts disjoint from demonstrations for task %s" % task_id)
        tasks[str(task_id)] = dict(
            name=task.name, prompt=task.language, indices=indices, excluded=excluded
        )
    manifest = dict(
        suite=args.suite,
        tasks=tasks,
        seed=args.seed,
        view="original",
        trials=args.trials,
        horizon=400,
        replan_steps=5,
    )
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    if args.manifest.exists():
        previous = json.loads(args.manifest.read_text())
        if (
            any(previous.get(key) != value for key, value in manifest.items() if key != "tasks")
            or set(previous.get("tasks", {})) != set(tasks)
            or any(
                previous["tasks"][task].get(key) != value
                for task, spec in tasks.items()
                for key, value in spec.items()
            )
        ):
            raise ValueError("Evaluation starts or protocol changed")
    else:
        args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    if args.prepare_only:
        return
    count = args.trials - args.offset if args.count is None else args.count
    if args.offset < 0 or count <= 0 or args.offset + count > args.trials:
        raise ValueError("Invalid rollout shard")
    args.out.mkdir(parents=True, exist_ok=True)
    records_path = args.out / "episodes.jsonl"
    records = (
        [json.loads(line) for line in records_path.read_text().splitlines()]
        if records_path.exists()
        else []
    )
    expected = {
        (task_id, i)
        for task_id in args.ids
        for i in tasks[str(task_id)]["indices"][args.offset : args.offset + count]
    }
    done = {(row["task_id"], row["state_index"]) for row in records}
    if len(done) != len(records) or not done <= expected:
        raise ValueError("Existing rollouts contain duplicate or unexpected starts")
    client = api["_websocket_client_policy"].WebsocketClientPolicy("127.0.0.1", args.port)
    for task_id in args.ids:
        task = suite.get_task(task_id)
        initial_states = suite.get_task_init_states(task_id)
        env, prompt = api["_get_libero_env"](task, 256, args.seed, None)
        try:
            for state_index in tasks[str(task_id)]["indices"][args.offset : args.offset + count]:
                if (task_id, state_index) in done:
                    continue
                np.random.seed(args.seed)
                env.seed(args.seed)
                env.reset()
                observation = env.set_init_state(initial_states[state_index])
                for _ in range(10):
                    observation, _, _, _ = env.step(api["LIBERO_DUMMY_ACTION"])
                actions = deque()
                for step in range(manifest["horizon"]):
                    if not actions:
                        images = []
                        for name in ("agentview_image", "robot0_eye_in_hand_image"):
                            image = np.ascontiguousarray(observation[name][::-1, ::-1])
                            images.append(
                                api["image_tools"].convert_to_uint8(
                                    api["image_tools"].resize_with_pad(image, 224, 224)
                                )
                            )
                        request = {
                            "observation/image": images[0],
                            "observation/wrist_image": images[1],
                            "observation/state": np.concatenate(
                                [
                                    observation["robot0_eef_pos"],
                                    api["_quat2axisangle"](observation["robot0_eef_quat"].copy()),
                                    observation["robot0_gripper_qpos"],
                                ]
                            ),
                            "prompt": str(prompt),
                            "pilot_seed": args.seed + task_id * 1000000 + state_index * 1000 + step,
                        }
                        chunk = client.infer(request)["actions"]
                        if len(chunk) < manifest["replan_steps"] or not np.isfinite(chunk).all():
                            raise ValueError("Invalid policy actions")
                        actions.extend(chunk[: manifest["replan_steps"]])
                    observation, _, success, _ = env.step(actions.popleft().tolist())
                    if success or step + 1 == manifest["horizon"]:
                        record = dict(
                            task_id=task_id,
                            state_index=state_index,
                            success=bool(success),
                            steps=step + 1,
                        )
                        break
                with records_path.open("a") as stream:
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                records.append(record)
                print(json.dumps(record), flush=True)
        finally:
            env.close()
    if {(row["task_id"], row["state_index"]) for row in records} != expected:
        raise ValueError("Incomplete rollout shard")
    summary = {
        str(task_id): dict(
            episodes=count,
            successes=sum(bool(row["success"]) for row in records if row["task_id"] == task_id),
        )
        for task_id in args.ids
    }
    (args.out / "complete.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
