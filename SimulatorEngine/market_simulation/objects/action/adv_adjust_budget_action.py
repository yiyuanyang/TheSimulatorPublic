"""
    ================= Adv Adjust Budget Action ===================
    This is used to represent advertiser agent adjusting the daily
    budget of the ad, based on historical performance.
    ==============================================================
"""

from simulator_base.action.action import Action
from simulator_base.orchestrator.orchestrator import Orchestrator
from ..state.advertising_budget_state import AdvertisingBudgetState
from ..state.advertiser_intent_state import AdvertiserIntentState
from datetime import timedelta


class AdvAdjustBudgetAction(Action):
    def __init__(
        self,
        consideration_frequency: timedelta = timedelta(days=30)
    ):
        super().__init__(
            "AdvAdjustBudgetAction",
            consideration_frequency
        )

    def evaluate(self) -> bool:
        return True

    def act(self):
        adv_intent: AdvertiserIntentState = self.subject.get_state(
            'AdvertiserIntentState'
        )
        budget_adjustment_performance_incremental = \
            adv_intent.budget_adjustment_performance_incremental
        current_time = Orchestrator.get_current_time(self)
        last_evaluation_period = current_time - self.simulation_interval
        last_period_roi = self.subject.roi_after_date(last_evaluation_period)
        target_roi = adv_intent.target_roi
        roi_improvement = (last_period_roi - target_roi) / target_roi

        # roi improvement would correspond to a proportional budget
        # increase
        adv_budget: AdvertisingBudgetState = self.subject.get_state(
            'AdvertisingBudgetState'
        )
        current_budget = adv_budget.daily_budget
        if roi_improvement > 0:
            new_budget = (
                current_budget * (
                    1 + roi_improvement
                ) * budget_adjustment_performance_incremental
            )
            adv_budget.daily_budget = new_budget
        else:
            # if the roi is not improving, we can reduce the budget,
            # but not below the minimum budget
            new_budget = current_budget * (
                1 - roi_improvement
            ) * budget_adjustment_performance_incremental
            adv_budget.daily_budget = new_budget
