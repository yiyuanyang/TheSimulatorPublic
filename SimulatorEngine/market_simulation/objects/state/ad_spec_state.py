"""
    ================ Ad Spec State =========================
    Describe the targeting and basic status of the ad, would
    used for retrieving this ad when matching with user
    side info.
    ========================================================
"""

from simulator_base.state.passive_state import PassiveState
from simulator_base.types.types import GenderType
from ..types.types import AppSurfaceType, AdCategory, AdFormat
from typing import List


class AdSpecState(PassiveState):
    def __init__(
        self,
        surfaces: List[AppSurfaceType],
        target_country: List[str],
        target_min_age: int,
        target_max_age: int,
        target_gender: List[GenderType],
        ad_category: AdCategory,
        ad_format: AdFormat,
    ):
        super().__init__("AdSpecState")
        self._surfaces: List[AppSurfaceType] = surfaces
        self._country: List[str] = target_country
        self._ad_category: AdCategory = ad_category
        self._ad_format: AdFormat = ad_format
        self._min_age: int = target_min_age
        self._max_age: int = target_max_age
        self._gender: List[GenderType] = target_gender

    @property
    def surfaces(self) -> List[AppSurfaceType]:
        return self._surfaces

    @property
    def country(self) -> List[str]:
        return self._country

    @property
    def ad_category(self) -> AdCategory:
        return self._ad_category

    @property
    def ad_format(self) -> AdFormat:
        return self._ad_format

    @property
    def min_age(self) -> int:
        return self._min_age

    @property
    def max_age(self) -> int:
        return self._max_age

    @property
    def gender(self) -> List[GenderType]:
        return

    def country_match(self, country: str) -> bool:
        return country in self._country

    def surface_match(self, surface: AppSurfaceType) -> bool:
        return surface in self._surfaces

    def age_match(self, age: int) -> bool:
        return self._min_age <= age <= self._max_age

    def gender_match(self, gender: GenderType) -> bool:
        return gender in self._gender

    def validate_object(self):
        super().validate_object()
        if not self._surfaces:
            raise Exception("Ad must target at least one surface")
        if not self._country:
            raise Exception("Ad must target at least one country")
        if self._ad_category is None:
            raise Exception("Ad must have a category")
        if self._ad_format is None:
            raise Exception("Ad must have a format")
