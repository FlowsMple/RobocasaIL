from robocasa.environments.kitchen.kitchen import *


class UtilizeWaterVariance(Kitchen):
    SOFT_FOOD = ["eggplant", "pear"]
    HARD_FOOD = ["carrot", "apple"]

    def __init__(self, *args, **kwargs):
        self.ep_food = None
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.sink = self.get_fixture(FixtureType.SINK)
        self.init_robot_base_ref = self.sink

    def get_ep_meta(self):

        ep_meta = super().get_ep_meta()
        # don't specify the food name to force policy to reason visually
        ep_meta["lang"] = (
            "Turn on the sink to a high water pressure for hard food and low water "
            "pressure for softer fruits."
        )
        return ep_meta

    def _reset_internal(self):
        super()._reset_internal()
        self.sink.set_handle_state(mode="off", env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        cfgs = []
        food = self.rng.choice(self.HARD_FOOD + self.SOFT_FOOD)
        self.ep_food = food
        cfgs.append(
            dict(
                name=food,
                obj_groups=food,
                placement=dict(
                    fixture=self.get_fixture(FixtureType.COUNTER, ref=self.sink),
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        handle_state = self.sink.get_handle_state(env=self)
        if self.ep_food in self.SOFT_FOOD:
            return handle_state["water_pressure"] == "low"

        return handle_state["water_pressure"] == "high"
