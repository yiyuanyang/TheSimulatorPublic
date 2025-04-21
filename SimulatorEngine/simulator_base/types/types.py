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


class CommandPriority(StrEnum):
    # Command to be executed at the start of the next tick
    IMMEDIATE = "Immediate"
    # Commands that are executed at a specific time
    SCHEDULED = "Scheduled"


class CommandType(StrEnum):
    # simple commands
    PAUSE = "Pause"
    START = "Start"
    STOP = "Stop"
    SAVE = "Save"
    LOAD = "Load"
    ADD_AGENT = "AddAgent"
    ADD_ENV = "AddEnv"
    ADD_EVENT = "AddEvent"
    ADD_EFFECT = "AddEffect"
    ADD_ACTION = "AddAction"
    ADD_STATE = "AddState"
    MODIFY_AGENT = "ModifyAgent"
    MODIFY_ENV = "ModifyEnv"
    MODIFY_EVENT = "ModifyEvent"
    MODIFY_EFFECT = "ModifyEffect"
    MODIFY_ACTION = "ModifyAction"
    MODIFY_STATE = "ModifyState"
    REMOVE_AGENT = "RemoveAgent"
    REMOVE_ENV = "RemoveEnv"
    REMOVE_EVENT = "RemoveEvent"
    REMOVE_EFFECT = "RemoveEffect"
    REMOVE_ACTION = "RemoveAction"
    REMOVE_STATE = "RemoveState"


class CommandField(StrEnum):
    COMMAND_TYPE = "CommandType"
    COMMAND_PRIORITY = "CommandPriority"
    SCHEDULED_TIME = "ScheduledTime"
    # content of command
    TARGET_ID = "TargetId"
    TARGET_ATTRIBUTE = "TargetAttribute"
    TARGET_VALUE = "TargetValue"
