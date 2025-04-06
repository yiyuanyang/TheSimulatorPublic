"""
    =========== User Factory ============
    Object that accepts a set of initial
    parameters and then generate a ton of
    different users
    =====================================
"""

from typing import final
from simulator_base.util.printer import printer
from simulator_base.state.personal_info_state import PersonalInfoState
from simulator_base.types.types import GenderType
from simulator_base.orchestrator.orchestrator import Orchestrator
from .user import User
from ..state.user_intent_state import UserIntentState
from ..state.user_intent_state import get_user_intents_baseline
from ..state.app_behavior_state import AppBehaviorState
from ..state.disposable_income_state import DisposableIncomeState
from ..state.purchases_state import PurchasesState
from ..state.user_ad_view_history_state import UserAdViewHistoryState
from ..state.user_ad_conversion_history_state import (
    UserAdConversionHistoryState,
)
from ...config.market_config import get_config
from ..types.types import AppBehaviorFieldState
from ..effect.income_effect import IncomeEffect
from ..action.browse_app_action import BrowseAppAction
from datetime import datetime, timedelta
from typing import List
import numpy as np
import random


@final
class UserFactory:
    def __init__(self):
        pass

    def _apply_personal_info(
        self,
        user: User,
        user_config: dict
    ):
        gender = random.choice(
            list(GenderType)
        )
        age = random.randint(
            user_config['min_age'],
            user_config['max_age']
        )
        # key value pair of country vs its probability
        per_country_probability: dict[str, float] = user_config[
            'per_country_user_proportion'
        ]
        user_country = random.choices(
            list(per_country_probability.keys()),
            weights=list(per_country_probability.values()),
            k=1
        )[0]
        current_time = Orchestrator.get_global_time()
        # generate a birth day that is in the past
        # consider the possibility between year - age, and year - age - 1
        # based on selected birth month
        birth_month = random.randint(1, 12)
        if birth_month > current_time.month:
            birth_year = current_time.year - age - 1
        else:
            birth_year = current_time.year - age
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            birth_day = random.randint(1, 31)
        elif birth_month in [4, 6, 9, 11]:
            birth_day = random.randint(1, 30)
        else:
            if (
                birth_year % 4 == 0
                and (birth_year % 100 != 0 or birth_year % 400 == 0)
            ):
                # leap year
                birth_day = random.randint(1, 29)
            else:
                birth_day = random.randint(1, 28)
        birth_day = datetime(
            birth_year,
            birth_month,
            birth_day,
        )
        personal_info = PersonalInfoState(
            gender=gender,
            birth_day=birth_day,
            country=user_country,
        )
        user.add_object(personal_info)

    def _apply_tracking_states(
        self,
        user: User,
        user_config: dict
    ):
        simulation_interval = timedelta(
            seconds=user_config['user_simulation_interval']
        )
        view_history_days = user_config['ad_view_history_days']
        purchase_history_days = user_config['ad_purchase_history_days']
        user.add_object(UserAdViewHistoryState(timedelta(
            days=view_history_days
        )))
        user.add_object(UserAdConversionHistoryState(timedelta(
            days=purchase_history_days
        )))
        user.add_object(PurchasesState())
        user.add_object(DisposableIncomeState(0))
        user.add_object(BrowseAppAction(simulation_interval))

    def _apply_income_effect(
        self,
        user: User,
        user_config: dict
    ):
        income_config = user_config['income_config']
        monthly_income = np.random.lognormal(
            mean=income_config['income_mu'],
            sigma=income_config['income_sigma'],
        )
        processed_income = max(monthly_income, 0)
        income_effect = IncomeEffect(processed_income)
        user.add_object(income_effect)

    def _apply_user_intent(self, user: User, user_config: dict):
        intent_config = user_config['intent_config']
        intent_baseline = get_user_intents_baseline()
        for intent, value in intent_baseline.items():
            intent_value = random.gauss(
                intent_config['intent_mean'],
                intent_config['intent_std']
            )
            intent_value = max(min(intent_value, 1), 0)
            intent_baseline[intent] = intent_value
        user_intent_state = UserIntentState(intent_baseline)
        user.add_object(user_intent_state)

    def _apply_app_behavior(
        self,
        user: User,
        user_config: dict,
        env_config: dict
    ):
        browsing_config = user_config['browsing_config']
        daily_active_cnt = random.gauss(
            browsing_config['daily_active_cnt_mean'],
            browsing_config['daily_active_cnt_std']
        )
        twenty_four_hours = timedelta(hours=24)
        user_simulation_interval_raw_sec = user_config[
            'user_simulation_interval'
        ]
        user_simulation_interval = timedelta(
            seconds=user_simulation_interval_raw_sec
        )
        consideration_cnt = twenty_four_hours / user_simulation_interval
        active_probability = daily_active_cnt / consideration_cnt

        session_length = random.gauss(
            browsing_config['session_length_mean'],
            browsing_config['session_length_std']
        )
        session_length = max(session_length, 0)
        # per surface probability should add up to 1
        all_surfaces = env_config['enabled_surfaces']
        per_surface_probability = {
            surface: random.uniform(0, 1)
            for surface in all_surfaces
        }
        prob_sum = sum(per_surface_probability.values())
        per_surface_probability = {
            surface: prob / prob_sum
            for surface, prob in per_surface_probability.items()
        }
        app_behavior_config = {
            AppBehaviorFieldState.SESSION_ACTIVE_PROBABILITY:
                active_probability,
            AppBehaviorFieldState.SESSION_DURATION_MEAN: session_length,
            AppBehaviorFieldState.SESSION_DURATION_STDEV: session_length / 10,
            AppBehaviorFieldState.PER_SURFACE_PROBABILITY:
                per_surface_probability,
        }
        app_behavior = AppBehaviorState(app_behavior_config)
        user.add_object(app_behavior)

    def _create_user_single(
        self,
        env_config: dict,
        user_config: dict,
    ) -> User:
        user = User()
        sim_interval_raw_sec = user_config['user_simulation_interval']
        user.simulation_interval = timedelta(seconds=sim_interval_raw_sec)
        self._apply_personal_info(user, user_config)
        self._apply_tracking_states(user, user_config)
        self._apply_income_effect(user, user_config)
        self._apply_user_intent(user, user_config)
        self._apply_app_behavior(user, user_config, env_config)
        return user

    def create_users(self, start: bool = True) -> List[User]:
        users = []
        market_config = get_config()
        user_config = market_config.get_user_config()
        env_config = market_config.get_environment_config()
        user_count = user_config['user_count']
        for _ in range(user_count):
            user = self._create_user_single(env_config, user_config)
            users.append(user)
        if start:
            for user in users:
                user.start()
        printer(f"Loaded {len(users)} users out of {user_count}", "LOG")
        return users
