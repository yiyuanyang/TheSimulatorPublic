"""
    ============ Delete Ad Action ===============
    This represents Ad deleting itself, once
    it observes that it has exhausted its budget
    and has no duration left
    ============================================
"""

from simulator_base.action.action import Action
from ..state.ad_budget_state import AdBudgetState
from datetime import timedelta


class StopAdAction(Action):
    def __init__(self):
        super().__init__("StopAdAction", timedelta(hours=1))

    def evaluate(self) -> bool:
        ad_budget_state = self.subject.get_state("AdBudgetState")
        if isinstance(ad_budget_state, AdBudgetState):
            return ad_budget_state.has_ended
        else:
            raise Exception(
                "Ad does not have AdBudgetState"
            )

    def act(self):
        """
        This action would pause the ad
        """
        self.subject.stop_ad()
