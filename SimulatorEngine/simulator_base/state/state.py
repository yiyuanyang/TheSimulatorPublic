"""
    ======= Abstract Class : State =========
    A state describe certain features of an
    object / agent in the simulation. They
    are evaluated last in every tick of the
    simulation. They are mostly modified by
    actions and effects, and in rare occasions
    trigger side effect themselves.
    ========================================
"""

from simulator_base.object_base.object_with_subject import ObjectWithSubject
from abc import abstractmethod


class State(ObjectWithSubject):
    def __init__(self, state_type: str):
        super().__init__("State", state_type)

    @abstractmethod
    def simulate(self):
        pass

    def __str__(self):
        return f"{self.object_subtype}_{super().__str__()}"
