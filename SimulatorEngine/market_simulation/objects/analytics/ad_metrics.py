"""
    =============== Ad Metrics ========================
    Keeps track of various metrics for a particular
    ad. Such as reach, impressions, clicks, conversions,
    value, CPM, CVR, CPA, and calibration.
    ==================================================
"""

from simulator_base.orchestrator.orchestrator import Orchestrator
from simulator_base.analytics.metric import Metric
from market_simulation.config.market_config import get_config
from market_simulation.objects.ads.ad import Ad
from market_simulation.objects.state.ad_budget_state import AdBudgetState
from market_simulation.objects.state.ad_spec_state import AdSpecState
from market_simulation.objects.types.types import (
    AdEventFields,
    AdEventType,
)
from typing import final


class AdMetrics(Metric):
    def __init__(self):
        market_config = get_config().get_analytics_config()
        super().__init__("AdMetrics", market_config['ad'])

    @final
    def column_names(self) -> list[str]:
        return [
            "country",
            "reach",
            "total_revenue",
            "remaining_daily_budget",
            "remaining_total_budget",
            "remaining_duration",
            "roas",
            "roi",
            "daily_budget",
            "total_conversions",
            "total_impressions",
            "total_value",
            "over_delivery",
            "cpm",
            "cpa",
            "calibration",
            "cvr",
            "value_calibration",
            "avg_paced_bid",
            "bidding_strategy",
            "target_surfaces",
            "ad_format",
            "ad_goal",
            "ad_category",
            "target_gender",
            "target_age_min",
            "target_age_max",
        ]

    @final
    def calculate(self):
        current_time = Orchestrator.get_current_time(self._subject)
        cutoff_time = current_time - self._aggregation_window
        ad: Ad = self._subject
        if ad.ended:
            self.destroy()
        ad_budget_state: AdBudgetState = ad.get_state("AdBudgetState")
        ad_spec_state: AdSpecState = ad.get_state("AdSpecState")
        remaining_total_budget = ad_budget_state.remaining_budget
        remaining_duration = ad_budget_state.remaining_duration
        all_impressions = ad.impressions
        all_conversions = ad.conversions

        reached_users = set()
        total_revenue = 0
        remaining_daily_budget = ad_budget_state.remaining_daily_budget
        daily_budget = ad_budget_state.daily_budget
        total_conversions = 0
        total_impressions = 0
        total_value = 0
        over_delivery = 0
        predicted_conversions = 0
        predicted_value = 0
        paced_bid_total = 0

        # from back to front
        start_index = len(all_impressions) - 1
        while start_index >= 0:
            impression = all_impressions[start_index]
            if impression[AdEventFields.EVENT_TIME] < cutoff_time:
                break
            start_index -= 1
            reached_users.add(impression[AdEventFields.USER].id)
            total_impressions += 1
            total_revenue += impression[AdEventFields.COST]
            over_delivery += impression[AdEventFields.PRICE] \
                - impression[AdEventFields.COST]
            paced_bid_total += impression[AdEventFields.PACED_BID]
            if impression[AdEventFields.AD].ad_goal == AdEventType.CONVERSIONS:
                predicted_conversions += impression[
                    AdEventFields.PREDICTED_PROBABILITY
                ]
                predicted_value += impression[
                    AdEventFields.PREDICTED_PROBABILITY
                ] * \
                    impression[AdEventFields.PACED_BID]
            else:
                total_value += impression[AdEventFields.PACED_BID]
                predicted_value += impression[AdEventFields.BID]
        start_index = len(all_conversions) - 1
        while start_index >= 0:
            conversion = all_conversions[start_index]
            if conversion[AdEventFields.EVENT_TIME] < cutoff_time:
                break
            start_index -= 1
            total_conversions += 1
            total_value += conversion[AdEventFields.PACED_BID]

        cpm = total_revenue / total_impressions * 1000 \
            if total_impressions > 0 else 0
        cpa = total_revenue / total_conversions \
            if total_conversions > 0 else 0
        cvr = total_conversions / total_impressions \
            if total_impressions > 0 else 0
        calibration = (
            predicted_conversions / total_conversions
            if total_conversions > 0
            else 0
        )
        value_calibration = predicted_value / total_value \
            if total_value > 0 else 0
        reach = len(reached_users)
        avg_paced_bid = paced_bid_total / total_impressions \
            if total_impressions > 0 else 0

        if ad.ad_goal == AdEventType.CONVERSIONS and total_revenue > 0:
            sales = total_conversions * ad.product_price * ad.profit_margin
            roas = sales / total_revenue
            profit = sales - total_revenue
            roi = profit / total_revenue
        else:
            roas = None
            roi = None

        return [
            ad.country,
            reach,
            total_revenue,
            remaining_daily_budget,
            remaining_total_budget,
            remaining_duration,
            roas,
            roi,
            daily_budget,
            total_conversions,
            total_impressions,
            total_value,
            over_delivery,
            cpm,
            cpa,
            calibration,
            cvr,
            value_calibration,
            avg_paced_bid,
            ad_budget_state.bidding_strategy,
            ad_spec_state.surfaces,
            ad_spec_state.ad_format,
            ad.ad_goal,
            ad_spec_state.ad_category,
            ad_spec_state.gender,
            ad_spec_state.min_age,
            ad_spec_state.max_age
        ]
