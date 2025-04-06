"""
    Global configuration file used for the simulation
"""


import yaml
from datetime import date, timedelta, datetime
from uuid import uuid4
import random
import numpy as np
from typing import Optional
import os


class GlobalConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalConfig, cls).__new__(cls)
            cls._instance._simulation_unique_id = str(uuid4())
        return cls._instance

    @classmethod
    def get_simulation_unique_id(cls):
        if cls._instance is None:
            cls._instance = GlobalConfig()
        return cls._instance._simulation_unique_id

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GlobalConfig()
        return cls._instance

    @classmethod
    def get_random_seed(cls):
        return cls._instance._simulation_config.get('random_seed', 1)

    def get_exp_output_path(self):
        """
            Get the output path for the experiment
        """
        save_path = self._analytics_config["save_path"]
        experiment_name_with_id = self._simulation_config['experiment_name'] \
            + "_" + self.get_simulation_unique_id()
        complete_save_path = os.path.join(
            save_path,
            experiment_name_with_id
        )
        return complete_save_path

    def setup(self, config_path: str = 'config/global_config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            self._simulation_config = config['simulation_config']
            self._analytics_config = config['analytics_config']
            self._debug_config = config['debug_config']
            random_seed = self._simulation_config.get('random_seed', 1)
            random.seed(random_seed)
            np.random.seed(random_seed)
            # copy the global config into the target metrics folder
            exp_output = self.get_exp_output_path()
            yaml_copy_path = os.path.join(
                exp_output,
                'global_config.yaml'
            )
            os.makedirs(exp_output, exist_ok=True)
            with open(yaml_copy_path, 'w') as yaml_copy_file:
                yaml.dump(
                    config,
                    yaml_copy_file,
                    sort_keys=False,
                    default_flow_style=False
                )

    @property
    def simulation_config(self) -> dict:
        return self._simulation_config

    @property
    def end_time(self) -> Optional[datetime]:
        end_time_str = self._simulation_config.get('end_time')
        if end_time_str:
            return datetime.fromisoformat(end_time_str)
        return None

    @property
    def debug_config(self) -> dict:
        return self._debug_config

    @property
    def analytics_config(self) -> dict:
        return self._analytics_config

    def return_str_field(self, field: str) -> str:
        return self._simulation_config.get(field, '')

    def get_tick_interval_seconds(self) -> timedelta:
        tick_interval = self.return_str_field('tick_interval_seconds')
        return timedelta(seconds=tick_interval)

    def get_output_warning_level(self) -> str:
        return self._debug_config['output_warning_level']

    def get_start_date(self) -> datetime:
        date_str = self.return_str_field('start_date')
        cur_date = date.fromisoformat(date_str)
        return datetime.combine(cur_date, datetime.min.time())

    def print_all(self) -> bool:
        return self._debug_config['print_all_behaviors_for_debug']

    def get_analytics_config(self):
        return self._analytics_config

    def get_analytics_field(self, field: str):
        if self._analytics_config and self._analytics_config.get(field):
            return self._analytics_config[field]
        return None


def get_config() -> GlobalConfig:
    """
        Get the global configuration object
    """
    return GlobalConfig.get_instance()
