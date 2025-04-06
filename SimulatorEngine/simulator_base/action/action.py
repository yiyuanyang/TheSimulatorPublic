"""
    ======== Abstract Class : Action ===========
    An action is an actor reliant object. During
    every tick of the simulation for agents, we
    evaluate if each of the action should be
    performed, and later in action evaluation
    we would perform all confirmed actions.
    Actions would then change certain states
    of the objects, and in very rare cases,
    change the environment objects.
    ============================================
"""

from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.object_base.object_with_subject import ObjectWithSubject
from abc import abstractmethod
from typing import final, Optional
from datetime import timedelta


class Action(ObjectWithSubject):
    def __init__(
        self,
        action_type: str,
        evaluation_interval: timedelta,
    ):
        super().__init__("Action", object_subtype=action_type)
        self._should_act = False
        self._last_action_object_lifetime: Optional[timedelta] = None
        self.simulation_interval = evaluation_interval

    # ============= Abstract Methods ================

    @abstractmethod
    def evaluate(self) -> bool:
        """
            ====== Must Implement =========
            Evaluate whether during current
            simulation cycle if the action
            should be performed.
            ===============================
        """
        return False

    @abstractmethod
    def act(self):
        """
            ====== Must Implement ==========
            Perform the action
            ================================
        """
        pass

    # ============= User Accessible Public Methods ==============

    def __str__(self):
        return f"{self.object_subtype}_{super().__str__()}"

    # =============== System Accessible Public Methods =================

    @final
    def simulate(self):
        """
            Simulate the action
        """
        if self._should_act:
            self._last_action_object_lifetime = self.object_lifetime
            self.act()
        self._should_act = False
        super().simulate()

    @final
    def to_dict(self) -> dict:
        """
            Serialize the action
        """
        dict_base = super().to_dict()
        action_data = {
            'should_act': self._should_act,
            'last_action_object_lifetime': self._last_action_object_lifetime,
            'subject': self.subject.id,
        }
        dict_base.update(action_data)
        return dict_base

    @final
    def from_dict(self, object_data: dict):
        """
            Deserialize the action
        """
        super().from_dict(object_data)
        self._should_act = object_data.get('should_act', False)
        self._last_action_object_lifetime = object_data.get(
            'last_action_object_lifetime', None
        )
        actor_id = object_data.get('actor', None)
        if actor_id is not None:
            raise Exception(
                f"Actor id missing in actor deserialization {self.id}"
            )
        actor = get_orchestrator().get_agent(actor_id)
        actor.add_object(self)

    # ============= Private Helper Methods =============
    @final
    def _evaluate(self):
        """
            This is performed
            when we tick on the agent
            to evaluate if the action
            would later be performed
        """
        self._should_act = self.evaluate()
