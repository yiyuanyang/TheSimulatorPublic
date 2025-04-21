"""
    ================= Orchestrator ====================
    The Orchestrator is a singleton class responsible
    for keeping track of all objects in the simulation,
    moving them through time, and performing lifecycle
    managements.

    All objects that are derived classes of ObjectBase
    are automatically registered with the Orchestrator
    upon instantiation.

    It reconciles the internal concept of a single
    simulation 'tick' with the simulated time, which
    is based on seconds, minutes and etc.
    ===================================================
"""

from simulator_base.util.printer import printer
from simulator_base.config.global_config import (
    get_config,
    GlobalConfig
)
from simulator_base.object_base.id_generator import IDGenerator
from simulator_base.orchestrator.objects_manager import ObjectsManager
from ..object_base.object_base import ObjectBase
from datetime import datetime, timedelta
import math
import time
import pickle
import os


class Orchestrator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            if getattr(cls, "_is_unpickling", False):
                cls._instance = super().__new__(cls)
                return cls._instance

            global_config = get_config()
            if global_config.simulation_config['load_from_snapshot']:
                Orchestrator.load_simulation(
                    global_config.simulation_config['snapshot_directory']
                )
            else:
                cls._instance = super(Orchestrator, cls).__new__(cls)
                cls._instance._objects_manager = ObjectsManager()
                cls._instance._id_generator = IDGenerator()
                cls._instance._current_time = None
                cls._instance._total_ticks = 0
                cls._instance._is_ticking = False
                cls._instance._last_save_time = None
                cls._instance._end_time = None
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Orchestrator()
        return cls._instance

    def setup_time(self):
        # skip if time all exists
        if self._current_time is not None \
           or self._end_time is not None:
            return
        global_config = get_config()
        self._end_time = global_config.end_time
        sim_config = global_config.simulation_config
        automatic_start = sim_config.get('automatic_start', True)
        if automatic_start:
            self._is_simulation_paused = False
        else:
            self._is_simulation_paused = True
        self._automatic_tick = sim_config.get(
            'automatic_tick',
            True
        )
        start_date = global_config.get_start_date()
        tick_interval = global_config.get_tick_interval_seconds()
        self._start_date = start_date
        self._current_time = start_date
        self._tick_interval = tick_interval
        if start_date.tzinfo is not None:
            self._tzinfo = start_date.tzinfo

    def add_object(self, obj: ObjectBase):
        self._objects_manager.add_object(obj)

    def next_id(self, prefix: str = "") -> str:
        """
            Get the next id for the object
        """
        return self._id_generator.next_id(prefix)

    def get_object(self, object_type: str, object_id: str):
        """
            Get the object by its type and id
        """
        return self._objects_manager.get_object(object_type, object_id)

    def add_scheduled_command(self, command: tuple[datetime, callable]):
        self._objects_manager.add_scheduled_command(command)

    def remove_object(self, obj: ObjectBase):
        self._objects_manager.remove_object(obj)

    def simulation_loaded(self):
        """
            If object manager is not empty
            it means simulation is already loaded
            and ready for use
        """
        return not self._objects_manager.is_empty

    def start_simulation(self):
        pass

    def stop_simulation(self):
        for obj in self._objects_manager.get_all_objects():
            obj.destroy()
        self._objects_manager = ObjectsManager()

    def pause_simulation(self):
        for obj in self._objects_manager.get_all_objects():
            obj.pause()
        printer("Simulation paused", "LOG")
        self._is_simulation_paused = True

    def unpause_simulation(self):
        for obj in self._objects_manager.get_all_objects():
            obj.unpause()
        printer("Simulation resumed", "LOG")
        self._is_simulation_paused = False

    def get_all_agents(self, update_index: bool = False):
        return self._objects_manager.get_agent_objects(update_index)

    def get_environment(self, environment_type: str):
        return self._objects_manager.get_environment(environment_type)

    def get_environment_with_filter(
        self,
        filter_fn: callable,
    ) -> ObjectBase:
        """
            Get all environments that match the filter
            function
        """
        all_environments = self._objects_manager.get_environment_objects()
        for environment in all_environments:
            if filter_fn(environment):
                return environment

    def run_simulation(self):
        while (
            self._end_time is None
            or self._current_time < self._end_time
        ):
            self.tick()

    def tick(self):
        """
            The objects are returned in the order
            of Environment, Event, Effect, Agent, Action,
            and lastly State. This is used to
            represent a hierarchy of changes, of agent
            observing the environment and context
            and decide upon actions that eventually
            changes the state of the agent itself
            and other things.
        """
        # ================ Command Reader ===============
        # Reading the external command would happen even
        # if simulation itself is paused (or you won't be able to
        # unpause it)
        scheduled_commands = self._objects_manager.get_scheduled_commands(
            self.get_global_time()
        )
        for command in scheduled_commands:
            command[1]()
        command_reader = self._objects_manager.get_command_reader()
        if command_reader is not None:
            if self._is_simulation_paused:
                # if simulation is paused, we don't want to
                # read the command too frequently
                time.sleep(1)
            command_reader.tick()

        # ================ Actual Simulation ===============

        if self._is_simulation_paused:
            return
        if self._is_ticking:
            raise RuntimeError("Orchestrator is already ticking")
        self._is_ticking = True
        global_config = get_config()
        debug_config = global_config.debug_config
        time_indicator_print_interval_raw_hr = debug_config.get(
            'time_indicator_print_interval', 1
        )
        print_interval = timedelta(
            hours=time_indicator_print_interval_raw_hr
        )
        ticks_per_print = math.ceil(print_interval / self._tick_interval)
        if self._total_ticks % ticks_per_print == 0:
            printer(
                "==================== "
                + self.get_global_time().isoformat()
                + "====================",
                "LOG"
            )
        environments = self._objects_manager.get_environment_objects(True)
        for environment in environments:
            environment.tick()
        events = self._objects_manager.get_event_objects(True)
        for event in events:
            event.tick()
        effects = self._objects_manager.get_effect_objects(True)
        for effect in effects:
            effect.tick()
        agents = self._objects_manager.get_agent_objects(True)
        for agent in agents:
            agent.tick()
        actions = self._objects_manager.get_action_objects(True)
        for action in actions:
            action.tick()
        states = self._objects_manager.get_state_objects(True)
        for state in states:
            state.tick()
        metrics = self._objects_manager.get_metric_objects(True)
        for metric in metrics:
            metric.tick()
        self._current_time += self._tick_interval
        self._total_ticks += 1
        self._is_ticking = False
        self.save_simulation()

    @classmethod
    def get_current_time(cls, object: ObjectBase):
        """
            Get the current time for object based on
            object's own timezone
        """
        if object is None:
            raise RuntimeError("Cannot get relative time without object")
        if object is not None and object.object_timezone is not None:
            return cls._instance._current_time.astimezone(
                object.object_timezone
            )
        return cls._instance._current_time

    def save_simulation(self):
        """
            Save the simulation state to a file
        """
        # periodically pickle up the entire simulation and save locally
        global_config = get_config()
        snapshot_config = global_config.snapshot_config
        should_save = snapshot_config.get('should_save', False)
        if not should_save:
            return
        should_save_at_start = snapshot_config.get(
            'should_save_at_start',
            False
        )
        snapshot_save_interval = snapshot_config.get(
            'snapshot_save_interval',
            None
        )
        snapshot_save_interval_secs = timedelta(
            seconds=snapshot_save_interval
        )
        if snapshot_save_interval is None:
            return
        if self._last_save_time is None and not should_save_at_start:
            return
        if self._last_save_time is not None and \
                self._current_time - self._last_save_time < \
                snapshot_save_interval_secs:
            return
        self._last_save_time = self._current_time
        global_config.save_global_config_snapshot(self._total_ticks)
        snapshot_dir = global_config.get_snapshot_path(
            self._total_ticks
        )
        orchestrator_snapshot_dir = os.path.join(
            snapshot_dir,
            'orchestrator_snapshot.pkl'
        )
        with open(orchestrator_snapshot_dir, 'wb') as file:
            pickle.dump(self, file)
        printer(
            f"Saved simulation state at {self._current_time.isoformat()}",
            "LOG"
        )

    @classmethod
    def load_simulation(cls, load_dir: str):
        """
            Load the simulation state from a file
            delete everything that already exists
        """
        cls._is_unpickling = True
        if cls._instance is not None:
            cls._instance._objects_manager.clear()
        GlobalConfig.load_global_config_snapshot(load_dir)
        orchestrator_snapshot_dir = os.path.join(
            load_dir,
            'orchestrator_snapshot.pkl'
        )
        with open(orchestrator_snapshot_dir, 'rb') as file:
            cls._instance = pickle.load(file)
        cls._is_unpickling = False
        printer(
            f"Loaded simulation state at "
            f"{cls._instance._current_time.isoformat()}",
            "LOG"
        )
        cls._instance._objects_manager.rehydrate()
        printer(
            "Rehydrated simulation state",
            "LOG"
        )

    @classmethod
    def get_global_time(cls):
        """
            Get time of the orchestrator / global clock
        """
        return cls._instance._current_time

    def destroy(self):
        self._objects_manager.clear()
        self.stop_simulation()


def get_orchestrator():
    return Orchestrator.get_instance()
