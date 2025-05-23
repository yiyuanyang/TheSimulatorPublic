"""
    ========= Abstract Object : Event ==========
    An event is like a single use action. It
    can apply a single time state change to some
    objects or leave a particular effect on
    objects. It will trigger upon its target
    time, and then it will be removed from the
    simulation.
    ============================================
"""

from ..object_base.simulation_object import SimulationObject
from ..orchestrator.orchestrator import Orchestrator
from datetime import datetime
from abc import abstractmethod
from typing import final


class Event(SimulationObject):
    def __init__(
        self,
        event_type: str,
        start_time: datetime
    ):
        super().__init__('Event', event_type)
        self._start_time = start_time

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @final
    def can_start(self) -> bool:
        """
            This is performed
            when we tick on the agent
            to evaluate if the action
            would later be performed
        """
        current_time = Orchestrator.get_current_time(self)
        if self._start_time > current_time:
            return False
        return self.should_start()

    def should_start(self) -> bool:
        """
            ========== May Override =================
            Custom logic to determine if event should
            start.
        """
        return True

    @abstractmethod
    def apply(self):
        """
            Perform the action
        """
        pass

    def __str__(self):
        return f"{self.object_subtype}_{super().__str__()}"

    # =================== System Accessible Public Methods ==================

    def rehydrate(self):
        """
            events generally do not need rehydration
        """
        pass

    @final
    def simulate(self):
        """
            Perform the simulation once it can
            start, and then destroy itself.
        """
        super().simulate()
        if self.can_start():
            self.apply()
            self.destroy()
