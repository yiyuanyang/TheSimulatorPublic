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

from simulator_base.object_base.object_with_subject import ObjectWithSubject
from abc import abstractmethod
from typing import final, Optional
from datetime import timedelta


class Action(ObjectWithSubject):
    def __init__(
        self,
        action_type: str,
        evaluation_interval: timedelta,
        simulate_on_first_tick: bool = False,
    ):
        super().__init__("Action", object_subtype=action_type)
        self._should_act = False
        self._last_action_object_lifetime: Optional[timedelta] = None
        self.simulation_interval = evaluation_interval
        self._simulate_on_first_tick = simulate_on_first_tick

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
