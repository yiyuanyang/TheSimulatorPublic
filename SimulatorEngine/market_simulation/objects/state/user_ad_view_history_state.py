"""
    ========= User Ad View History State ==========
    This state represent the more user view a non
    awareness ad, there would be an increase in the
    chance of conversion for certain time period.
    And if the ad is a conversion ad, then user
    intent would be reduced instead due to ad
    fatigue.
    ==============================================
"""

from simulator_base.state.active_state import ActiveState
from simulator_base.agent.agent import Agent
from simulator_base.orchestrator.orchestrator import Orchestrator
from ...config.market_config import get_config
from ..types.types import AdEventList, AdEvent, AdEventFields, AdEventType
from datetime import timedelta


class UserAdViewHistoryState(ActiveState):
    def __init__(
        self,
        memory_duration: timedelta = timedelta(days=7),
    ):
        super().__init__("UserAdViewHistoryState")
        self._ad_view_history: AdEventList = []
        self._memory_duration = memory_duration

    def view_ad(self, ad_event: AdEvent):
        if ad_event[AdEventFields.EVENT_TYPE] != AdEventType.IMPRESSIONS:
            raise ValueError(
                (
                    "AdEventType must be IMPRESSIONS to be viewed in "
                    "UserAdViewHistoryState"
                )
            )
        self._ad_view_history.append(ad_event)

    def get_event_cnt_on_advertiser(
        self,
        event_type: AdEventType,
        advertiser: Agent
    ) -> int:
        cnt = 0
        for event in self._ad_view_history:
            if (
                event[AdEventFields.AD].owner == advertiser
                and event[AdEventFields.EVENT_TYPE] == event_type
            ):
                cnt += 1
        return cnt

    def get_event_cnt_on_ad(
        self,
        event_type: AdEventType,
        ad: Agent
    ) -> int:
        cnt = 0
        for event in self._ad_view_history:
            if (
                event[AdEventFields.AD] == ad
                and event[AdEventFields.EVENT_TYPE] == event_type
            ):
                cnt += 1
        return cnt

    def get_ad_view_history_factor(self, ad: Agent) -> float:
        """
            Awareness ads improve user sentiment to the advertiser
            whereas conversion ads reduce user sentiment to the particular
            ad.
        """
        user_config = get_config().get_user_config()
        intent_config = user_config["intent_config"]
        awareness_improvement = intent_config["awareness_improvement"]
        ad_fatigue = intent_config["ad_fatigue"]
        awareness_cnt = self.get_event_cnt_on_advertiser(
            AdEventType.IMPRESSIONS,
            ad.owner
        )
        conversions_cnt = self.get_event_cnt_on_ad(
            AdEventType.CONVERSIONS, ad
        )
        awareness_factor = min(1.5, 1 + awareness_cnt * awareness_improvement)
        conversion_factor = max(0.5, 1 - conversions_cnt * ad_fatigue)
        return awareness_factor * conversion_factor

    def _remove_old_ad_views(self):
        today = Orchestrator.get_current_time(self)
        time_threshold = today - self._memory_duration
        # since ad views are stored in order of time
        # we can remove ad views until we reach a
        # view that is within the memory duration
        while self._ad_view_history and self._ad_view_history[0][
            AdEventFields.EVENT_TIME
        ] < time_threshold:
            self._ad_view_history.pop(0)

    def update(self):
        super().update()
        self._remove_old_ad_views()
