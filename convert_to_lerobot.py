import os
import json
import random
import shutil
import argparse
from pathlib import Path
from typing import Callable
from functools import partial

import h5py
import numpy as np
import torch
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map


AGENTVIEW_LEFT = "robot0_agentview_left.mp4"
AGENTVIEW_RIGHT = "robot0_agentview_right.mp4"
EYE_IN_HAND = "robot0_eye_in_hand.mp4"

FEATURES = {
    "observation.images.agentview_left": {
        "dtype": "video",
        "shape": [224, 224, 3],
        "names": ["height", "width", "channel"],
        "video_info": {
            "video.fps": 25.0,
            "video.codec": "h264",
            "video.pix_fmt": "yuv420p",
            "video.is_depth_map": False,
            "has_audio": False,
        },
    },
    "observation.images.agentview_right": {
        "dtype": "video",
        "shape": [224, 224, 3],
        "names": ["height", "width", "channel"],
        "video_info": {
            "video.fps": 25.0,
            "video.codec": "h264",
            "video.pix_fmt": "yuv420p",
            "video.is_depth_map": False,
            "has_audio": False,
        },
    },
    "observation.images.eye_in_hand": {
        "dtype": "video",
        "shape": [224, 224, 3],
        "names": ["height", "width", "channel"],
        "video_info": {
            "video.fps": 25.0,
            "video.codec": "h264",
            "video.pix_fmt": "yuv420p",
            "video.is_depth_map": False,
            "has_audio": False,
        },
    },
    "observation.state": {
        "dtype": "float32",
        "shape": [8],
        "names": [
            "robot0_joint1",
            "robot0_joint2",
            "robot0_joint3",
            "robot0_joint4",
            "robot0_joint5",
            "robot0_joint6",
            "robot0_joint7",
            "gripper0_right_finger_joint",
        ],
    },
    "action": {
        "dtype": "float32",
        "shape": [8],
        "names": [
            "robot0_joint1",
            "robot0_joint2",
            "robot0_joint3",
            "robot0_joint4",
            "robot0_joint5",
            "robot0_joint6",
            "robot0_joint7",
            "gripper0_right_finger_joint",
        ],
    },
    "episode_index": {
        "dtype": "int64",
        "shape": [1],
        "names": None,
    },
    "frame_index": {
        "dtype": "int64",
        "shape": [1],
        "names": None,
    },
    "index": {
        "dtype": "int64",
        "shape": [1],
        "names": None,
    },
    "task_index": {
        "dtype": "int64",
        "shape": [1],
        "names": None,
    },
}


def load_local_dataset(
    demo_and_file: tuple, src_path: str, task_id: str, video_skip: int, format: str
) -> list | None:
    demo_id, hdf5_file = demo_and_file
    f = h5py.File(hdf5_file, "r")
    if format == "robocasa":
        ob_dir = Path("/".join(hdf5_file.split("/")[:-2])) / f"{demo_id}"
    elif format == "lightwheel":
        demo_dir = hdf5_file.split("/")[-2]
        ob_dir = Path(src_path) / f"{task_id}" / f"{demo_dir}"

    # Note: the state is downsampled by video_skip
    # state_pos = np.array(f["data/{}/states".format(demo_id)][::video_skip, 1:14])
    state_joint_pos = np.array(
        f["data/{}/obs/robot0_joint_pos".format(demo_id)][::video_skip]
    )
    state_gripper = np.array(
        f["data/{}/obs/robot0_gripper_qpos".format(demo_id)][::video_skip, 0]
    ).reshape(-1, 1)
    states_value = np.hstack([state_joint_pos, state_gripper]).astype(np.float32)
    demo_len = states_value.shape[0]
    action_value = np.zeros((demo_len, 8))
    action_value[: demo_len - 1, :7] = np.array(
        f["data/{}/obs/robot0_joint_pos".format(demo_id)][::video_skip][1:]
    )
    action_value[-1, :7] = action_value[-2, :7]
    action_value[:, 7] = f["data/{}/actions".format(demo_id)][::video_skip, 6]
    action_value = action_value.astype(np.float32)

    frames = [
        {
            "observation.state": states_value[i],
            "action": action_value[i],
        }
        for i in range(len(states_value))
    ]

    v_path = ob_dir / "videos"
    videos = {
        "observation.images.agentview_left": v_path / AGENTVIEW_LEFT,
        "observation.images.agentview_right": v_path / AGENTVIEW_RIGHT,
        "observation.images.eye_in_hand": v_path / EYE_IN_HAND,
    }

    task = get_task_instruction(f, demo_id)

    return frames, videos, task


