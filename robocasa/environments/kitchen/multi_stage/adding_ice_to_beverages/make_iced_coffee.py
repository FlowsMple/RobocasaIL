from robocasa.environments.kitchen.kitchen import *


class MakeIcedCoffee(Kitchen):
    """
    Make Iced Coffee: Add a single ice cube to a glass of coffee.

    Simulates picking up one ice cube and placing it into a glass cup that represents coffee.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.cabinet = self.register_fixture_ref("cabinet", dict(id=FixtureType.CABINET))
        self.counter = self.register_fixture_ref("counter", dict(id=FixtureType.COUNTER, ref=self.cabinet))
        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Pick up an ice cube and place it in the glass of coffee."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        OU.add_obj_liquid_site(self, "cup", [0.65, 0.45, 0.25, 0.8])

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="ice_bowl",
                obj_groups="bowl",
                object_scale=[1, 1, 0.75],
                init_robot_here=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cabinet,
                    ),
                    size=(1.0, 0.4),
                    pos=(0, -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="ice_cube1",
                obj_groups="ice_cube",
                object_scale=0.8,
                placement=dict(
                    object="ice_bowl",
                    size=(1.0, 1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="ice_cube2",
                obj_groups="ice_cube",
                object_scale=0.8,
                placement=dict(
                    object="ice_bowl",
                    size=(1.0, 1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="cup",
                obj_groups="glass_cup",
                object_scale=[1.25, 1.25, 1],
                placement=dict(
                    fixture=self.counter,
                    reuse_region_from="ice_bowl",
                    size=(0.5, 0.25),
                    pos=(0, -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        ice1_in_cup = OU.check_obj_in_receptacle(self, "ice_cube1", "cup", th=0.5)
        ice2_in_cup = OU.check_obj_in_receptacle(self, "ice_cube2", "cup", th=0.5)
        ice_in_cup = ice1_in_cup or ice2_in_cup
        
        gripper_far_from_ice1 = OU.gripper_obj_far(self, "ice_cube1", th=0.15)
        gripper_far_from_ice2 = OU.gripper_obj_far(self, "ice_cube2", th=0.15)
        gripper_far = gripper_far_from_ice1 and gripper_far_from_ice2
        
        return ice_in_cup and gripper_far
