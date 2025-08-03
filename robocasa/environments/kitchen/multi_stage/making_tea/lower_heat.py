from robocasa.environments.kitchen.kitchen import *


class LowerHeat(Kitchen):
    """
    Lower Heat: composite task for Making Tea activity.
    Simulates the task of lowering the heat of a kettle on the stove.
    Steps:
        1. Lower the heat of the burner.
    """

    def __init__(self, knob_id="random", *args, **kwargs):
        self.knob_id = knob_id
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.stove = self.register_fixture_ref("stove", dict(id=FixtureType.STOVE))
        self.init_robot_base_ref = self.stove

        if "refs" in self._ep_meta:
            self.knob = self._ep_meta["refs"]["knob"]
        else:
            valid_knobs = [
                k for (k, v) in self.stove.knob_joints.items() if v is not None
            ]
            if self.knob_id == "random":
                self.knob = self.rng.choice(list(valid_knobs))
            else:
                assert self.knob_id in valid_knobs
                self.knob = self.knob_id

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = f"Lower the heat of the kettle."
        ep_meta["refs"] = ep_meta.get("refs", {})
        ep_meta["refs"]["knob"] = self.knob
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.stove.set_knob_state(mode="high", knob=self.knob, env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="kettle",
                obj_groups=("kettle_non_electric"),
                placement=dict(
                    fixture=self.stove,
                    sample_region_kwargs=dict(
                        locs=[self.knob],
                    ),
                    ensure_object_boundary_in_range=False,
                    size=(0.05, 0.05),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        knobs_state = self.stove.get_knobs_state(env=self)
        knob_value = knobs_state[self.knob]

        LOW_HEAT_UPPER_THRESHOLD = self.stove.STOVE_HIGH_MIN - 0.00000001
        LOW_HEAT_LOWER_THRESHOLD = 0.35
        knob_at_low = (
            LOW_HEAT_LOWER_THRESHOLD <= np.abs(knob_value) <= LOW_HEAT_UPPER_THRESHOLD
        )

        return knob_at_low
