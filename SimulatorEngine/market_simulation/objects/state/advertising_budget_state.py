"""
    ============= Advertising Budget State ================
    This represents the amount of money the advertiser has
    in total to spend on advertising. With an assumed daily
    spending rate. This number can increase subject to the
    ROI of the advertising product.
    =======================================================
"""

from simulator_base.state.passive_state import PassiveState


class AdvertisingBudgetState(PassiveState):
    def __init__(
        self,
        daily_budget: float = 0,
    ):
        super().__init__("AdvertisingBudgetState")
        self._daily_budget = daily_budget
        self._remaining_budget = daily_budget

    @property
    def daily_budget(self) -> float:
        return self._daily_budget

    @daily_budget.setter
    def daily_budget(self, value: float):
        self._daily_budget = value

    @property
    def utilized_budget(self) -> float:
        return self.subject.utilized_budget

    @property
    def remaining_percentage(self) -> float:
        return 1 - self.utilized_budget / self._daily_budget

    def can_spend(self, amount: float) -> bool:
        return self.remaining_percentage * self._daily_budget >= amount
