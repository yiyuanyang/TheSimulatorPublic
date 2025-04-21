"""
    ============== Required Setup ==================
    -------------   DO NOT MODIFY  -----------------
    required_setup enables all core functionalities
    of the bare minimum simulator. There is no
    object contained in this simulation environment
    and a custom setup function that adds simulated
    object is required to actually simulate anything.
    =================================================
"""

from simulator_base.orchestrator.orchestrator import Orchestrator
from simulator_base.config.global_config import GlobalConfig
from simulator_base.command.command_reader import CommandReader

GLOBAL_CONFIG_PATH = (
    "./global_config.yaml"
)


def required_setup():
    global_config = GlobalConfig.get_instance()
    global_config.setup(GLOBAL_CONFIG_PATH)
    orchestrator = Orchestrator.get_instance()
    orchestrator.setup_time()
    command_reader = CommandReader()
    command_reader.start()
    return orchestrator
