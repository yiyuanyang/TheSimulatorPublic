"""
    ============= Abstract Class: Independent Object ============
    This is the base class for both Agent and Environment. Both
    can own states, action and effects. This abstract class mostly
    handles the logic related to the access, removal and maintenance
    of those three fields.
    =============================================================
"""

from simulator_base.object_base.object_base import ObjectBase
from simulator_base.state.state import State
from simulator_base.action.action import Action
from simulator_base.effect.effect_base import EffectBase
from simulator_base.orchestrator.orchestrator import get_orchestrator
from abc import abstractmethod
from typing import List, final


class IndependentObject(ObjectBase):
    def __init__(self, object_type: str, object_subtype: str):
        super().__init__(object_type, object_subtype)
        self._objects: dict[str, list[ObjectBase]] = {
            'State': [],
            'Action': [],
            'Effect': []
        }

    @abstractmethod
    def required_objects(self) -> List[str]:
        """
            ========= Must Implement ============
            Specify the required states, actions
            and effects for the agent with object
            subtype.
            =====================================
        """
        return []

    @final
    def add_object(self, object: ObjectBase, start: bool = True):
        """
            Add the field to the list if it is not
            already in the list.
        """
        if object not in self._objects[object.object_type]:
            self._objects[object.object_type].append(object)
            object.subject = self
            if start:
                object.start()

    @final
    def remove_object(self, object: ObjectBase):
        """
            Remove the object from the list
        """
        if object in self._objects[object.object_type]:
            self._objects[object.object_type].remove(object)
            object.subject = None

    # ============= User Accessible Public Methods ==============

    @final
    def get_state(self, state_type: str) -> State:
        return self._get_object('State', state_type)

    @final
    def get_action(self, action_type: str) -> Action:
        return self._get_object('Action', action_type)

    @final
    def get_effect(self, effect_type: str) -> EffectBase:
        return self._get_object('Effect', effect_type)

    # ============= System Accessible Public Methods ==============

    @final
    def before_destroy(self):
        for _, items in self._objects.items():
            for item in items:
                item.destroy()

    @final
    def before_pause(self):
        for _, items in self._objects.items():
            for item in items:
                item.pause()

    @final
    def before_unpause(self):
        for _, items in self._objects.items():
            for item in items:
                item.unpause()

    @final
    def validate_object(self):
        """
            This is to ensure the object is instantiated
            with all of the required fields.
        """
        all_objects = []
        for _, items in self._objects.items():
            for item in items:
                all_objects.append(item.object_subtype)
        required_objects = self.required_objects()
        for object_subtype in required_objects:
            if object_subtype not in all_objects:
                raise Exception(
                    (
                        f"Object {object_subtype} is required for agent "
                        f"{self.object_subtype}"
                    )
                )

    @final
    def simulate(self):
        super().simulate()
        self._evaluate()

    def __str__(self):
        return f"{self.object_type} {self._id} of type {self.object_subtype}"

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        all_objects = self._objects['State'] + \
            self._objects['Action'] + \
            self._objects['Effect']
        all_objects_dict_pairs = [
            (obj.object_subtype, obj.to_dict()) for obj in all_objects
        ]
        base_dict['objects'] = all_objects_dict_pairs
        return base_dict

    def from_dict(self, object_data: dict):
        super().from_dict()
        object_dict_pairs = object_data['objects']
        for object_dict_pair in object_dict_pairs:
            init_class = get_orchestrator().map_object(
                object_dict_pair[0]
            )
            state = init_class.deserialize(object_dict_pair[1])
            self.add_object(state)

    # ============= Private Helper Methods =============

    @final
    def _evaluate(self):
        """
            Evaluate all possible actions
            and decide if they would be
            acted upon.

            In the separate action evaluation
            cycle, actions that are marked as
            true would be acted upon.
        """
        for action in self._objects['Action']:
            action._evaluate()

    @final
    def _get_object(self, object_type: str, object_subtype: str) -> ObjectBase:
        """
            Get the object from the list
        """
        for obj in self._objects[object_type]:
            if obj.object_subtype == object_subtype:
                return obj
        return None
