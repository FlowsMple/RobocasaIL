from robocasa.environments.kitchen.kitchen import *


class FlipSausage(Kitchen):
    """
    Flip Sausage: composite task for Frying Foods activity.

    Simulates flipping a sausage while frying.

    Steps:
        1) Pick up the sausage in the pan on the stove.
        2) Flip it by rotating it at least 35 degrees.
        3) Place the sausage back in the pan.
    """

    def __init__(self, obj_registries=None, *args, **kwargs):
        obj_registries = obj_registries or []
        obj_registries = list(obj_registries)
        if "aigen" not in obj_registries:
            obj_registries.append("aigen")
        super().__init__(obj_registries=obj_registries, *args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        self.stove = self.register_fixture_ref("stove", dict(id=FixtureType.STOVE))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.stove)
        )

        self.init_robot_base_ref = self.stove

        if "refs" in self._ep_meta:
            self.knob = self._ep_meta["refs"]["knob"]
        else:
            valid_knobs = []

            for knob, joint in self.stove.knob_joints.items():
                if joint is not None and not knob.startswith("rear"):
                    valid_knobs.append(knob)

            self.knob = self.rng.choice(list(valid_knobs))

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Flip the sausage in the pan on the stove by rotating or rolling it."
        ep_meta["knob"] = self.knob
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.stove.set_knob_state(env=self, rng=self.rng, knob=self.knob, mode="on")
        self.flipped = False
        self.sausage_gripped = False
        self.timer = 0

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="sausage",
                obj_groups="sausage",
                placement=dict(
                    fixture=self.stove,
                    sample_region_kwargs=dict(
                        locs=[self.knob],
                    ),
                    ensure_object_boundary_in_range=False,
                    size=(0.05, 0.05),
                    try_to_place_in="pan",
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check for successful flip of the sausage. In this version, success requires:
        1. The sausage is grasped at some point.
        2. The sausage's orientation has changed significantly (at least 35 degrees in roll OR pitch).
        3. The sausage is back fully inside the pan.
        """
        sausage_body_id = self.obj_body_id["sausage"]
        sausage_pos = np.array(self.sim.data.body_xpos[sausage_body_id])
        sausage_quat = np.array(self.sim.data.body_xquat[sausage_body_id])

        if not hasattr(self, "initial_sausage_quat"):
            self.initial_sausage_quat = sausage_quat

        gripped_now = OU.check_obj_grasped(self, "sausage")
        if not self.sausage_gripped:
            self.sausage_gripped = OU.check_obj_grasped(self, "sausage")
            if not gripped_now:
                return False

        init_roll, init_pitch, init_yaw = OU.quaternion_to_euler(
            self, self.initial_sausage_quat
        )
        curr_roll, curr_pitch, curr_yaw = OU.quaternion_to_euler(self, sausage_quat)

        roll_diff = np.abs((curr_roll - init_roll + np.pi) % (2 * np.pi) - np.pi)
        pitch_diff = np.abs((curr_pitch - init_pitch + np.pi) % (2 * np.pi) - np.pi)

        roll_threshold = np.pi * (35 / 180)  # only 35 degrees necessary
        pitch_threshold = np.pi * (35 / 180)

        flipped_orientation = roll_diff > roll_threshold or pitch_diff > pitch_threshold

        sausage_fully_in_pan = self.stove.obj_fully_inside_receptacle(
            self, "sausage", "sausage_container", tol=0.01
        )

        if flipped_orientation:
            self.flipped = True

        if not self.flipped:
            return False

        if sausage_fully_in_pan:
            self.timer += 1

        if self.timer >= 20:
            return True
        else:
            return False
