"""
    ========== Abstract Class: Object With Subject ===========
    This represents the base class for objects that ties itself
    with a particular agent or called subject. Basically,
    State, Action and Effect.
    ==========================================================
"""

from simulator_base.object_base.simulation_object import SimulationObject
from simulator_base.orchestrator.orchestrator import get_orchestrator
from typing import final


class ObjectWithSubject(SimulationObject):
    def __init__(
        self,
        object_type: str,
        object_subtype: str,
    ):
        super().__init__(object_type, object_subtype)
        self._subject: SimulationObject = None

    # ============== User Accessible Public Properties ===============

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, subject):
        """
        Set the subject of this object.
        """
        self._subject = subject

    # ============= System Accessible Public Methods =============

    @final
    def validate_object(self):
        if self._subject is None:
            raise Exception(
                f"Object {self.object_subtype} has no subject"
            )

    @final
    def before_destroy(self):
        """
            Remove action from the agent
        """
        self.subject.remove_object(self)

    def rehydrate(self):
        """
            Once reloaded, add itself back to orchestrator
            given its saves where handled by its subject
        """
        orchestrator = get_orchestrator()
        orchestrator.add_object(self)

    # ================= System Function Overrides ==================

    def __getstate__(self):
        """
            turn subject into id
        """
        state = self.__dict__.copy()
        state["_subject"] = None
        return state

    def __setstate__(self, state):
        """
            set subject from id
        """
        self.__dict__.update(state)
