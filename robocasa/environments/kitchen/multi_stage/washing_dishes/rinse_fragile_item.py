from robocasa.environments.kitchen.kitchen import *


class RinseFragileItem(Kitchen):
    """
    Rinse Fragile Item: composite task for Washing Dishes activity.

    Simulates the process of rinsing and securing a fragile item without breaking it.

    Steps:
        1) Gently pick up the fragile item and navigate to the sink
        2) Rinse the item under running water
        3) Place the item on a drying rack
    """

    def __init__(self, enable_fixtures=None, *args, **kwargs):
        enable_fixtures = enable_fixtures or []
        enable_fixtures = list(enable_fixtures) + ["dish_rack"]
        super().__init__(enable_fixtures=enable_fixtures, *args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.sink = self.register_fixture_ref("sink", dict(id=FixtureType.SINK))
        self.dish_rack = self.register_fixture_ref(
            "dish_rack", dict(id=FixtureType.DISH_RACK)
        )
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=FixtureType.STOVE)
        )
        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Rinse the teapot for 100 timesteps and place it in the dish rack when done."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.teapot_contact_time = 0

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="obj",
                obj_groups="teapot",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=FixtureType.STOVE,
                    ),
                    size=(0.45, 0.45),
                    pos=("ref", -0.5),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        water_on = self.sink.get_handle_state(env=self)["water_on"]
        if not water_on:
            return False

        in_water = self.sink.obj_in_water_stream(
            self, "teapot", self.sink, water_radius=0.10, partial_check=False
        )

        if in_water:
            self.teapot_contact_time += 1

        gripper_far_teapot = OU.gripper_obj_far(self, obj_name="teapot")
        teapot_in_rack = OU.check_obj_fixture_contact(self, "teapot", self.dish_rack)

        return self.teapot_contact_time >= 100 and gripper_far_teapot and teapot_in_rack
