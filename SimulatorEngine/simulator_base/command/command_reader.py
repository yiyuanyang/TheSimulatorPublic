"""
    ============== Command ==================
    Command is a class that "participates" in
    the simulation, it tries to read from the
    command file periodically to see if there
    is any external command to execute for
    the simulation.
    ==========================================
"""

from simulator_base.object_base.simulation_object import SimulationObject
from simulator_base.orchestrator.orchestrator import Orchestrator
from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.config.global_config import get_config
from simulator_base.types.types import (
    CommandType,
    CommandField,
    CommandPriority
)
from simulator_base.command.command_util import (
    pause_simulation,
    resume_simulation,
    stop_simulation,
)
import json
from datetime import datetime, timedelta
import os


class CommandReader(SimulationObject):
    def __init__(self):
        super().__init__("CommandReader", "CommandReader")
        global_config = get_config()
        command_config = global_config.command_config
        sim_interval = command_config["command_read_interval"]
        self.simulation_interval = timedelta(
            seconds=sim_interval
        )

    def log_scheduled_command(self, commands: list):
        """
        Log the scheduled commands to a file
        """
        command_dir = get_config().get_exp_output_path()
        scheduled_command_save_path = os.path.join(
            command_dir,
            "scheduled_commands.json"
        )
        if not os.path.exists(scheduled_command_save_path):
            # create the path
            os.makedirs(
                command_dir,
                exist_ok=True
            )
            with open(scheduled_command_save_path, "w") as f:
                json.dump(commands, f)
        else:
            with open(scheduled_command_save_path, "r+") as f:
                command_list = json.load(f)
                command_list.extend(commands)
                f.seek(0)
                f.truncate()
                json.dump(command_list, f)

    def read_command(self):
        """
        Read the command file and execute the commands
        """
        current_time = Orchestrator.get_global_time()
        command_dir = get_config().get_command_path()
        # read the command json file
        complete_command_path = os.path.join(
            command_dir,
            "command.json"
        )
        if not os.path.exists(command_dir):
            # create the path
            os.makedirs(command_dir, exist_ok=True)
            with open(complete_command_path, "w") as f:
                json.dump([], f)
        command_list = []
        with open(complete_command_path, "r+") as f:
            try:
                command_list = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return
            if len(command_list) > 0:
                # write to a temp file of empty list
                # and replace the original file to
                # avoid conflict
                temp_file = os.path.join(command_dir, "temp.json")
                with open(temp_file, "w") as temp_f:
                    empty_list = json.dumps([])
                    temp_f.write(empty_list)
                    temp_f.close()
                os.replace(temp_file, complete_command_path)
            else:
                return
        # convert the list of commands into callables and
        # insert into orchestrator's scheduled commands
        orchestrator = get_orchestrator()
        scheduled_commands_to_log = []
        for command in command_list:
            command_type: CommandType = command.get(
                CommandField.COMMAND_TYPE
            )
            command_priority = command.get(
                CommandField.COMMAND_PRIORITY
            )
            if command_priority == CommandPriority.IMMEDIATE:
                scheduled_time = current_time
            else:
                scheduled_time = datetime.fromisoformat(
                    command.get(CommandField.SCHEDULED_TIME)
                )
            scheduled_commands_to_log.append(
                (scheduled_time.isoformat(), command)
            )
            match command_type:
                case CommandType.PAUSE:
                    orchestrator.add_scheduled_command(
                        (scheduled_time, pause_simulation)
                    )
                case CommandType.START:
                    orchestrator.add_scheduled_command(
                        (scheduled_time, resume_simulation)
                    )
                case CommandType.STOP:
                    orchestrator.add_scheduled_command(
                        (scheduled_time, stop_simulation)
                    )
        self.log_scheduled_command(scheduled_commands_to_log)

    def rehydrate(self):
        """
            Rehydrate the command reader,
            nothing to do here
        """
        pass

    def simulate(self):
        """
            Every simulation interval's job is to read
            the command file and place them into orchestrator
            command queue
        """
        self.read_command()

    def validate_object(self):
        pass
