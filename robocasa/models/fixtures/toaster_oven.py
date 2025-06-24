from robocasa.models.fixtures import Fixture
import numpy as np


class ToasterOven(Fixture):
    """
    Toaster Oven fixture class
    """

    def __init__(
        self,
        xml="fixtures/toaster_ovens/ToasterOven055",
        name="toaster_oven",
        *args,
        **kwargs,
    ):
        super().__init__(
            xml=xml, name=name, duplicate_collision_geoms=False, *args, **kwargs
        )

        self._door = 0.0
        self._doneness = 0.0
        self._function = 0.0
        self._temperature = 0.0
        self._time = 0.0
        self._rack = 0.0
        self._tray = 0.0

        self._door_target = None
        self._last_time_update = None

        # Initialize joint names dictionary
        joint_prefix = self._get_joint_prefix()
        self._joint_names = {
            "door": f"{joint_prefix}door_joint",
            "doneness": f"{joint_prefix}knob_doneness_joint",
            "function": f"{joint_prefix}knob_function_joint",
            "temperature": f"{joint_prefix}knob_temp_joint",
            "time": f"{joint_prefix}knob_time_joint",
            "rack": f"{joint_prefix}rack0_joint",
            "tray": f"{joint_prefix}tray0_joint",
        }

    def get_reset_region_names(self):
        return ("rack0", "rack1", "tray0", "tray1")

    def _get_joint_prefix(self):
        return f"{self.naming_prefix}"

    def set_doneness(self, env, doneness_val):
        """
        Sets the oven's doneness level

        Args:
            doneness_val (float): normalized value between 0 (off) and 1 (dark)
        """
        self._doneness = np.clip(doneness_val, 0.0, 1.0)
        joint_name = self._joint_names["doneness"]
        self.set_joint_state(
            env=env, min=self._doneness, max=self._doneness, joint_names=[joint_name]
        )

    def set_function(self, env, function_val):
        """
        Sets the oven's function

        Args:
            function_val (float): normalized value between 0 and 1
        """
        self._function = np.clip(function_val, 0.0, 1.0)
        joint_name = self._joint_names["function"]
        self.set_joint_state(
            env=env, min=self._function, max=self._function, joint_names=[joint_name]
        )

    def set_temperature(self, env, temp):
        """
        Sets the oven's temperature

        Args:
            temp (float): normalized value between 0 (min) and 1 (max)
        """
        self._temperature = np.clip(temp, 0.0, 1.0)
        joint_name = self._joint_names["temperature"]
        self.set_joint_state(
            env=env,
            min=self._temperature,
            max=self._temperature,
            joint_names=[joint_name],
        )

    def set_time(self, env, time):
        """
        Sets the oven's time

        Args:
            time (float): Normalized time value between 0 (min) and 1 (max)
        """
        self._time = np.clip(time, 0.0, 1.0)
        joint_name = self._joint_names["time"]
        self.set_joint_state(
            env=env, min=self._time, max=self._time, joint_names=[joint_name]
        )

    def slide_rack(self, env, value=1.0):
        """
        Slides the oven's rack or tray

        Args:
            value (float): normalized value between 0 (closed) and 1 (open)
        """
        door_pos = self.get_joint_state(env, [self._joint_names["door"]])[
            self._joint_names["door"]
        ]

        if door_pos <= 0.99:
            self.open_door(env)

        # Use rack if available, otherwise use tray
        if self._joint_names["rack"] in env.sim.model.joint_names:
            joint_name = self._joint_names["rack"]
            self._rack = value
        else:
            joint_name = self._joint_names["tray"]
            self._tray = value

        self.set_joint_state(env=env, min=value, max=value, joint_names=[joint_name])

    def update_state(self, env):
        """
        Update the state of the toaster oven
        """
        for name, jn in self._joint_names.items():
            if jn in env.sim.model.joint_names:
                state = self.get_joint_state(env, [jn])[jn]
                if name == "time" and state > 0:
                    if self._last_time_update is None:
                        self._last_time_update = env.sim.data.time
                    else:
                        time_elapsed = env.sim.data.time - self._last_time_update
                        state = max(0, state - time_elapsed / 3000)
                        self.set_joint_state(
                            env=env,
                            min=state,
                            max=state,
                            joint_names=[jn],
                        )
                else:
                    self._last_time_update = None
                setattr(self, f"_{name}", state)

    def check_rack_contact(self, env, obj_name):
        """
        Checks whether the specified object is in contact with the rack or tray of the toaster oven.
        """
        # Use rack if available, otherwise use tray
        if self._joint_names["rack"] in env.sim.model.joint_names:
            contact_name = self._joint_names["rack"].removesuffix("_joint")
        else:
            contact_name = self._joint_names["tray"].removesuffix("_joint")

        body_id = env.sim.model.body_name2id(contact_name)
        shelf_geoms = [
            env.sim.model.geom_id2name(i)
            for i in range(env.sim.model.ngeom)
            if env.sim.model.geom_bodyid[i] == body_id
        ]

        body_id = env.obj_body_id[obj_name]
        item_geoms = [
            env.sim.model.geom_id2name(gid)
            for gid in range(env.sim.model.ngeom)
            if env.sim.model.geom_bodyid[gid] == body_id
        ]

        return env.check_contact(shelf_geoms, item_geoms)

    def get_state(self, env):
        """
        Returns the current state of the toaster oven as a dictionary.
        """
        st = {}
        for name, jn in self._joint_names.items():
            if jn in env.sim.model.joint_names:
                st[name] = getattr(self, f"_{name}", None)
        return st

    @property
    def nat_lang(self):
        return "toaster oven"
