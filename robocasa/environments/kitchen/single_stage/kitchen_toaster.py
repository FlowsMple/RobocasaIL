from robocasa.environments.kitchen.kitchen import *


class TurnOnToaster(Kitchen):
    """
    Class encapsulating the atomic toaster press button tasks.

    Args:
        behavior (str): "turn_on" or "turn_off". Used to define the desired
            toaster manipulation behavior for the task
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the toaster tasks
        """
        super()._setup_kitchen_references()
        self.toaster = self.get_fixture(FixtureType.TOASTER)
        self.init_robot_base_ref = self.toaster

    def get_ep_meta(self):
        """
        Get the episode metadata for the toaster tasks.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Fully pull down the lever on the toaster to turn it on."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the toaster tasks. This includes the object placement configurations.
        Place the object inside the toaster

        Returns:
            list: List of object configurations.
        """
        cfgs = []
        cfgs.append(
            dict(
                name="sandwich_bread_toaster",
                obj_groups=("sandwich_bread",),
                rotate_upright=True,
                object_scale=0.80,
                placement=dict(
                    fixture=self.toaster,
                    rotation=(0, 0),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        """
        Check if the toaster manipulation task is successful.

        Returns:
            bool: True if the task is successful, False otherwise.
        """
        toast_slot = 0
        for slot_pair in range(len(self.toaster.get_state(self).keys())):
            if self.toaster.check_slot_contact(
                self, "sandwich_bread_toaster", slot_pair
            ):
                toast_slot = slot_pair
                break

        return self.toaster.get_state(self, slot_pair=toast_slot)["turned_on"]


class ToasterToPlate(Kitchen):
    """
    Class encapsulating the task of taking items out of the toaster and placing them on a plate.

    Steps:
        Take the toasted item out of the toaster and place it on a plate.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the toaster to plate task
        """
        super()._setup_kitchen_references()
        self.toaster = self.get_fixture(FixtureType.TOASTER)
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.toaster)
        )
        self.init_robot_base_ref = self.toaster

    def get_ep_meta(self):
        """
        Get the episode metadata for the toaster to plate task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = "Place the toasted item on a plate."
        return ep_meta

    def _setup_scene(self):
        super()._setup_scene()

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the toaster to plate task.
        Places a toasted item in the toaster and a plate on the counter.
        """
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups=("sandwich_bread",),
                rotate_upright=True,
                placement=dict(
                    fixture=self.toaster,
                    rotation=(0, 0),
                ),
            )
        )
        cfgs.append(
            dict(
                name="plate",
                obj_groups="plate",
                graspable=False,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.toaster,
                    ),
                    size=(0.80, 0.30),
                    pos=("ref", -1.0),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        """
        Check if the toaster to plate task is successful.
        Checks if the object is on the plate and the gripper is far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_on_plate = OU.check_obj_in_receptacle(self, "obj", "plate")
        gripper_obj_far = OU.gripper_obj_far(self)
        return obj_on_plate and gripper_obj_far
