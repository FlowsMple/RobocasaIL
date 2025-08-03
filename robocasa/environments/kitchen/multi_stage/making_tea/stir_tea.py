from robocasa.environments.kitchen.kitchen import *


class StirTea(Kitchen):
    """Stir Tea: composite task for Making Tea activity.
    Simulates the task of stirring tea with a spoon in a pitcher.
    Steps:
        1. Add sweetener to the tea.
        2. Stir the tea with a spoon in the pitcher."""

    NUM_STIRS_FOR_SUCCESS = 15

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, size=(0.6, 0.4), full_depth_region=True),
        )
        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()

        ep_meta[
            "lang"
        ] = f"Add sugar cube to the tea and stir it. Let go of the spoon once done."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        OU.add_obj_liquid_site(self, "pitcher", (0.49, 0.12, 0.025, 0.4))
        self.stirred_timesteps = 0

    def _get_obj_cfgs(self):
        cfgs = []
        cfgs.append(
            dict(
                name="pitcher",
                obj_groups="jug_wide_opening",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(top_size=(0.6, 0.4), full_depth_region=True),
                    size=(1, 0.4),
                    pos=(0, -1.0),
                ),
                init_robot_here=True,
                object_scale=[1.5, 1.5, 1.0],
            )
        )

        cfgs.append(
            dict(
                name="spoon",
                obj_groups="spoon",
                placement=dict(
                    fixture=self.counter,
                    size=(1, 0.4),
                    pos=(0, -1.0),
                    reuse_region_from="pitcher",
                ),
                object_scale=[0.8, 1.4, 3],
            )
        )

        cfgs.append(
            dict(
                name="sugar_cube",
                obj_groups="sugar_cube",
                placement=dict(
                    fixture=self.counter,
                    size=(1, 0.15),
                    pos=(0, -1.0),
                    reuse_region_from="pitcher",
                ),
                object_scale=1.3,
            )
        )

        return cfgs

    def _detect_stirring(self, movement_threshold=0.08):
        spoon_pos = np.array(self.sim.data.body_xpos[self.obj_body_id["spoon"]])
        prev_spoon_pos = getattr(self, f"prev_spoon_pos", spoon_pos)
        movement_vector = spoon_pos - prev_spoon_pos
        movement_magnitude = np.linalg.norm(movement_vector[:2]) * 10
        movement_detected = movement_magnitude > movement_threshold
        setattr(self, "prev_spoon_pos", spoon_pos)
        return movement_detected

    def _check_success(self):
        sugar_in_pitcher = OU.check_obj_in_receptacle(self, "sugar_cube", "pitcher")
        spoon_in_pitcher = OU.object_contact_with_liquid(self, "spoon", "pitcher")
        if spoon_in_pitcher and sugar_in_pitcher and self._detect_stirring():
            self.stirred_timesteps += 1
        gripper_obj_far = OU.gripper_obj_far(self, obj_name="spoon")
        return (
            sugar_in_pitcher
            and self.stirred_timesteps > self.NUM_STIRS_FOR_SUCCESS
            and gripper_obj_far
        )
