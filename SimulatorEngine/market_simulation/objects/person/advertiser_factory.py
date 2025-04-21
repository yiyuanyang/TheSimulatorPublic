"""
    ============ Advertiser Factory ================
    Object that accepts a set of initial parameters
    and then generate a ton of different advertisers
    ================================================
"""

from simulator_base.util.printer import printer
from simulator_base.types.types import GenderType
from simulator_base.state.personal_info_state import PersonalInfoState
from market_simulation.objects.analytics.advertiser_metrics import (
    AdvertiserMetrics
)
from ...config.market_config import get_config
from ..person.advertiser import Advertiser
from ..state.advertising_budget_state import AdvertisingBudgetState
from ..state.advertiser_intent_state import AdvertiserIntentState
from ..action.create_ad_action import CreateAdAction
from ..action.adv_adjust_budget_action import AdvAdjustBudgetAction
from ..types.types import (
    AdEventType,
    AdFormat,
    AppSurfaceType,
    BiddingStrategy,
    AdCategory,
)
import random
from scipy import stats
from datetime import timedelta
import numpy as np
from typing import List


class AdvertiserFactory:
    def __init__(self):
        pass

    def apply_create_ad_action(
        self,
        advertiser: Advertiser,
        adv_config: dict
    ):
        budget_config = adv_config['budget_config']
        ad_creation_interval_raw_min = budget_config['ad_creation_interval']
        ad_creation_interval = timedelta(
            minutes=ad_creation_interval_raw_min
        )
        create_ad_action = CreateAdAction(ad_creation_interval)
        advertiser.add_object(create_ad_action)

    def apply_advertising_budget_state(
        self, advertiser: Advertiser,
        adv_config: dict,
    ) -> float:
        """
            Advertiser has a daily budget state that
            gets refreshed every day and consumed every day.
        """
        budget_config = adv_config['budget_config']
        budget = np.random.lognormal(
            mean=budget_config['budget_mu'],
            sigma=budget_config['budget_sigma'],
        )
        advertising_budget_state = AdvertisingBudgetState(budget)
        advertiser.add_object(advertising_budget_state)
        return budget

    def apply_adv_adjust_budget_action(
        self,
        advertiser: Advertiser,
        budget: float,
        adv_config: dict,
    ):
        """
            Advertiser regularly reviews performance of the ad
            (in terms of ROI) and adjust the budget accordingly.
        """
        config = adv_config['budget_config']
        dist = stats.lognorm(
            s=config['budget_sigma'],
            scale=np.exp(config['budget_mu'])
        )
        large_threshold = dist.ppf(config['large_percentile'])
        medium_threshold = dist.ppf(config['medium_percentile'])
        if budget > large_threshold:
            adjust_frequency = timedelta(
                days=config['large_adv_adjust_period']
            )
        elif budget > medium_threshold:
            adjust_frequency = timedelta(
                days=config['medium_adv_adjust_period']
            )
        else:
            adjust_frequency = timedelta(
                days=config['small_adv_adjust_period']
            )
        adv_adjust_budget_action = AdvAdjustBudgetAction(
            adjust_frequency
        )
        advertiser.add_object(adv_adjust_budget_action)

    def apply_advertiser_intent_state(
        self,
        advertiser: Advertiser,
        adv_config: dict,
        env_config: dict,
        user_config: dict,
    ):
        """
            Advertisers would like to show their ads on
            specified surfaces, and to people of certain
            demographics. They also only create ads with
            certain formats and outcomes.
        """
        intent_config = adv_config['intent_config']
        budget_config = adv_config['budget_config']
        outcomes: List[AdEventType] = intent_config[
            'allowed_ad_goal'
        ] if random.random() > intent_config[
            'percent_adv_enabling_awareness_ads'
        ] else [AdEventType.CONVERSIONS]
        # can be only one, or two or three of the formats
        formats: List[AdFormat] = random.sample(
            intent_config['allowed_formats'],
            k=random.randint(1, len(intent_config['allowed_formats'])),
        )
        # surfaces are randomly selected from all possible
        # surfaces
        surfaces: List[AppSurfaceType] = random.sample(
            env_config['enabled_surfaces'],
            k=random.randint(1, len(env_config['enabled_surfaces'])),
        )
        # product price is from a lognormal distribution
        # with mean and sigma from the intent_config
        product_price = np.random.lognormal(
            mean=intent_config['price_mu'],
            sigma=intent_config['price_sigma'],
        )
        # profit margin is from a normal distribution
        profit_margin = np.random.normal(
            loc=intent_config['profit_margin_mean'],
            scale=intent_config['profit_margin_std'],
        )
        # target roi is from a uniform distribution
        target_roi = np.random.normal(
            loc=intent_config['target_roi_mean'],
            scale=intent_config['target_roi_std'],
        )
        # bidding strategy could be MAX_OUTCOME_WITHOUT_COST_CAP
        # MAX_OUTCOME_WITH_COST_CAP or COST_CAP
        bidding_strategy = random.choice(
            intent_config['allowed_bidding_strategies']
        )
        # if bidding strategy is cost cap or max outcome with cost cap
        # then cost cap is from a uniform distribution from 50% of
        # product profit to 100% of product profit
        profit = product_price * profit_margin
        cost_cap = random.uniform(
            profit * 0.5,
            profit,
        ) if bidding_strategy in [
            BiddingStrategy.COST_CAP,
            BiddingStrategy.MAX_OUTCOME_WITH_COST_CAP,
        ] else None
        # category is randomly selected from all possible
        # categories
        category = random.choice(list(AdCategory))
        # country is same as this factory

        all_countries: dict[str, float] = adv_config[
            'per_country_advertiser_proportion'
        ]
        adv_country = random.choices(
            list(all_countries.keys()),
            weights=list(all_countries.values()),
            k=1
        )[0]
        personal_info_state = PersonalInfoState(
            name=None,
            birth_day=None,
            country=adv_country,
        )
        # min age is from a uniform distribution
        # from 18 to 30
        min_age = random.randint(
            user_config['min_age'],
            intent_config['age_threshold']
        )
        # max age is from a uniform distribution
        # from 40 to 65
        max_age = random.randint(
            intent_config['age_threshold'],
            user_config['max_age']
        )
        # target gender is randomly selected from all possible
        genders: List[GenderType] = random.sample(
            list(GenderType),
            k=random.randint(1, len(GenderType)),
        )
        # max ads per day is from a uniform distribution
        # from 1 to 10
        max_ads_per_day = random.randint(1, 10)
        # max_budget_percent_per_ad is from a uniform distribution
        # from 0.1 to 0.5 if max ads per day is higher than 1
        if max_ads_per_day == 1:
            max_budget_percent_per_ad = 1
            min_budget_percent_per_ad = 1
        else:
            max_budget_percent_per_ad = random.uniform(0.1, 0.5)
            min_budget_percent_per_ad = random.uniform(
                0.1,
                max_budget_percent_per_ad,
            )
        # max duration is from a uniform distribution
        # from 1 to 30 days
        max_duration = timedelta(days=random.randint(1, 30))
        # min duration is from a uniform distribution
        # from 1 to max duration
        min_duration = timedelta(
            days=random.randint(1, max_duration.days),
        )
        performance_incremental = budget_config['performance_incremental']
        intent_state = AdvertiserIntentState(
            outcomes=outcomes,
            formats=formats,
            surfaces=surfaces,
            bidding_strategy=bidding_strategy,
            cost_cap=cost_cap,
            category=category,
            target_country=adv_country,
            target_min_age=min_age,
            target_max_age=max_age,
            target_gender=genders,
            max_ads_per_day=max_ads_per_day,
            max_budget_percent_per_ad=max_budget_percent_per_ad,
            min_budget_percent_per_ad=min_budget_percent_per_ad,
            max_duration_per_ad=max_duration,
            min_duration_per_ad=min_duration,
            product_price=product_price,
            profit_margin=profit_margin,
            target_roi=target_roi,
            budget_adjustment_performance_incremental=performance_incremental
        )
        advertiser.add_object(personal_info_state)
        advertiser.add_object(intent_state)

    def create_advertiser(
        self,
        adv_config: dict,
        env_config: dict,
        user_config: dict,
    ) -> Advertiser:
        advertiser = Advertiser()
        self.apply_create_ad_action(advertiser, adv_config)
        budget = self.apply_advertising_budget_state(
            advertiser,
            adv_config
        )
        self.apply_adv_adjust_budget_action(
            advertiser,
            budget,
            adv_config
        )
        self.apply_advertiser_intent_state(
            advertiser,
            adv_config,
            env_config,
            user_config
        )
        adv_metrics = AdvertiserMetrics()
        adv_metrics.attach(advertiser)
        return advertiser

    def create_advertisers(self, start: bool = True) -> List[Advertiser]:
        adv_config = get_config().get_advertiser_config()
        env_config = get_config().get_environment_config()
        user_config = get_config().get_user_config()
        advertisers = []
        advertiser_cnt = adv_config['advertiser_count']
        for _ in range(advertiser_cnt):
            advertisers.append(
                self.create_advertiser(
                    adv_config,
                    env_config,
                    user_config
                )
            )
        if start:
            for advertiser in advertisers:
                advertiser.start()
        printer(f"Loaded {len(advertisers)} advertisers", "LOG")
        return advertisers
