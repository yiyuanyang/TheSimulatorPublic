"""
    =========== Ad Outcome State =============
    This file describes the currently obtained
    outcome of the ad, and allows for easy
    aggregation of the ad's performance by
    different axis.
    ==========================================
"""

from simulator_base.state.passive_state import PassiveState
from ..types.types import AdEvent, AdEventList, AdEventType, AdEventFields
from datetime import timedelta, datetime


class AdOutcomeState(PassiveState):
    def __init__(
        self,
        goal: AdEventType = AdEventType.CONVERSIONS,
        aggregation_frequency=timedelta(hours=6),
    ):
        super().__init__(
            "AdOutcomeState",
            # calculate current outcome every 6 hours
        )
        self._impressions: AdEventList = []
        self._conversions: AdEventList = []
        self._goal = goal
        self.simulation_interval = aggregation_frequency

    @property
    def impressions(self) -> AdEventList:
        return self._impressions

    @property
    def conversions(self) -> AdEventList:
        return self._conversions

    @property
    def goal(self) -> AdEventType:
        return self._goal

    def append_outcome(self, event: AdEvent):
        if event[AdEventFields.EVENT_TYPE] == AdEventType.IMPRESSIONS:
            self._impressions.append(event)
        elif event[AdEventFields.EVENT_TYPE] == AdEventType.CONVERSIONS:
            self._conversions.append(event)

    def get_outcomes(
        self,
        event_type: AdEventType = None,
        filter_fn: callable = None
    ) -> AdEventList:
        if filter_fn:
            if event_type == AdEventType.IMPRESSIONS:
                return list(filter(filter_fn, self._impressions))
            if event_type == AdEventType.CONVERSIONS:
                return list(filter(filter_fn, self._conversions))
        else:
            if event_type == AdEventType.IMPRESSIONS:
                return self._impressions
            if event_type == AdEventType.CONVERSIONS:
                return self._conversions

    def _event_date_match(self, event: AdEvent, date: datetime = None) -> bool:
        if date is None:
            return True
        return event[AdEventFields.EVENT_TIME].date() == date.date()

    def get_optimized_events(self, date: datetime = None) -> AdEventList:
        """
            Get all outcomes that match the desired goal
            if date is provided, only get outcomes that happen
            within the same day as the date.
        """
        return self.get_outcomes(
            self._goal,
            filter_fn=lambda event: self._event_date_match(event, date)
        )

    def get_impressions(self, date: datetime = None) -> AdEventList:
        return self.get_outcomes(
            AdEventType.IMPRESSIONS,
            filter_fn=lambda event: self._event_date_match(event, date)
        )

    def get_conversions_rate(self, date: datetime = None) -> float:
        impressions = len(self.get_impressions(date))
        conversions = len(self.get_optimized_events(date))
        if impressions == 0:
            return 0
        return conversions / impressions
