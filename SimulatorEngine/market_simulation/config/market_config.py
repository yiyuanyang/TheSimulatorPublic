"""
    ============== Market Config =======================
    This defines a globally accessible market
    config that loads all necessary setup configurations
    for the market simulation. This mostly includes
    1. Environment config
        This mostly describes the countries, surfaces
        and etc
    2. User Config
        How often do users browse content, what is their
        purchase power and etc.
    3. Advertiser Config
        How often do they create ads, their budget, their
        goal and ROI and etc.
    4. Delivery Config
        How ranking models are simulated, how pacing is
        done
    5. Analytics Config
        How frequently do we dump the metrics, how often
        do we calculate them and etc.
    ====================================================
"""

from simulator_base.util.printer import printer
from simulator_base.config.global_config import get_config as get_global_config
import yaml
import os


class MarketConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketConfig, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MarketConfig()
        return cls._instance

    def setup(
        self,
        config_path: str = 'market_simulation/config/market_config.yaml'
    ):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            self._user_config = config['user_config']
            self._advertiser_config = config['advertiser_config']
            self._environment_config = config['environment_config']
            self._delivery_config = config['delivery_config']
            self._analytics_config = config['analytics_config']
            g_config = get_global_config()
            exp_output = g_config.get_exp_output_path()
            yaml_copy_path = os.path.join(
                exp_output,
                'market_config.yaml'
            )
            os.makedirs(exp_output, exist_ok=True)
            with open(yaml_copy_path, 'w') as yaml_copy_file:
                yaml.dump(
                    config,
                    yaml_copy_file,
                    sort_keys=False,
                    default_flow_style=False
                )
        printer("Loaded Market Config", "LOG")

    def get_environment_config(self) -> dict:
        return self._environment_config

    def get_user_config(self) -> dict:
        return self._user_config

    def get_advertiser_config(self) -> dict:
        return self._advertiser_config

    def get_delivery_config(self) -> dict:
        return self._delivery_config

    def get_analytics_config(self) -> dict:
        return self._analytics_config


def get_config() -> MarketConfig:
    return MarketConfig()
