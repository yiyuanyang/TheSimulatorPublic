"""
    ======= Purchases State ===========
    This represents the purchases done
    by the user within a time period.
    These information would help adjust
    user intent.
    ===================================
"""

from simulator_base.state.active_state import ActiveState
from ..types.types import AdCategory, PurchaseHistory
from simulator_base.orchestrator.orchestrator import Orchestrator
from typing import List, final
from datetime import datetime, timedelta


@final
class PurchasesState(ActiveState):
    def __init__(
        self,
        purchases: PurchaseHistory = None,
        memory_duration: timedelta = timedelta(days=30),
    ):
        super().__init__("PurchasesState", memory_duration)
        self._memory_duration = memory_duration
        if purchases:
            self._purchases = purchases
        else:
            self._purchases = {}
            for category in AdCategory:
                self._purchases[category] = []

    def add_purchase(self, category: AdCategory, purchase_time: datetime):
        self._purchases[category].append(purchase_time)

    def get_purchases(self, category: AdCategory) -> List[datetime]:
        return self._purchases[category]

    @property
    def purchases(self) -> PurchaseHistory:
        return self._purchases

    def _remove_old_purchases(self):
        today = Orchestrator.get_current_time(self)
        time_threshold = today - self._memory_duration
        # since purchases are stored in order of time
        # we can remove purchases until we reach a
        # purchase that is within the memory duration
        while self._purchases and self._purchases[0] < time_threshold:
            self._purchases.pop(0)

    def update(self):
        super().update()
        self._remove_old_purchases()
