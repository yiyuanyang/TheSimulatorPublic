"""
This file contains the Person class, which is the base class
for all people in the simulation.
"""

from ..agent.agent import Agent
from typing import List, Optional


class Person(Agent):
    """
        A basic person object that initialize itself
        with certain info, such as gender, name,
        birthday and country.
    """
    def __init__(
        self,
        person_type: Optional[str] = None,
    ):
        super().__init__("Person")
        self._person_type = person_type

    def required_objects(self) -> List[str]:
        return ['PersonalInfoState']

    @property
    def person_type(self) -> str:
        return self._person_type

    @property
    def name(self) -> str:
        return self.get_state('PersonalInfoState').name

    @property
    def gender(self) -> str:
        return self.get_state('PersonalInfoState').gender

    @property
    def age(self) -> int:
        return self.get_state('PersonalInfoState').age

    @property
    def country(self) -> str:
        return self.get_state('PersonalInfoState').country
