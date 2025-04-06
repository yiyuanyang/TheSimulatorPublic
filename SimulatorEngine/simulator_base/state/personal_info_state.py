"""
    ========== Personal Info State ============
    This represents the basic info for a person
    agent in the simulation.
    ============================================
"""

from ..state.passive_state import PassiveState
from ..orchestrator.orchestrator import Orchestrator
from ..types.types import GenderType
from datetime import datetime
from faker import Faker
from typing import final


@final
class PersonalInfoState(PassiveState):
    def __init__(
        self,
        gender: GenderType = None,
        birth_day: datetime = None,
        country: str = None,
        name: str = None
    ):
        super().__init__("PersonalInfoState")
        self._gender = gender
        self._name = name
        self._birth_day = birth_day
        self._country = country
        self._randomize_info()

    def _randomize_info(self):
        fake = Faker()
        if not self._gender:
            self._gender = fake.random_element(
                [GenderType.FEMALE, GenderType.MALE]
            )
        if not self._name:
            if self._gender == GenderType.MALE:
                self._name = fake.name_male()
            else:
                self._name = fake.name_female()
        if not self._birth_day:
            self._birth_day = fake.date_of_birth()
        if not self._country:
            self._country = fake.country()

    @property
    def gender(self):
        return self._gender

    @property
    def name(self):
        return self._name

    @property
    def birth_day(self):
        return self._birth_day

    @property
    def age(self):
        today = Orchestrator.get_current_time(self)
        age = today.year - self._birth_day.year
        if today.month < self._birth_day.month or (
            today.month == self._birth_day.month and
            today.day < self._birth_day.day
        ):
            age -= 1
        return age

    @property
    def country(self):
        return self._country
