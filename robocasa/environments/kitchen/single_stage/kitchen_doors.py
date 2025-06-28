from robocasa.environments.kitchen.kitchen import *


class ManipulateDoor(Kitchen):
    """
    Class encapsulating the atomic manipulate door tasks.

    Args:
        behavior (str): "open" or "close". Used to define the desired
            door manipulation behavior for the task.

        fixture_id (str): The door fixture id to manipulate.
    """

    def __init__(self, fixture_id, behavior="open", *args, **kwargs):
        assert behavior in ["open", "close"]
        self.fixture_id = fixture_id
        self.behavior = behavior
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the door tasks.
        """
        super()._setup_kitchen_references()
        self.fxtr = self.register_fixture_ref("fxtr", dict(id=self.fixture_id))
        self.init_robot_base_ref = self.fxtr

    def get_ep_meta(self):
        """
        Get the episode metadata for the door tasks.
        This includes the language description of the task.

        Returns:
            dict: Episode metadata.
        """
        ep_meta = super().get_ep_meta()
        if isinstance(self.fxtr, HingeCabinet) or isinstance(
            self.fxtr, FridgeFrenchDoor
        ):
            door_name = "doors"
        else:
            door_name = "door"
        ep_meta["lang"] = f"{self.behavior} the {self.fxtr.nat_lang} {door_name}"
        return ep_meta

    def _setup_scene(self):
        """
        Reset the environment internal state for the door tasks.
        This includes setting the door state based on the behavior.
        """
        if self.behavior == "open":
            self.fxtr.close_door(env=self)
        elif self.behavior == "close":
            self.fxtr.open_door(env=self)
        # set the door state then place the objects otherwise objects initialized in opened drawer will fall down before the drawer is opened
        super()._setup_scene()

    def _check_success(self):
        """
        Check if the door manipulation task is successful.

        Returns:
            bool: True if the task is successful, False otherwise.
        """
        if self.behavior == "open":
            return self.fxtr.is_open(env=self)
        elif self.behavior == "close":
            return self.fxtr.is_closed(env=self)

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the door tasks. This includes the object placement configurations.
        Place one object inside the door fixture and 1-4 distractors on the counter.
        """
        cfgs = []

        cfgs.append(
            dict(
                name="door_obj",
                obj_groups="all",
                graspable=True,
                microwavable=(True if isinstance(self.fxtr, Microwave) else None),
                placement=dict(
                    fixture=self.fxtr,
                    size=(0.30, 0.30),
                    pos=(None, -1.0),
                ),
            )
        )

        # distractors
        num_distr = self.rng.integers(1, 4)
        for i in range(num_distr):
            cfgs.append(
                dict(
                    name=f"distr_counter_{i+1}",
                    obj_groups="all",
                    placement=dict(
                        fixture=self.get_fixture(FixtureType.COUNTER, ref=self.fxtr),
                        sample_region_kwargs=dict(
                            ref=self.fxtr,
                        ),
                        size=(1.0, 0.50),
                        pos=(None, -1.0),
                        offset=(0.0, 0.10),
                    ),
                )
            )

        return cfgs


class ManipulateLowerDoor(ManipulateDoor):
    X_OFS = 0.2
    Y_OFS = -0.1

    def __init__(
        self,
        fixture_id,
        behavior="open",
        robot_spawn_deviation_pos_x=0.05,
        *args,
        **kwargs,
    ):
        self.robot_side = ""
        self.fixture_id = fixture_id
        assert behavior in ["open", "close"]
        self.behavior = behavior
        super().__init__(
            robot_spawn_deviation_pos_x=robot_spawn_deviation_pos_x,
            fixture_id=fixture_id,
            behavior=behavior,
            *args,
            **kwargs,
        )

    def _load_model(self):
        super()._load_model()
        self._place_robot()

    def _place_robot(self):
        x_ofs = (self.fxtr.width / 2) + self.X_OFS
        TEST_OFS = 0.23
        inits = []

        # compute where the robot placement if it is to the left of the drawer
        (
            robot_base_pos_left,
            robot_base_ori_left,
        ) = EnvUtils.compute_robot_base_placement_pose(
            self, ref_fixture=self.fxtr, offset=(-x_ofs, self.Y_OFS)
        )
        # get a test point to check if the robot is in contact with any fixture.
        test_pos_left, _ = EnvUtils.compute_robot_base_placement_pose(
            self, ref_fixture=self.fxtr, offset=(-x_ofs - TEST_OFS, self.Y_OFS)
        )

        # check if the robot will be in contact with any fixture or wall during initialization
        if not self.check_fxtr_contact(test_pos_left) and not self._point_outside_scene(
            test_pos_left
        ):
            # drawer is to the right of the robot
            inits.append((robot_base_pos_left, robot_base_ori_left, "right"))

        # compute where the robot placement if it is to the right of the drawer
        (
            robot_base_pos_right,
            robot_base_ori_right,
        ) = EnvUtils.compute_robot_base_placement_pose(
            self, ref_fixture=self.fxtr, offset=(x_ofs, self.Y_OFS)
        )
        # get a test point to check if the robot is in contact with any fixture if initialized to the right of the drawer
        test_pos_right, _ = EnvUtils.compute_robot_base_placement_pose(
            self, ref_fixture=self.fxtr, offset=(x_ofs + TEST_OFS, self.Y_OFS)
        )

        if not self.check_fxtr_contact(
            test_pos_right
        ) and not self._point_outside_scene(test_pos_right):
            inits.append((robot_base_pos_right, robot_base_ori_right, "left"))

        if len(inits) == 0:
            return False
        random_index = self.rng.integers(len(inits))
        robot_base_pos, robot_base_ori, side = inits[random_index]
        self.drawer_side = side
        self.init_robot_base_pos_anchor = robot_base_pos
        self.init_robot_base_ori_anchor = robot_base_ori
        return True

    def check_fxtr_contact(self, pos):
        """
        Check if the point is in contact with any fixture

        Args:
            pos (tuple): The position of the point to check

        Returns:
            bool: True if the point is in contact with any fixture, False otherwise
        """
        fxtrs = [
            fxtr
            for fxtr in self.fixtures.values()
            if isinstance(fxtr, Counter)
            or isinstance(fxtr, Stove)
            or isinstance(fxtr, Stovetop)
            or isinstance(fxtr, HousingCabinet)
            or isinstance(fxtr, SingleCabinet)
            or isinstance(fxtr, HingeCabinet)
            or isinstance(fxtr, Fridge)
            or (isinstance(fxtr, Wall) and not isinstance(fxtr, Floor))
        ]

        for fxtr in fxtrs:
            # get bounds of fixture
            if OU.point_in_fixture(point=pos, fixture=fxtr, only_2d=True):
                return True
        return False

    def _point_outside_scene(self, pos):
        walls = [
            fxtr for (name, fxtr) in self.fixtures.items() if isinstance(fxtr, Floor)
        ]
        return not any(
            [
                OU.point_in_fixture(point=pos, fixture=wall, only_2d=True)
                for wall in walls
            ]
        )


