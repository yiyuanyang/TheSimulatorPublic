"""
    =========== Abstract Class : Simulation Object ===========
    A wrapper class on top of object class. It has access to
    orchestrator (as opposed to being only referenced by the
    orchestrator).
    All subsequent classes would reference simulation object
    instead of object base class.
    ===========================================================
"""

from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.object_base.object_base import ObjectBase


class SimulationObject(ObjectBase):
    def __init__(
        self,
        object_type: str,
        object_subtype: str,
    ):
        orchestrator = get_orchestrator()
        self._id = orchestrator.next_id(object_type)
        super().__init__(object_type, object_subtype)
        orchestrator.add_object(self)

    def destroy(self):
        """
        """
        super().destroy()
        get_orchestrator().remove_object(self)
