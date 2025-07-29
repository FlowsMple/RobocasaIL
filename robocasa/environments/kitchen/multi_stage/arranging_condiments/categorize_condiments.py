from robocasa.environments.kitchen.kitchen import *


class CategorizeCondiments(Kitchen):
    """
    Categorizes Condiments: composite task for Arranging Condiments activity.

    Simulates the task of categorizing the condiments in the cabinet.

    Steps:
        Put the shaker from the counter next to the shaker in the cabinet. 
        Put the condiment bottle from the counter next to the condiment bottle in the cabinet.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.cab = self.register_fixture_ref(
            "cab", dict(id=FixtureType.CABINET)
        )
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.cab)
        )
        self.init_robot_base_ref = self.counter

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Put the shaker and condiment bottle from the counter next to their counterparts in the cabinet."
        return ep_meta

    def _setup_scene(self):
        """
        Resets simulation internal configurations.
        """
        super()._setup_scene()
        self.cab.open_door(self)

    def _get_obj_cfgs(self):
        cfgs = []
        cfgs.append(
            dict(
                name="obj1",
                obj_groups=["condiment_bottle", "ketchup", "syrup_bottle"],
                graspable=True,
                init_robot_here=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.50, 0.30),
                    pos=("ref", -1),
                ),
            )
        )

        cfgs.append(
            dict(
                name="obj2",
                obj_groups="shaker",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.50, 0.30),
                    pos=("ref", -1),
                ),
            )
        )
    

        # randomize the side of the cabinet that already has a can
        side = int(self.rng.choice([-1, 1]))

        cfgs.append(
            dict(
                name="cab_obj1",
                obj_groups=["condiment_bottle", "ketchup", "syrup_bottle"],
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.2, 0.30),
                    pos=(side, -0.3),
                ),
            )
        )

        cfgs.append(
            dict(
                name="cab_obj2",
                obj_groups="shaker",
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.2, 0.30),
                    pos=(side * -1, 0.3),
                ),
            )
        )

        cfgs.append(
            dict(
                name="distr_counter1",
                obj_groups="all",
                exclude_obj_groups=["condiment"],
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(1.0, 0.30),
                    pos=(0.0, 1.0),
                    offset=(0.0, -0.05),
                ),
            )
        )

        return cfgs


    def _check_obj_in_cab(self, obj_name):
        return OU.obj_inside_of(self, obj_name, self.cab) and self._close_to_cab_cans(
            obj_name
        )
        
    def _dist_between_obj(self, obj_name1, obj_name2):
        obj1 = self.objects[obj_name1]
        obj2 = self.objects[obj_name2]

        obj1_pos = np.array(self.sim.data.body_xpos[self.obj_body_id[obj1.name]])
        obj2_pos = np.array(self.sim.data.body_xpos[self.obj_body_id[obj2.name]])
        return np.linalg.norm(obj1_pos - obj2_pos)

    def _check_success(self):
        obj1_inside_cab = OU.obj_inside_of(self, "obj1", self.cab)
        obj2_inside_cab = OU.obj_inside_of(self, "obj2", self.cab)

        dist_to_obj1 = self._dist_between_obj("cab_obj1", "obj1")
        dist_to_obj2 = self._dist_between_obj("cab_obj2", "obj2")
        dist_apart = self._dist_between_obj("obj1", "obj2")
        ratio = 1.5 
        
        cans_close = dist_to_obj1 * ratio < dist_apart and dist_to_obj2 * ratio < dist_apart
    

        gripper_obj_far = OU.gripper_obj_far(self, "obj1") and OU.gripper_obj_far(
            self, "obj2"
        )

        return obj1_inside_cab and obj2_inside_cab and cans_close and gripper_obj_far
