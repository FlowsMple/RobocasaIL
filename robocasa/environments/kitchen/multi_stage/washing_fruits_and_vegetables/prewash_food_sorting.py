from robocasa.environments.kitchen.kitchen import *
from robocasa.models.objects.kitchen_objects import get_cats_by_type


class PrewashFoodSorting(Kitchen):
    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.sink = self.register_fixture_ref("sink", dict(id=FixtureType.SINK))
        self.cabinet = self.register_fixture_ref(
            "cabinet", dict(id=FixtureType.CABINET, ref=self.sink)
        )
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.sink)
        )
        self.init_robot_base_ref = self.cabinet

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        food12_name = self.get_obj_lang("food1")
        food3_name = self.get_obj_lang("food3")
        ep_meta["lang"] = (
            f"Pick the {food12_name}s from the cabinet and place them in one bowl. "
            f"Place the {food3_name} in the other bowl."
        )
        return ep_meta

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()
        self.cabinet.open_door(self)

    def _get_obj_cfgs(self):

        food_items = get_cats_by_type(
            types=["vegetable", "fruit"], obj_registries=self.obj_registries
        )
        food1, food2 = self.rng.choice(food_items, size=2, replace=False)

        cfgs = []

        cfgs.append(
            dict(
                name="food1",
                obj_groups=food1,
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.cabinet,
                    size=(0.3, 0.3),
                    pos=(0, -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="food2",
                obj_groups=food1,
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.cabinet,
                    size=(0.3, 0.3),
                    pos=(0, -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="food3",
                obj_groups=food2,
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.sink,
                    size=(0.2, 0.2),
                    pos=(0, 1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="bowl1",
                obj_groups="bowl",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.50, 0.50),
                    pos=("ref", -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="bowl2",
                obj_groups="bowl",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.50, 0.50),
                    pos=("ref", -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):

        food1_in_bowl1 = OU.check_obj_in_receptacle(self, "food1", "bowl1")
        food1_in_bowl2 = OU.check_obj_in_receptacle(self, "food1", "bowl2")
        food2_in_bowl1 = OU.check_obj_in_receptacle(self, "food2", "bowl1")
        food2_in_bowl2 = OU.check_obj_in_receptacle(self, "food2", "bowl2")
        food3_in_bowl1 = OU.check_obj_in_receptacle(self, "food3", "bowl1")
        food3_in_bowl2 = OU.check_obj_in_receptacle(self, "food3", "bowl2")

        food12_in_bowl_1 = food1_in_bowl1 and food2_in_bowl1
        food12_in_bowl_2 = food1_in_bowl2 and food2_in_bowl2

        return (food12_in_bowl_1 and food3_in_bowl2) or (
            food12_in_bowl_2 and food3_in_bowl1
        )
