import json
from pathlib import Path
import tempfile

import h5py
import numpy as np
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

from runtime import load, save

CAMERAS = ("agentview_rgb", "eye_in_hand_rgb")
NATIVE_IMAGE_SHAPE = (128, 128, 3)


def features():
    rgb = {"dtype": "image", "shape": NATIVE_IMAGE_SHAPE, "names": ["height", "width", "channel"]}
    return {
        "image": dict(rgb),
        "wrist_image": dict(rgb),
        "state": {"dtype": "float32", "shape": (8,), "names": ["state"]},
        "actions": {"dtype": "float32", "shape": (7,), "names": ["actions"]},
    }


def check_or_create(path, expected):
    if path.exists():
        if load(path) != expected:
            raise ValueError(f"Frozen contract changed: {path}")
    else:
        save(path, expected)


def capture_split(path, suite, task, name, prompt, raw_path, ids, feature_spec):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=f".{path.name}.", dir=path.parent) as staging:
            temporary = Path(staging) / path.name
            dataset = LeRobotDataset.create(
                path.name,
                root=temporary,
                fps=10,
                robot_type="panda",
                features=feature_spec,
                use_videos=False,
            )
            rows = []
            with h5py.File(raw_path) as raw:
                for idx in ids:
                    demo = raw["data"][f"demo_{idx}"]
                    actions = np.asarray(demo["actions"], dtype=np.float32)
                    keep = []
                    for step, action in enumerate(actions):
                        idle = np.linalg.norm(action[:-1]) < 1e-4
                        if idle and (not keep or action[-1] == actions[keep[-1], -1]):
                            continue
                        keep.append(step)
                    observation = demo["obs"]
                    state = np.concatenate(
                        [observation["ee_states"][:], observation["gripper_states"][:]], axis=-1
                    ).astype("float32")
                    main, wrist = [observation[camera][:] for camera in CAMERAS]
                    if (
                        state.shape != (len(actions), 8)
                        or actions.shape != (len(actions), 7)
                        or not keep
                        or main.shape != (len(actions), *NATIVE_IMAGE_SHAPE)
                        or wrist.shape != main.shape
                        or main.dtype != np.uint8
                        or wrist.dtype != np.uint8
                    ):
                        raise ValueError(f"Unexpected recorded tensors for task {task}, demo {idx}")
                    for step in keep:
                        dataset.add_frame(
                            {
                                "image": np.ascontiguousarray(main[step, ::-1, ::-1]),
                                "wrist_image": np.ascontiguousarray(wrist[step, ::-1, ::-1]),
                                "state": state[step],
                                "actions": actions[step],
                                "task": prompt,
                            }
                        )
                    dataset.save_episode()
                    rows.append(
                        {
                            "demo_index": idx,
                            "frames": len(keep),
                            "source_frames": len(actions),
                            "suite": suite,
                            "bddl": name,
                        }
                    )
                    print(f"{path.name} demo {idx}: {len(keep)} frames", flush=True)
            save(temporary / "meta/source_episodes.json", rows)
            save(temporary / "meta/bddl_tasks.json", [name] * len(ids))
            temporary.rename(path)

    raw_records = load(path / "meta/source_episodes.json")
    episodes = [json.loads(line) for line in (path / "meta/episodes.jsonl").read_text().splitlines()]
    if [r["demo_index"] for r in raw_records] != ids or len(episodes) != len(ids):
        raise ValueError(f"Saved demonstration split differs from the manifest: {path}")
    data = []
    offset = 0
    frame_count = sum(record["length"] for record in episodes)
    for idx, (raw, episode) in enumerate(zip(raw_records, episodes, strict=True)):
        if (
            raw["bddl"] != name
            or raw["suite"] != suite
            or episode["episode_index"] != idx
            or episode["length"] != raw["frames"]
            or episode["tasks"] != [prompt]
        ):
            raise ValueError(f"Saved episode {idx} differs from its source: {path}")
        data.append(
            {
                "dataset": str(path),
                "episode": idx,
                "demo": raw["demo_index"],
                "offset": offset,
                "length": episode["length"],
                "dataset_frames": frame_count,
                "bddl": name,
            }
        )
        offset += episode["length"]
    print(f"{path.name}: {len(data)} demos, {frame_count} frames", flush=True)
    return data


def validate_raw_demos(raw_path, suite, task, name, ids):
    with h5py.File(raw_path) as raw:
        group = raw["data"]
        if group.attrs.get("macros_image_convention") != "opengl" or not str(
            group.attrs.get("bddl_file_name")
        ).endswith(f"/{suite}/{name}.bddl"):
            raise ValueError(f"Wrong source recording for {suite} task {task}")
        if set(group) != {f"demo_{i}" for i in ids}:
            raise ValueError(f"Unexpected demonstration IDs for {suite} task {task}")
        for key, demo in group.items():
            if not (demo["rewards"][-1] > 0 and demo["dones"][-1]):
                raise ValueError(f"Unsuccessful raw demo: task {task}, source {key}")
