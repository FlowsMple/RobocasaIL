from robocasa.environments.kitchen.kitchen import *


class PrepareVegetableRoasting(Kitchen):
    def __init__(self, *args, **kwargs):
        # internal state variables for the task
        self.vegetable_washed = False
        self.washed_time = 0
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        self.sink = self.register_fixture_ref("sink", dict(id=FixtureType.SINK))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.sink, size=(0.6, 0.6))
        )
        self.fridge = self.register_fixture_ref("fridge", dict(id=FixtureType.FRIDGE))
        self.init_robot_base_ref = self.fridge

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        vegetable = self.get_obj_lang("vegetable")
        ep_meta["lang"] = (
            f"Pick the {vegetable} "
            "from the fridge and place it in the sink. "
            f"Then turn on the sink to wash the {vegetable}. "
            "Then place the vegetable on the tray next to the sink."
        )
        return ep_meta

    def _reset_internal(self):
        # reset task progress variables
        self.vegetable_washed = False
        self.washed_time = 0
        self.fridge.open_door(self)
        super()._reset_internal()

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="vegetable",
                obj_groups=("vegetable"),
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.fridge,
                    size=(0.3, 0.25),
                    pos=(0, -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="tray",
                obj_groups="tray",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink, loc="left_right", top_size=(0.6, 0.6)
                    ),
                    size=(0.6, 0.6),
                    pos=("ref", -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        vegetables_in_sink = OU.obj_inside_of(self, "vegetable", self.sink)
        # make sure the vegetable washed for at least 10 steps
        if self.sink.check_obj_under_water(self, "vegetable") and vegetables_in_sink:
            self.washed_time += 1
            self.vegetable_washed = self.washed_time > 10
        else:
            self.washed_time = 0
        vegetables_on_tray = OU.check_obj_in_receptacle(self, f"vegetable", "tray")

        return (
            self.vegetable_washed
            and vegetables_on_tray
            and OU.gripper_obj_far(self, "vegetable")
        )
