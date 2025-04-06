"""
    =============== Ad Factory =================
    Ad factory class, used to generate a new ad.
    ============================================
"""

from simulator_base.types.types import GenderType
from simulator_base.agent.agent import Agent
from ..ads.ad import Ad
from ..state.ad_outcome_state import AdOutcomeState
from ..state.ad_budget_state import AdBudgetState
from ..state.ad_spec_state import AdSpecState
from ..action.stop_ad_action import StopAdAction
from ..types.types import (
    AdEvent,
    AdFormat,
    AppSurfaceType,
    BiddingStrategy,
    AdCategory,
)
from datetime import timedelta
from typing import List, Optional


def create_ad(
    advertiser: Agent,
    ad_outcome: AdEvent,
    ad_format: AdFormat,
    target_country: str,
    target_min_age: int,
    target_max_age: int,
    target_gender: List[GenderType],
    category: AdCategory,
    bidding_strategy: BiddingStrategy,
    cost_cap: Optional[float],
    ad_surfaces: List[AppSurfaceType],
    ad_budget: float,
    duration: timedelta
):
    ad = Ad()
    ad.owner = advertiser
    ad.add_object(AdOutcomeState(ad_outcome))
    ad.add_object(AdBudgetState(
        duration,
        ad_budget,
        bidding_strategy,
        cost_cap
    ))
    ad.add_object(
        AdSpecState(
            ad_surfaces,
            target_country,
            target_min_age,
            target_max_age,
            target_gender,
            category,
            ad_format,
        ),
    )
    ad.add_object(StopAdAction())
    return ad
