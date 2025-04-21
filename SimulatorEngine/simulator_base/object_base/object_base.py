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

from ..config.global_config import GlobalConfig
from abc import abstractmethod, ABC
from typing import final
from datetime import timedelta, timezone
import math


class ObjectBase(ABC):

    def __init__(
        self,
        object_type: str,
        object_subtype: str,
    ):
        self._object_type = object_type
        self._object_subtype = object_subtype
        self._setup_fields(
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

    def rehydrate(self):
        """
            ======== May Implement ============
            After loading this object from save, actions
            such as relinking and etc it
            needs to perform to be ready for simulation.

            The returning value indicates whether rehydration
            was successful and can also indicate if additional
            round of rehydration is needed.
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

    def destroy(self):
        """
            Removes the object from the simulation
            and destroys it.
        """
        self.before_destroy()

    def __str__(self) -> str:
        return f"{self._object_type}_{self.id}"

    # ============= System Accessible Public Functions ============

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
        paused: bool = True,
        tick_count: int = 0,
        simulation_count: int = 0,
        tick_since_last_simulation: int = None,
        simulation_interval_ticks: int = 1,
        object_timezone: timezone = None,
        simulate_on_first_tick: bool = False,
    ):
        self._paused = paused
        self._tick_count = tick_count
        self._simulation_count = simulation_count
        self._tick_since_last_simulation = tick_since_last_simulation
        self._simulation_interval_ticks = simulation_interval_ticks
        self._timezone = object_timezone
        self._simulate_on_first_tick = simulate_on_first_tick
