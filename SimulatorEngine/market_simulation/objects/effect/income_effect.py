"""
    ========== Income Effect =========
    This represents monthly income for
    users in the simulation. This is
    used to increase the disposable income
    of the user.
    ==================================
"""

from simulator_base.effect.active_effect import ActiveEffect
from datetime import timedelta
from typing import final


@final
class IncomeEffect(ActiveEffect):
    def __init__(
        self,
        income: float = 0
    ):
        super().__init__(
            'IncomeEffect',
            application_time_interval=timedelta(days=14),
        )
        self._income = income

    def apply(self):
        disposable_income_state = self.subject.get_state(
            'DisposableIncomeState'
        )
        if disposable_income_state:
            disposable_income_state.increase(self._income)
        else:
            raise Exception(
                'Error when applying income effect: '
                'DisposableIncomeState not found for agent'
            )
