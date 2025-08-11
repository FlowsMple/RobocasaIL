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
import sys

current_file_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_file_path)
sys.path.append(parent_dir)
from DP.dp_model import DP


def playback_trajectory_with_env_multi_cam(
    env,
    initial_state,
    states,
    video_writers=None,
    video_skip=1,
    camera_names=None,
    first=False,
    verbose=False,
    camera_height=512,
    camera_width=512,
    image_cam=None,
    model=None,
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
        video_skip (int): determines rate at which environment frames are written to video
        camera_names (list): determines which camera(s) are used for rendering. Pass more than
            one to output a video with multiple camera views concatenated horizontally.
        first (bool): if True, only use the first frame of each episode.
    """
    write_video = video_writers is not None
    video_count = 0

    if verbose:
        ep_meta = json.loads(initial_state["ep_meta"])
        lang = ep_meta.get("lang", None)
        if lang is not None:
            print(colored(f"Instruction: {lang}", "green"))
        print(colored("Spawning environment...", "yellow"))
    reset_to(env, initial_state)

    traj_len = states.shape[0]

    print(colored("Running episode...", "yellow"))
    step_lim = 20
    step_cnt = 0

    while step_cnt < step_lim:
        start = time.time()
        step_cnt += 1
        print(f"{step_cnt}/{step_lim}")
        # on-screen render

        # video render
        for cam_name, video_writer in zip(camera_names, video_writers):
            im = env.sim.render(
                height=camera_height, width=camera_width, camera_name=cam_name
            )[::-1]
            video_writer.append_data(im)
            image_cam[cam_name].append(im)
        left_cam = np.moveaxis(image_cam["robot0_agentview_left"][0], -1, 0) / 255
        # right_cam era = (np.moveaxis(image_cam['robot0_agentview_right'][0],-1,0) / 255)
        # hand_camera = (np.moveaxis(image_cam['robot0_eye_in_hand'][0],-1,0) / 255)
        observation = dict(
            left_cam=left_cam,
            # right_camera=right_camera,
            # hand_camera=hand_camera
        )
        observation["agent_pos"] = env.sim.data.qpos[4:12]
        actions = model.get_action(observation)

        for action in actions[0:3]:
            action_dict = dict()
            action_dict["right"] = action[:7]
            action_dict["right_gripper"] = action[7:8]
            raction = env.robots[0].create_action_vector(action_dict)
            obs, _, _, _ = env.step(raction)
            for cam_name, video_writer in zip(camera_names, video_writers):
                im = env.sim.render(
                    height=camera_height, width=camera_width, camera_name=cam_name
                )[::-1]
                video_writer.append_data(im)
                image_cam[cam_name].append(im)
            left_cam = np.moveaxis(image_cam["robot0_agentview_left"][0], -1, 0) / 255
            # right_camera = (np.moveaxis(image_cam['robot0_agentview_right'][0],-1,0) / 255)
            # hand_camera = (np.moveaxis(image_cam['robot0_eye_in_hand'][0],-1,0) / 255)
            observation = dict(
                left_cam=left_cam,
                # right_camera=right_camera,
                # hand_camera=hand_camera
            )
            observation["agent_pos"] = np.append(
                obs["robot0_joint_pos"], obs["robot0_gripper_qpos"][0]
            )
            model.update_obs(observation)


def reset_to(env, state):
    """
    Reset to a specific simulator state.

    Args:
        state (dict): current simulator state that contains one or more of:
            - states (np.ndarray): initial state of the mujoco environment
            - model (str): mujoco scene xml

    Returns:
        observation (dict): observation dictionary after setting the simulator state (only
            if "states" is in @state)
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
        # this reset is necessary.
        # while the call to env.reset_from_xml_string does call reset,
        # that is only a "soft" reset that doesn't actually reload the model.
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
        # hide teleop visualization after restoring from model
        # env.sim.model.site_rgba[env.eef_site_id] = np.array([0., 0., 0., 0.])
        # env.sim.model.site_rgba[env.eef_cylinder_id] = np.array([0., 0., 0., 0.])
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

    # if should_ret:
    #     # only return obs if we've done a forward call - otherwise the observations will be garbage
    #     return get_observation()
    return None


def playback_dataset(
    hdf5_file, args, write_video: bool, src_path: str, processed_path: str, model
):
    # create environment only if not playing back with observations
    idx, hdf5_file = hdf5_file
    processed_file = os.path.join(processed_path, f"episode{idx}.hdf5")
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)

    env_meta = get_env_metadata_from_dataset(dataset_path=hdf5_file)
    controller_path = os.path.join(
        os.path.dirname(robosuite.__file__),
        "controllers/config/robots/default_pandaomron_qpos.json",
    )
    env_meta["env_kwargs"][
        "controller_configs"
    ] = robosuite.controllers.load_composite_controller_config(
        controller=controller_path
    )
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
        src_ep_path = os.path.join(ep_file, "eval_videos")
        if not os.path.exists(src_ep_path):
            os.makedirs(src_ep_path)
        else:
            os.system(f"rm -rf {src_ep_path}/*")
            # raise ValueError("Episode {} already exists".format(ep))

        video_writers = []
        fps = int(50 / args.video_skip)
        for camera in args.render_image_names:
            video_path = os.path.join(src_ep_path, "{}.mp4".format(camera))
            video_writer = imageio.get_writer(
                video_path, fps=fps, codec="h264", pixelformat="yuv420p"
            )
            video_writers.append(video_writer)

        image_cam = dict()
        for name in args.render_image_names:
            image_cam[name] = []
        # prepare initial state to reload from
        states = f["data/{}/states".format(ep)][()]
        initial_state = dict(states=states[0])
        initial_state["model"] = f["data/{}".format(ep)].attrs["model_file"]
        initial_state["ep_meta"] = f["data/{}".format(ep)].attrs.get("ep_meta", None)

        if args.extend_states:
            states = np.concatenate((states, [states[-1]] * 50))

        playback_trajectory_with_env_multi_cam(
            env=env,
            initial_state=initial_state,
            states=states,
            video_writers=video_writers,
            video_skip=args.video_skip,
            camera_names=args.render_image_names,
            first=args.first,
            verbose=args.debug,
            camera_height=args.camera_height,
            camera_width=args.camera_width,
            image_cam=image_cam,
            model=model,
        )
        for video_writer in video_writers:
            video_writer.close()
    f.close()
    if write_video:
        print(colored("Saved videos to {}".format(src_ep_path), "green"))

    if env is not None:
        env.close()
    # import pdb
    # pdb.set_trace()


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

    n_obs_steps = 3
    n_action_steps = 6
    # ckpt_path = "/workspace/IL/checkpoints/DP/bs-128/only_left_camera/OpenOven-robocasa-100-0/600.ckpt"
    ckpt_path = "/workspace/IL/robocasa/policy/DP/checkpoints/OpenOven-1-20-0/600.ckpt"
    model = DP(ckpt_path, n_obs_steps=n_obs_steps, n_action_steps=n_action_steps)
    # import pdb
    # pdb.set_trace()
    hdf5_files.sort()
    hdf5_files = enumerate(hdf5_files)
    for hdf5_file in tqdm(hdf5_files):
        playback_dataset(hdf5_file, args, write_video, src_path, processed_path, model)


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

    # How often to write video frames during the playback
    parser.add_argument(
        "--video_skip",
        type=int,
        default=1,
        help="render frames to video every n steps",
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

    # Only use the first frame of each episode
    parser.add_argument(
        "--first",
        action="store_true",
        help="only use the first frame of each episode",
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
