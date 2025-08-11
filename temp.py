import os
import json
import time
import random
import argparse
from functools import partial

import h5py
import imageio
import numpy as np
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from termcolor import colored

import robosuite
from robocasa.scripts.dataset_scripts.playback_dataset import (
    get_env_metadata_from_dataset,
)
import cv2


def images_encoding(imgs):
    encode_data = []
    padded_data = []
    max_len = 0
    for i in range(len(imgs)):
        success, encoded_image = cv2.imencode(".jpg", imgs[i])
        jpeg_data = encoded_image.tobytes()
        encode_data.append(jpeg_data)
        max_len = max(max_len, len(jpeg_data))
    # padding
    for i in range(len(imgs)):
        padded_data.append(encode_data[i].ljust(max_len, b"\0"))
    return encode_data, max_len


def playback_trajectory_with_env_multi_cam(
    env,
    initial_state,
    states,
    actions=None,
    video_writers=None,
    camera_names=None,
    verbose=False,
    camera_height=512,
    camera_width=512,
    image_cam=None,
    obs_actions=None,
):
    """
    Helper function to playback a single trajectory using the simulator environment.
    If @actions are not None, it will play them open-loop after loading the initial state.
    Otherwise, @states are loaded one by one.

    Args:
        env (instance of EnvBase): environment
        initial_state (dict): initial simulation state to load
        states (np.array): array of simulation states to load
        actions (np.array): if provided, play actions back open-loop instead of using @states
        render (bool): if True, render on-screen
        video_writers (list of imageio writers): video writers
        camera_names (list): determines which camera(s) are used for rendering. Pass more than
            one to output a video with multiple camera views concatenated horizontally.
    """

    # load the initial state
    ## this reset call doesn't seem necessary.
    ## seems ok to remove but haven't fully tested it.
    ## removing for now
    # env.reset()

    if verbose:
        ep_meta = json.loads(initial_state["ep_meta"])
        lang = ep_meta.get("lang", None)
        if lang is not None:
            print(colored(f"Instruction: {lang}", "green"))
        print(colored("Spawning environment...", "yellow"))
    reset_to(env, initial_state)

    traj_len = states.shape[0]
    action_playback = actions is not None
    if action_playback:
        assert states.shape[0] == actions.shape[0]

    print(colored("Running episode...", "yellow"))
    for i in range(traj_len):
        start = time.time()

        if action_playback:
            # import pdb
            # pdb.set_trace()
            obs, _, _, _ = env.step(actions[i])
            obs_actions.append(env.sim.data.qpos[4:12])
        else:
            reset_to(env, {"states": states[i]})

        for cam_name, video_writer in zip(camera_names, video_writers):
            im = env.sim.render(
                height=camera_height, width=camera_width, camera_name=cam_name
            )[::-1]
            video_writer.append_data(im)
            image_cam[cam_name].append(im)

    reset_to(env, initial_state)
    for i in range(traj_len):
        start = time.time()

        if action_playback:
            # import pdb
            # pdb.set_trace()
            env.sim.data.qpos[4:12] = obs_actions[i]
            env.sim.forward()
            # obs,_,_,_ = env.step(actions[i])
            # obs_actions.append(env.sim.data.qpos[4:12])
        else:
            reset_to(env, {"states": states[i]})

        for cam_name, video_writer in zip(camera_names, video_writers):
            im = env.sim.render(
                height=camera_height, width=camera_width, camera_name=cam_name
            )[::-1]
            video_writer.append_data(im)
            image_cam[cam_name].append(im)


def reset_to(env, state):
    """
    Reset to a specific simulator state.

    Args:
        state (dict): current simulator state that contains one or more of:
            - states (np.ndarray): initial state of the mujoco environment
            - model (str): mujoco scene xml

    """
    should_ret = False
    if "model" in state:
        if state.get("ep_meta", None) is not None:
            # set relevant episode information
            ep_meta = json.loads(state["ep_meta"])
        else:
            ep_meta = {}
        if hasattr(env, "set_attrs_from_ep_meta"):  # older versions had this function
            env.set_attrs_from_ep_meta(ep_meta)
        elif hasattr(env, "set_ep_meta"):  # newer versions
            env.set_ep_meta(ep_meta)
        env.reset()
        robosuite_version_id = int(robosuite.__version__.split(".")[1])
        if robosuite_version_id <= 3:
            from robosuite.utils.mjcf_utils import postprocess_model_xml

            xml = postprocess_model_xml(state["model"])
        else:
            # v1.4 and above use the class-based edit_model_xml function
            xml = env.edit_model_xml(state["model"])

        env.reset_from_xml_string(xml)
        env.sim.reset()
    if "states" in state:
        env.sim.set_state_from_flattened(state["states"])
        env.sim.forward()
        should_ret = True

    # update state as needed
    if hasattr(env, "update_sites"):
        # older versions of environment had update_sites function
        env.update_sites()
    if hasattr(env, "update_state"):
        # later versions renamed this to update_state
        env.update_state()

    return None


