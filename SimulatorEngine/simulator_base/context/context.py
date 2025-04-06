"""
    ========= Global Context =========
    Global context is an object owned
    by the orchestrator to manage all
    objects that are present in the
    simulation.
    ==================================
"""

from ..object_base.object_base import ObjectBase
from typing import List
import heapq


class Context:
    def __init__(self):
        # this is an ordered list of objects
        # based on object type
        self._objects: dict[str, List[ObjectBase]] = {
            "Environment": [],
            "Event": [],
            "Effect": [],
            "Agent": [],
            "Action": [],
            "State": [],
            'Metric': []
        }
        self._round_robin_index = {
            "Environment": 0,
            "Event": 0,
            "Effect": 0,
            "Agent": 0,
            "Action": 0,
            "State": 0,
            "Metric": 0
        }
        self._scheduled_events: ObjectBase = []
        heapq.heapify(self._scheduled_events)
        self._internal_round_robin_index = 0

    def add_object(self, obj: ObjectBase):
        self._objects[obj.object_type].append(obj)

    def remove_object(self, obj: ObjectBase):
        self._objects[obj.object_type] = [
                o for o in self._objects[obj.object_type]
                if o.id != obj.id
            ]

    def get_round_robin_ordered_objects(
        self,
        object_type
    ) -> List[ObjectBase]:
        """
            This function returns the objects
            in a round robin fashion, ensuring
            no evaluation bias towards the
            earlier objects
        """
        objects = self._objects[object_type]
        if len(objects) == 0:
            return []
        index = self._internal_round_robin_index
        object_round_robin_index = index % len(objects)
        return objects[object_round_robin_index:] + \
            objects[:object_round_robin_index]

    def get_agent(self, agent_id: str) -> ObjectBase:
        for obj in self._objects["Agent"]:
            if obj.id == agent_id:
                return obj

    def get_environment(self, environment_type: str) -> ObjectBase:
        for obj in self._objects["Environment"]:
            if obj.object_subtype == environment_type:
                return obj

    def get_environment_with_id(self, environment_id: str) -> ObjectBase:
        for obj in self._objects["Environment"]:
            if obj.id == environment_id:
                return obj

    def get_agent_with_id(self, agent_id: str) -> ObjectBase:
        for obj in self._objects["Agent"]:
            if obj.id == agent_id:
                return obj

    def get_environment_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["Environment"] += 1
        return self.get_round_robin_ordered_objects("Environment")

    def get_event_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["Event"] += 1
        return self.get_round_robin_ordered_objects("Event")

    def get_effect_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["Effect"] += 1
        return self.get_round_robin_ordered_objects("Effect")

    def get_agent_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["Agent"] += 1
        return self.get_round_robin_ordered_objects("Agent")

    def get_action_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["Action"] += 1
        return self.get_round_robin_ordered_objects("Action")

    def get_state_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["State"] += 1
        return self.get_round_robin_ordered_objects("State")

    def get_metric_objects(self, update_index=False) -> List[ObjectBase]:
        if update_index:
            self._round_robin_index["Metric"] += 1
        return self.get_round_robin_ordered_objects("Metric")

    def get_all_objects(self) -> List[ObjectBase]:
        return_list = []
        return_list.extend(self.get_environment_objects())
        return_list.extend(self.get_effect_objects())
        return_list.extend(self.get_agent_objects())
        return_list.extend(self.get_action_objects())
        return_list.extend(self.get_state_objects())
        return_list.extend(self.get_metric_objects())
        return return_list
