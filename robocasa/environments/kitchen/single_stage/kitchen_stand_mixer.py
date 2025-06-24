from robocasa.environments.kitchen.kitchen import *


class OpenStandMixerHead(Kitchen):
    """
    Class encapsulating the atomic stand mixer head tasks.

    Args:
        behavior (str): "open". Used to define the desired head manipulation
            behavior for the task.
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["stand_mixer"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.stand_mixer = self.get_fixture(FixtureType.STAND_MIXER)
        self.init_robot_base_ref = self.stand_mixer

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Open the head of the stand mixer."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _check_success(self):
        """
        Check if the stand mixer head is open.

        Returns:
            bool: True if the head is open, False otherwise.
        """
        return self.stand_mixer.get_state(self)["head"] > 0.99


class CloseStandMixerHead(Kitchen):
    """
    Class encapsulating the atomic stand mixer head tasks.

    Args:
        behavior (str): "close". Used to define the desired head manipulation
            behavior for the task.
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["stand_mixer"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.stand_mixer = self.get_fixture(FixtureType.STAND_MIXER)
        self.init_robot_base_ref = self.stand_mixer

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Close the head of the stand mixer."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.stand_mixer.set_head_pos(self)

    def _check_success(self):
        """
        Check if the stand mixer head is closed.

        Returns:
            bool: True if the head is closed, False otherwise.
        """
        return self.stand_mixer.get_state(self)["head"] < 0.01


class PlaceInStandMixerBowl(Kitchen):
    """
    Class encapsulating the task of placing food items in the stand mixer bowl.

    Args:
        behavior (str): "place". Used to define the desired item placement behavior.
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["stand_mixer"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.stand_mixer = self.get_fixture(FixtureType.STAND_MIXER)
        self.counter = self.get_fixture(
            FixtureType.COUNTER_NON_CORNER, ref=self.stand_mixer
        )

        self.init_robot_base_ref = self.stand_mixer

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Place the food item in the stand mixer bowl."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.stand_mixer.set_head_pos(self)

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="obj",
                obj_groups=("cheese", "bread", "cake"),
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.stand_mixer,
                        loc="left_right",
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        """
        Check if the food item is inside the stand mixer bowl.

        Returns:
            bool: True if the food item is inside the bowl, False otherwise.
        """
        return self.stand_mixer.check_item_in_bowl(self, "obj") and OU.gripper_obj_far(
            self, "obj"
        )
