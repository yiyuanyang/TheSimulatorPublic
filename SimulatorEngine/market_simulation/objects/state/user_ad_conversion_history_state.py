"""
    ======== User Ad Conversion History State ============
    User Ad View History state would increase and decrease
    probability. This may not be the case for conversion.
    
    This state is used only for tracking purposes.
    ======================================================
"""

from simulator_base.orchestrator.orchestrator import Orchestrator
from simulator_base.state.active_state import ActiveState
from ..types.types import AdEvent, AdEventFields, AdEventType
from datetime import timedelta


class UserAdConversionHistoryState(ActiveState):
    def __init__(
        self,
        memory_duration: timedelta = timedelta(days=14),
    ):
        super().__init__("UserAdConversionHistoryState")
        self._ad_conversion_history = []
        self._memory_duration = memory_duration

    def convert_ad(self, ad_event: AdEvent):
        if ad_event[AdEventFields.EVENT_TYPE] != AdEventType.CONVERSIONS:
            raise ValueError(
                "AdEventType must be CONVERSIONS to be converted in "
                "UserAdConversionHistoryState"
            )
        self._ad_conversion_history.append(ad_event)

    def _remove_old_conversions(self):
        # remove conversions that are older than memory duration
        current_time = Orchestrator.get_current_time(self.subject)
        earliest_time = current_time - self._memory_duration
        while self._ad_conversion_history and self._ad_conversion_history[0][
            AdEventFields.EVENT_TIME
        ] < earliest_time:
            self._ad_conversion_history.pop(0)

    def update(self):
        super().update()
        self._remove_old_conversions()
