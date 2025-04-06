"""
    ============== Ad ======================
    This represents a single ad, created
    by the advertiser agent based on budget.

    The ad agent has the following responsibilities
    that are expressed in actions and states:

    1. It tracks its own budget and duration
    and would delete itself once completed.

    2. It would pace its own spending so
    that it does not spend too soon, nor
    unable to spend all.
    ========================================
"""

from simulator_base.agent.agent import Agent
from simulator_base.orchestrator.orchestrator import Orchestrator
from ..state.ad_outcome_state import AdOutcomeState
from ..state.advertiser_intent_state import AdvertiserIntentState
from ..state.ad_budget_state import AdBudgetState
from ..types.types import (
    AdEventType,
    AdEventFields,
    AdEventList,
    TargetingFilter,
    TargetingFilterFields,
    AdEvent,
)
from ..state.ad_spec_state import AdSpecState
from datetime import datetime, timedelta


class Ad(Agent):
    def __init__(self):
        super().__init__("Ad")
        self._owner: Agent = None

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value: Agent):
        value._active_ads.append(self)
        self._owner = value

    @property
    def ad_goal(self) -> str:
        return self.get_state('AdOutcomeState').goal

    @property
    def paced_bid(self) -> float:
        budget_state: AdBudgetState = self.get_state('AdBudgetState')
        return budget_state.paced_bid

    @property
    def country(self) -> str:
        spec_state: AdSpecState = self.get_state('AdSpecState')
        return spec_state.country

    @property
    def category(self) -> str:
        spec_state: AdSpecState = self.get_state('AdSpecState')
        return spec_state.ad_category

    @property
    def impressions(self) -> AdEventList:
        out_come_state: AdOutcomeState = self.get_state('AdOutcomeState')
        return out_come_state.impressions

    @property
    def ended(self) -> bool:
        budget_state = self.get_state('AdBudgetState')
        return budget_state.has_ended

    @property
    def conversions(self) -> AdEventList:
        out_come_state: AdOutcomeState = self.get_state('AdOutcomeState')
        return out_come_state.conversions

    @property
    def product_price(self) -> float:
        advertiser_intent: AdvertiserIntentState = self.owner.get_state(
            'AdvertiserIntentState'
        )
        return advertiser_intent.product_price

    @property
    def profit_margin(self) -> float:
        advertiser_intent: AdvertiserIntentState = self.owner.get_state(
            'AdvertiserIntentState'
        )
        return advertiser_intent.profit_margin

    def total_profit(self, date: datetime = None) -> float:
        total_sales = self.total_sales(date)
        profit_margin = self.owner.get_state(
            'AdvertiserIntentState'
        ).profit_margin
        return total_sales * profit_margin

    def total_profit_after_date(self, date: datetime = None) -> float:
        today = Orchestrator.get_current_time(self)
        total_profit = 0
        while date < today:
            total_profit += self.total_profit(date)
            date += timedelta(days=1)
        return total_profit

    def total_sales(self, date: datetime = None) -> float:
        out_come_state: AdOutcomeState = self.get_state('AdOutcomeState')
        if out_come_state.goal == AdEventType.CONVERSIONS:
            conversions_cnt = len(out_come_state.get_optimized_events(date))
            advertiser_intent: AdvertiserIntentState = self.owner.get_state(
                'AdvertiserIntentState'
            )
            product_price = advertiser_intent.product_price
            profit_margin = advertiser_intent.profit_margin
            return conversions_cnt * product_price * profit_margin
        else:
            return 0

    def total_sales_after_date(self, date: datetime = None) -> float:
        today = Orchestrator.get_current_time(self)
        total_sales = 0
        while date < today:
            total_sales += self.total_sales(date)
            date += timedelta(days=1)
        return total_sales

    def total_cost(self, date: datetime = None) -> float:
        budget_state: AdBudgetState = self.get_state('AdBudgetState')
        return budget_state.get_spend(date)

    def total_cost_after_date(self, date: datetime = None) -> float:
        today = Orchestrator.get_current_time(self)
        total_cost = 0
        while date < today:
            total_cost += self.total_cost(date)
            date += timedelta(days=1)
        return total_cost

    def apply_event(self, event: AdEvent) -> float:
        cost = 0
        if event[AdEventFields.EVENT_TYPE] == AdEventType.IMPRESSIONS:
            budget_state: AdBudgetState = self.get_state('AdBudgetState')
            cost = budget_state.spend(event[AdEventFields.PRICE])
        event[AdEventFields.COST] = cost
        out_come_state: AdOutcomeState = self.get_state('AdOutcomeState')
        out_come_state.append_outcome(event)
        # if it is impression, also spend the budget
        return cost

    def roas(self, date: datetime = None) -> float:
        """
            Return on Ad Spend (ROAS) on current ad
        """
        if self.ad_goal != AdEventType.CONVERSIONS:
            raise Exception("ROAS is only available for conversion ads")
        total_cost = self.total_cost(date)
        if total_cost == 0:
            return 0
        return self.total_sales(date) / total_cost

    def roas_after_date(self, date: datetime = None) -> float:
        """
            Return on Ad Spend (ROAS) on current ad
        """
        if self.ad_goal != AdEventType.CONVERSIONS:
            raise Exception("ROAS is only available for conversion ads")
        total_cost = self.total_cost_after_date(date)
        if total_cost == 0:
            return 0
        return (
            self.total_sales_after_date(date) /
            total_cost
        )

    def roi(self, date: datetime = None) -> float:
        """
            Return on Investment (ROI) on current ad
        """
        if self.ad_goal != AdEventType.CONVERSIONS:
            raise Exception("ROI is only available for conversion ads")
        total_cost = self.total_cost(date)
        if total_cost == 0:
            return 0
        return self.total_profit(date) / total_cost

    def roi_after_date(self, date: datetime = None) -> float:
        """
            Return on Investment (ROI) on current ad
        """
        if self.ad_goal != AdEventType.CONVERSIONS:
            raise Exception("ROI is only available for conversion ads")
        total_cost = self.total_cost_after_date(date)
        if total_cost == 0:
            return 0
        return (
            self.total_profit_after_date(date) /
            total_cost
        )

    def was_running_after_date(self, date: datetime = None) -> bool:
        """
            Check if the ad was running after a certain date
        """
        budget_state: AdBudgetState = self.get_state('AdBudgetState')
        return budget_state.end_date > date

    def required_objects(self):
        return [
            'AdBudgetState',
            'AdOutcomeState',
            'AdSpecState',
            'StopAdAction',
        ]

    def validate_object(self):
        super().validate_object()
        if self._owner is None:
            raise Exception("Ad must have an advertiser as owner")
        if self._owner.object_subtype != 'Advertiser':
            raise Exception("Ad owner must be an advertiser")

    def matches_target(self, filter: TargetingFilter):
        spec_state: AdSpecState = self.get_state('AdSpecState')
        return (
            spec_state.country_match(filter[TargetingFilterFields.COUNTRY])
            and spec_state.surface_match(filter[TargetingFilterFields.SURFACE])
            and spec_state.age_match(filter[TargetingFilterFields.AGE])
            and spec_state.gender_match(filter[TargetingFilterFields.GENDER])
        )

    def stop_ad(self):
        self.owner.remove_ad(self)
        self.owner.append_inactive_ad(self)
        self.pause()
