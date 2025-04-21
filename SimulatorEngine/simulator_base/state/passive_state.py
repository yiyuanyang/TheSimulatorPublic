"""
    ========== Passive State ===============
    Passive states represent states that
    are only updated by actions and effects,
    and do not update themselves. Compared
    to active states, which update themselves,
    or static states, which do not change.
    ========================================
"""

from .state import State
from typing import final


class PassiveState(State):
    def __init__(self, state_type: str):
        super().__init__(state_type)

    @final
    def simulate(self):
        pass
