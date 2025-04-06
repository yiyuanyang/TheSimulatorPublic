"""
    ============= all ads environment ==============
    An environment object that holds and tracks all
    available ads for today. This enables the ads to
    be later fetched for viewing for users.
    ================================================
"""

from simulator_base.environment.environment import Environment


class AllAdsEnvironment(Environment):
    def __init__(self):
        super().__init__("AllAdsEnvironment")

    def destroy(self):
        raise Exception("AllAdsEnvironment object cannot be destroyed")

    def required_objects(self):
        return ['AllActiveAdsState']

    def validate_object(self):
        super().validate_object()

    @property
    def active_ads(self):
        return self.get_state('AllActiveAdsState').active_ads
