import yaml
import os
import numpy as np

import robocasa


def random_sample_guaranteed(data, num_samples):
    """
    Copied from Geimini

    Randomly samples from a list, ensuring each element is represented at least once.

    Args:
        data: The list to sample from.
        num_samples: The total number of samples to generate.

    Returns:
        A list containing the random samples.
    """
    unique_elements = list(data)  # Get unique elements
    rng.shuffle(unique_elements)

    # if num_samples < len(unique_elements):
    #     raise ValueError(
    #         "Number of samples must be at least the number of unique elements."
    #     )

    # Start with each unique element once
    sample = list(unique_elements)[:num_samples]

    # Perform remaining random selections with replacement
    remaining_samples = num_samples - len(unique_elements)
    if remaining_samples > 0:
        sample.extend(
            rng.choice(data, size=remaining_samples)
        )  # Use random.choices for replacement

    # Shuffle for a completely random appearance
    rng.shuffle(sample)

    result = []
    for item in sample:
        if isinstance(item, str):
            result.append(str(item))
        else:
            result.append(item)
    return result


# Example usage:
NUM_TRAIN_STYTLES = 50
styles_base_path = os.path.join(
    robocasa.__path__[0], "models/assets/scenes/kitchen_styles"
)
fixtures_reg_base_path = os.path.join(
    robocasa.__path__[0], "models/assets/fixtures/fixture_registry"
)

rng = np.random.default_rng()

all_fixtures = {}
train_fixtures = {}
test_fixtures = {}

for style_i in range(1, 11):
    style_path = os.path.join(styles_base_path, "test", f"style{style_i:03d}.yaml")

    with open(style_path, "r") as f:
        style_dict = yaml.safe_load(f)

    for (k, v) in style_dict.items():
        if k not in test_fixtures:
            test_fixtures[k] = []
        test_fixtures[k].append(v)

for fixture_name in test_fixtures.keys():
    fixture_reg_path = os.path.join(fixtures_reg_base_path, f"{fixture_name}.yaml")
    if not os.path.exists(fixture_reg_path):
        continue
    with open(fixture_reg_path, "r") as f:
        fixture_reg = yaml.safe_load(f)
    if "default" in fixture_reg:
        del fixture_reg["default"]
    all_fixtures[fixture_name] = list(fixture_reg.keys())

for fixture_name in all_fixtures:
    all_items = all_fixtures[fixture_name]
    test_items = test_fixtures[fixture_name]
    if fixture_name == "cabinet":
        all_cabinet_panels = [
            item for item in all_items if item.startswith("CabinetDoorPanel")
        ]
        test_cabinet_panels = [
            default_item
            for item in test_items
            for default_item in item["default"]
            if default_item.startswith("CabinetDoorPanel")
        ]
        train_cabinet_panels = [
            item for item in all_cabinet_panels if item not in test_cabinet_panels
        ]
        train_fixtures["cab_panel"] = train_cabinet_panels

        all_handles = [item for item in all_items if item.startswith("CabinetHandle")]
        test_handles = [
            default_item
            for item in test_items
            for default_item in item["default"]
            if default_item.startswith("CabinetHandle")
        ]
        train_handles = [item for item in all_handles if item not in test_handles]
        train_fixtures["cab_handle"] = train_handles

        train_cab_textures = []
        for tex_i in range(1, 101):
            train_cab_textures.append(f"gentex{tex_i:03d}")
        train_fixtures["cab_texture"] = train_cab_textures
    elif fixture_name == "counter":
        train_items = []
        for tex_i in range(1, 101):
            train_items.append(dict(default=[f"gentex{tex_i:03d}"]))
        train_fixtures[fixture_name] = train_items
    elif fixture_name == "wall":
        train_items = [item for item in all_items if item.startswith("gentex")]
        train_fixtures[fixture_name] = train_items
    elif fixture_name == "floor":
        train_items = [item for item in all_items if item.startswith("gentex")]
        train_fixtures[fixture_name] = train_items
    else:
        train_items = [item for item in all_items if item not in test_items]
        train_fixtures[fixture_name] = train_items

### populate new styles ###
train_styles = [dict() for _ in range(NUM_TRAIN_STYTLES)]
for fixture_name in all_fixtures:
    if any(
        [
            fixture_name == name
            for name in ["cabinet", "cab_texture", "cab_handle", "cab_panel"]
        ]
    ):
        continue
    train_items = train_fixtures[fixture_name]
    rng.shuffle(train_items)
    assignments = random_sample_guaranteed(train_items, NUM_TRAIN_STYTLES)
    for i in range(NUM_TRAIN_STYTLES):
        train_styles[i][fixture_name] = assignments[i]

# get the cabinet assignments
cab_panels = train_fixtures["cab_panel"]
cab_handles = train_fixtures["cab_handle"]
cab_textures = train_fixtures["cab_texture"]
rng.shuffle(cab_panels)
rng.shuffle(cab_handles)
rng.shuffle(cab_textures)
cab_panels_sampled = random_sample_guaranteed(cab_panels, NUM_TRAIN_STYTLES)
cab_handles_sampled = random_sample_guaranteed(cab_handles, NUM_TRAIN_STYTLES)
cab_textures_sampled = random_sample_guaranteed(cab_textures, NUM_TRAIN_STYTLES)
for i in range(NUM_TRAIN_STYTLES):
    train_styles[i]["cabinet"] = dict(
        default=[cab_textures_sampled[i], cab_panels_sampled[i], cab_handles_sampled[i]]
    )

# save informatation to json files
for i in range(NUM_TRAIN_STYTLES):
    style_i = 11 + i
    style_path = os.path.join(styles_base_path, "train", f"style{style_i:03d}.yaml")
    with open(style_path, "w") as f:
        yaml.dump(train_styles[i], f, default_flow_style=False)
