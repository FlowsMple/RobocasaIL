import numpy as np
from robocasa.models.fixtures import Fixture
import robosuite.utils.transform_utils as T
from robocasa.utils.object_utils import obj_inside_of

class Fridge(Fixture):
    """
    Fridge fixture class
    """

    def __init__(
        self, xml="fixtures/fridges/Refrigerator033", name="fridge", *args, **kwargs
    ):
        super().__init__(
            xml=xml, name=name, duplicate_collision_geoms=False, *args, **kwargs
        )
        self._fridge_door_joint_names = []
        self._freezer_door_joint_names = []

        for joint_name in self._joint_infos:
            stripped_name = joint_name[len(self.name) + 1 :]
            if "door" in stripped_name and "fridge" in stripped_name:
                self._fridge_door_joint_names.append(joint_name)
            elif "door" in stripped_name and "freezer" in stripped_name:
                self._freezer_door_joint_names.append(joint_name)

        self._fridge_reg_names = [
            reg_name for reg_name in self._regions.keys() if "fridge" in reg_name
        ]
        self._freezer_reg_names = [
            reg_name for reg_name in self._regions.keys() if "freezer" in reg_name
        ]

    def get_reset_regions(
        self,
        env,
        compartment="fridge",
        z_range=(0.50, 1.50),
        rack_index=None,
        drawer=False,
        reg_type=("shelf"),
    ):
        """
        Returns reset regions inside the fridge or freezer as a dictionary of offsets and sizes.

        Args:
            env (Kitchen): the environment the fridge belongs to
            compartment (str): "fridge" or "freezer" — which compartment to query
            z_range (tuple): optional Z bounds to filter usable regions by height
            rack_index (int or None): if set, selects a specific shelf by index
                (0 = lowest, -1 = highest, -2 = second highest)
            reg_type (tuple or str): can be combination of shelf or drawer. specifies
                whether to use shelves or drawers, or both

        Returns:
            dict: mapping from region name to { "offset": (x, y, z), "size": (sx, sy) }
        """
        assert compartment in ["fridge", "freezer"]

        if isinstance(reg_type, str):
            reg_type = tuple([reg_type])
            for t in reg_type:
                assert t in ["shelf", "drawer"]

        if "drawer" in reg_type:
            # rack index not supported for drawers
            assert rack_index is None
        
        region_names = []
        for reg_name in self.get_reset_region_names():
            if compartment not in reg_name:
                continue

            if "drawer" in reg_name:
                # it is a drawer
                if "drawer" not in reg_type:
                    continue
            else:
                # it is a shelf
                if "shelf" not in reg_type:
                    continue
 
            region_names.append(reg_name)

        reset_regions = {}

        for name in region_names:
            reg = self._regions.get(name)
            if reg is None:
                continue
            p0, px, py, pz = reg["p0"], reg["px"], reg["py"], reg["pz"]
            height = pz[2] - p0[2]
            if height < 0.20 and not drawer:
                continue

            # bypass z-range check if rack_index is specified or drawer=True
            is_drawer = "drawer" in name
            bypass_z_range = (rack_index is not None) if not is_drawer else True
            if not bypass_z_range:
                reg_abs_z = self.pos[2] + p0[2]
                if reg_abs_z < z_range[0] or reg_abs_z > z_range[1]:
                    continue

            offset = (np.mean((p0[0], px[0])), np.mean((p0[1], py[1])), p0[2])
            size = (px[0] - p0[0], py[1] - p0[1])
            reset_regions[name] = {"offset": offset, "size": size}

        # sort by Z height (top shelf first)
        sorted_regions = sorted(
            reset_regions.items(),
            key=lambda item: self.pos[2] + self._regions[item[0]]["p0"][2],
            reverse=False,
        )

        if rack_index is not None and "drawer" not in reg_type:
            if rack_index == -1:
                return dict([sorted_regions[-1]]) if sorted_regions else {}
            elif rack_index == -2:
                if len(sorted_regions) > 1:
                    return dict([sorted_regions[-2]])
                else:
                    return dict([sorted_regions[-1]]) if sorted_regions else {}
            elif 0 <= rack_index < len(sorted_regions):
                return dict([sorted_regions[rack_index]])
            else:
                raise ValueError(
                    f"rack_index {rack_index} out of range for {compartment} regions. "
                    f"Available indices: {list(range(len(sorted_regions)))}"
                )

        return dict(sorted_regions)

    def is_open(self, env, entity="fridge", th=0.90):
        """
        checks whether the fixture is open
        """
        joint_names = None
        if entity == "fridge":
            joint_names = self._fridge_door_joint_names
        elif entity == "freezer":
            joint_names = self._freezer_door_joint_names

        return super().is_open(env, joint_names, th=th)

    def is_closed(self, env, entity="fridge", th=0.005):
        """
        checks whether the fixture is closed
        """
        joint_names = None
        if entity == "fridge":
            joint_names = self._fridge_door_joint_names
        elif entity == "freezer":
            joint_names = self._freezer_door_joint_names

        return super().is_closed(env, joint_names, th=th)

    def open_door(self, env, min=0.90, max=1.0, entity="fridge"):
        """
        helper function to open the door. calls set_door_state function
        """
        joint_names = None
        if entity == "fridge":
            joint_names = self._fridge_door_joint_names
        elif entity == "freezer":
            joint_names = self._freezer_door_joint_names
        self.set_joint_state(env=env, min=min, max=max, joint_names=joint_names)

    def close_door(self, env, min=0.0, max=0.0, entity="fridge"):
        """
        helper function to close the door. calls set_door_state function
        """
        joint_names = None
        if entity == "fridge":
            joint_names = self._fridge_door_joint_names
        elif entity == "freezer":
            joint_names = self._freezer_door_joint_names
        self.set_joint_state(env=env, min=min, max=max, joint_names=joint_names)

    def get_reset_region_names(self):
        return self._fridge_reg_names + self._freezer_reg_names
    
    def check_rack_contact(
        self,
        env,
        object_name,
        rack_index=None,
        compartment="fridge",
    ):
        region_names = [
            name
            for name in self.get_reset_regions(env, compartment=compartment, rack_index=rack_index)
        ]

        orig_get_int = self.get_int_sites

        def get_int_sites_filtered(relative=False):
            sites = orig_get_int(relative=relative)
            return {rn: sites[rn] for rn in region_names}

        self.get_int_sites = get_int_sites_filtered
        inside = obj_inside_of(env, object_name, self.name, partial_check=False)

        self.get_int_sites = orig_get_int

        return inside

    @property
    def nat_lang(self):
        return "fridge"


class FridgeFrenchDoor(Fridge):
    def __init__(self, xml="fixtures/fridges/Refrigerator064", *args, **kwargs):
        super().__init__(xml=xml, *args, **kwargs)


class FridgeSideBySide(Fridge):
    def __init__(self, xml="fixtures/fridges/Refrigerator031", *args, **kwargs):
        super().__init__(xml=xml, *args, **kwargs)


class FridgeBottomFreezer(Fridge):
    def __init__(self, xml="fixtures/fridges/Refrigerator060", *args, **kwargs):
        super().__init__(xml=xml, *args, **kwargs)
