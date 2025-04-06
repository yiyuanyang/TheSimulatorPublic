"""
    ============ Ad Budget State ===============
    Ad Budget State describes the current
    and remaining duration / budget of the ad,
    and the bidding strategy of the ad, as well
    as the calculated paced bid and pacing
    multipliers, to help the ad achieve its
    maximal outcome.
    ============================================
"""


from simulator_base.state.active_state import ActiveState
from simulator_base.orchestrator.orchestrator import Orchestrator
from ...config.market_config import get_config
from ..types.types import BiddingStrategy
from datetime import timedelta, datetime, date
from typing import final, Optional


class AdBudgetState(ActiveState):
    def __init__(
        self,
        duration: timedelta = timedelta(days=1),
        daily_budget: float = 0,
        bidding_strategy: BiddingStrategy = (
            BiddingStrategy.MAX_OUTCOME_WITHOUT_COST_CAP
        ),
        cost_cap: float = None,
    ):
        super().__init__("AdBudgetState", timedelta(hours=1))
        self._duration: timedelta = duration
        self._budget = duration.days * daily_budget
        self._remaining_budget = duration.days * daily_budget
        self._daily_budget = daily_budget
        self._remaining_daily_budget = daily_budget
        self._over_delivery = 0
        market_config = get_config()
        delivery_config = market_config.get_delivery_config()
        pacing_config = delivery_config["pacing_config"]
        starting_pacing_multiplier = pacing_config[
            "starting_pacing_multiplier"
        ]
        self._current_pacing_multiplier = starting_pacing_multiplier
        self._bidding_strategy = bidding_strategy
        self._cost_cap = cost_cap
        self._daily_spent: dict[date, float] = {}
        self._end_date = None
        self._pacing_adjustment_counter = 0
        self._start_pacing_time = None
        self._target_end_time = None
        self._last_pacing_period_start_time = None

    # ============= User Accessible Public Methods ==============

    @property
    def bidding_strategy(self) -> BiddingStrategy:
        """
            The bidding strategy of the ad.
        """
        return self._bidding_strategy

    @property
    def remaining_daily_budget(self) -> float:
        """
            The remaining daily budget for the ad.
        """
        return self._remaining_daily_budget

    @property
    def daily_budget(self) -> float:
        """
            How much the ad is targeting to
            spend every simulated day.
        """
        return self._daily_budget

    @property
    def remaining_duration(self) -> timedelta:
        """
            Number of days left for the ad to
            run.
        """
        current_time = Orchestrator.get_current_time(self.subject)
        if self._target_end_time is None:
            return self._target_end_time - current_time
        return timedelta(hours=0)

    @property
    def remaining_budget(self) -> float:
        """
            Total unspent budget for the ad
            for the entire duration.
        """
        return self._remaining_budget

    @property
    def over_delivery(self) -> float:
        """
            'Illegal' charges on the ad budget
            this mostly represent billing on the
            ad after budget has depleted. Since
            the system has delays in various data
            sources, this is inevitable.
        """
        return self._over_delivery

    @property
    def has_ended(self) -> bool:
        """
            Whether the ad has finished.
        """
        if self._target_end_time is None:
            return False
        current_time = Orchestrator.get_current_time(self.subject)
        return current_time > self._target_end_time

    @property
    def end_date(self) -> Optional[datetime]:
        """
            The date when the ad finished.
        """
        return self._target_end_time

    def start_pacing(self):
        current_time = Orchestrator.get_current_time(self.subject)
        self._start_pacing_time = current_time
        self._last_pacing_period_start_time = current_time
        self._target_end_time = current_time + self._duration

    def can_spend(self, amount: float):
        return (not self.has_ended
                and self._remaining_daily_budget >= amount
                and self._remaining_budget >= amount)

    def spend(self, amount: float) -> float:
        current_date = Orchestrator.get_current_time(self).date()
        if current_date not in self._daily_spent:
            self._daily_spent[current_date] = 0
        proposed_spending = 0
        if self._remaining_daily_budget < amount:
            proposed_spending = self._remaining_daily_budget
            self._over_delivery += amount - self._remaining_daily_budget
            self._remaining_daily_budget = 0
            self._remaining_budget = max(0, self._remaining_budget - amount)
        else:
            proposed_spending = amount
            self._remaining_daily_budget -= amount
            self._remaining_budget -= amount
        self._daily_spent[current_date] += proposed_spending
        return proposed_spending

    def get_spend(self, date: datetime = None) -> float:
        if date is None:
            return self._budget - self._remaining_budget
        if date not in self._daily_spent:
            return 0
        return self._daily_spent[date]

    @property
    def paced_bid(self):
        """
            Conceptually, this is essentially ad making a limit order
            in the market, and participate in auction for all conversions
            below this price.
        """
        pacing_config = get_config().get_delivery_config()['pacing_config']
        adjustment_interval = pacing_config["adjustment_interval"]
        max_bid = pacing_config["max_bid"]
        if self._bidding_strategy == BiddingStrategy.COST_CAP:
            return self._cost_cap
        proposed_paced_bid = None
        if self._pacing_adjustment_counter < adjustment_interval:
            self._pacing_adjustment_counter += 1
            proposed_paced_bid = self._current_pacing_multiplier
        else:
            proposed_paced_bid = self.pacing_multiplier
        calculated_bid = max_bid * proposed_paced_bid
        if self._bidding_strategy == \
                BiddingStrategy.MAX_OUTCOME_WITH_COST_CAP:
            return min(self._cost_cap, calculated_bid)
        elif self._bidding_strategy == \
                BiddingStrategy.MAX_OUTCOME_WITHOUT_COST_CAP:
            return calculated_bid
        else:
            raise Exception("Invalid bidding strategy")

    @property
    def pacing_multiplier(self):
        """
            A number between 0 and 1 that tries
            to spend the total daily budget
            within the 24 hours while maximizing
            the outcomes. Opportunity curve is
            equivalent to the time curve if user
            per hour activity difference is not modeled.
            Otherwise, an opportunity curve needs to be
            explicitly modeled.
        """
        self._current_pacing_multiplier = self._pacing_multiplier_readonly()
        return self._current_pacing_multiplier

    @final
    def before_start(self):
        super().before_start()
        self.start_pacing()

    def update(self):
        if self._start_pacing_time is None:
            return
        current_time = Orchestrator.get_current_time(self)
        # if it has being 24 hours since last pacing period
        # and we are not yet at the end of the ad, refresh
        # the daily budget
        if current_time > self._target_end_time:
            self.subject.pause()
        elif current_time - self._last_pacing_period_start_time > \
                timedelta(days=1):
            self._last_pacing_period_start_time = current_time
            self._remaining_daily_budget = self._daily_budget

    def validate_object(self):
        """
            Duration has to be in exact number of days.
            No extra seconds or minutes, but exact
            number of days.
            Budget has to be a number greater than
            0 and divisible by duration.
        """
        super().validate_object()
        if self._bidding_strategy != \
                BiddingStrategy.MAX_OUTCOME_WITHOUT_COST_CAP:
            if self._cost_cap is None:
                raise Exception(
                    "Cost cap has to be set for this bidding strategy"
                )
        if self._duration.total_seconds() % 86400 != 0:
            raise Exception("Duration has to be in exact number of days")
        if self._budget <= 0:
            raise Exception("Budget has to be greater than 0")

    # ================= Private Helper Methods ==================

    def _pacing_multiplier_readonly(self):
        """
            This calculates pacing multiplier
            without modify the current pacing multiplier
            for debugging purposes only.
        """
        expected_hourly_spend = self._daily_budget / 24
        current_time = Orchestrator.get_current_time(self)
        hours_passed = (
            current_time - self._last_pacing_period_start_time
        ).total_seconds() / 3600
        remaining_hours = 24 - hours_passed
        if remaining_hours == 0:
            return 0
        expected_remaining_budget = remaining_hours * expected_hourly_spend
        pacing_config = get_config().get_delivery_config()['pacing_config']
        alpha = pacing_config["alpha"]
        epsilon = pacing_config["epsilon"]
        factor = self._remaining_daily_budget / expected_remaining_budget - 1
        delta = self._current_pacing_multiplier * alpha * factor + epsilon
        return max(min(self._current_pacing_multiplier + delta, 1), 0)

    def _get_paced_bid_readonly(self) -> float:
        pacing_config = get_config().get_delivery_config()['pacing_config']
        max_bid = pacing_config["max_bid"]
        return max_bid * self._pacing_multiplier_readonly()
