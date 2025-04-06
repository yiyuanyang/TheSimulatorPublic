"""
    ======== Abstract Class: ObjectBase =========
    ObjectBase is the base class for all objects
    that are simulated in this simulation engine.

    It allows for user defined logic for what
    each object would do upon its own simulation
    cycle, as well as what it does at the start
    of the simulation and before the object
    gets discarded.

    Do not directly inherit this class. Utilize
    child classes such as Environment, Event,
    Effect, Agent, State and Actions.
    ==============================================
"""

from simulator_base.object_base.id_generator import IDGenerator
from ..config.global_config import GlobalConfig
from ..util.signal import emit
from abc import abstractmethod, ABC
from typing import final
from datetime import timedelta, timezone
import math
import json


class ObjectBase(ABC):

    def __init__(
        self,
        object_type: str,
        object_subtype: str,
        alternative_constructor: bool = False
    ):
        self._object_type = object_type
        self._object_subtype = object_subtype
        self._cleanup_fn_list: list[callable] = []
        if not alternative_constructor:
            self._setup_fields(
                id=IDGenerator.get_instance().next_id(object_type),
                paused=True,
                tick_count=0,
                simulation_count=0,
                tick_since_last_simulation=None,
                simulation_interval_ticks=1,
                object_timezone=None,
                simulate_on_first_tick=False,
            )

    # ============= Abstract Methods ===============

    @abstractmethod
    def simulate(self):
        """
            ======== Must Implement ===========
            Perform object specific logic
            once it starts its simulation cycle
            ===================================
        """
        pass

    @abstractmethod
    def validate_object(self):
        """
            ========= Must Implement ===========
            A validation function to check if
            the created object is correctly
            configured and ready to participate.
            ====================================
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
            ======== Must Implement ===========
            Convert the object into dictionary
            representation to ready for
            serialization, only need to handle
            data specific to the child class.
            ===================================
        """
        return {}

    @abstractmethod
    def from_dict(self, object_values: dict):
        """
            ======== Must Implement ============
            Assign field values and setup object
            based on a dictionary, only need to
            handle data specific to the child
            class.
            ====================================
        """
        pass

    def before_start(self):
        """
            ======== May Implement ============
            Perform object specific logic
            before it starts its simulation cycle
            ====================================
        """
        pass

    def before_destroy(self):
        """
            ======== May Implement =============
            Unlink the object from the simulation
            before formally remove it.
            =====================================
        """
        pass

    def before_pause(self):
        """
            ======== May Implement ============
        """
        pass

    def before_unpause(self):
        """
            ======== May Implement ============
        """
        pass

    # ========== User Accessible Public Properties ==========

    @property
    def id(self) -> str:
        return self._id

    @property
    def object_type(self) -> str:
        return self._object_type

    @property
    def object_subtype(self) -> str:
        return self._object_subtype

    @property
    def paused(self) -> bool:
        """
            Whether the object is paused or not.
        """
        return self._paused

    @property
    def simulation_interval(self) -> timedelta:
        """
            Time interval between every simulation
            cycle for current object, can be different
            than global default.
        """
        global_config = GlobalConfig.get_instance()
        tick_interval = global_config.get_tick_interval_seconds()
        return tick_interval * self._simulation_interval_ticks

    @simulation_interval.setter
    def simulation_interval(self, time_interval: timedelta):
        """
            Sets a time interval that is longer than the global
            simulation frequency. Since most objects do not
            make decision on the smallest time interval.
        """
        global_config = GlobalConfig.get_instance()
        tick_interval = global_config.get_tick_interval_seconds()
        self._simulation_interval_ticks = math.ceil(
            time_interval.total_seconds() / tick_interval.total_seconds()
        )

    @property
    def object_lifetime(self) -> timedelta:
        """
            How long this object has been active in
            the simulation, paused time is not counted.
        """
        global_config = GlobalConfig.get_instance()
        tick_interval = global_config.get_tick_interval_seconds()
        return tick_interval * self._tick_count

    @property
    def object_timezone(self) -> timezone:
        return self._timezone

    @object_timezone.setter
    def object_timezone(self, tz: timezone):
        self._timezone = tz

    @property
    def simulation_count(self) -> int:
        """
            How many times this object has been
            simulated.
        """
        return self._simulation_count

    # =============== User Accessible Public Methods ================

    @final
    def start(self):
        """
            Must Be Called!
            Start has to be called on an object for it to be able to
            participate in the simulation.
        """
        self.validate_object()
        self.before_start()
        self.unpause()

    @final
    def pause(self):
        """
            This stops the object from getting ticked via the simulation
            but does not prevent it from being accessible to other objects.
        """
        self.before_pause()
        self._paused = True

    @final
    def unpause(self):
        """
            Called upon simulation unpause
        """
        self.before_unpause()
        self._paused = False

    @final
    def destroy(self):
        """
            Removes the object from the simulation
            and destroys it.
        """
        for fn in self._cleanup_fn_list:
            try:
                fn()
            except Exception as e:
                print(f"Error in cleanup function: {e}")
        self.before_destroy()
        emit('object_destruction', self)

    @final
    def serialize(self) -> str:
        return json.dumps(self._to_dict())

    @classmethod
    @final
    def deserialize(cls, json_str: str):
        """
            Deserialize the object from
            a json string
        """
        object_values = json.loads(json_str)
        return cls._from_dict(object_values)

    def __str__(self) -> str:
        return f"{self._object_type}_{self.id}"

    # ============= System Accessible Public Functions ============

    @final
    def add_cleanup_fn(self, fn: callable):
        """
            Add a cleanup function to the object
            that will be called when the object
            is destroyed.
        """
        self._cleanup_fn_list.append(fn)

    @final
    def tick(self):
        """
            This function is called by the orchestrator
            to tick on the object.
        """
        if not self._paused:
            if (
                self._tick_since_last_simulation is None
                and self._simulate_on_first_tick
            ) or (
                self._tick_since_last_simulation is not None
                and self._tick_since_last_simulation >=
                    self._simulation_interval_ticks
            ):
                self.simulate()
                self._simulation_count += 1
                self._tick_since_last_simulation = 1
            else:
                if self._tick_since_last_simulation is None:
                    self._tick_since_last_simulation = 1
                else:
                    self._tick_since_last_simulation += 1
            self._tick_count += 1

    # ============= Private Helper Methods =================

    @final
    def _setup_fields(
        self,
        id: str,
        paused: bool = True,
        tick_count: int = 0,
        simulation_count: int = 0,
        tick_since_last_simulation: int = None,
        simulation_interval_ticks: int = 1,
        object_timezone: timezone = None,
        simulate_on_first_tick: bool = False,
    ):
        self._id = id
        self._paused = paused
        self._tick_count = tick_count
        self._simulation_count = simulation_count
        self._tick_since_last_simulation = tick_since_last_simulation
        self._simulation_interval_ticks = simulation_interval_ticks
        self._timezone = object_timezone
        self._simulate_on_first_tick = simulate_on_first_tick
        emit('object_creation', self)

    @final
    def _to_dict(self) -> dict:
        """
            Convert the object into dictionary
            representation for serialization,
            local saving, and client interactions
        """
        object_values = {
            'id': self.id,
            'object_type': self._object_type,
            'object_subtype': self._object_subtype,
            'paused': self._paused,
            'tick_count': self._tick_count,
            'simulation_count': self._simulation_count,
            'tick_since_last_simulation': self._tick_since_last_simulation,
            'simulation_interval_ticks': self._simulation_interval_ticks,
            'object_timezone':
                self._timezone.utcoffset(None).total_seconds() / 3600
            if self._timezone else None,
            'simulate_on_first_tick': self._simulate_on_first_tick
        }
        child_class_dict = self.to_dict()
        if child_class_dict:
            object_values.update(child_class_dict)
        return object_values

    @classmethod
    @final
    def _from_dict(cls, object_values: dict = None):
        """
            Convert the object from dictionary
            representation into the object itself
        """
        if object_values is None:
            raise ValueError(
                "Object values must be provided for deserialization."
            )
        obj = cls(
            object_type=object_values['object_type'],
            object_subtype=object_values['object_subtype'],
            alternative_constructor=True
        )
        obj._setup_fields(
            id=object_values['id'],
            paused=object_values['paused'],
            tick_count=object_values['tick_count'],
            simulation_count=object_values['simulation_count'],
            tick_since_last_simulation=object_values[
                'tick_since_last_simulation'
            ],
            simulation_interval_ticks=object_values[
                'simulation_interval_ticks'
            ],
            object_timezone=timezone(timedelta(
                hours=object_values['object_timezone']
            ))
            if object_values['object_timezone'] is not None else None,
            simulate_on_first_tick=object_values['simulate_on_first_tick']
        )
        obj.from_dict(object_values)
        return obj
