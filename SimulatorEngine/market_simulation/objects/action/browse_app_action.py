"""
    =============== Browse App Action ======================
    This represents the action of determining and performing
    the action of browsing an app. This action is performed
    by the user agent.
    ========================================================
"""


from simulator_base.action.action import Action
from simulator_base.orchestrator.orchestrator import Orchestrator
from simulator_base.object_base.object_base import ObjectBase
from ..state.app_behavior_state import AppBehaviorState
from datetime import timedelta


class BrowseAppAction(Action):
    def __init__(
        self,
        browsing_interval: timedelta = timedelta(hours=1),
    ):
        super().__init__(
            "BrowseAppAction",
            browsing_interval
        )

    def evaluate(self) -> bool:
        # delete
        app_behavior_state: AppBehaviorState = self.subject.get_state(
            "AppBehaviorState"
        )
        return app_behavior_state.get_is_user_active()

    def act(self):
        app_behavior_state: AppBehaviorState = self.subject.get_state(
            "AppBehaviorState"
        )
        app_surface = app_behavior_state.get_user_active_surface()
        browsing_time = app_behavior_state.get_user_active_duration()

        def surface_filter_fun(environment: ObjectBase):
            if (
                environment is None or
                environment.object_subtype != "SurfaceEnvironment"
            ):
                return False
            return environment.surface_type == app_surface

        surface_environment = Orchestrator.get_instance() \
            .get_environment_with_filter(filter_fn=surface_filter_fun)

        surface_environment.browse_surface(self.subject, browsing_time)
