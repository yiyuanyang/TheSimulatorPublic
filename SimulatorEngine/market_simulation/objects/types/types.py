"""
    This file contains the definition of the types used in the simulation.
"""

from enum import StrEnum
from datetime import datetime
from typing import Any


class TargetingFilterFields(StrEnum):
    COUNTRY = "country"
    AGE = "age"
    GENDER = "gender"
    SURFACE = "surface"


TargetingFilter = dict[TargetingFilterFields, Any]


class AdCategory(StrEnum):
    TECHNOLOGY = "technology"
    FASHION = "fashion"
    ENTERTAINMENT = "entertainment"
    HOME_LIFESTYLE = "home_lifestyle"
    FOOD_DRINK = "food_drink"
    HEALTH_FITNESS = "health_fitness"
    TRAVEL_LEISURE = "travel_leisure"
    FINANCE = "finance"
    AUTOMOTIVE = "automotive"
    EDUCATION = "education"
    OTHER = "other"


IntentValues = dict[AdCategory, float]
PurchaseHistory = dict[AdCategory, list[datetime]]


class AppBehaviorFieldState(StrEnum):
    SESSION_ACTIVE_PROBABILITY = "session_active_probability"
    SESSION_DURATION_MEAN = "session_duration_mean"
    SESSION_DURATION_STDEV = "session_duration_stdev"
    PER_SURFACE_PROBABILITY = "per_surface_probability"


class AppSurfaceType(StrEnum):
    CONTENT_FEED = "content_feed"
    VIDEO_FEED = "video_feed"
    COMMERCE = "commerce"


class AdFormat(StrEnum):
    SINGLE_IMAGE = "single_image"
    SINGLE_VIDEO = "single_video"
    CAROUSEL = "carousel"


class AdEventType(StrEnum):
    IMPRESSIONS = "impressions"  # Reach
    CONVERSIONS = "conversions"  # Purchase


class BiddingStrategy(StrEnum):
    MAX_OUTCOME_WITHOUT_COST_CAP = "max_outcome_without_cost_cap"
    MAX_OUTCOME_WITH_COST_CAP = "max_outcome_with_cost_cap"
    COST_CAP = "cost_cap"


class AuctionType(StrEnum):
    GENERALIZED_FIRST_PRICE = "generalized_first_price"
    GENERALIZED_SECOND_PRICE = "generalized_second_price"
    VICKREY_CLARKE_GROVES = "vickrey_clarke_groves"


class OrganicEventType(StrEnum):
    SURFACE_ENTER = "surface_enter"


class OrganicEventFields(StrEnum):
    USER = "user"
    EVENT_TYPE = "event_type"
    SURFACE = "surface"
    EVENT_TIME = "event_time"


OrganicEvent = dict[OrganicEventFields, any]
OrganicEventList = list[OrganicEvent]


class AdEventFields(StrEnum):
    USER = "user"
    AD = "ad"
    EVENT_TYPE = "event_type"
    SURFACE = "surface"
    BID = "bid"  # Auction bid amount for impression
    PRICE = "price"  # Price of the slot
    COST = "cost"  # Amount paid by advertiser
    PACED_BID = "paced_bid"  # Paced Bid Amount For Conversion
    TRUE_PROBABILITY = "true_probability"
    PREDICTED_PROBABILITY = "predicted_probability"
    EVENT_TIME = "event_time"


AdEvent = dict[AdEventFields, any]

AdEventList = list[AdEvent]


class AuctionResultFields(StrEnum):
    AD = "ad"
    BID = "bid"
    PRICE = "price"
    PACED_BID = "paced_bid"
    TRUE_PROBABILITY = "true_probability"
    PREDICTED_PROBABILITY = "predicted_probability"


AuctionResults = dict[AuctionResultFields, any]


class ObjectSubType(StrEnum):
    # Action - Advertiser
    ADV_ADJUST_BUDGET_ACTION = "AdvAdjustBudgetAction"
    CREATE_AD_ACTION = "CreateAdAction"
    # Action - Ad
    STOP_AD_ACTION = "StopAdAction"
    # Action - User
    BROWSE_APP_ACTION = "BrowseAppAction"
    # State - User
    APP_BEHAVIOR_STATE = "AppBehaviorState"
    DISPOSABLE_INCOME_STATE = "DisposableIncomeState"
    PURCHASES_STATE = "PurchasesState"
    USER_AD_CONVERSION_HISTORY_STATE = "UserAdConversionHistoryState"
    USER_AD_VIEW_HISTORY_STATE = "UserAdViewHistoryState"
    PERSONAL_INFO_STATE = "PersonalInfoState"
    USER_INTENT_STATE = "UserIntentState"
    # State - Advertiser
    ADVERTISER_INTENT_STATE = "AdvertiserIntentState"
    ADVERTISING_BUDGET_STATE = "AdvertisingBudgetState"
    # State - Ad
    AD_BUDGET_STATE = "AdBudgetState"
    AD_SPEC_STATE = "AdSpecState"
    AD_OUTCOME_STATE = "AdOutcomeState"
    # State - Env
    ALL_ACTIVE_ADS_STATE = "AllActiveAdsState"
    # Effect - env
    OVER_CALIBRATION_EFFECT = "OverCalibrationEffect"
    SURFACE_DOWN_EFFECT = "SurfaceDownEffect"
    # Effect - User
    INCOME_EFFECT = "IncomeEffect"
    # Agent - Ad
    AD = "Ad"
    # Agent - Advertiser
    ADVERTISER = "Advertiser"
    # Agent - User
    USER = "User"
    # Metrics - Ad
    AD_METRICS = "AdMetrics"
    # Metrics - environment
    SURFACE_METRICS = "SurfaceMetrics"
    # Environment - Surface
    SURFACE_ENVIRONMENT = "SurfaceEnvironment"
    ALL_ADS_ENVIRONMENT = "AllAdsEnvironment"
    AUCTION_ENVIRONMENT = "AuctionEnvironment"
    TARGETING_ENVIRONMENT = "TargetingEnvironment"
    RANKING_ENVIRONMENT = "RankingEnvironment"
