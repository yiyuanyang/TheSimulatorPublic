"""
    ================ Surface Environment =================
    Surface environment, contains basic information around
    the surface type, the ad load on the surface and etc.
    =====================================================
"""

from simulator_base.environment.environment import Environment
from simulator_base.orchestrator.orchestrator import (
    get_orchestrator
)
from simulator_base.agent.agent import Agent
from market_simulation.objects.auction.auction_environment import (
    AuctionEnvironment
)
from ..types.types import (
    AppSurfaceType,
    AdEventList,
    AdEventFields,
    AuctionResults,
    AuctionResultFields,
    AdEventType,
    OrganicEventType,
    OrganicEventFields,
    OrganicEvent,
    OrganicEventList
)
from datetime import timedelta, datetime
from copy import deepcopy
from random import random


class SurfaceEnvironment(Environment):
    def __init__(
        self,
        surface_type: AppSurfaceType,
        ad_load: float,  # Impressions Per Seconds
        fetch_cnt: int = 0,
    ):
        super().__init__("SurfaceEnvironment")
        self._surface_type = surface_type
        # this is described as number of ads viewed
        # per second on the surface
        self._ad_load = ad_load
        self._impressions: AdEventList = []
        self._outcomes: AdEventList = []
        self._visits: OrganicEventList = []
        self._fetch_cnt = fetch_cnt
        self.simulation_interval = timedelta(hours=12)

    @property
    def visits(self) -> OrganicEventList:
        return self._visits

    @property
    def impressions(self) -> AdEventList:
        return self._impressions

    @property
    def outcomes(self) -> AdEventList:
        return self._outcomes

    @property
    def surface_type(self) -> AppSurfaceType:
        return self._surface_type

    def _position_decay(
        self,
        position: int,
    ) -> float:
        return 0.95 ** position

    def browse_surface(
        self,
        user: Agent,
        time: timedelta
    ):
        orchestrator = get_orchestrator()
        user_time = orchestrator.get_current_time(user)
        organic_event: OrganicEvent = {
            OrganicEventFields.USER: user,
            OrganicEventFields.EVENT_TYPE: OrganicEventType.SURFACE_ENTER,
            OrganicEventFields.SURFACE: self._surface_type,
            OrganicEventFields.EVENT_TIME: user_time
        }
        self._visits.append(organic_event)
        surface_down_effect = self.get_effect('SurfaceDownEffect')
        if surface_down_effect \
           and surface_down_effect.can_apply() \
           and surface_down_effect.is_surface_down:
            return
        total_impressions = int(self._ad_load * time.total_seconds())
        auction_environment: AuctionEnvironment = orchestrator.get_environment(
            'AuctionEnvironment'
        )
        ranked_ads = auction_environment.fetch_and_price_all_ads(
            user,
            self._surface_type,
            ad_cnt=self._fetch_cnt
        )
        viewed_ads = ranked_ads[:total_impressions]
        event_base: AdEventList = {
            AdEventFields.USER: None,
            AdEventFields.AD: None,
            AdEventFields.EVENT_TYPE: None,
            AdEventFields.SURFACE: self._surface_type,
            AdEventFields.BID: None,
            AdEventFields.COST: None,
            AdEventFields.TRUE_PROBABILITY: None,
            AdEventFields.PREDICTED_PROBABILITY: None,
            AdEventFields.EVENT_TIME: None
        }
        self.view_ads(user, event_base, viewed_ads, user_time, time)
        self.convert(user, event_base, viewed_ads, user_time, time)

    def view_ads(
        self,
        user: Agent,
        event_base: AdEventList,
        ranked_ads: AuctionResults,
        start_time: datetime,
        duration: timedelta
    ) -> float:
        if len(ranked_ads) == 0:
            return
        individual_interval_float = duration.total_seconds() / len(ranked_ads)
        individual_interval_timedelta = timedelta(
            seconds=individual_interval_float
        )
        for index, item in enumerate(ranked_ads):
            event = deepcopy(event_base)
            event[AdEventFields.USER] = user
            event[AdEventFields.AD] = item[AuctionResultFields.AD]
            event[AdEventFields.EVENT_TYPE] = AdEventType.IMPRESSIONS
            event[AdEventFields.BID] = item[AuctionResultFields.BID]
            event[AdEventFields.PACED_BID] = item[
                AuctionResultFields.PACED_BID
            ]
            event[AdEventFields.PRICE] = item[AuctionResultFields.PRICE]
            event[AdEventFields.COST] = 0
            event[AdEventFields.TRUE_PROBABILITY] = item[
                AuctionResultFields.TRUE_PROBABILITY]
            event[AdEventFields.PREDICTED_PROBABILITY] = item[
                AuctionResultFields.PREDICTED_PROBABILITY
            ]
            event[AdEventFields.EVENT_TIME] = start_time + index * \
                individual_interval_timedelta
            cost = item[AuctionResultFields.AD].apply_event(event)
            event[AdEventFields.COST] = cost
            self._impressions.append(event)
            user.view_ad(event)

    def convert(
        self,
        user: Agent,
        event_base: AdEventList,
        ranked_ads: AuctionResults,
        start_time: datetime,
        duration: timedelta
    ):
        if len(ranked_ads) == 0:
            return
        individual_interval_float = duration.total_seconds() / len(ranked_ads)
        individual_interval_timedelta = timedelta(
            seconds=individual_interval_float
        )
        for index, item in enumerate(ranked_ads):
            if item[AuctionResultFields.AD].ad_goal == AdEventType.IMPRESSIONS:
                continue
            event = deepcopy(event_base)
            event[AdEventFields.USER] = user
            event[AdEventFields.AD] = item[AuctionResultFields.AD]
            event[AdEventFields.EVENT_TYPE] = AdEventType.CONVERSIONS
            event[AdEventFields.BID] = item[AuctionResultFields.BID]
            event[AdEventFields.PRICE] = item[AuctionResultFields.PRICE]
            event[AdEventFields.COST] = 0
            event[AdEventFields.PACED_BID] = item[
                AuctionResultFields.PACED_BID
            ]
            event[AdEventFields.TRUE_PROBABILITY] = item[
                AuctionResultFields.TRUE_PROBABILITY]
            event[AdEventFields.PREDICTED_PROBABILITY] = item[
                AuctionResultFields.PREDICTED_PROBABILITY
            ]
            event[AdEventFields.EVENT_TIME] = start_time + index * \
                individual_interval_timedelta

            # simulate the conversion
            success = random() < item[AuctionResultFields.TRUE_PROBABILITY]
            if success:
                user.convert_ad(event)
                self._outcomes.append(event)
                item[AuctionResultFields.AD].apply_event(event)

    def simulate(self):
        """
            Remove impressions and outcomes that are older than
            7 days.
        """
        today = get_orchestrator().get_current_time(self)
        # from front to back
        while self._impressions and \
                (today - self._impressions[0][AdEventFields.EVENT_TIME]) > \
                timedelta(days=7):
            self._impressions.pop(0)
        while self._outcomes and \
                (today - self._outcomes[0][AdEventFields.EVENT_TIME]) > \
                timedelta(days=7):
            self._outcomes.pop(0)
        while self._visits and \
                (today - self._visits[0][OrganicEventFields.EVENT_TIME]) > \
                timedelta(days=7):
            self._visits.pop(0)

    @property
    def ad_load(self):
        return self._ad_load

    @ad_load.setter
    def ad_load(self, value):
        self._ad_load = value

    def __str__(self):
        super_str = super().__str__()
        return f"{self._surface_type}_{super_str}"