class OpenDoor(ManipulateDoor):
    def __init__(self, *args, **kwargs):
        super().__init__(behavior="open", *args, **kwargs)


class CloseDoor(ManipulateDoor):
    def __init__(self, *args, **kwargs):
        super().__init__(behavior="close", *args, **kwargs)


class OpenCabinet(OpenDoor):
    def __init__(self, fixture_id=FixtureType.CABINET_WITH_DOOR, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class CloseCabinet(CloseDoor):
    def __init__(self, fixture_id=FixtureType.CABINET_WITH_DOOR, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class OpenMicrowave(OpenDoor):
    def __init__(self, fixture_id=FixtureType.MICROWAVE, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class CloseMicrowave(CloseDoor):
    def __init__(self, fixture_id=FixtureType.MICROWAVE, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class OpenFridge(OpenDoor):
    def __init__(self, fixture_id=FixtureType.FRIDGE, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class CloseFridge(CloseDoor):
    def __init__(self, fixture_id=FixtureType.FRIDGE, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class OpenDropDownDoor(ManipulateLowerDoor):
    def __init__(self, *args, **kwargs):
        super().__init__(behavior="open", *args, **kwargs)


class CloseDropDownDoor(ManipulateLowerDoor):
    def __init__(self, *args, **kwargs):
        super().__init__(behavior="close", *args, **kwargs)


class OpenOven(OpenDropDownDoor):
    EXCLUDE_LAYOUTS = Kitchen.OVEN_EXCLUDED_LAYOUTS

    def __init__(self, fixture_id=FixtureType.OVEN, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class CloseOven(CloseDropDownDoor):
    EXCLUDE_LAYOUTS = Kitchen.OVEN_EXCLUDED_LAYOUTS
    Y_OFS = -0.25

    def __init__(self, fixture_id=FixtureType.OVEN, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class OpenDishwasher(OpenDropDownDoor):
    # with lower x_ofs the base of the robots sometimes blocks the door from closing all the way
    X_OFS = 0.275

    def __init__(self, fixture_id=FixtureType.DISHWASHER, *args, **kwargs):
        super().__init__(
            fixture_id=fixture_id, robot_spawn_deviation_pos_x=0, *args, **kwargs
        )


class CloseDishwasher(CloseDropDownDoor):
    X_OFS = 0.25
    Y_OFS = -0.25

    def __init__(self, fixture_id=FixtureType.DISHWASHER, *args, **kwargs):
        super().__init__(fixture_id=fixture_id, *args, **kwargs)


class OpenToasterOvenDoor(Kitchen):
    """
    Class encapsulating the atomic toaster oven door tasks.

    Args:
        behavior (str): "open". Used to define the desired door manipulation
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
        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Open the toaster oven door."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _check_success(self):
        return self.toaster_oven.is_open(self)


class CloseToasterOvenDoor(Kitchen):
    """
    Class encapsulating the atomic toaster oven door tasks.

    Args:
        behavior (str): "close". Used to define the desired door manipulation
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
        self.init_robot_base_ref = self.toaster_oven

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Close the toaster oven door."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()
        self.toaster_oven.open_door(self)

    def _check_success(self):
        return self.toaster_oven.is_closed(self)
