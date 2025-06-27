from robocasa.environments.kitchen.kitchen import *


class AdjustToasterOvenTemperature(Kitchen):
    """
    Class encapsulating the atomic toaster oven temperature tasks.

    Args:
        behavior (str): "adjust". Used to define the desired temperature
            manipulation behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["toaster_oven"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.toaster_oven = self.register_fixture_ref(
            "toaster_oven", dict(id=FixtureType.TOASTER_OVEN)
        )
        self.initial_temp = float(self.rng.random())

        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        direction = "Increase" if self.should_increase else "Decrease"
        ep_meta["lang"] = f"{direction} the toaster oven temperature."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.toaster_oven.set_temperature(self, self.initial_temp)
        self.should_increase = self.initial_temp < 0.5

    def _check_success(self):
        toaster_oven_state = self.toaster_oven.get_state(self)
        current_temp = toaster_oven_state["temperature"]
        temp_diff = current_temp - self.initial_temp

        if self.should_increase:
            return temp_diff >= 0.15
        else:
            return temp_diff <= -0.15


class TurnOnToasterOven(Kitchen):
    """
    Class encapsulating the atomic toaster oven timer tasks.

    Args:
        behavior (str): "turn_on". Used to define the desired timer
            manipulation behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["toaster_oven"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.toaster_oven = self.register_fixture_ref(
            "toaster_oven", dict(id=FixtureType.TOASTER_OVEN)
        )
        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Turn on the toaster oven by setting the timer."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _check_success(self):
        return self.toaster_oven.get_state(self)["time"] >= 0.1


class SlideToasterOvenRack(Kitchen):
    """
    Class encapsulating the atomic toaster oven rack sliding tasks.

    Args:
        behavior (str): "pull" or "push". Used to define the desired rack
            sliding behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["toaster_oven"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.toaster_oven = self.register_fixture_ref(
            "toaster_oven", dict(id=FixtureType.TOASTER_OVEN)
        )
        self.init_robot_base_ref = self.toaster_oven
        self.should_pull = self.rng.random() > 0.5

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        direction = "out" if self.should_pull else "in"
        ep_meta["lang"] = f"Fully slide the toaster oven rack {direction}."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.toaster_oven.open_door(self)

        if not self.should_pull:
            self.toaster_oven.slide_rack(self)

    def _check_success(self):
        toaster_oven_state = self.toaster_oven.get_state(self)

        if "rack" in toaster_oven_state:
            current_pos = toaster_oven_state["rack"]
        else:
            current_pos = toaster_oven_state["tray"]

        if self.should_pull:
            return current_pos >= 0.95
        else:
            return current_pos <= 0.05