def get_task_instruction(f: h5py.File, task_demo: str) -> dict:
    """Get task language instruction"""
    ep_meta = json.loads(f["data/{}".format(task_demo)].attrs["ep_meta"])
    task_instruction = ep_meta["lang"]
    print(f"Get Task Instruction <{task_instruction}>")
    return task_instruction


def convert_robocasa(args):
    if args.tgt_repo_id is None:
        repo_id = f"robocasa/{args.src_path.split('/')[-1]}"
    else:
        repo_id = f"robocasa/{args.tgt_repo_id}"

    if os.path.exists(f"{args.tgt_path}/{repo_id}"):
        raise ValueError(f"Dataset {repo_id} already exists")

    hdf5_files = []
    for root, dirs, files in os.walk(args.src_path):
        for dir in dirs:
            if not dir.startswith("demo"):
                files = os.listdir(os.path.join(root, dir))
                if "mg" in args.src_path:
                    hdf5_files.extend(
                        [
                            os.path.join(root, dir, f)
                            for f in files
                            if f.endswith(".hdf5")
                        ]
                    )
                else:
                    hdf5_files.extend(
                        [
                            os.path.join(root, dir, f)
                            for f in files
                            if f.endswith(".hdf5") and "mg" not in root
                        ]
                    )
    hdf5_files.sort()
    import pdb

    pdb.set_trace()
    for hdf5_file in tqdm(hdf5_files):
        f = h5py.File(hdf5_file, "r")

        # list of all demonstration episodes (sorted in increasing number order)
        if args.filter_key is not None:
            print("NOTE: using filter key {}".format(args.filter_key))
            demos = [
                elem.decode("utf-8")
                for elem in np.array(f["mask/{}".format(args.filter_key)])
            ]
        elif "data" in f.keys():
            demos = sorted(list(f["data"].keys()))

        inds = np.argsort([int(elem[5:]) for elem in demos])
        demos = [demos[i] for i in inds]

        # maybe reduce the number of demonstrations to playback
        if args.n is not None:
            random.shuffle(demos)
            demos = demos[: args.n]

        if args.style_id is not None:
            demos = [
                demo
                for demo in demos
                if json.loads(f["data"][demo].attrs["ep_meta"])["style_id"]
                == args.style_id
            ]

        task_id = None

        if args.debug:
            raw_datasets = [
                load_local_dataset(
                    (demo, hdf5_file),
                    args.src_path,
                    task_id,
                    args.video_skip,
                    args.format,
                )
                for demo in tqdm(demos)
            ]
        else:
            raw_datasets = process_map(
                partial(
                    load_local_dataset,
                    src_path=args.src_path,
                    task_id=task_id,
                    video_skip=args.video_skip,
                    format=args.format,
                ),
                [(demo, hdf5_file) for demo in demos],
                max_workers=os.cpu_count() // 2,
                desc="Generating local dataset",
            )
        import pdb

        pdb.set_trace()


def convert_lightwheel(args):
    repo_id = f"robocasa/{args.src_path.split('/')[-1]}"

    if os.path.exists(f"{args.tgt_path}/{repo_id}"):
        raise ValueError(f"Dataset {repo_id} already exists")

    task_ids = sorted(os.listdir(args.src_path))
    demo = "demo_1"

    for task_id in task_ids[: args.n]:
        episode_ids = sorted(os.listdir(os.path.join(args.src_path, task_id)))
        hdf5_files = [
            os.path.join(args.src_path, task_id, episode_id, "ep_demo.hdf5")
            for episode_id in episode_ids
        ]

        if args.debug:
            raw_datasets = [
                load_local_dataset(
                    (demo, hdf5_file),
                    args.src_path,
                    task_id,
                    args.video_skip,
                    args.format,
                )
                for hdf5_file in tqdm(hdf5_files)
            ]
        else:
            raw_datasets = process_map(
                partial(
                    load_local_dataset,
                    src_path=args.src_path,
                    task_id=task_id,
                    video_skip=args.video_skip,
                    format=args.format,
                ),
                [(demo, hdf5_file) for hdf5_file in hdf5_files],
                max_workers=os.cpu_count() // 2,
                desc="Generating local dataset",
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src_path",
        type=str,
        default="./data/OpenOven",
    )
    parser.add_argument(
        "--task_id",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--filter_key",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--n",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--tgt_path",
        type=str,
        default="datasets/lerobot",
    )
    parser.add_argument(
        "--tgt_repo_id",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--video_skip",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="robocasa",
    )
    parser.add_argument(
        "--style_id",
        type=int,
        default=None,
    )
    args = parser.parse_args()

    if args.format == "robocasa":
        convert_robocasa(args)
    elif args.format == "lightwheel":
        convert_lightwheel(args)
