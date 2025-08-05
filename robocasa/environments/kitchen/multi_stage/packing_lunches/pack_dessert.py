from robocasa.environments.kitchen.kitchen import *


class PackDessert(Kitchen):
    """
    Pack Dessert: composite task for Packing Lunches activity.

    Simulates the task of adding dessert to a tupperware that already contains a cooked item.

    Steps:
        1. Take the dessert item and add it to a tupperware that contains a cooked item.
        2. Ensure both items are properly packed in the tupperware.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER)
        )
        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        sweets_lang = self.get_obj_lang("dessert")
        cooked_lang = self.get_obj_lang("cooked_food")
        ep_meta["lang"] = (
            f"Add the {sweets_lang} to the tupperware that contains the {cooked_lang}."
        )
        return ep_meta

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="cooked_food",
                obj_groups="cooked_food",
                init_robot_here=True,
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    size=(0.5, 0.5),
                    pos=(0, -1.0),
                    try_to_place_in="tupperware",
                    try_to_place_in_kwargs=dict(
                        object_scale=(2.5, 2.5, 1.25),
                    ),
                    rotation=(0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="dessert",
                obj_groups="sweets",
                exclude_obj_groups="sugar_cube",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    reuse_region_from="cooked_food_container",
                    size=(0.5, 0.2),
                    pos=(0, -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        return (
            OU.check_obj_in_receptacle(self, "cooked_food", "cooked_food_container")
            and OU.check_obj_in_receptacle(self, "dessert", "cooked_food_container")
            and OU.gripper_obj_far(self, "dessert")
        )
