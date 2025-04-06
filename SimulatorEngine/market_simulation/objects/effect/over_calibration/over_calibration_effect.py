"""
    ======== OverCalibrationEffect ========
    This represents model over predicting
    the potential outcome of the ad.
    =======================================
"""

from simulator_base.effect.passive_effect import PassiveEffect
from datetime import datetime, timedelta


class OverCalibrationEffect(PassiveEffect):
    def __init__(
        self,
        over_calibration: float = 0,
        start_time: datetime = None,
        duration: timedelta = None,
    ):
        super().__init__(
            'OverCalibrationEffect',
            effect_start_time=start_time,
            effect_end_time=duration,
        )
        self._over_calibration = over_calibration

    @property
    def over_calibration(self) -> float:
        return self._over_calibration

    @over_calibration.setter
    def over_calibration(self, value: float):
        self._over_calibration = value

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'over_calibration': self._over_calibration,
        })

    def from_dict(self, data: dict):
        super().from_dict(data)
        self._over_calibration = data.get('over_calibration')
