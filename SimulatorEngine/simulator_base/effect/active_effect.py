"""
    ======= Abstract Class : Active Effect =========
    Active effect (as opposed to passive effect) are
    effects that periodically apply changes to agent
    environment and states. A good example is illness,
    it will continuously reduce health bar from the
    patient on a schedule that isn't dictated by the
    agent or subject themselves. Hence the difference
    from passive effect, which is a more "referenced"
    effect which is referenced / utilized for adjusted
    calculation when agent or other objects trigger
    certain behavior or actions, a good example is
    tax, it will be applied on top of a person's bill
    whenever the person purchase something.
    ================================================
"""

from .effect_base import EffectBase
from ..orchestrator.orchestrator import Orchestrator
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import final


class ActiveEffect(EffectBase):
    def __init__(
        self,
        effect_type: str,
        application_time_interval: timedelta = timedelta(hours=1),
        duration: timedelta = None,
    ):
        super().__init__(effect_type, application_time_interval)
        self._duration = duration
        self._target_end_time = None
        self._simulate_on_first_tick = True

    @final
    def before_start(self):
        super().before_start()
        if self._duration is not None:
            current_time = Orchestrator.get_current_time(self.subject)
            self._target_end_time = current_time + self._duration

    @final
    def should_remove(self) -> bool:
        if self._target_end_time is not None:
            if Orchestrator.get_current_time(self) > \
               self._target_end_time:
                return True
        return False

    def evaluate(self) -> bool:
        """
            Evaluate whether effect at hand
            should be
            executed in the current
            simulation cycle.
        """
        return True

    @abstractmethod
    def apply(self):
        """
            Apply the effect to the subject
        """
        pass

    @final
    def simulate(self):
        super().simulate()
        if self.should_remove():
            self.destroy()
        if self.evaluate():
            self.apply()

    def __str__(self):
        return f"{self.object_subtype}_{super().__str__()}"

    @final
    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            "target_end_time": self._target_end_time.isoformat(),
            "duration": self._duration.total_seconds(),
        })
        return base_dict

    @final
    def from_dict(self, data: dict):
        super().from_dict(data)
        self._target_end_time = datetime.fromisoformat(
            data["target_end_time"]
        ) if data["target_end_time"] is not None else None
        self._duration = timedelta(seconds=data["duration"])
