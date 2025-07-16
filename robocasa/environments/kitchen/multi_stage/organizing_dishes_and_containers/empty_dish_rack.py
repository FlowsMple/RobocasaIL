from robocasa.environments.kitchen.kitchen import *


class EmptyDishRack(Kitchen):
    """
    Empty Dish Drying Rack: composite task for Organizing Dishes and Containers.

    Simulates the task of removing all drinking containers from the dish rack and placing them in the cabinet.

    Steps:
        Pick up all mugs and cups from the dish rack.
        Place them inside the cabinet where all cups and mugs go.
    """

    EXCLUDE_LAYOUTS = Kitchen.DOUBLE_CAB_EXCLUDED_LAYOUTS

    def __init__(self, enable_fixtures=None, *args, **kwargs):
        enable_fixtures = enable_fixtures or []
        enable_fixtures = list(enable_fixtures) + ["dish_rack"]
        # style id is 1 until other dish rack int regions are annotated
        kwargs["style_ids"] = 1
        super().__init__(enable_fixtures=enable_fixtures, *args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.dish_rack = self.register_fixture_ref(
            "dish_rack", dict(id=FixtureType.DISH_RACK)
        )
        self.cabinet = self.register_fixture_ref(
            "cabinet", dict(id=FixtureType.CABINET_DOUBLE_DOOR, ref=self.dish_rack)
        )
        self.init_robot_base_ref = self.dish_rack

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Pick up the mug from the dish rack and place it inside the cabinet where all mugs go."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.cabinet.open_door(env=self)

    def _get_obj_cfgs(self):
        cfgs = []

        for i in range(2):
            cfgs.append(
                dict(
                    name=f"cabinet_mug{i+1}",
                    obj_groups="mug",
                    placement=dict(
                        fixture=self.cabinet,
                        size=(0.40, 0.20),
                        pos=(-0.9 + (i * 0.3), -1.0),
                    ),
                )
            )

        cfgs.append(
            dict(
                name="mug",
                obj_groups="mug",
                object_scale=0.85,
                placement=dict(
                    fixture=self.dish_rack,
                    size=(0.3, 0.3),
                    pos=(-1.0, -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        if not OU.obj_inside_of(self, "mug", self.cabinet):
            return False

        if OU.gripper_obj_far(self, obj_name="mug"):
            return True
        else:
            return False
