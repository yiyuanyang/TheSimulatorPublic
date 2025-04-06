"""
    ========== Disposable Income State ==========
    This state represents how much money the user
    has left at every point in time. It can be
    reduced via purchases, taxes and etc, and can
    increase from monthly paycheck and others.
    =============================================
"""

from simulator_base.state.passive_state import PassiveState


class DisposableIncomeState(PassiveState):
    def __init__(
        self,
        disposable_income: float = 0
    ):
        super().__init__("DisposableIncomeState")
        self._disposable_income = disposable_income

    @property
    def disposable_income(self) -> float:
        return self._disposable_income

    def can_purchase(self, amount: float) -> bool:
        return self._disposable_income >= amount

    def purchase(self, amount: float):
        if not self.can_purchase(amount):
            raise Exception(
                "User does not have enough money to purchase"
            )
        self._disposable_income -= amount

    def increase(self, amount: float):
        self._disposable_income += amount
