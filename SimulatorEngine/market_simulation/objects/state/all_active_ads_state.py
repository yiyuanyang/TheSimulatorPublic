"""
    =========== All Active Ads State ============
    This is part of the all ads environment that
    periodically summarizes all active ads for
    the recommendation system to retrieve.
    =============================================
"""

from simulator_base.state.active_state import ActiveState
from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.agent.agent import Agent
from typing import List
from datetime import timedelta


class AllActiveAdsState(ActiveState):
    def __init__(
        self,
        ad_scan_interval: timedelta = timedelta(minutes=30),
    ):
        super().__init__("AllActiveAdsState")
        self._active_ads: List[Agent] = []
        self.simulation_interval = ad_scan_interval

    @property
    def active_ads(self) -> List[Agent]:
        return self._active_ads

    def update(self):
        """
            Find all ads that are available and active
            and set to active ads field
        """
        all_agents = get_orchestrator().get_all_agents()
        active_ads = [
            agent for agent in all_agents
            if agent.object_subtype == "Ad"
            and not agent.get_state("AdBudgetState").has_ended
        ]
        self._active_ads = active_ads