def playback_dataset(
    hdf5_file, args, write_video: bool, src_path: str, processed_path: str
):
    # create environment only if not playing back with observations
    idx, hdf5_file = hdf5_file
    processed_file = os.path.join(processed_path, f"episode{idx}.hdf5")
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)

    env_meta = get_env_metadata_from_dataset(dataset_path=hdf5_file)
    # # if args.use_abs_actions:
    # env_meta["env_kwargs"]["controller_configs"][
    #     "control_delta"
    # ] = False  # absolute action space

    env_kwargs = env_meta["env_kwargs"]
    env_kwargs["env_name"] = env_meta["env_name"]
    env_kwargs["has_renderer"] = False
    env_kwargs["renderer"] = "mjviewer"
    env_kwargs["has_offscreen_renderer"] = write_video
    env_kwargs["use_camera_obs"] = False
    env_kwargs["generative_textures"] = False

    if args.debug:
        print(
            colored(
                "Initializing environment for {}...".format(env_kwargs["env_name"]),
                "yellow",
            )
        )

    env = robosuite.make(**env_kwargs)

    f = h5py.File(hdf5_file, "r")

    # list of all demonstration episodes (sorted in increasing number order)
    if args.filter_key is not None:
        print("using filter key: {}".format(args.filter_key))
        demos = [
            elem.decode("utf-8")
            for elem in np.array(f["mask/{}".format(args.filter_key)])
        ]
    elif "data" in f.keys():
        demos = list(f["data"].keys())

    inds = np.argsort([int(elem[5:]) for elem in demos])
    demos = [demos[i] for i in inds]

    # maybe reduce the number of demonstrations to playback
    if args.n is not None:
        random.shuffle(demos)
        demos = demos[: args.n]

    for ind in range(len(demos)):
        ep = demos[ind]
        if len(demos) > 1:
            ep_file = "/".join(hdf5_file.split("/")[:-2]) + "/" + ep
            print(colored("\nPlaying back episode: {}".format(ep), "yellow"))
        else:
            ep_file = "/".join(hdf5_file.split("/")[:-1])
        src_ep_path = os.path.join(ep_file, "videos")
        if not os.path.exists(src_ep_path):
            os.makedirs(src_ep_path)
        else:
            os.system(f"rm -rf {src_ep_path}/*")
            # raise ValueError("Episode {} already exists".format(ep))

        video_writers = []
        fps = 50
        for camera in args.render_image_names:
            video_path = os.path.join(src_ep_path, "{}.mp4".format(camera))
            video_writer = imageio.get_writer(
                video_path, fps=fps, codec="h264", pixelformat="yuv420p"
            )
            video_writers.append(video_writer)

        image_cam = dict()
        for name in args.render_image_names:
            image_cam[name] = []
        obs_actions = []
        # prepare initial state to reload from
        states = f["data/{}/states".format(ep)][()]
        initial_state = dict(states=states[0])
        initial_state["model"] = f["data/{}".format(ep)].attrs["model_file"]
        initial_state["ep_meta"] = f["data/{}".format(ep)].attrs.get("ep_meta", None)

        if args.extend_states:
            states = np.concatenate((states, [states[-1]] * 50))

        # supply actions if using open-loop action playback
        actions = None
        assert not (
            args.use_actions and args.use_abs_actions
        )  # cannot use both relative and absolute actions
        if args.use_actions:
            actions = f["data/{}/actions".format(ep)][()]
        elif args.use_abs_actions:
            actions = f["data/{}/actions_abs".format(ep)][()]  # absolute actions
        playback_trajectory_with_env_multi_cam(
            env=env,
            initial_state=initial_state,
            states=states,
            actions=actions,
            video_writers=video_writers,
            camera_names=args.render_image_names,
            verbose=args.debug,
            camera_height=args.camera_height,
            camera_width=args.camera_width,
            image_cam=image_cam,
            obs_actions=obs_actions,
        )
        for video_writer in video_writers:
            video_writer.close()
    with h5py.File(processed_file, "w") as sav:
        image = sav.create_group("observation")
        joint_action = sav.create_group("joint_action")
        obs_actions = np.array(obs_actions)
        joint_action.create_dataset("right_arm", data=obs_actions[:, :7])
        joint_action.create_dataset("right_gripper", data=obs_actions[:, 7:8])
        joint_action.create_dataset("vector", data=obs_actions)
        encode_data, max_len = images_encoding(image_cam[args.render_image_names[0]])
        image.create_dataset("left_camera/rgb", data=encode_data, dtype=f"S{max_len}")
        encode_data, max_len = images_encoding(image_cam[args.render_image_names[1]])
        image.create_dataset("right_camera/rgb", data=encode_data, dtype=f"S{max_len}")
        encode_data, max_len = images_encoding(image_cam[args.render_image_names[2]])
        image.create_dataset("head_camera/rgb", data=encode_data, dtype=f"S{max_len}")
    f.close()
    if write_video:
        print(colored("Saved videos to {}".format(src_ep_path), "green"))

    if env is not None:
        env.close()


