"""
    ============== Ranking Environment ====================
    Ranking Environment, given a user and ad pair,
    would simulate a "true" probability which would later
    be used to simulate whether or not the event would
    occur or not, and at the same, based on a preset
    noise factor, introduce another "predicted" probability
    that would be used in auction to rank the ads.

    The probability is calculated as an function of:

    1. User's age, country and gender
    2. User's category interest and surface interest
    3. The surface the ad is being displayed on
    4. Ad's category.
    5. Ads goal (conversion / impression)
    =======================================================
"""

from simulator_base.environment.environment import Environment
from simulator_base.agent.agent import Agent
from simulator_base.orchestrator.orchestrator import get_orchestrator
from ...config.market_config import get_config
from .targeting_environment import TargetingEnvironment
from .ranking import (
    get_age_factor,
    get_gender_factor,
    get_income_savings_factor,
    get_ad_goal_factor,
    get_ad_format_surface_factor,
)
from ..types.types import (
    AdEventType,
    AppSurfaceType,
    TargetingFilterFields,
    TargetingFilter
)
import numpy as np


class RankingEnvironment(Environment):
    def __init__(self):
        super().__init__("RankingEnvironment")

    def fetch_and_rank_all_ads(
        self,
        user: Agent,
        surface: AppSurfaceType
    ) -> list[tuple[Agent, tuple[float, float]]]:
        """
            return a list of ad candidates with their
            respective "true" and "predicted" probability
        """
        targeting_filter: TargetingFilter = {
            TargetingFilterFields.COUNTRY: user.country,
            TargetingFilterFields.AGE: user.age,
            TargetingFilterFields.GENDER: user.gender,
            TargetingFilterFields.SURFACE: surface,
        }
        targeting_environment: TargetingEnvironment = get_orchestrator()\
            .get_environment('TargetingEnvironment')
        all_available_ads = targeting_environment.get_ads_with_filters(
            targeting_filter
        )
        return [
            (ad, self.get_probability(user, ad, surface))
            for ad in all_available_ads
        ]

    def get_probability(
        self,
        user: Agent,
        ad: Agent,
        surface: AppSurfaceType
    ) -> tuple[float, float]:
        """
            Get the "true" and "predicted" probability
            of the desired ad event given the user and ad pair.

            This is essentially the process of letting models
            making a prediction on the ad / organic pair.
        """
        ad_goal = ad.ad_goal
        if ad_goal == AdEventType.IMPRESSIONS:
            # if impression is delivered it will 100% be seen
            return 1, 1
        true_probability = self._get_true_probability(user, ad, surface)
        predicted_probability = self._get_predicted_probability(
            true_probability
        )
        return true_probability, predicted_probability

    def _get_predicted_probability(
        self,
        true_probability: float,
    ) -> float:
        """
            Apply gaussian noise to the true probability
            to simulate the predicted probability where
            model can be inaccurate
        """
        delivery_config = get_config().get_delivery_config()
        model_config = delivery_config['model_config']
        model_noise_factor = model_config['model_noise_factor']
        noise_std = true_probability * model_noise_factor
        return max(min(true_probability + np.random.normal(
            0, noise_std
        ), 1), 0)

    def _get_true_probability(
        self,
        user: Agent,
        ad: Agent,
        surface: AppSurfaceType
    ) -> float:
        """
            Simulates the "true" probability of desired
            ad event given the user and ad pair based on
            a variety of factors.
        """
        if ad.ad_goal == AdEventType.IMPRESSIONS:
            return 1
        ad_spec_state = ad.get_state('AdSpecState')
        ad_category = ad_spec_state.ad_category
        category_intent_factor = user.get_state('UserIntentState').get_intent(
            ad_category
        )
        user_ad_view_history_state = user.get_state(
            'UserAdViewHistoryState'
        )
        age_factor = get_age_factor(user)
        gender_factor = get_gender_factor(user)
        income_savings_factor = get_income_savings_factor(user, ad)
        ad_goal_factor = get_ad_goal_factor(ad)
        format_factor = get_ad_format_surface_factor(ad, surface)
        ad_view_history_factor = (
            user_ad_view_history_state.get_ad_view_history_factor(ad)
        )
        calibration_factor = 1
        env_over_calibration_effect = self.get_effect('OverCalibrationEffect')
        ad_over_calibration_effect = ad.get_effect('OverCalibrationEffect')
        if env_over_calibration_effect \
           and env_over_calibration_effect.can_apply():
            calibration_factor = (
                calibration_factor +
                env_over_calibration_effect.over_calibration
            )
        if ad_over_calibration_effect \
           and ad_over_calibration_effect.can_apply():
            calibration_factor = (
                calibration_factor +
                ad_over_calibration_effect.over_calibration
            )
        return (
            category_intent_factor
            * age_factor
            * gender_factor
            * income_savings_factor
            * ad_goal_factor
            * format_factor
            * ad_view_history_factor
            * calibration_factor
        )
