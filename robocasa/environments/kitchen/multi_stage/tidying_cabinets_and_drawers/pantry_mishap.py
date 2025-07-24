from robocasa.environments.kitchen.kitchen import *
from robocasa.environments.kitchen.single_stage.kitchen_drawer import *

# inherit from ManipulateDrawer class to start off the task with the drawer open
class PantryMishap(ManipulateDrawer):
    """
    Pantry Mishap: composite task for Tidying Cabinets And Drawers activity.

    Simulates the task of organizing the pantry after a mishap from the incorrect
    placement of items in the cabinet.

    Steps:
        Open the cabinet. Pick the vegetable and place it on the counter. Pick the
        canned food and place it in the drawer. Close the cabinet.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(behavior="close", *args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.drawer)
        )

        self.cab = self.register_fixture_ref(
            "cab", dict(id=FixtureType.CABINET, ref=self.drawer)
        )

        self.init_robot_base_ref = self.cab

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        vegetable = self.get_obj_lang("vegetable")
        ep_meta["lang"] = (
            f"Place the {vegetable} on the counter and the canned food in the open drawer. "
            "Close the cabinet."
        )
        return ep_meta

    def _setup_scene(self):
        """
        Resets simulation internal configurations.
        """
        super()._setup_scene()
        self.cab.open_door(env=self)

    def _get_obj_cfgs(self):
        cfgs = []
        cfgs.append(
            dict(
                name="vegetable",
                obj_groups="vegetable",
                placement=dict(
                    fixture=self.cab,
                    size=(0.5, 0.2),
                    pos=(0, -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="canned_food",
                obj_groups="canned_food",
                placement=dict(
                    fixture=self.cab,
                    size=(0.50, 0.20),
                    pos=(0, -1.0),
                ),
            )
        )
        return cfgs

    def _check_success(self):
        vegetable_on_counter = OU.check_obj_fixture_contact(
            self, "vegetable", self.counter
        )
        canned_food_in_drawer = OU.obj_inside_of(self, "canned_food", self.drawer)

        cab_closed = self.cab.is_closed(env=self)

        return vegetable_on_counter and canned_food_in_drawer and cab_closed
