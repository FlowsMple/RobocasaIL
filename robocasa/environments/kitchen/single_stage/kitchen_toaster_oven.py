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
        direction = "up" if self.should_increase else "down"
        ep_meta[
            "lang"
        ] = f"Adjust the toaster oven temperature {direction} from its current setting."
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


class PlaceItemIntoToasterOven(Kitchen):
    """
    Class encapsulating the atomic toaster oven item placement tasks.

    Args:
        behavior (str): "place". Used to define the desired item placement
            behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["toaster_oven"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.toaster_oven = self.register_fixture_ref(
            "toaster_oven", dict(id=FixtureType.TOASTER_OVEN)
        )
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.toaster_oven)
        )
        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Place the item on the rack of the toaster oven."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.toaster_oven.slide_rack(self)

    def _get_obj_cfgs(self):
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups=("bread_food"),
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.toaster_oven,
                        loc="left_right",
                    ),
                    size=(0.45, 0.30),
                    pos=("ref", -1.0),
                    try_to_place_in="plate",
                ),
            )
        )
        return cfgs

    def _check_success(self):
        return self.toaster_oven.check_rack_contact(self, "obj") and OU.gripper_obj_far(
            self, "obj"
        )


class TakeItemOutToasterOven(Kitchen):
    """
    Class encapsulating the atomic toaster oven item removal tasks.

    Args:
        behavior (str): "take_out". Used to define the desired item removal
            behavior for the task
    """

    def __init__(self, *args, **kwargs):
        kwargs["enable_fixtures"] = ["toaster_oven"]
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.toaster_oven = self.register_fixture_ref(
            "toaster_oven", dict(id=FixtureType.TOASTER_OVEN)
        )
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.toaster_oven)
        )
        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Take the item out and place it on the counter."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.toaster_oven.slide_rack(self)

    def _get_obj_cfgs(self):
        cfgs = []

        cfgs.append(
            dict(
                name="item",
                obj_groups=("bread_food"),
                graspable=True,
                placement=dict(
                    fixture=self.toaster_oven,
                    size=(0.50, 0.40),
                    pos=(0, -1.0),
                    offset=(0, -0.23),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        return OU.check_obj_fixture_contact(
            self, "item", self.counter
        ) and OU.gripper_obj_far(self, "item")


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
