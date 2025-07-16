from robocasa.environments.kitchen.kitchen import *


class GatherProduceWashing(Kitchen):
    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.sink = self.register_fixture_ref("sink", dict(id=FixtureType.SINK))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.sink)
        )
        self.fridge = self.register_fixture_ref("fridge", dict(id=FixtureType.FRIDGE))
        self.init_robot_base_ref = self.fridge

    def _reset_internal(self):
        self.fridge.open_door(self)
        super()._reset_internal()

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        food0_lang = self.get_obj_lang("food0")
        food1_lang = self.get_obj_lang("food1")
        ep_meta["lang"] = (
            f"Pick {food0_lang} from the fridge and {food1_lang} "
            "from the counter and place them in the bowl next to the sink."
        )
        return ep_meta

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="food0",
                obj_groups=("fruit", "vegetable"),
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.fridge,
                    size=(0.3, 0.25),
                    pos=(0, -1.0),
                    sample_region_kwargs=dict(reg_type="fridge"),
                ),
            )
        )

        cfgs.append(
            dict(
                name=f"food1",
                obj_groups=("fruit", "vegetable"),
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.4, 0.40),
                    pos=("ref", -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="bowl",
                obj_groups="bowl",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.40, 0.40),
                    pos=("ref", -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        return OU.check_obj_in_receptacle(
            self, "food0", "bowl"
        ) and OU.check_obj_in_receptacle(self, "food1", "bowl")
