"""
    ======= Abstract Class : Passive Effect ===============
    Compared to active effects that periodically
    applies changes to states. Passive effects are
    called upon and referenced when actions from
    agents happen. The difference between the two
    is that active effect proactively changes
    things whereas passive effect amplifies or
    reduces the effects of other actions.

    And another question may arise on the difference between
    passive effect and passive state. The idea is that
    passive effect is only temporarily applied to an agent
    whereas passive state is considered permanently applied.
    =======================================================
"""

from simulator_base.orchestrator.orchestrator import Orchestrator
from .effect_base import EffectBase
from datetime import datetime, timedelta
from typing import final


class PassiveEffect(EffectBase):
    def __init__(
        self,
        effect_type: str,
        effect_start_time: datetime,
        duration: timedelta,
    ):
        super().__init__(effect_type)
        self._effect_start_time = effect_start_time
        self._effect_end_time = effect_start_time + duration \
            if duration else None
        self._simulate_on_first_tick = True

    # Custom Evaluation function would be required
    def can_apply(self) -> bool:
        """
            Check if the effect can be applied
            to the object.
        """
        current_time = Orchestrator.get_current_time(self.subject)
        if current_time > self._effect_start_time and \
                (self._effect_end_time is None or
                    current_time < self._effect_end_time):
            return True
        return False

    @final
    def simulate(self):
        """
            Passive effect are not simulated, they
            just and react to other changes.
        """
        super().simulate()

    def __str__(self):
        return f"{self.object_subtype}_{super().__str__()}"

    # =================== System Accessible Public Methods ==================

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            "effect_start_time": self._effect_start_time,
            "effect_end_time": self._effect_end_time,
        })
        return base_dict

    def from_dict(self, data: dict):
        super().from_dict(data)
        self._effect_start_time = data.get("effect_start_time")
        self._effect_end_time = data.get("effect_end_time")
