"""
    ======== Abstract Class : Agent =================
    The agent class inherits most of its logic from
    the IndependentObject class and mostly uses its
    object type "Agent" to distinguish its simulation
    order from "Environment" which is simulated first.
    ================================================
"""

from ..object_base.independent_object import IndependentObject


class Agent(IndependentObject):
    def __init__(self, agent_type: str):
        super().__init__('Agent', agent_type)
