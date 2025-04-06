"""
    =========== Surface Metrics =============================
    Keeps track of various metrics for a particular
    surface, such as daily active users, revenue, value,
    conversion rate, Cost Per Action, Cost Per Thousand (CPM)
    =========================================================
"""

from simulator_base.orchestrator.orchestrator import Orchestrator
from simulator_base.analytics.metric import Metric
from market_simulation.config.market_config import get_config
from market_simulation.objects.types.types import (
    AdEventFields,
    AdEventType,
)
from market_simulation.objects.environment.surface_environment import (
    SurfaceEnvironment,
)
from typing import final


class SurfaceMetrics(Metric):
    def __init__(self):
        market_config = get_config().get_analytics_config()
        surface_metric_config = market_config['surface']
        super().__init__("SurfaceMetrics", surface_metric_config)

    @final
    def column_names(self) -> list[str]:
        return [
            "unique_users",
            "total_value",
            "total_revenue",
            "total_conversions",
            "total_impressions",
            "cpm",
            "cpa",
            "calibration",
            "cvr",
            "value_calibration"
        ]

    @final
    def calculate(self):
        # Removed unused variable assignment
        current_time = Orchestrator.get_current_time(self._subject)
        surface_environment: SurfaceEnvironment = self._subject
        all_visits = surface_environment.visits
        total_conversions = 0
        total_impressions = 0
        predicted_conversions = 0
        predicted_value = 0
        total_value = 0
        total_revenue = 0
        users = set()

        cutoff_time = current_time - self._aggregation_window
        # from back to front
        start_index = len(all_visits) - 1
        while start_index >= 0:
            organic_event = all_visits[start_index]
            if organic_event[AdEventFields.EVENT_TIME] >= cutoff_time:
                users.add(organic_event[AdEventFields.USER].id)
            start_index -= 1
        start_index = len(surface_environment.impressions) - 1
        while start_index >= 0:
            ad_event = surface_environment.impressions[start_index]
            if ad_event[AdEventFields.EVENT_TIME] >= cutoff_time:
                total_impressions += 1
                total_revenue += ad_event[AdEventFields.COST]
                if (
                    ad_event[AdEventFields.AD].ad_goal
                    == AdEventType.IMPRESSIONS
                ):
                    total_value += ad_event[AdEventFields.BID]
                    predicted_value += ad_event[AdEventFields.BID]
                else:
                    predicted_conversions += ad_event[
                        AdEventFields.PREDICTED_PROBABILITY
                    ]
                    predicted_value += ad_event[AdEventFields.PACED_BID] \
                        * ad_event[AdEventFields.PREDICTED_PROBABILITY]
            else:
                break
            start_index -= 1
        start_index = len(surface_environment.outcomes) - 1
        while start_index >= 0:
            ad_event = surface_environment.outcomes[start_index]
            if ad_event[AdEventFields.EVENT_TIME] >= cutoff_time:
                total_value += ad_event[AdEventFields.PACED_BID]
                total_conversions += 1
            else:
                break
            start_index -= 1

        return [
            len(users),
            total_value,
            total_revenue,
            total_conversions,
            total_impressions,
            total_revenue / total_impressions * 1000
            if total_impressions > 0 else 0,  # CPM
            total_revenue / total_conversions
            if total_conversions > 0 else 0,  # CPA
            predicted_conversions / total_conversions
            if total_conversions > 0 else 0,  # Calibration
            total_conversions / total_impressions
            if total_impressions > 0 else 0,  # CVR
            predicted_value / total_value
            if total_value > 0 else 0  # Value Calibration
        ]
