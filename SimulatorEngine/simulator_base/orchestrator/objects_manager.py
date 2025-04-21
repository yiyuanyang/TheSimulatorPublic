"""
    ========= Objects Manager =========
    Manages all participating objects
    in the simulation.
    ==================================
"""

from ..object_base.object_base import ObjectBase
from typing import List
import heapq
from datetime import datetime


class ObjectsManager:
    def __init__(self):
        self._command_reader = None
        # Heap queue for scheduled commands
        # with each being pair of (datetime, callable)
        # if datetime is null, then the callable should be
        # executed immediately
        self._scheduled_commands: List[tuple[datetime, callable]] = []
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
        heapq.heapify(self._scheduled_commands)
        self._internal_round_robin_index = 0
        # for rehydration purposes only
        self._total_object_cnt = None

    @property
    def is_empty(self) -> bool:
        """
            Check if any object exists in the manager
        """
        return len(self._objects["Environment"]) == 0 and \
            len(self._objects["Event"]) == 0 and \
            len(self._objects["Effect"]) == 0 and \
            len(self._objects["Agent"]) == 0 and \
            len(self._objects["Action"]) == 0 and \
            len(self._objects["State"]) == 0 and \
            len(self._objects["Metric"]) == 0

    def add_scheduled_command(self, command: tuple[datetime, callable]):
        """
            Add a scheduled command to the queue
        """
        heapq.heappush(self._scheduled_commands, command)

    def add_object(self, obj: ObjectBase):
        if obj.object_type == "CommandReader":
            self._command_reader = obj
        else:
            self._objects[obj.object_type].append(obj)

    def remove_object(self, obj: ObjectBase):
        self._objects[obj.object_type] = [
                o for o in self._objects[obj.object_type]
                if o.id != obj.id
            ]

    def get_object(self, object_type: str, object_id: str):
        """
            Get the object by its type and id
        """
        if object_type not in self._objects:
            raise Exception(f"Object type {object_type} not found")
        for obj in self._objects[object_type]:
            if obj.id == object_id:
                return obj
        return None

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

    def get_scheduled_commands(
        self,
        time_threshold: datetime
    ) -> List[tuple[datetime, callable]]:
        """
            Get all scheduled commands that are
            before the time threshold
        """
        scheduled_commands = []
        while len(self._scheduled_commands) > 0:
            command = self._scheduled_commands[0]
            if command[0] <= time_threshold:
                heapq.heappop(self._scheduled_commands)
                scheduled_commands.append(command)
            else:
                break
        return scheduled_commands

    def get_command_reader(self) -> ObjectBase:
        return self._command_reader

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

    def clear(self):
        """
        del all of the objects and clear stored
        values
        """
        self._command_reader = None
        self._scheduled_commands.clear()
        for key in self._objects:
            for obj in self._objects[key]:
                del obj
        self._round_robin_index = {
            "Environment": 0,
            "Event": 0,
            "Effect": 0,
            "Agent": 0,
            "Action": 0,
            "State": 0,
            "Metric": 0
        }
        self._internal_round_robin_index = 0
        self._total_object_cnt = None

    def rehydrate(self):
        """
            Once initial raw reloading is done, need
            to rehydrate the objects by re-establishing
            the links among them.
            And this mostly applies to the independent objects
        """
        for obj in self.get_environment_objects():
            obj.rehydrate()
        for obj in self.get_event_objects():
            obj.rehydrate()
        for obj in self.get_agent_objects():
            obj.rehydrate()
        for obj in self.get_metric_objects():
            obj.rehydrate()
        # the rehydration of effect, action and states
        # are handled by the respective independent objects
        # tally up the total object count
        total_object_cnt = 0
        for key, value in self._objects.items():
            total_object_cnt += len(value)
        if self._total_object_cnt != total_object_cnt:
            raise Exception(
                (
                    (
                        f"Total rehydrated object count mismatch"
                        f": {self._total_object_cnt} "
                        f"!= {total_object_cnt}"
                    )
                )
            )
        # now sort the objects according to the original id order
        # according to how it was saved in __getstate__
        for key in self._objects:
            temp_list = self._objects[key]
            for target_id in self._object_ids[key]:
                for obj in temp_list:
                    if obj.id == target_id:
                        temp_list.append(obj)
                        break
            self._objects[key] = temp_list
        # now remove the object ids
        self._object_ids = {}

    def __getstate__(self):
        default_state = self.__dict__.copy()
        default_state["_objects"] = self.__dict__["_objects"].copy()
        default_state["_scheduled_commands"] = []
        default_state["_object_ids"] = {}
        # turn state, action and effects into ids
        default_state["_object_ids"]["Environment"] = [
            obj.id for obj in default_state["_objects"]["Environment"]
        ]
        default_state["_object_ids"]["Event"] = [
            obj.id for obj in default_state["_objects"]["Event"]
        ]
        default_state["_object_ids"]["Agent"] = [
            obj.id for obj in default_state["_objects"]["Agent"]
        ]
        default_state["_object_ids"]["State"] = [
            obj.id for obj in default_state["_objects"]["State"]
        ]
        default_state["_object_ids"]["Action"] = [
            obj.id for obj in default_state["_objects"]["Action"]
        ]
        default_state["_object_ids"]["Effect"] = [
            obj.id for obj in default_state["_objects"]["Effect"]
        ]
        default_state["_object_ids"]["Metric"] = [
            obj.id for obj in default_state["_objects"]["Metric"]
        ]
        total_object_cnt = 0
        for key in default_state["_objects"]:
            total_object_cnt += len(default_state["_objects"][key])
        default_state["_total_object_cnt"] = total_object_cnt
        default_state["_objects"]["State"] = []
        default_state["_objects"]["Action"] = []
        default_state["_objects"]["Effect"] = []
        return default_state

    def __setstate__(self, state):
        self.__dict__.update(state)
