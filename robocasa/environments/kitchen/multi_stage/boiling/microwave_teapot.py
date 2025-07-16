from robocasa.environments.kitchen.kitchen import *


class MicrowaveTeapot(Kitchen):
    """
    Microwave Teapot: composite task for Boiling Water activity.

    Simulates the task of boiling water in a teapot using the microwave.

    Steps:
        1) Pick a teapot filled with water from the counter.
        2) Open the microwave door.
        3) Place the teapot inside.
        4) Close the microwave door.
        5) Press the start button to begin boiling (simulated).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.microwave = self.register_fixture_ref(
            "microwave", dict(id=FixtureType.MICROWAVE)
        )
        self.sink = self.register_fixture_ref("sink", dict(id=FixtureType.SINK))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.sink)
        )
        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Pick the teapot filled with water from the counter, open the microwave, place it inside, close the door, and press the start button."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.microwave.open_door(env=self)

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="teapot",
                obj_groups="teapot",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.40, 0.20),
                    pos=("ref", -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        teapot_in_microwave = OU.obj_inside_of(self, "teapot", self.microwave)
        gripper_obj_far = OU.gripper_obj_far(self, "teapot")

        door_closed = self.microwave.is_closed(env=self)
        start_pressed = self.microwave.get_state()["turned_on"]

        return teapot_in_microwave and door_closed and start_pressed and gripper_obj_far