def main(args):
    # some arg checking
    write_video = True
    if args.dataset.endswith(".hdf5"):
        src_path = os.path.dirname("/".join(args.dataset.split("/")[:-1]))
    else:
        src_path = args.dataset
    processed_path = os.path.join(src_path, "processed_data")
    # Auto-fill camera rendering info if not specified
    if args.render_image_names is None:
        # We fill in the automatic values
        env_meta = get_env_metadata_from_dataset(dataset_path=args.dataset)
        args.render_image_names = "robot0_agentview_center"

    if args.use_obs:
        assert write_video, "playback with observations can only write to video"
        assert (
            not args.use_actions and not args.use_abs_actions
        ), "playback with observations is offline and does not support action playback"

    hdf5_files = []
    if args.dataset.endswith(".hdf5"):
        hdf5_files.append(args.dataset)
    else:
        for root, dirs, files in os.walk(args.dataset):
            for dir in dirs:
                if dir.startswith("demo"):
                    dirs.remove(dir)
            hdf5_files.extend(
                [os.path.join(root, f) for f in files if f.endswith(".hdf5")]
            )
    hdf5_files.sort()
    hdf5_files = hdf5_files[:20]
    hdf5_files = enumerate(hdf5_files)
    if args.debug:
        for hdf5_file in tqdm(hdf5_files):
            playback_dataset(hdf5_file, args, write_video, src_path, processed_path)
    else:
        process_map(
            partial(
                playback_dataset,
                args=args,
                write_video=write_video,
                src_path=src_path,
                processed_path=processed_path,
            ),
            hdf5_files,
            max_workers=args.max_workers,
            desc="Generating videos",
        )


def get_playback_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="path to hdf5 dataset or directory of hdf5 files",
    )
    parser.add_argument(
        "--filter_key",
        type=str,
        default=None,
        help="(optional) filter key, to select a subset of trajectories in the file",
    )

    # number of trajectories to playback. If omitted, playback all of them.
    parser.add_argument(
        "--n",
        type=int,
        default=None,
        help="(optional) stop after n trajectories are played",
    )

    # Use image observations instead of doing playback using the simulator env.
    parser.add_argument(
        "--use-obs",
        action="store_true",
        help="visualize trajectories with dataset image observations instead of simulator",
    )

    # Playback stored dataset actions open-loop instead of loading from simulation states.
    parser.add_argument(
        "--use-actions",
        action="store_true",
        help="use open-loop action playback instead of loading sim states",
    )

    # Playback stored dataset absolute actions open-loop instead of loading from simulation states.
    parser.add_argument(
        "--use-abs-actions",
        action="store_true",
        help="use open-loop action playback with absolute position actions instead of loading sim states",
    )

    # Dump a video of the dataset playback to the specified path
    parser.add_argument(
        "--video_path",
        type=str,
        default=None,
        help="(optional) render trajectories to this video file path",
    )

    # camera names to render, or image observations to use for writing to video
    parser.add_argument(
        "--render_image_names",
        type=str,
        nargs="+",
        default=[
            "robot0_agentview_left",
            "robot0_agentview_right",
            "robot0_eye_in_hand",
        ],
        help="(optional) camera name(s) / image observation(s) to use for rendering on-screen or to video. Default is"
        "None, which corresponds to a predefined camera for each env type",
    )

    parser.add_argument(
        "--extend_states",
        action="store_true",
        help="play last step of episodes for 50 extra frames",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="log additional information",
    )

    parser.add_argument(
        "--camera_height",
        type=int,
        default=240,
        help="(optional, for offscreen rendering) height of image observations",
    )

    parser.add_argument(
        "--camera_width",
        type=int,
        default=320,
        help="(optional, for offscreen rendering) width of image observations",
    )

    parser.add_argument(
        "--max_workers",
        type=int,
        default=os.cpu_count() // 4,
        help="maximum number of workers to use for video generation",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_playback_args()
    main(args)
