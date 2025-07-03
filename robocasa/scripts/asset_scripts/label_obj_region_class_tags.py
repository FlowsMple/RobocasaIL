"""
Scan through objects and label liquid/reg_int tags with class="region" tag
"""

import robocasa
import os
from lxml import etree
from robosuite.utils.mjcf_utils import find_elements

objs_folder = os.path.join(robocasa.__path__[0], "models/assets/objects")

model_path_list = []
for root, dirs, files in os.walk(objs_folder):
    for filename in files:
        if filename.endswith(".xml"):
            model_path_list.append(os.path.join(root, filename))


for model_path in model_path_list:
    tree = etree.parse(model_path)
    root = tree.getroot()
    liquid_geom = find_elements(root, tags="geom", attribs={"name": "liquid"})
    reg_int_geom = find_elements(root, tags="geom", attribs={"name": "reg_int"})

    modified = False
    if liquid_geom is not None:
        liquid_geom.set("class", "region")
        modified = True
    if reg_int_geom is not None:
        reg_int_geom.set("class", "region")
        modified = True

    if modified is True:
        tree.write(model_path, pretty_print=True)
