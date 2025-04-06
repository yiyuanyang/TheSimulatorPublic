"""
    ================== Create Ad Action ===================
    This represents the advertiser action of creating an ad

    Advertiser can periodically review available left over
    budget and create a new ad.
    ========================================================
"""

from simulator_base.action.action import Action
from market_simulation.objects.analytics.ad_metrics import AdMetrics
from ..ads.ad_factory import create_ad
from ..state.advertiser_intent_state import AdvertiserIntentState
from datetime import timedelta


class CreateAdAction(Action):
    def __init__(
        self,
        ad_creation_interval: timedelta = timedelta(days=1),
    ):
        super().__init__("CreateAdAction", ad_creation_interval)

    def evaluate(self) -> bool:
        advertiser_intent_state: AdvertiserIntentState = \
            self.subject.get_state("AdvertiserIntentState")
        return advertiser_intent_state.can_create_ad()

    def act(self):
        intent_state: AdvertiserIntentState = self.subject.get_state(
            "AdvertiserIntentState"
        )
        ad_budget = intent_state.get_ad_daily_budget()
        ad = create_ad(
            advertiser=self.subject,
            ad_outcome=intent_state.get_outcome(),
            ad_format=intent_state.get_format(),
            target_country=intent_state.target_country,
            target_min_age=intent_state.target_min_age,
            target_max_age=intent_state.target_max_age,
            target_gender=intent_state.target_gender,
            category=intent_state.category,
            bidding_strategy=intent_state.bidding_strategy,
            cost_cap=intent_state.cost_cap,
            ad_surfaces=intent_state.get_surfaces(),
            ad_budget=ad_budget,
            duration=intent_state.get_duration(),
        )
        ad_metrics = AdMetrics()
        ad_metrics.attach(ad)
        ad.start()
