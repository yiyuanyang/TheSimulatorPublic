"""
    ============== Advertiser Metrics ========================
    Keeps track of various metrics for a particular advertiser
    such as number of active ads, number of past active ads.
    total impressions, revenue and conversions.
    ==========================================================
"""

from simulator_base.analytics.metric import Metric
from market_simulation.objects.person.advertiser import Advertiser
from market_simulation.config.market_config import get_config
from typing import final


class AdvertiserMetrics(Metric):
    def __init__(self):
        market_config = get_config().get_analytics_config()
        super().__init__("AdvertiserMetrics", market_config['advertiser'])

    def column_names(self) -> list[str]:
        return [
            "country",
            "active_ads",
            "past_ad_cnt",
            "daily_budget",
            "utilized_budget",
        ]

    @final
    def calculate(self):
        adv: Advertiser = self._subject
        country = adv.country
        active_ads = len(adv.active_ads)
        past_ad_cnt = len(adv.inactive_ads)
        daily_budget = adv.total_budget
        utilized_budget = adv.utilized_budget
        return [
            country,
            active_ads,
            past_ad_cnt,
            daily_budget,
            utilized_budget,
        ]
