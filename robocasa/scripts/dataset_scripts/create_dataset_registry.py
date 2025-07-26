import os
from collections import OrderedDict
from pathlib import Path
import h5py
import numpy as np
import json
from tqdm import tqdm
import robocasa
import robocasa.macros as macros


# scan for datasets

ds_base_path = macros.DATASET_BASE_PATH or os.path.join(os.path.dirname(robocasa.__path__[0]), "datasets")
v05_base_path = os.path.join(ds_base_path, "v0.5")
composite_base_path = os.path.join(v05_base_path, "train", "composite")
atomic_base_path = os.path.join(v05_base_path, "train", "atomic")

ds_paths = []
print("Scanning for datasets...")
for root, dirs, files in os.walk(atomic_base_path):
    for f in files:
        if f == "demo.hdf5":
            ds_paths.append(os.path.join(root, f))
ds_paths.sort()

print("Reading configs...")
ds_configs = {}
for ds_path in tqdm(ds_paths):
    is_mg = ("/mg/" in ds_path)

    f = h5py.File(ds_path)

    # get the env name
    try:
        # env_name = f["data"].attrs["env"]
        env_args = json.loads(f["data"].attrs["env_args"])
        env_name = env_args["env_name"]
    except Exception as e:
        print("Exception reading", ds_path)
        f.close()
        continue
    
    if env_name not in ds_configs:
        ds_configs[env_name] = dict()

    if is_mg:
        if "mg_path" in ds_configs[env_name]:
            print("mg path already detected!", ds_path)
            continue
    else:
        if "human_path" in ds_configs[env_name]:
            print("human path already detected!", ds_path)
            continue
    
    # get the traj_lengths
    try:
        demos = sorted(list(f["data"].keys()))
        traj_lengths = []
        action_min = np.inf
        action_max = -np.inf
        for ep in demos:
            traj_lengths.append(f["data/{}/actions".format(ep)].shape[0])
            action_min = min(action_min, np.min(f["data/{}/actions".format(ep)][()]))
            action_max = max(action_max, np.max(f["data/{}/actions".format(ep)][()]))
        traj_lengths = np.array(traj_lengths)
    except Exception as e:
        print("Exception reading...")
        f.close()
        continue

    f.close()

    # only include datasets that have at least 100 trajectories
    if len(traj_lengths) < 100:
        continue

    # compute dataset horizon
    mean, std = np.mean(traj_lengths), np.std(traj_lengths)
    # round to next hundred steps
    horizon = int(((mean + 2 * std) // 100 * 100) + 100)
    
    rel_dir = os.path.relpath(os.path.dirname(ds_path), ds_base_path)

    if is_mg:
        ds_configs[env_name]["mg_path"] = rel_dir
    else:
        ds_configs[env_name]["horizon"] = horizon
        ds_configs[env_name]["human_path"] = rel_dir
    
print()
print()
print()
for env_name, cfg in ds_configs.items():
    text = f"{env_name}=dict(\n"
    for k, v in cfg.items():
        v_str = repr(v).replace("\'", "\"")
        text += f"    {k}={v_str},\n"
    text += "),"
    print(text)
