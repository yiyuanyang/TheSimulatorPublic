"""
    Based on global config
    and print level, determine wheter
    or not to print the message
    to console
"""

from ..config.global_config import GlobalConfig


def printer(message: str, level: str = "DEBUG"):
    print_level = GlobalConfig.get_instance().get_output_warning_level()
    if level == "DEBUG" and (
        print_level == "DEBUG"
        or print_level == "LOG"
    ):
        print(message)
    elif (level == "WARNING"
          and print_level == "DEBUG"
          or print_level == "WARNING"
          or print_level == "LOG"
          ):
        print(message)
    elif level == "ERROR":
        print(message)


def simulation_printer(message: str):
    """
        Print message to console
        that is from the simulation
    """
    print(message)
