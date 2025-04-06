"""
    ========== Abstract Class: Object With Subject ===========
    This represents the base class for objects that ties itself
    with a particular agent or called subject. Basically,
    State, Action and Effect.
    ==========================================================
"""

from simulator_base.object_base.object_base import ObjectBase
from typing import final


class ObjectWithSubject(ObjectBase):
    def __init__(
        self,
        object_type: str,
        object_subtype: str,
    ):
        super().__init__(object_type, object_subtype)
        self._subject = None

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

    def to_dict(self) -> dict:
        """
            Convert the object to a dictionary
        """
        dict_base = super().to_dict()
        obj_data = {
            'subject_id': self.subject.id,
        }
        dict_base.update(obj_data)
        return dict_base

    def from_dict(self, object_data: dict):
        """
            Convert the object from a dictionary
        """
        super().from_dict(object_data)
