"""
    ======== Consumption Behavior State ====================
    This represents a "personal config" that describes the
    kind of actions and general tendency of behavior on the
    internet.
    ========================================================
"""


from simulator_base.state.passive_state import PassiveState
from ...objects.types.types import AppBehaviorFieldState, AppSurfaceType
import random
from datetime import timedelta
from typing import Any


class AppBehaviorState(PassiveState):
    def __init__(self, config: dict[AppBehaviorFieldState, Any]):
        super().__init__("AppBehaviorState")
        self._config = config
        self._hourly_active_probability = config[
            AppBehaviorFieldState.SESSION_ACTIVE_PROBABILITY
        ]
        self._hourly_active_duration_mean = config[
            AppBehaviorFieldState.SESSION_DURATION_MEAN
        ]
        self._hourly_active_duration_stdev = config[
            AppBehaviorFieldState.SESSION_DURATION_STDEV
        ]
        self._per_surface_probability = config[
            AppBehaviorFieldState.PER_SURFACE_PROBABILITY
        ]

    @property
    def config(self) -> dict:
        return self.config

    def get_is_user_active(self) -> bool:
        """
            This function can only be called at most once
            per an hour
        """
        return random.random() < self._hourly_active_probability

    def get_user_active_duration(self) -> timedelta:
        total_seconds = random.gauss(
            self._hourly_active_duration_mean,
            self._hourly_active_duration_stdev
        )
        return timedelta(seconds=total_seconds)

    def get_user_active_surface(self) -> AppSurfaceType:
        return random.choices(
            list(self._per_surface_probability.keys()),
            weights=self._per_surface_probability.values(),
            k=1
        )[0]
