"""
    ============= Abstract Class: Independent Object ============
    This is the base class for both Agent and Environment. Both
    can own states, action and effects. This abstract class mostly
    handles the logic related to the access, removal and maintenance
    of those three fields.
    =============================================================
"""

from simulator_base.object_base.simulation_object import SimulationObject
from simulator_base.object_base.object_with_subject import ObjectWithSubject
from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.state.state import State
from simulator_base.action.action import Action
from simulator_base.effect.effect_base import EffectBase
from abc import abstractmethod
from typing import List, final, Optional


class IndependentObject(SimulationObject):
    def __init__(self, object_type: str, object_subtype: str):
        super().__init__(object_type, object_subtype)
        self._objects: dict[str, dict[str, ObjectWithSubject]] = {
            'State': {},
            'Action': {},
            'Effect': {}
        }
        # this is used to keep track of the related objects
        self._associated_objects: dict[str, list[IndependentObject]] = {}
        # for rehydration purposes only
        self._associated_object_ids: dict[str, list[tuple[str, str]]] = {}

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
    def add_object(self, object: SimulationObject, start: bool = True):
        """
            Add the field to the list if it is not
            already in the list.
        """
        if object.object_subtype not in self._objects[object.object_type]:
            self._objects[object.object_type][object.object_subtype] = object
            object.subject = self
            if start:
                object.start()

    @final
    def remove_object(self, object: SimulationObject):
        """
            Remove the object from the list
        """
        if object.object_subtype in self._objects[object.object_type]:
            self._objects[object.object_type].pop(object.object_subtype)

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

    @final
    def associate(
        self,
        relation: str,
        associated_object: SimulationObject
    ):
        """
            Associate the object with the relation
            and the associated object.
        """
        if relation not in self._associated_objects:
            self._associated_objects[relation] = []
        self._associated_objects[relation].append(associated_object)

    @final
    def get_associated_object(
        self,
        relation: str
    ) -> SimulationObject:
        """
            Get the associated object
        """
        return self.get_associated_objects(relation)[0]

    @final
    def get_associated_objects(
        self,
        relation: str
    ) -> List[SimulationObject]:
        """
            Get the associated objects
        """
        if relation not in self._associated_objects:
            self._associated_objects[relation] = []
        return self._associated_objects[relation]

    # ============= System Accessible Public Methods ==============

    @final
    def before_destroy(self):
        for _, items in self._objects.items():
            for _, item in items.items():
                item.destroy()

    @final
    def before_pause(self):
        for _, items in self._objects.items():
            for _, item in items.items():
                item.pause()

    @final
    def before_unpause(self):
        for _, items in self._objects.items():
            for _, item in items.items():
                item.unpause()

    @final
    def validate_object(self):
        """
            This is to ensure the object is instantiated
            with all of the required fields.
        """
        all_objects = []
        for _, items in self._objects.items():
            for _, item in items.items():
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
        self._evaluate()

    def __str__(self):
        return f"{self.object_type} {self._id} of type {self.object_subtype}"

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
        for _, action in self._objects['Action'].items():
            action._evaluate()

    @final
    def _get_object(
        self,
        object_type: str,
        object_subtype: str
    ) -> Optional[SimulationObject]:
        """
            Get the object from the list
        """
        # if key exist is not checked to save simulation
        # speed / time
        return self._objects[object_type].get(
            object_subtype,
            None
        )

    def rehydrate(self):
        """
            Independent object are saved as part of the orchestrator
            and the dependent object are saved alongside with them.
            After loading up the simulation from saves
            need to re-establish object connections and relations,
            especially the dependent objects.
        """
        # we need to add the state, action and event,
        # objects back to the orchestrator
        for _, items in self._objects.items():
            for key, item in items.items():
                item.subject = self
                item.rehydrate()
        for key, items in self._associated_object_ids.items():
            for item in items:
                # we need to get the object from the orchestrator
                # and set it as the associated object
                obj = get_orchestrator().get_object(item[1], item[0])
                if obj is not None:
                    self.associate(key, obj)

    # =============== Serialization Methods ================
    def __getstate__(self):
        default_state = self.__dict__.copy()
        # turning all associated objects into ids
        default_state["_associated_object_ids"] = {
            key: [(obj.id, obj.object_type) for obj in value]
            for key, value in default_state["_associated_objects"].items()
        }
        default_state["_associated_objects"] = {}
        return default_state

    def __setstate__(self, state):
        # we will try to re-establish the object associations
        # in the rehydration process
        self.__dict__.update(state)
