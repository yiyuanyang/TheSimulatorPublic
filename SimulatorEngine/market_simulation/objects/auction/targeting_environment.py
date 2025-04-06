"""
    ================ Targeting Filter Stage =============
    This file contains a functional implementation of
    the targeting filter stage of the ad tech system.

    Targeting filter stage is represented via
    an Environment as it affects all ads and users.

    User side would send a request for ads with
    information such as country, age, gender and surface,
    the goal of the targeting filter stage is to find
    all available ads that meets the user's criteria.
    =====================================================
"""

from simulator_base.environment.environment import Environment
from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.object_base.object_base import ObjectBase
from .all_ads_environment import AllAdsEnvironment
from ..types.types import TargetingFilter


class TargetingEnvironment(Environment):
    def __init__(self):
        super().__init__("TargetingEnvironment")

    def get_ads_with_filters(
        self,
        filters: TargetingFilter
    ):
        """
            Get all ads that meets the user's criteria
        """
        all_ads_environment: AllAdsEnvironment = (
            get_orchestrator().get_environment('AllAdsEnvironment')
        )
        all_ads = all_ads_environment.active_ads
        return [
            ad for ad in all_ads
            if self._ad_meets_filters(ad, filters)
        ]

    def _ad_meets_filters(
        self,
        ad: ObjectBase,
        filters: TargetingFilter
    ):
        """
            Check if the ad meets the user's criteria
        """
        return ad.matches_target(filters)
