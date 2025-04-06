"""
    Contains various constants and equations for the simulation
"""

from simulator_base.types.types import GenderType
from simulator_base.agent.agent import Agent
from ...config.market_config import get_config
from market_simulation.objects.types.types import (
    AdEventType,
    AdFormat,
    AppSurfaceType,
)
import math

"""
    ================== Ranking Section =====================
"""


def get_age_factor(user: Agent) -> float:
    """
        Calculate the age factor
        on event probability.

        Assuming 35 is when spending
        power is at peak. The factor
        is calculated that at 35
        the factor is 1.0 and when
        age gets to 18 or 65, the
        factor becomes 0.5
    """
    user_config = get_config().get_user_config()
    intent_config = user_config['intent_config']
    peak_age = intent_config['peak_age']
    age = user.age
    if age > peak_age:
        return max(math.exp(-0.01 * (age - peak_age) ** 1.2), 0)
    else:
        return max(math.exp(-0.01 * (peak_age - age) ** 1.5), 0)


def get_gender_factor(user: Agent) -> float:
    """
        Generally female are slightly more
        likely to convert than male.
    """
    user_config = get_config().get_user_config()
    intent_config = user_config['intent_config']
    gender_factor = intent_config['gender_factor']
    if user.gender == GenderType.FEMALE:
        return 1
    else:
        return gender_factor * 1.0


def get_income_savings_factor(user: Agent, ad: Agent):
    user_config = get_config().get_user_config()
    intent_config = user_config['intent_config']
    no_decay_ratio = intent_config['no_decay_income_price_ratio']
    user_disposable_income_state = user.get_state("DisposableIncomeState")
    total_savings = user_disposable_income_state.disposable_income
    advertiser: Agent = ad.owner
    product_price = advertiser.get_state("AdvertiserIntentState").product_price
    # Only 20% of savings is considered available for spending.
    effective_income = 0.25 * total_savings

    # Compute the ratio of effective income to product price.
    ratio = effective_income / product_price
    # If the effective income is less
    # than the product price, return 0 probability.
    if ratio < 1:
        return 0.0

    score = math.log10(ratio / no_decay_ratio * 100) / 2
    return min(max(score, 0), 1)


def get_ad_goal_factor(ad: Agent) -> float:
    """
        Different goals have different conversion
        rate
    """
    user_config = get_config().get_user_config()
    intent_config = user_config['intent_config']
    event_probability_baseline = intent_config['event_probability_baseline']
    ad_goal = ad.ad_goal

    if ad_goal == AdEventType.CONVERSIONS:
        # Conversions are rare
        return event_probability_baseline['conversions']
    elif ad_goal == AdEventType.IMPRESSIONS:
        # Impression will 100% happen if shown
        # there should be no probability
        return 1
    else:
        raise Exception("Invalid ad goal")


def get_ad_format_surface_factor(
    ad: Agent,
    surface: AppSurfaceType
):
    """
        Different formats works differently
        on each surface.

        single image is best on content feed
        single video is best on video feed
        carousel is best on commerce
    """
    ad_spec_state = ad.get_state("AdSpecState")
    format = ad_spec_state.ad_format
    if format == AdFormat.SINGLE_IMAGE:
        if surface == AppSurfaceType.CONTENT_FEED:
            return 1
        elif surface == AppSurfaceType.VIDEO_FEED:
            return 0.5
        elif surface == AppSurfaceType.COMMERCE:
            return 0.75
    elif format == AdFormat.SINGLE_VIDEO:
        if surface == AppSurfaceType.CONTENT_FEED:
            return 0.75
        elif surface == AppSurfaceType.VIDEO_FEED:
            return 1
        elif surface == AppSurfaceType.COMMERCE:
            return 0.5
    elif format == AdFormat.CAROUSEL:
        if surface == AppSurfaceType.CONTENT_FEED:
            return 0.75
        elif surface == AppSurfaceType.VIDEO_FEED:
            return 0.5
        elif surface == AppSurfaceType.COMMERCE:
            return 1
    else:
        raise Exception("Invalid ad format")
