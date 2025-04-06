"""
    ============= Advertiser Intent State ========================
    This represents the intent of the advertiser
    looking for what type of outcome (reach or conversions)
    the type of ads they create (format)
    and the places they advertise (surface)
    ==============================================================
"""

from simulator_base.types.types import GenderType
from simulator_base.state.passive_state import PassiveState
from ..types.types import (
    AdFormat,
    AppSurfaceType,
    AdEventType,
    AdCategory,
    BiddingStrategy,
)
from typing import List
from datetime import timedelta
import random


class AdvertiserIntentState(PassiveState):
    def __init__(
        self,
        outcomes: List[AdEventType] = [AdEventType.CONVERSIONS],
        formats: List[AdFormat] = [AdFormat.SINGLE_IMAGE],
        surfaces: List[AppSurfaceType] = [
            AppSurfaceType.CONTENT_FEED
        ],
        bidding_strategy: BiddingStrategy = (
            BiddingStrategy.MAX_OUTCOME_WITHOUT_COST_CAP
        ),
        cost_cap: float = None,
        category: AdCategory = AdCategory.OTHER,
        target_country: str = "US",
        target_min_age: int = 18,
        target_max_age: int = 65,
        target_gender: list[GenderType] = [GenderType.MALE, GenderType.FEMALE],
        max_ads_per_day: int = 5,
        max_budget_percent_per_ad: float = 0.5,
        min_budget_percent_per_ad: float = 0.1,
        max_duration_per_ad: timedelta = timedelta(days=30),
        min_duration_per_ad: timedelta = timedelta(days=1),
        product_price: float = 100,
        profit_margin: float = 0.2,
        target_roi: float = 0.2,
        budget_adjustment_performance_incremental: float = 0.5,
    ):
        super().__init__("AdvertiserIntentState")
        self._outcome = outcomes
        self._format = formats
        self._surface = surfaces
        self._max_ads_per_day = max_ads_per_day
        self._max_budget_percent_per_ad = max_budget_percent_per_ad
        self._min_budget_percent_per_ad = min_budget_percent_per_ad
        self._current_ad_cnt = 0
        self._product_price = product_price
        self._max_duration_per_ad = max_duration_per_ad
        self._min_duration_per_ad = min_duration_per_ad
        self._profit_margin = profit_margin
        self._target_country = target_country
        self._target_min_age = target_min_age
        self._target_max_age = target_max_age
        self._target_gender = target_gender
        self._category = category
        self._bidding_strategy = bidding_strategy
        self._cost_cap = cost_cap
        self._target_roi = target_roi
        self._budget_adjustment_performance_incremental = (
            budget_adjustment_performance_incremental
        )

    @property
    def bidding_strategy(self) -> BiddingStrategy:
        return self._bidding_strategy

    @property
    def cost_cap(self) -> float:
        return self._cost_cap

    @property
    def category(self) -> AdCategory:
        return self._category

    @property
    def target_country(self) -> str:
        return self._target_country

    @property
    def target_min_age(self) -> int:
        return self._target_min_age

    @property
    def target_max_age(self) -> int:
        return self._target_max_age

    @property
    def target_gender(self) -> list[GenderType]:
        return self._target_gender

    @property
    def ad_cnt(self) -> int:
        return self._current_ad_cnt

    @ad_cnt.setter
    def ad_cnt(self, value: int):
        self._current_ad_cnt = value

    @property
    def product_price(self) -> float:
        return self._product_price

    @property
    def target_roi(self) -> float:
        return self._target_roi

    @property
    def profit_margin(self) -> float:
        return self._profit_margin

    @property
    def budget_adjustment_performance_incremental(self) -> float:
        return self._budget_adjustment_performance_incremental

    def get_outcome(self) -> AdEventType:
        """
            If advertiser does not have a conversion
            ad, then prioritize creating one
        """
        active_ads = self.subject.has_active_ad_outcome(
            AdEventType.CONVERSIONS
        )
        if not active_ads:
            return AdEventType.CONVERSIONS
        return random.choice(self._outcome)

    def get_format(self) -> AdFormat:
        return random.choice(self._format)

    def get_duration(self) -> timedelta:
        """
            Exact integer number of days
        """
        return timedelta(
            days=random.randint(
                self._min_duration_per_ad.days,
                self._max_duration_per_ad.days
            )
        )

    def get_surfaces(self) -> List[AppSurfaceType]:
        return self._surface

    def get_ad_daily_budget(self) -> float:
        proposed_budget_percent = random.uniform(
            self._min_budget_percent_per_ad,
            self._max_budget_percent_per_ad
        )
        adv_budget_state = self.subject.get_state(
            "AdvertisingBudgetState"
        )
        min(
            proposed_budget_percent,
            adv_budget_state.remaining_percentage
        )
        return adv_budget_state.daily_budget * proposed_budget_percent

    def can_create_ad(self):
        remaining_budget_ratio = self.subject.get_state(
            "AdvertisingBudgetState"
        ).remaining_percentage
        return (
            self._current_ad_cnt < self._max_ads_per_day
            and remaining_budget_ratio >= self._min_budget_percent_per_ad
        )
