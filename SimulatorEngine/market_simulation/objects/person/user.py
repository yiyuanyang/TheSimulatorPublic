"""
    ======== User =============
    This represents a user
    in the ad market simulation

    requires:
        - PersonalInfo
        - PurchasesState
        - DisposableIncomeState
        - UserIntentState
        - IncomeEffect
    ===========================
"""

from simulator_base.person.person import Person
from ..types.types import AdEvent, AdEventFields
from typing import final


@final
class User(Person):
    def __init__(self):
        super().__init__("User")

    def required_objects(self):
        return [
            'PurchasesState',
            'DisposableIncomeState',
            'UserIntentState',
            'UserAdViewHistoryState',
            'UserAdConversionHistoryState',
            'AppBehaviorState',
            'IncomeEffect',
            'BrowseAppAction',
            'PersonalInfoState'
        ]

    def view_ad(self, ad_event: AdEvent):
        """
            Adding an impression event to user's view history
            so that it can be used to calculate the impact
            of awareness ad's lift on ad performance and
            ad fatigue from conversion ad.
        """
        view_state = self.get_state('UserAdViewHistoryState')
        view_state.view_ad(ad_event)

    def convert_ad(self, ad_event: AdEvent):
        """
            Adding a conversion event to user's conversion history
            every conversion on the same category would reduce
            the user's future probability on purchasing item of the
            same category again.
        """
        convert_state = self.get_state('UserAdConversionHistoryState')
        convert_state.convert_ad(ad_event)
        purchase_state = self.get_state('PurchasesState')
        ad_category = ad_event[AdEventFields.AD].category
        purchase_state.add_purchase(
            ad_category,
            ad_event[AdEventFields.EVENT_TIME]
        )

    def __str__(self):
        return f"user_({super().__str__()})"
