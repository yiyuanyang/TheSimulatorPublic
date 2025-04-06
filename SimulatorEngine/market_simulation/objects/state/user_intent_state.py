"""
    ========= User Intent State ==========
    This represents the intent of the user
    have on each category of items. For
    each category, a 0-1 number is assigned
    where 0 represents there is zero chance
    the user would convert on the ad, where
    1 represents the original ad probability
    would apply.
    ======================================
"""

from simulator_base.state.passive_state import PassiveState
from simulator_base.agent.agent import Agent
from ...config.market_config import get_config
from ..types.types import AdCategory, IntentValues, PurchaseHistory
from functools import cache
from typing import Optional


class UserIntentState(PassiveState):
    def __init__(self, intents: IntentValues = None):
        super().__init__("UserIntentState")
        if intents:
            self._validate_intents(intents)
            self._intents = intents
        else:
            self._intents = {
                AdCategory.TECHNOLOGY: 0.1,
                AdCategory.FASHION: 0.1,
                AdCategory.ENTERTAINMENT: 0.1,
                AdCategory.HOME_LIFESTYLE: 0.1,
                AdCategory.FOOD_DRINK: 0.1,
                AdCategory.HEALTH_FITNESS: 0.1,
                AdCategory.TRAVEL_LEISURE: 0.1,
                AdCategory.FINANCE: 0.1,
                AdCategory.AUTOMOTIVE: 0.1,
                AdCategory.EDUCATION: 0.1,
                AdCategory.OTHER: 0.1,
            }

    def _validate_intent(self, category: AdCategory, intent: float):
        if intent < 0 or intent > 1:
            raise Exception(
                f"Intent value for {category} is not between 0 and 1"
            )

    def _validate_intents(self, intents: IntentValues):
        if len(intents) != 11:
            raise Exception(
                "Intents should have 11 categories, one for each category"
            )
        for category, intent in intents.items():
            self._validate_intent(category, intent)

    def _get_subject_purchases(self) -> Optional[PurchaseHistory]:
        purchases_state = self.subject.get_state("PurchasesState")
        if purchases_state:
            return purchases_state.purchases
        return None

    def set_intent(self, category: AdCategory, intent: float):
        self._validate_intent(category, intent)
        self._intents[category] = intent

    def get_intent(self, category: AdCategory) -> float:
        purchases = self._get_subject_purchases()
        modifier = _purchase_intent_decay_category(
            purchases,
            category
        )
        return self._intents[category] * modifier

    @property
    def intents(self) -> IntentValues:
        existing_intents = self._intents.copy()
        return apply_purchase_intent_decay(self.subject, existing_intents)

    @intents.setter
    def intents(self, intents: IntentValues):
        self._validate_intents(intents)
        self._intents = intents


def get_user_intents_baseline() -> IntentValues:
    return {
        AdCategory.TECHNOLOGY: 1,
        AdCategory.FASHION: 1,
        AdCategory.ENTERTAINMENT: 1,
        AdCategory.HOME_LIFESTYLE: 1,
        AdCategory.FOOD_DRINK: 1,
        AdCategory.HEALTH_FITNESS: 1,
        AdCategory.TRAVEL_LEISURE: 1,
        AdCategory.FINANCE: 1,
        AdCategory.AUTOMOTIVE: 1,
        AdCategory.EDUCATION: 1,
        AdCategory.OTHER: 1,
    }


def apply_intent_modifier(
    intents: IntentValues,
    modifier: IntentValues
) -> IntentValues:
    """
    This function would apply the modifier
    to the intents. The modifier would be
    a dictionary with the same keys as the
    intents dictionary
    """
    for category, intent in intents.items():
        intents[category] = intent * modifier[category]
    return intents


@cache
def _get_purchase_intent_decay_factor() -> float:
    """
    This function would calculate the decay
    factor for the given category based on
    the purchases made by the user
    """
    market_config = get_config()
    intent_config = market_config.get_user_config()['intent_config']
    return intent_config['per_purchase_intent_decay']


def _purchase_intent_decay_category(
    purchases: Optional[PurchaseHistory],
    category: AdCategory
) -> float:
    return _get_purchase_intent_decay_factor() ** len(
        purchases.get(category, [])
    )


def apply_purchase_intent_decay(
    subject: Agent,
    current_intents: IntentValues
) -> IntentValues:
    """
    This function would calculate based on user's purchases
    the intent decay from each category. The more the user
    made purchase in a single category the less likely the user
    would make more purchases in that category
    """
    purchases = subject.get_state("PurchasesState").purchases
    intent_baseline = get_user_intents_baseline()
    for category, purchases in purchases.items():
        intent_baseline[category] *= _purchase_intent_decay_category(
            purchases
        )
    return apply_intent_modifier(current_intents, intent_baseline)
