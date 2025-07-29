from robocasa.environments.kitchen.kitchen import *


class OrganizeCondiments(Kitchen):
    """
    Organize Condiments: composite task for Arranging Condiments activity.

    Simulates the task of organizing the condiments in the cabinet.

    Steps:
        Place the shakers and condiments close together. 
        Organize the shakers to be in front of the condiments.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()
        self.cab = self.register_fixture_ref(
            "cab", dict(id=FixtureType.CABINET)
        )
        self.init_robot_base_ref = self.cab

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = (
            "Place the shakers and condiments close together. "
            "Organize the shakers to be in front of the condiments."
        )
        return ep_meta

    def _setup_scene(self):
        """
        Resets simulation internal configurations.
        """
        super()._setup_scene()
        self.cab.open_door(self)

    def _get_obj_cfgs(self):
        cfgs = []
        # randomize the side of the cabinet that already has a can
        side = int(self.rng.choice([-1, 1]))

        cfgs.append(
            dict(
                name="cab_obj1",
                obj_groups=["condiment_bottle", "ketchup", "syrup_bottle"],
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.5, 0.20),
                    pos=(0, -1.0),
                ),
            )
        )
        
        cfgs.append(
            dict(
                name="cab_obj2",
                obj_groups=["condiment_bottle", "ketchup", "syrup_bottle"],
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.5, 0.20),
                    pos=(0, -1.0),
                ),
            )
        )

        cfgs.append(
            dict(
                name="cab_obj3",
                obj_groups="shaker",
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.5, 0.20),
                    pos=(0, -1.0),
                ),
            )
        )
        
        cfgs.append(
            dict(
                name="cab_obj4",
                obj_groups="shaker",
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.5, 0.20),
                    pos=(0, -1.0),
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
    
    def _obj_to_robot(self, obj_name):
        obj = self.objects[obj_name]
        obj_pos = np.array(self.sim.data.body_xpos[self.obj_body_id[obj.name]])
        robot_pos = self.sim.data.site_xpos[self.robots[0].eef_site_id["right"]]
        return np.linalg.norm(obj_pos - robot_pos)

    def _check_success(self):
        
        dist_obj2 = self._dist_between_obj("cab_obj1", "cab_obj2")
        dist_obj3 = self._dist_between_obj("cab_obj1", "cab_obj3")
        dist_obj4 = self._dist_between_obj("cab_obj1", "cab_obj4")

        objs_close = dist_obj2 < 0.2 and dist_obj3 < 0.2 and dist_obj4 < 0.2
        
        robot_obj1 = self._obj_to_robot("cab_obj1")
        robot_obj2 = self._obj_to_robot("cab_obj2")
        robot_obj3 = self._obj_to_robot("cab_obj3")
        robot_obj4 = self._obj_to_robot("cab_obj4")
        
        threshold = 0.025
        
        shakers_infront = robot_obj3 + threshold < robot_obj1 and robot_obj3 + threshold < robot_obj2 and robot_obj4 + threshold < robot_obj1 and robot_obj4 + threshold < robot_obj2

        gripper_obj_far = OU.gripper_obj_far(self, "cab_obj3") and OU.gripper_obj_far(
            self, "cab_obj4"
        )
        
        return shakers_infront and objs_close and gripper_obj_far
