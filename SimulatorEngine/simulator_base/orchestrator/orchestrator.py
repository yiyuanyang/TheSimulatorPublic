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
from simulator_base.config.global_config import get_config
from ..object_base.object_base import ObjectBase
from ..context.context import Context
from ..util.signal import subscribe
from market_simulation.objects.types.types import ObjectSubType
from datetime import datetime, timedelta
import math


class Orchestrator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Orchestrator, cls).__new__(cls)
            cls._instance.context = Context()
            cls._instance._current_time = None
            cls._instance._tick_interval = None
            cls._instance._start_date = None
            cls._instance.total_ticks = 0
            cls._instance._is_ticking = False
            cls._instance._object_mapping_fn = None
            subscribe('object_creation', cls._instance.add_object)
            subscribe('object_destruction', cls._instance.remove_object)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Orchestrator()
        return cls._instance

    def setup_object_mapping(self, object_mapping_fn: callable):
        self._object_mapping_fn = object_mapping_fn

    def map_object(self, obj_subtype: ObjectSubType):
        return self._object_mapping_fn(None, obj_subtype)

    def get_subject(self, subject_id: str) -> ObjectBase:
        """
            Both environment and agent can be
            subject of action, state and effect
            so search through both list to find it
        """
        environment = self.context.get_environment_with_id(subject_id)
        if environment is not None:
            return environment
        agent = self.context.get_agent_with_id(subject_id)
        if agent is not None:
            return agent
        raise RuntimeError(
            f"Subject with id {subject_id} not found"
        )

    def get_all_objects(self) -> list[ObjectBase]:
        """
            Get all objects in the simulation
        """
        return self.context.get_all_objects()

    def add_object(self, obj: ObjectBase):
        if obj not in self.context.get_all_objects():
            self.context.add_object(obj)

    def remove_object(self, obj: ObjectBase):
        self.context.remove_object(obj)

    def start_simulation(self):
        pass

    def stop_simulation(self):
        for obj in self.context.get_all_objects():
            obj.destroy()
        self.context = Context()

    def pause_simulation(self):
        for obj in self.context.get_all_objects():
            obj.pause()

    def unpause_simulation(self):
        for obj in self.context.get_all_objects():
            obj.unpause()

    def setup_time(
        self,
        start_date: datetime,
        tick_interval: timedelta,
    ):
        if start_date.tzinfo is not None:
            self._tzinfo = start_date.tzinfo
        self._start_date = start_date
        self._current_time = start_date
        self._tick_interval = tick_interval

    def get_agent(self, agent_id: str):
        return self.context.get_agent(agent_id)

    def get_all_agents(self, update_index: bool = False):
        return self.context.get_agent_objects(update_index)

    def get_environment(self, environment_type: str):
        return self.context.get_environment(environment_type)

    def get_environment_with_filter(
        self,
        filter_fn: callable,
    ) -> ObjectBase:
        """
            Get all environments that match the filter
            function
        """
        all_environments = self.context.get_environment_objects()
        for environment in all_environments:
            if filter_fn(environment):
                return environment

    def progress_until_time(self, end_time: datetime):
        """
            Progress time until a given end time.
        """
        if self._is_ticking:
            raise RuntimeError("Orchestrator is already ticking")
        if self._current_time is None:
            raise RuntimeError("Orchestrator is not initialized")
        if end_time < self._current_time:
            raise RuntimeError("End time is before current time")
        time_delta = end_time - self._current_time
        total_ticks = time_delta / self._tick_interval
        for i in range(int(total_ticks)):
            self.tick()

    def progress_time(self, time_delta: timedelta):
        """
            Progress time by a given delta.
        """
        if self._is_ticking:
            raise RuntimeError("Orchestrator is already ticking")
        if self._current_time is None:
            raise RuntimeError("Orchestrator is not initialized")
        if time_delta < timedelta(0):
            raise RuntimeError("Time delta is negative for progression")
        total_ticks = time_delta / self._tick_interval
        if total_ticks >= 1:
            for i in range(int(total_ticks)):
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
        if self.total_ticks % ticks_per_print == 0:
            printer(
                "==================== "
                + self.get_global_time().isoformat()
                + "====================",
                "LOG"
            )
        environments = self.context.get_environment_objects(True)
        for environment in environments:
            environment.tick()

        events = self.context.get_event_objects(True)
        for event in events:
            event.tick()

        effects = self.context.get_effect_objects(True)
        for effect in effects:
            effect.tick()

        agents = self.context.get_agent_objects(True)
        for agent in agents:
            agent.tick()

        actions = self.context.get_action_objects(True)
        for action in actions:
            action.tick()

        states = self.context.get_state_objects(True)
        for state in states:
            state.tick()

        metrics = self.context.get_metric_objects(True)
        for metric in metrics:
            metric.tick()

        self._current_time += self._tick_interval
        self.total_ticks += 1
        self._is_ticking = False

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

    @classmethod
    def get_global_time(cls):
        """
            Get time of the orchestrator / global clock
        """
        return cls._instance._current_time

    def destroy(self):
        self.stop_simulation()


def get_orchestrator():
    return Orchestrator.get_instance()
