"""
    ========== Effect Base ==========
    Represent the base class for all
    effects in the simulation.
    ==================================
"""

from simulator_base.object_base.object_with_subject import ObjectWithSubject
from datetime import timedelta


class EffectBase(ObjectWithSubject):
    def __init__(
        self,
        effect_type: str,
        simulation_interval: timedelta = None,
    ):
        super().__init__("Effect", effect_type)
        self._simulate_on_first_tick = True
        self.simulation_interval = simulation_interval

    def __str__(self):
        return f"{self.object_subtype}_{super().__str__()}"
