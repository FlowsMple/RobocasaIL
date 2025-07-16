from copy import deepcopy
import numpy as np
import re
from robocasa.environments.kitchen.kitchen import *
from robocasa.models.fixtures import Fixture
from robocasa.models.objects.objects import MJCFObject
from robosuite.utils.transform_utils import convert_quat
import robosuite.utils.transform_utils as T
from robosuite.utils.mjcf_utils import (
    array_to_string,
    string_to_array,
    xml_path_completion,
)


class Sink(Fixture):
    """
    Sink fixture class. The sink has a handle_joint that can be turned on and off to simulate water flow

    Args:
        xml (str): path to mjcf xml file

        name (str): name of the object
    """

    def __init__(self, xml="fixtures/sink.xml", name="sink", *args, **kwargs):
        self._handle_joint = None
        self._water_site = None
        self._high_water_radius = None

        super().__init__(
            xml=xml, name=name, duplicate_collision_geoms=False, *args, **kwargs
        )

    def get_reset_region_names(self):
        return ("basin", "basin_right", "basin_left")

    def update_state(self, env):
        """
        Updates the water flowing of the sink based on the handle_joint position

        Args:
            env (MujocoEnv): environment
        """
        state = self.get_handle_state(env)
        water_on = state["water_on"]

        site_id = env.sim.model.site_name2id("{}water".format(self.naming_prefix))

        if water_on:
            if state["water_pressure"] == "low":
                env.sim.model.site_size[site_id][0] = self.high_water_radius * 0.75
            elif state["water_pressure"] == "high":
                env.sim.model.site_size[site_id][0] = self.high_water_radius
            env.sim.model.site_rgba[site_id][3] = 0.5
        else:
            env.sim.model.site_rgba[site_id][3] = 0.0

    def set_handle_state(self, env, rng, mode="on"):
        """
        Sets the state of the handle_joint based on the mode parameter

        Args:
            env (MujocoEnv): environment

            rng (np.random.Generator): random number generator

            mode (str): "on", "off", or "random"
        """
        assert mode in ["on", "off", "random"]
        if mode == "random":
            mode = rng.choice(["on", "off"])

        if mode == "off":
            joint_val = 0.0
        elif mode == "on":
            joint_val = rng.uniform(0.40, 0.50)

        env.sim.data.set_joint_qpos(
            "{}handle_joint".format(self.naming_prefix), joint_val
        )

    def set_temp_state(self, env, rng, min_temp=0.0, max_temp=1.0):
        """
        Sets the temperature of the sink water using a normalized range.

        Args:
            env (MujocoEnv): environment
            rng (np.random.Generator): random number generator
            min_temp (float): normalized minimum temp value in range [0, 1]
            max_temp (float): normalized maximum temp value in range [0, 1]
        """

        assert min_temp <= max_temp, "min_temp must be less than or equal to max_temp"

        joint_name = f"{self.naming_prefix}handle_temp_joint"
        joint_id = env.sim.model.joint_name2id(joint_name)
        joint_range = env.sim.model.jnt_range[joint_id]

        lo, hi = joint_range
        temp_actual = -1 * rng.uniform(
            lo + min_temp * (hi - lo), lo + max_temp * (hi - lo)
        )

        env.sim.data.set_joint_qpos(joint_name, temp_actual)

        midpoint = (lo + hi) / 2
        self.water_temp_state = "cold" if temp_actual < midpoint else "hot"

    def get_handle_state(self, env):
        """
        Gets the state of the handle_joint

        Args:
            env (MujocoEnv): environment

        Returns:
            dict describing:
                - handle_joint: actual qpos of the on/off joint
                - water_on: bool if water is flowing
                - spout_joint: actual qpos of spout rotation
                - spout_ori: string in {left, center, right}
                - temp_joint: actual qpos of the temperature joint
                - water_temp_state: "hot" or "cold" (based on temp_joint)
                - water_temp: normalized float [0, 1] (0 = coldest, 1 = hottest)
        """
        handle_state = {}
        if self.handle_joint is None:
            return handle_state

        # On/Off joint
        handle_joint_id = env.sim.model.joint_name2id(
            f"{self.naming_prefix}handle_joint"
        )
        handle_joint_max = string_to_array(self.handle_joint.get("range"))[1]
        handle_joint_qpos = deepcopy(env.sim.data.qpos[handle_joint_id])

        # TODO: use joint ranges instead of harcoded values like np.pi and 0.2
        handle_joint_qpos = handle_joint_qpos % (2 * np.pi)
        if handle_joint_qpos < 0:
            handle_joint_qpos += 2 * np.pi

        joint_use_ratio = handle_joint_qpos / handle_joint_max
        handle_state["handle_joint"] = handle_joint_qpos
        handle_state["water_on"] = 0.40 < handle_joint_qpos < np.pi

        if joint_use_ratio > 0.5 and handle_state["water_on"]:
            handle_state["water_pressure"] = "high"
        elif handle_state["water_on"]:
            handle_state["water_pressure"] = "low"
        else:
            handle_state["water_pressure"] = "zero"

        # Spout rotation
        spout_joint_id = env.sim.model.joint_name2id(f"{self.naming_prefix}spout_joint")
        spout_joint_qpos = deepcopy(env.sim.data.qpos[spout_joint_id])
        spout_joint_qpos = spout_joint_qpos % (2 * np.pi)
        if spout_joint_qpos < 0:
            spout_joint_qpos += 2 * np.pi
        handle_state["spout_joint"] = spout_joint_qpos
        if np.pi <= spout_joint_qpos <= 2 * np.pi - np.pi / 6:
            spout_ori = "left"
        elif np.pi / 6 <= spout_joint_qpos <= np.pi:
            spout_ori = "right"
        else:
            spout_ori = "center"
        handle_state["spout_ori"] = spout_ori

        # Temperature joint
        temp_joint_id = env.sim.model.joint_name2id(
            f"{self.naming_prefix}handle_temp_joint"
        )
        temp_joint_qpos = deepcopy(env.sim.data.qpos[temp_joint_id])
        handle_state["temp_joint"] = float(temp_joint_qpos)

        lo, hi = env.sim.model.jnt_range[temp_joint_id]
        normalized_temp = 1.0 - ((temp_joint_qpos - lo) / (hi - lo))
        normalized_temp = float(np.clip(normalized_temp, 0.0, 1.0))
        handle_state["water_temp"] = normalized_temp

        handle_state["water_temp_state"] = "hot" if normalized_temp >= 0.5 else "cold"

        return handle_state

    def get_obj_basin_loc(self, env, obj_name, partial_check=False):
        """
        Determine whether an object is in the left basin, right basin, or neither
        of a double-basin sink, taking into account the sink's rotation.
        Args:
            env (MujocoEnv): The environment instance.
            obj_name (str): Name of the object.
            partial_check (bool): If True, checks only the center of the object
                rather than full bounding box.
        Returns:
            str: "left" if in left basin, "right" if in right basin, or "none" otherwise.
        """

        obj = env.objects[obj_name]
        obj_pos_world = env.sim.data.body_xpos[env.obj_body_id[obj_name]]

        # Get the sink (fixture) world position and rotation.
        fixture_pos_world = np.array(self.pos)
        fixture_euler = np.array([0, 0, self.rot])
        fixture_mat = T.euler2mat(fixture_euler)
        fixture_mat_inv = np.linalg.inv(fixture_mat)

        # Get the object's quaternion (convert to xyzw if needed).
        obj_quat = T.convert_quat(
            env.sim.data.body_xquat[env.obj_body_id[obj_name]], to="xyzw"
        )

        if partial_check:
            points_world = [obj_pos_world]
            threshold = 0.0
        else:
            points_world = obj.get_bbox_points(trans=obj_pos_world, rot=obj_quat)
            threshold = 0.05

        points_local = []
        for p_w in points_world:
            rel = p_w - fixture_pos_world
            p_local = fixture_mat_inv @ rel
            points_local.append(p_local)

        pattern_left = re.compile(r".*reg_basin_left$")
        pattern_right = re.compile(r".*reg_basin_right$")

        left_region_elem = None
        right_region_elem = None

        for geom in self.worldbody.iter("geom"):
            geom_name = geom.get("name")
            if geom_name and pattern_left.search(geom_name):
                if left_region_elem is None:
                    left_region_elem = geom
            if geom_name and pattern_right.search(geom_name):
                if right_region_elem is None:
                    right_region_elem = geom

        if left_region_elem is None or right_region_elem is None:
            raise ValueError(
                "Could not find basin region geoms 'reg_basin_left' or 'reg_basin_right' in sink XML."
            )

        left_center = string_to_array(left_region_elem.get("pos"))
        left_halfsize = string_to_array(left_region_elem.get("size"))

        right_center = string_to_array(right_region_elem.get("pos"))
        right_halfsize = string_to_array(right_region_elem.get("size"))

        lower_bound_left = left_center[:2] - left_halfsize[:2] - threshold
        upper_bound_left = left_center[:2] + left_halfsize[:2] + threshold
        left_inside = True
        for p in points_local:
            if not (
                lower_bound_left[0] <= p[0] <= upper_bound_left[0]
                and lower_bound_left[1] <= p[1] <= upper_bound_left[1]
            ):
                left_inside = False
                break
        if left_inside:
            return "left"

        lower_bound_right = right_center[:2] - right_halfsize[:2] - threshold
        upper_bound_right = right_center[:2] + right_halfsize[:2] + threshold
        right_inside = True
        for p in points_local:
            if not (
                lower_bound_right[0] <= p[0] <= upper_bound_right[0]
                and lower_bound_right[1] <= p[1] <= upper_bound_right[1]
            ):
                right_inside = False
                break
        if right_inside:
            return "right"

        return "none"

    def obj_in_water_stream(
        self, env, obj_name, sink_name, water_radius=0.10, partial_check=False
    ):
        """
        Checks if an object's bounding box (or center) intersects a vertical
        cylindrical water stream from the spout top down to the sink bottom.

        Args:
            env (MujocoEnv): The simulation environment.
            obj_name (str): Name of the object in env.objects.
            sink_name (str): Name of the sink fixture in env.
            water_radius (float): Radius (meters) for the cylindrical stream.
            partial_check (bool): If True, only check the object's center.

        Returns:
            bool: True if the object is inside the water stream, False otherwise.
        """
        obj = env.objects[obj_name]
        sink = env.get_fixture(sink_name)

        try:
            spout_top_id = env.sim.model.geom_name2id(f"{sink.naming_prefix}spout_main")
        except ValueError:
            # Try fallback: use any geom ending in "spout_main"
            candidates = [
                name for name in env.sim.model.geom_names if name.endswith("spout_main")
            ]
            if not candidates:
                raise ValueError(f"Could not find spout_main geom for {sink_name}")
            spout_top_id = env.sim.model.geom_name2id(candidates[0])

        spout_top_pos = env.sim.data.geom_xpos[spout_top_id].copy()

        # Attempt to get bottom Z height using int_p0 site or bottom geom
        sink_bottom_z = None
        try:
            int_p0_id = env.sim.model.site_name2id(f"{sink.naming_prefix}int_p0")
            sink_bottom_z = env.sim.data.site_xpos[int_p0_id][2]
        except ValueError:
            # Try fallback: site ending with "int_p0"
            matching_sites = [
                name for name in env.sim.model.site_names if name.endswith("int_p0")
            ]
            if matching_sites:
                site_id = env.sim.model.site_name2id(matching_sites[0])
                sink_bottom_z = env.sim.data.site_xpos[site_id][2]
            else:
                try:
                    bottom_geom_id = env.sim.model.geom_name2id(
                        f"{sink.naming_prefix}bottom"
                    )
                    sink_bottom_z = env.sim.data.geom_xpos[bottom_geom_id][2]
                except ValueError:
                    matching_geoms = [
                        name
                        for name in env.sim.model.geom_names
                        if name.endswith("bottom")
                    ]
                    if matching_geoms:
                        geom_id = env.sim.model.geom_name2id(matching_geoms[0])
                        sink_bottom_z = env.sim.data.geom_xpos[geom_id][2]
                    else:
                        print(
                            f"[Warning] Could not find sink bottom reference for {sink_name}"
                        )
                        return False

        water_top_z = spout_top_pos[2]
        water_bottom_z = sink_bottom_z

        if water_top_z < water_bottom_z:
            water_top_z, water_bottom_z = water_bottom_z, water_top_z

        spout_xy = spout_top_pos[:2]

        obj_pos = env.sim.data.body_xpos[env.obj_body_id[obj.name]]
        obj_quat = convert_quat(
            env.sim.data.body_xquat[env.obj_body_id[obj.name]], to="xyzw"
        )

        if partial_check:
            points_to_check = [obj_pos]
        else:
            points_to_check = obj.get_bbox_points(trans=obj_pos, rot=obj_quat)

        for pt in points_to_check:
            pt_xy, pt_z = pt[:2], pt[2]

            if water_bottom_z < pt_z < water_top_z:
                if np.linalg.norm(pt_xy - spout_xy) < water_radius:
                    return True

        return False

    @property
    def handle_joint(self):
        """
        Returns the joint element which represents the handle_joint of the sink
        """
        if self._handle_joint is None:
            self._handle_joint = self.worldbody.find(
                "./body/body/body/joint[@name='{}handle_joint']".format(
                    self.naming_prefix
                )
            )

        return self._handle_joint

    @property
    def water_site(self):
        """
        Returns the site element which represents the water flow of the sink
        """
        if self._water_site is None:
            self._water_site = self.worldbody.find(
                "./body/body/body/site[@name='{}water']".format(self.naming_prefix)
            )

        return self._water_site

    @property
    def high_water_radius(self):
        if self._high_water_radius is None:
            self._high_water_radius = string_to_array(self.water_site.get("size"))[0]
        return self._high_water_radius

    @property
    def nat_lang(self):
        return "sink"

    def check_obj_under_water(self, env, obj_name, xy_thresh=None):
        if xy_thresh is None:
            xy_thresh = env.objects[obj_name].horizontal_radius
        obj_pos = np.array(env.sim.data.body_xpos[env.obj_body_id[obj_name]])
        water_site_id = env.sim.model.site_name2id(self.water_site.get("name"))
        water_site_pos = env.sim.data.site_xpos[water_site_id]
        xy_check = np.linalg.norm(obj_pos[0:2] - water_site_pos[0:2]) < xy_thresh
        z_check = (
            obj_pos[2]
            < water_site_pos[2] + string_to_array(self.water_site.get("size"))[1]
        )
        return xy_check and z_check and self.get_handle_state(env)["water_on"]
