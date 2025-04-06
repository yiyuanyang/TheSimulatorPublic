"""
    Object Type, Object Subtype and Class Mapping
    given a string return the Class so that
    it can be referenced for object creation
"""

from simulator_base.types.types import BaseObjectType
from simulator_base.action.action import Action
from simulator_base.state.state import State
from simulator_base.effect.effect_base import EffectBase
from simulator_base.agent.agent import Agent
from simulator_base.environment.environment import Environment
from simulator_base.event.event import Event
from simulator_base.analytics.metric import Metric
from simulator_base.state.personal_info_state import PersonalInfoState
from market_simulation.objects.types.types import ObjectSubType
from market_simulation.objects.action.adv_adjust_budget_action import (
    AdvAdjustBudgetAction,
)
from market_simulation.objects.action.stop_ad_action import StopAdAction
from market_simulation.objects.action.browse_app_action import BrowseAppAction
from market_simulation.objects.state.app_behavior_state import AppBehaviorState
from market_simulation.objects.state.disposable_income_state import (
    DisposableIncomeState,
)
from market_simulation.objects.state.purchases_state import PurchasesState
from market_simulation.objects.state.user_ad_conversion_history_state import (
    UserAdConversionHistoryState
)
from market_simulation.objects.state.user_ad_view_history_state import (
    UserAdViewHistoryState,
)
from market_simulation.objects.state.user_intent_state import UserIntentState
from market_simulation.objects.state.advertiser_intent_state import (
    AdvertiserIntentState,
)
from market_simulation.objects.state.advertising_budget_state import (
    AdvertisingBudgetState,
)
from market_simulation.objects.state.ad_budget_state import AdBudgetState
from market_simulation.objects.state.ad_spec_state import AdSpecState
from market_simulation.objects.state.ad_outcome_state import AdOutcomeState
from market_simulation.objects.state.all_active_ads_state import (
    AllActiveAdsState
)
from market_simulation.objects.effect.over_calibration.\
    over_calibration_effect import OverCalibrationEffect
from market_simulation.objects.effect.surface_down.surface_down_effect import (
    SurfaceDownEffect
)
from market_simulation.objects.effect.income_effect import IncomeEffect
from market_simulation.objects.ads.ad import Ad
from market_simulation.objects.person.advertiser import Advertiser
from market_simulation.objects.person.user import User
from market_simulation.objects.analytics.ad_metrics import AdMetrics
from market_simulation.objects.analytics.surface_metrics import SurfaceMetrics
from market_simulation.objects.environment.surface_environment import (
    SurfaceEnvironment,
)
from market_simulation.objects.auction.all_ads_environment import (
    AllAdsEnvironment,
)
from market_simulation.objects.auction.auction_environment import (
    AuctionEnvironment,
)
from market_simulation.objects.auction.targeting_environment import (
    TargetingEnvironment,
)
from market_simulation.objects.auction.ranking_environment import (
    RankingEnvironment,
)


def get_mapped_obj_cls(
    object_type: BaseObjectType,
    object_subtype: ObjectSubType = None
):
    if object_subtype is None:
        match object_type:
            case BaseObjectType.ACTION:
                return Action
            case BaseObjectType.STATE:
                return State
            case BaseObjectType.EFFECT:
                return EffectBase
            case BaseObjectType.AGENT:
                return Agent
            case BaseObjectType.ENVIRONMENT:
                return Environment
            case BaseObjectType.EVENT:
                return Event
            case BaseObjectType.METRIC:
                return Metric
    else:
        match object_subtype:
            case ObjectSubType.ADV_ADJUST_BUDGET_ACTION:
                return AdvAdjustBudgetAction
            case ObjectSubType.CREATE_AD_ACTION:
                return CreateAdAction
            case ObjectSubType.PROGRESS_AD_ACTION:
                return ProgressAdAction
            case ObjectSubType.STOP_AD_ACTION:
                return StopAdAction
            case ObjectSubType.BROWSE_APP_ACTION:
                return BrowseAppAction
            case ObjectSubType.APP_BEHAVIOR_STATE:
                return AppBehaviorState
            case ObjectSubType.DISPOSABLE_INCOME_STATE:
                return DisposableIncomeState
            case ObjectSubType.PURCHASES_STATE:
                return PurchasesState
            case ObjectSubType.USER_AD_CONVERSION_HISTORY_STATE:
                return UserAdConversionHistoryState
            case ObjectSubType.USER_AD_VIEW_HISTORY_STATE:
                return UserAdViewHistoryState
            case ObjectSubType.PERSONAL_INFO_STATE:
                return PersonalInfoState
            case ObjectSubType.USER_INTENT_STATE:
                return UserIntentState
            case ObjectSubType.ADVERTISER_INTENT_STATE:
                return AdvertiserIntentState
            case ObjectSubType.ADVERTISING_BUDGET_STATE:
                return AdvertisingBudgetState
            case ObjectSubType.AD_BUDGET_STATE:
                return AdBudgetState
            case ObjectSubType.AD_SPEC_STATE:
                return AdSpecState
            case ObjectSubType.AD_OUTCOME_STATE:
                return AdOutcomeState
            case ObjectSubType.ALL_ACTIVE_ADS_STATE:
                return AllActiveAdsState
            case ObjectSubType.OVER_CALIBRATION_EFFECT:
                return OverCalibrationEffect
            case ObjectSubType.SURFACE_DOWN_EFFECT:
                return SurfaceDownEffect
            case ObjectSubType.INCOME_EFFECT:
                return IncomeEffect
            case ObjectSubType.AD:
                return Ad
            case ObjectSubType.ADVERTISER:
                return Advertiser
            case ObjectSubType.USER:
                return User
            case ObjectSubType.AD_METRICS:
                return AdMetrics
            case ObjectSubType.SURFACE_METRICS:
                return SurfaceMetrics
            case ObjectSubType.SURFACE_ENVIRONMENT:
                return SurfaceEnvironment
            case ObjectSubType.ALL_ADS_ENVIRONMENT:
                return AllAdsEnvironment
            case ObjectSubType.AUCTION_ENVIRONMENT:
                return AuctionEnvironment
            case ObjectSubType.TARGETING_ENVIRONMENT:
                return TargetingEnvironment
            case ObjectSubType.RANKING_ENVIRONMENT:
                return RankingEnvironment
