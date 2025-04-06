"""
    ============ Active State ==========
    This represents a state machine that
    would update itself based on previous
    states and maybe effects. Compared to
    a passive state, which would only
    receive updates from actions and
    effects.
    =====================================
"""

from .state import State
from datetime import timedelta
from abc import abstractmethod
from typing import final


class ActiveState(State):
    def __init__(
        self,
        state_type: str,
        update_interval: timedelta = timedelta(days=1),
    ):
        super().__init__(state_type)
        self.simulation_interval = update_interval

    def should_update(self):
        """
            ======= May Override ========
            Check whether the state should
            be refreshed
            ============================
        """
        return True

    @abstractmethod
    def update(self):
        """
            ======= Must Implement =======
            Update the state to newer value
            via observing the simulation
            ==============================
        """
        pass

    @final
    def simulate(self):
        super().simulate()
        if self.should_update():
            self.update()
