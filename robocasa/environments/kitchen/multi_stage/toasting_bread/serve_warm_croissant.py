from robocasa.environments.kitchen.kitchen import *


class ServeWarmCroissant(Kitchen):
    """
    Serve Warm Croissant: Serve warm croissant on plate.

    Steps:
        1. Open the toaster oven door.
        2. Pull out the rack.
        3. Pick up the croissant and place it on the plate.
    """

    def __init__(self, enable_fixtures=None, *args, **kwargs):
        enable_fixtures = enable_fixtures or []
        enable_fixtures = list(enable_fixtures) + ["toaster_oven"]
        super().__init__(enable_fixtures=enable_fixtures, *args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.toaster_oven = self.register_fixture_ref(
            "toaster_oven", dict(id=FixtureType.TOASTER_OVEN)
        )
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.toaster_oven)
        )
        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Take out the warm croissant from the toaster oven and place it on the plate."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _get_obj_cfgs(self):
        cfgs = []
        cfgs.append(
            dict(
                name="croissant",
                obj_groups="croissant",
                placement=dict(
                    fixture=self.toaster_oven,
                    size=(0.70, 0.25),
                    pos=(0, -1.0),
                ),
            )
        )
        cfgs.append(
            dict(
                name="plate",
                obj_groups="plate",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.toaster_oven,
                        loc="left_right",
                    ),
                    size=(0.7, 0.30),
                    pos=("ref", -1.0),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        return OU.check_obj_in_receptacle(
            self, "croissant", "plate"
        ) and OU.gripper_obj_far(self, "croissant")
