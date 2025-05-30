"""
    ============= Advertiser Agent =================
    This represents the advertiser agent, who has
    preference on the type of ad it likes to create
    surfaces they deliver to, as well as business
    category.

    The actions it takes is to respond slowly to
    performance improvement via increasing ads
    budget, and periodically adds money to his / her
    account to track newer ad.
    ================================================
"""


from simulator_base.person.person import Person
from ..ads.ad import Ad
from ..types.types import AdEventType
from datetime import datetime
from typing import List


class Advertiser(Person):
    def __init__(self):
        super().__init__("Advertiser")

    @property
    def active_ads(self) -> List[Ad]:
        return self.get_associated_objects('active_ads')

    @property
    def inactive_ads(self) -> List[Ad]:
        return self.get_associated_objects('inactive_ads')

    @property
    def active_ad_cnt(self) -> int:
        return len(self.active_ads)

    def has_active_ad_outcome(self, event_type: AdEventType) -> bool:
        return any([
            ad.get_state('AdOutcomeState').goal == event_type
            for ad in self.active_ads
        ])

    def append_ad(self, ad: Ad):
        self.active_ads.append(ad)

    def remove_ad(self, ad: Ad):
        self.active_ads.remove(ad)

    def append_inactive_ad(self, ad: Ad):
        self.inactive_ads.append(ad)

    def remove_inactive_ad(self, ad: Ad):
        self.inactive_ads.remove(ad)

    @property
    def total_budget(self) -> float:
        return self.get_state('AdvertisingBudgetState').daily_budget

    @property
    def utilized_budget(self) -> float:
        ads = self.active_ads
        return sum([
            ad.get_state('AdBudgetState').daily_budget for ad in ads
        ])

    def ads_after_date(self, date: datetime) -> List[Ad]:
        all_ads = self.active_ads + self.inactive_ads
        return [
            ad for ad in all_ads if ad.was_running_after_date(date)
        ]

    def roas_after_date(self, date: datetime) -> float:
        ads_after_date = self.ads_after_date(date)
        total_sales = sum([
            ad.total_sales_after_date(date) for ad in ads_after_date
        ])
        total_spend = sum([
            ad.total_cost_after_date(date) for ad in ads_after_date
        ])
        return total_sales / total_spend if total_spend > 0 else 0

    def roi_after_date(self, date: datetime) -> float:
        ads_after_date = self.ads_after_date(date)
        total_profit = sum([
            ad.total_profit_after_date(date) for ad in ads_after_date
        ])
        total_spend = sum([
            ad.total_cost_after_date(date) for ad in ads_after_date
        ])
        return total_profit / total_spend if total_spend > 0 else 0

    def required_objects(self):
        return [
            'AdvertisingBudgetState',
            'AdvertiserIntentState',
            'CreateAdAction',
            'AdvAdjustBudgetAction',
        ]

    def destroy(self):
        for ad in self.active_ads:
            ad.destroy()
        for ad in self.inactive_ads:
            ad.destroy()
        super().destroy()
