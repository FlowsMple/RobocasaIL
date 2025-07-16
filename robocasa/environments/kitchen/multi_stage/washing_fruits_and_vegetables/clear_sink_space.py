from robocasa.environments.kitchen.kitchen import *


class ClearSinkSpace(Kitchen):
    def __init__(self, *args, **kwargs):
        self.num_sink_objs = -1
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):

        super()._setup_kitchen_references()
        self.sink = self.register_fixture_ref(
            "sink",
            dict(id=FixtureType.SINK),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.sink),
        )
        self.init_robot_base_ref = self.sink

    def get_ep_meta(self):

        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = f"Clear the sink space by picking the objects in the sink and placing them on the counter."
        return ep_meta

    def _get_obj_cfgs(self):

        cfgs = []
        self.num_sink_objs = self.rng.choice([1, 2, 3])
        for i in range(self.num_sink_objs):
            cfgs.append(
                dict(
                    name=f"obj{i}",
                    exclude_obj_groups=["food"],
                    graspable=True,
                    washable=True,
                    placement=dict(
                        fixture=self.sink,
                        size=(0.25, 0.25),
                        pos=(0.0, 1.0),
                    ),
                )
            )
        return cfgs

    def _check_success(self):

        gripper_objs_far = all(
            [OU.gripper_obj_far(self, f"obj{i}") for i in range(self.num_sink_objs)]
        )
        objs_on_counter = all(
            [
                OU.check_obj_fixture_contact(self, f"obj{i}", self.counter)
                for i in range(self.num_sink_objs)
            ]
        )
        return objs_on_counter and gripper_objs_far
