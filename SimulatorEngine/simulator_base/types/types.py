from enum import StrEnum


class GenderType(StrEnum):
    MALE = "male"
    FEMALE = "female"


class BaseObjectType(StrEnum):
    ACTION = "Action"
    STATE = "State"
    EFFECT = "Effect"
    AGENT = "Agent"
    ENVIRONMENT = "Environment"
    METRIC = "Metric"
    EVENT = "Event"
