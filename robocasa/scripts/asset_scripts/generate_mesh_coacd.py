import os
import shutil
import trimesh
from pathlib import Path
import xml.etree.ElementTree as ET
import coacd
import robocasa.utils.model_zoo.mjcf_gen_utils as MJCFGenUtils

# configure root directory
LIGHTWHEEL_ROOT = "/Users/sepehrnasiriany/Downloads/straw/"
CANONICAL_PREFIX = "collision_mesh"
MAX_HULLS = 16

# configure excluded object types
EXCLUDE_DIRS = {}


def find_visual_dirs(root_dir):
    dirs = []
    for root, subdirs, files in os.walk(root_dir):
        if root.endswith("/visual") or root.endswith("/visual/"):
            object_type = Path(root).parents[1].name
            if object_type not in EXCLUDE_DIRS:
                dirs.append(root)
            else:
                print(f"Skipping excluded object type: {object_type}")
    return dirs


def indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for c in elem:
            indent_xml(c, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def process_directory(input_dir):
    input_path = Path(input_dir)
    obj_dir = input_path.parent
    prefix = obj_dir.name.split("_")[0]
    model_xml_path = obj_dir / "model.xml"
    collision_output_dir = obj_dir / "collision"

    print(f"\n=== Processing {obj_dir.name} ===")

    if collision_output_dir.exists():
        shutil.rmtree(collision_output_dir)
    os.makedirs(collision_output_dir, exist_ok=True)

    meshes = [trimesh.load(f, force="mesh") for f in input_path.glob("*.obj")]
    if not meshes:
        raise RuntimeError("No .obj meshes found in input directory")

    merged = trimesh.util.concatenate(meshes)
    merged_path = obj_dir / f"{CANONICAL_PREFIX}.obj"
    merged.export(merged_path, file_type="obj", include_texture=False)
    print(f"Exported merged mesh to {merged_path.name}")

    mesh_tm = trimesh.load(str(merged_path), force="mesh")
    mesh = coacd.Mesh(mesh_tm.vertices, mesh_tm.faces)
    parts = coacd.run_coacd(
        mesh,
        threshold=0.03,
        preprocess_mode="auto",
        mcts_max_depth=1,
        mcts_iterations=50,
        max_convex_hull=MAX_HULLS,
        decimate=True,
        max_ch_vertex=128,
    )

    tree = ET.parse(model_xml_path)
    root = tree.getroot()
    asset = root.find("asset")
    defaults = root.find("default")
    worldbody = root.find("worldbody")
    obj_body = worldbody.find(".//body[@name='object']")

    if asset is None or defaults is None or obj_body is None:
        raise RuntimeError("Missing <asset>, <default>, or <body name='object'> in XML")

    if not any(d.get("class") == "collision" for d in defaults.findall("default")):
        col_def = ET.SubElement(defaults, "default", {"class": "collision"})
        ET.SubElement(
            col_def, "geom", {"group": "0", "rgba": "0.5 0 0 0.5", "density": "1000.0"}
        )

    scale, refquat = None, None
    for mesh_tag in asset.findall("mesh"):
        if mesh_tag.get("scale") and mesh_tag.get("refquat"):
            scale = mesh_tag.get("scale")
            refquat = mesh_tag.get("refquat")
            break

    for m in list(asset.findall("mesh")):
        if "collision" in m.get("file", ""):
            asset.remove(m)

    def strip_geoms(body_elem):
        for g in list(body_elem.findall("geom")):
            if (
                g.get("class") == "collision" or "collision" in (g.get("mesh") or "")
            ) and g.get("group") != "1":
                body_elem.remove(g)
        for b in body_elem.findall("body"):
            strip_geoms(b)

    strip_geoms(obj_body)

    for i, (verts, faces) in enumerate(parts):
        mesh_name = f"{prefix}_collision_mesh_{i}"
        mesh_file = f"collision/{CANONICAL_PREFIX}_collision_{i}.obj"
        mesh_path = collision_output_dir / f"{CANONICAL_PREFIX}_collision_{i}.obj"
        trimesh.Trimesh(vertices=verts, faces=faces).export(mesh_path)

        m = ET.SubElement(
            asset,
            "mesh",
            {
                "file": mesh_file,
                "name": mesh_name,
            },
        )
        if scale:
            m.set("scale", scale)
        if refquat:
            m.set("refquat", refquat)

        ET.SubElement(
            obj_body, "geom", {"mesh": mesh_name, "type": "mesh", "class": "collision"}
        )

    merged_path.unlink()
    indent_xml(root)
    tree.write(str(model_xml_path), encoding="utf-8", xml_declaration=True)
    print("model.xml updated")


if __name__ == "__main__":
    visual_dirs = find_visual_dirs(LIGHTWHEEL_ROOT)
    for d in visual_dirs:
        process_directory(d)
