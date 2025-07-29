from robocasa.environments.kitchen.kitchen import *


class LineUpCondiments(Kitchen):
    """
    Line Up Condiments: composite task for Arranging Condiments activity.

    Simulates the task of organizing the condiments on a counter.

    Steps:
        Pick and place condiments on the counter in a line.
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
        ] = "Place condiments on the counter in a line side to side."
        return ep_meta

    def _get_obj_cfgs(self):
        cfgs = []
        cfgs.append(
            dict(
                name="obj1",
                obj_groups="condiment",
                graspable=True,
                init_robot_here=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.60, 0.30),
                    pos=("ref", -1),
                ),
            )
        )

        cfgs.append(
            dict(
                name="obj2",
                obj_groups="condiment",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.60, 0.30),
                    pos=("ref", -1),
                ),
            )
        )
        
        cfgs.append(
            dict(
                name="obj3",
                obj_groups="condiment",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.60, 0.30),
                    pos=("ref", -1),
                ),
            )
        )
        
        cfgs.append(
            dict(
                name="obj4",
                obj_groups="condiment",
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.60, 0.30),
                    pos=("ref", -1),
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
        
        cfgs.append(
            dict(
                name="distr_counter2",
                obj_groups="all",
                exclude_obj_groups=["condiment"],
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.50, 0.50),
                    pos=("ref", -1),
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
        
        #determine if the objects are in a line
        obj1_pos = np.array(self.sim.data.body_xpos[self.obj_body_id["obj1"]])
        obj2_pos = np.array(self.sim.data.body_xpos[self.obj_body_id["obj2"]])
        obj3_pos = np.array(self.sim.data.body_xpos[self.obj_body_id["obj3"]])
        obj4_pos = np.array(self.sim.data.body_xpos[self.obj_body_id["obj4"]])
        
        obj1_obj2_slope = (obj2_pos[1] - obj1_pos[1]) / (obj2_pos[0] - obj1_pos[0])
        obj1_obj3_slope = (obj3_pos[1] - obj1_pos[1]) / (obj3_pos[0] - obj1_pos[0])
        obj1_obj4_slope = (obj4_pos[1] - obj1_pos[1]) / (obj4_pos[0] - obj1_pos[0])
        
        slope_threshold = 0.15
        slope_match = (
            abs(obj1_obj2_slope - obj1_obj3_slope) < slope_threshold and
            abs(obj1_obj2_slope - obj1_obj4_slope) < slope_threshold
        )
        
        obj1_obj2_dist = np.linalg.norm(obj1_pos - obj2_pos)
        obj1_obj3_dist = np.linalg.norm(obj1_pos - obj3_pos)
        obj1_obj4_dist = np.linalg.norm(obj1_pos - obj4_pos)
        obj1_dist = min(obj1_obj2_dist, obj1_obj3_dist, obj1_obj4_dist)
        
        obj2_obj1_dist = np.linalg.norm(obj2_pos - obj1_pos)
        obj2_obj3_dist = np.linalg.norm(obj2_pos - obj3_pos)
        obj2_obj4_dist = np.linalg.norm(obj2_pos - obj4_pos)
        obj2_dist = min(obj2_obj1_dist, obj2_obj3_dist, obj2_obj4_dist)
        
        obj3_obj1_dist = np.linalg.norm(obj3_pos - obj1_pos)
        obj3_obj2_dist = np.linalg.norm(obj3_pos - obj2_pos)
        obj3_obj4_dist = np.linalg.norm(obj3_pos - obj4_pos)
        obj3_dist = min(obj3_obj1_dist, obj3_obj2_dist, obj3_obj4_dist)
        
        obj4_obj1_dist = np.linalg.norm(obj4_pos - obj1_pos)
        obj4_obj2_dist = np.linalg.norm(obj4_pos - obj2_pos)
        obj4_obj3_dist = np.linalg.norm(obj4_pos - obj3_pos)
        obj4_dist = min(obj4_obj1_dist, obj4_obj2_dist, obj4_obj3_dist)

        dist_threshold = 0.15
        dist_match = (
            obj1_dist < dist_threshold and
            obj2_dist < dist_threshold and
            obj3_dist < dist_threshold and
            obj4_dist < dist_threshold
        )
        
        gripper_obj_far = OU.gripper_obj_far(self, "obj1") and OU.gripper_obj_far( self, "obj2" ) and OU.gripper_obj_far( self, "obj3" ) and OU.gripper_obj_far( self, "obj4" ) 
        
        return slope_match and dist_match and gripper_obj_far
