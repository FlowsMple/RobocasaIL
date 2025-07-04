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
    unique_elements = list(set(data))  # Get unique elements

    if num_samples < len(unique_elements):
        raise ValueError(
            "Number of samples must be at least the number of unique elements."
        )

    # Start with each unique element once
    sample = list(unique_elements)

    # Perform remaining random selections with replacement
    remaining_samples = num_samples - len(unique_elements)
    if remaining_samples > 0:
        sample.extend(
            rng.choice(data, size=remaining_samples)
        )  # Use random.choices for replacement

    # Shuffle for a completely random appearance
    rng.shuffle(sample)

    return [str(item) for item in sample]


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
        if not isinstance(v, str):
            continue
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
    train_items = [item for item in all_items if item not in test_items]
    # shuffle all the elements
    rng.shuffle(train_items)
    train_fixtures[fixture_name] = train_items


### populate new styles ###
train_styles = [dict() for _ in range(NUM_TRAIN_STYTLES)]
for fixture_name in all_fixtures:
    train_items = train_fixtures[fixture_name]
    assignments = random_sample_guaranteed(train_items, NUM_TRAIN_STYTLES)
    for i in range(NUM_TRAIN_STYTLES):
        train_styles[i][fixture_name] = assignments[i]

for i in range(NUM_TRAIN_STYTLES):
    train_styles[i]["cabinet"] = dict(
        default=[
            "dark_blue",
            "handle_brass",
            "CabinetDoorPanel001",
            "CabinetHandle001",
        ],
        shelves="light_wood_planks_shelves",
    )
    train_styles[i]["counter"] = dict(
        default="dark_blue_base_marble_top",
        island="dark_blue_base_marble_top",
    )

# save informatation to json files
for i in range(NUM_TRAIN_STYTLES):
    style_i = 11 + i
    style_path = os.path.join(styles_base_path, "train", f"style{style_i:03d}.yaml")
    with open(style_path, "w") as f:
        yaml.dump(train_styles[i], f, default_flow_style=False)
