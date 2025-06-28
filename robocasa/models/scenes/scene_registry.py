from collections import OrderedDict
from enum import IntEnum
from robosuite.utils.mjcf_utils import xml_path_completion
import robocasa
import numpy as np


class LayoutType(IntEnum):
    """
    Enum for available layouts in RoboCasa environment
    """

    LAYOUT001 = 1
    LAYOUT002 = 2
    LAYOUT003 = 3
    LAYOUT004 = 4
    LAYOUT005 = 5
    LAYOUT006 = 6
    LAYOUT007 = 7
    LAYOUT008 = 8
    LAYOUT009 = 9
    LAYOUT010 = 10

    LAYOUT011 = 11
    LAYOUT012 = 12
    LAYOUT013 = 13
    LAYOUT014 = 14
    LAYOUT015 = 15
    LAYOUT016 = 16
    LAYOUT017 = 17
    LAYOUT018 = 18
    LAYOUT019 = 19
    LAYOUT020 = 20
    LAYOUT021 = 21
    LAYOUT022 = 22
    LAYOUT023 = 23
    LAYOUT024 = 24
    LAYOUT025 = 25
    LAYOUT026 = 26
    LAYOUT027 = 27
    LAYOUT028 = 28
    LAYOUT029 = 29
    LAYOUT030 = 30
    LAYOUT031 = 31
    LAYOUT032 = 32
    LAYOUT033 = 33
    LAYOUT034 = 34
    LAYOUT035 = 35
    LAYOUT036 = 36
    LAYOUT037 = 37
    LAYOUT038 = 38
    LAYOUT039 = 39
    LAYOUT040 = 40
    LAYOUT041 = 41
    LAYOUT042 = 42
    LAYOUT043 = 43
    LAYOUT044 = 44
    LAYOUT045 = 45
    LAYOUT046 = 46
    LAYOUT047 = 47
    LAYOUT048 = 48
    LAYOUT049 = 49
    LAYOUT050 = 50
    LAYOUT051 = 51
    LAYOUT052 = 52
    LAYOUT053 = 53
    LAYOUT054 = 54
    LAYOUT055 = 55
    LAYOUT056 = 56
    LAYOUT057 = 57
    LAYOUT058 = 58
    LAYOUT059 = 59
    LAYOUT060 = 60

    # negative values correspond to groups (see LAYOUT_GROUPS_TO_IDS)
    TEST = -1
    TRAIN = -2
    NO_ISLAND = -3
    ISLAND = -4
    DINING = -5


LAYOUT_GROUPS_TO_IDS = {
    -1: list(range(1, 11)),  # test
    -2: list(range(11, 61)),  # train
    -3: list(range(1, 61)),  # train and test
    -4: [1, 3, 5, 6, 8],  # no island
    -5: [2, 4, 7, 9, 10],  # island
    -6: [2, 4, 7, 8, 9, 10],  # dining
}


class StyleType(IntEnum):
    """
    Enums for available styles in RoboCasa environment
    """

    # INDUSTRIAL = 0
    # SCANDANAVIAN = 1
    # COASTAL = 2
    # MODERN_1 = 3
    # MODERN_2 = 4
    # TRADITIONAL_1 = 5
    # TRADITIONAL_2 = 6
    # FARMHOUSE = 7
    # RUSTIC = 8
    # MEDITERRANEAN = 9
    # TRANSITIONAL_1 = 10
    # TRANSITIONAL_2 = 11

    STYLE001 = 1
    STYLE002 = 2
    STYLE003 = 3
    STYLE004 = 4
    STYLE005 = 5
    STYLE006 = 6
    STYLE007 = 7
    STYLE008 = 8
    STYLE009 = 9
    STYLE010 = 10
    STYLE011 = 11
    STYLE012 = 12
    STYLE013 = 13

    PLAYGROUND_STYLE = 1001

    # negative values correspond to groups
    ALL = -1


STYLE_GROUPS_TO_IDS = {
    -1: list(range(1, 14)),  # all
    # -2: list(range(0, 13)),  # all the original styles
}


def get_layout_path(layout_id):
    """
    Get corresponding blueprint filepath (yaml) for a layout

    Args:
        layout_id (int or LayoutType): layout id (int or enum)

    Return:
        str: yaml path for specified layout
    """
    if (
        isinstance(layout_id, int)
        or isinstance(layout_id, np.int64)
        or isinstance(layout_id, np.int32)
    ):
        layout_int_to_name = dict(
            map(lambda item: (item.value, item.name.lower()), LayoutType)
        )
        layout_name = layout_int_to_name[layout_id]
    elif isinstance(layout_id, LayoutType):
        layout_name = layout_id.name.lower()
    else:
        raise ValueError

    # special case: if name starts with one letter, capitalize it
    if layout_name[1] == "_":
        layout_name = layout_name.capitalize()

    return xml_path_completion(
        f"scenes/kitchen_layouts/{layout_name}.yaml",
        root=robocasa.models.assets_root,
    )


def get_style_path(style_id):
    """
    Get corresponding blueprint filepath (yaml) for a style

    Args:
        style_id (int or StyleType): style id (int or enum)

    Return:
        str: yaml path for specified style
    """
    if (
        isinstance(style_id, int)
        or isinstance(style_id, np.int64)
        or isinstance(style_id, np.int32)
    ):
        style_int_to_name = dict(
            map(lambda item: (item.value, item.name.lower()), StyleType)
        )
        style_name = style_int_to_name[style_id]
    elif isinstance(style_id, StyleType):
        style_name = style_id.name.lower()
    else:
        raise ValueError

    return xml_path_completion(
        f"scenes/kitchen_styles/{style_name}.yaml",
        root=robocasa.models.assets_root,
    )


def unpack_layout_ids(layout_ids):
    if layout_ids is None:
        layout_ids = LayoutType.ALL

    if not isinstance(layout_ids, list):
        layout_ids = [layout_ids]

    all_layout_ids = []
    for id in layout_ids:
        if isinstance(id, dict):
            all_layout_ids.append(id)
        else:
            id = int(id)
            if id < 0:
                all_layout_ids += LAYOUT_GROUPS_TO_IDS[id]
            else:
                all_layout_ids.append(id)
    return all_layout_ids


def unpack_style_ids(style_ids):
    if style_ids is None:
        style_ids = StyleType.ALL

    if not isinstance(style_ids, list):
        style_ids = [style_ids]

    all_style_ids = []
    for id in style_ids:
        if isinstance(id, dict):
            all_style_ids.append(id)
        else:
            id = int(id)
            if id < 0:
                all_style_ids += STYLE_GROUPS_TO_IDS[id]
            else:
                all_style_ids.append(id)
    return all_style_ids
