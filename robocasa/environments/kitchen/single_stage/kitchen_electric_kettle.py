from robocasa.environments.kitchen.kitchen import *


class TurnOnElectricKettle(Kitchen):
    """
    Class encapsulating the atomic turn on electric kettle task.

    Args:
        behavior (str): "turn_on". Used to define the desired electric kettle
            manipulation behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["electric_kettle"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        self.electric_kettle = self.register_fixture_ref(
            "electric_kettle", dict(id=FixtureType.ELECTRIC_KETTLE)
        )
        self.init_robot_base_ref = self.electric_kettle

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Press down the lever to turn on the electric kettle."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _check_success(self):
        return self.electric_kettle.get_state(self)["turned_on"]


class CloseElectricKettleLid(Kitchen):
    """
    Class encapsulating the atomic close electric kettle lid task.

    Args:
        behavior (str): "close". Used to define the desired lid manipulation
            behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["electric_kettle"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        self.electric_kettle = self.register_fixture_ref(
            "electric_kettle", dict(id=FixtureType.ELECTRIC_KETTLE)
        )
        self.init_robot_base_ref = self.electric_kettle

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Close the lid of the electric kettle."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.electric_kettle.set_lid(self, lid_val=1.0)

    def _check_success(self):
        return self.electric_kettle.get_state(self)["lid"] <= 0.01


class OpenElectricKettleLid(Kitchen):
    """
    Class encapsulating the atomic open electric kettle lid task.

    Args:
        behavior (str): "open". Used to define the desired lid manipulation
            behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["electric_kettle"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        self.electric_kettle = self.register_fixture_ref(
            "electric_kettle", dict(id=FixtureType.ELECTRIC_KETTLE)
        )
        self.init_robot_base_ref = self.electric_kettle

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Press the button to open the lid of the electric kettle."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _check_success(self):
        return self.electric_kettle.get_state(self)["lid"] >= 0.95
