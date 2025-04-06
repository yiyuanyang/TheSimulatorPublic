"""
    ============ Surface Down Effect =================
    This represents that a surface is down, and cannot
    process request for ads.
    ===================================================
"""

from simulator_base.effect.passive_effect import PassiveEffect
from datetime import datetime, timedelta


class SurfaceDownEffect(PassiveEffect):
    def __init__(
        self,
        start_time: datetime,
        duration: timedelta,
    ):
        super().__init__(
            'SurfaceDownEffect',
            effect_start_time=start_time,
            effect_end_time=duration,
        )
        self._is_surface_down = True

    @property
    def is_surface_down(self) -> bool:
        return self._is_surface_down

    @is_surface_down.setter
    def is_surface_down(self, value: bool):
        self._is_surface_down = value

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'is_surface_down': self._is_surface_down,
        })
        return base_dict

    def from_dict(self, data: dict):
        super().from_dict(data)
        self._is_surface_down = data.get('is_surface_down')
