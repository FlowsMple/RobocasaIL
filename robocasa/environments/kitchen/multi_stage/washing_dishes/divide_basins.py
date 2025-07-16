from robocasa.environments.kitchen.kitchen import *


class DivideBasins(Kitchen):
    """
    Divide Basins: a composite task for Washing Dishes activity.

    One object begins in the right basin, representing an item that is already drying.
    Another object begins on the counter beside the sink and must be moved to the left basin for washing.
    """

    EXCLUDE_STYLES = [
        2,
        3,
        4,
        6,
        8,
        9,
        10,
        13,
        14,
        15,
        16,
        17,
        20,
        21,
        22,
        23,
        25,
        26,
        30,
        31,
        32,
        34,
        35,
        37,
        38,
        39,
        40,
        42,
        43,
        45,
        46,
        47,
        49,
        50,
        52,
        53,
        55,
        56,
        58,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        self.sink = self.register_fixture_ref("sink", dict(id=FixtureType.SINK))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.sink)
        )

        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()

        obj_to_wash_lang = self.get_obj_lang("obj_to_wash")
        obj_drying_lang = self.get_obj_lang("obj_drying")

        ep_meta["lang"] = (
            f"The {obj_to_wash_lang} is on the counter. Move it into the left basin of the sink for washing. "
            f"Make sure the {obj_drying_lang} is in the right basin for drying if not already there."
        )
        ep_meta["obj_to_wash_basin"] = "left"
        ep_meta["obj_drying_basin"] = "right"
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.sink.set_handle_state(env=self, rng=self.rng, mode="off")

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="obj_to_wash",
                obj_groups="stackable",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(ref=self.sink),
                    size=(0.4, 0.4),
                    pos=("ref", -0.5),
                ),
            )
        )

        cfgs.append(
            dict(
                name="obj_drying",
                obj_groups="receptacle",
                graspable=True,
                placement=dict(
                    fixture=self.sink,
                    size=(0.4, 0.4),
                    pos=(0, 1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        in_left_basin = (
            self.sink.get_obj_basin_loc(self, "obj_to_wash", self.sink) == "left"
        )
        gripper_far = OU.gripper_obj_far(self, obj_name="obj_to_wash")
        return in_left_basin and gripper_far
