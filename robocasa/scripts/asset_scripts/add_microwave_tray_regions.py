from lxml import etree
import numpy as np
import os
import argparse
import robocasa
from robosuite.utils.mjcf_utils import (
    find_elements,
    find_parent,
    array_to_string,
    string_to_array,
)


def add_microwave_tray_region(path):
    tree = etree.parse(path)
    root = tree.getroot()
    object_body = find_elements(root, "body", attribs={"name": "object"})
    tray_geom = find_elements(root, "geom", attribs={"name": "tray"})
    int_reg_geom = find_elements(root, "geom", attribs={"name": "reg_int"})

    int_reg_pos = string_to_array(int_reg_geom.get("pos"))
    int_reg_size = string_to_array(int_reg_geom.get("size"))

    pos = string_to_array(tray_geom.get("pos"))
    size = string_to_array(tray_geom.get("size"))
    top_height = int_reg_pos[2] + int_reg_size[2] - 0.001
    bottom_height = pos[2] + size[1] + 0.001
    pos[2] = np.mean([bottom_height, top_height])
    size[1] = (top_height - bottom_height) / 2

    tray_reg_geom = find_elements(root, "geom", attribs={"name": "reg_tray"})
    if tray_reg_geom is not None:
        parent = find_parent(root, tray_reg_geom)
        parent.remove(tray_reg_geom)
    tray_reg_geom = etree.fromstring(
        """<geom class="region" name="reg_tray" type="cylinder" pos="{pos}" size="{size}"/>""".format(
            pos=array_to_string(pos), size=array_to_string(size)
        )
    )
    object_body.append(tray_reg_geom)

    tree = etree.ElementTree(root)
    tree.write(
        path,
        pretty_print=True,  # Makes the output human-readable
        xml_declaration=True,  # Adds <?xml ...?> at the top
        encoding="UTF-8",  # Sets encoding
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mjcf",
        type=str,
        default=os.path.join(robocasa.__path__[0], "models/assets/fixtures/microwaves"),
    )
    args = parser.parse_args()

    mjcf_path_list = []

    if os.path.isdir(args.mjcf):
        mjcf_path_list = []
        for root, dirs, files in os.walk(args.mjcf):
            for file in files:
                if file.endswith(".xml"):
                    mjcf_path_list.append(os.path.join(root, file))
    else:
        mjcf_path_list = [args.mjcf]

    for path in mjcf_path_list:
        add_microwave_tray_region(path)
