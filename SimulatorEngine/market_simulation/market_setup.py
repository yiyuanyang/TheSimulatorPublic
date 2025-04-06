"""
    ============= Market Setup ===============
    This file setups all of the players in an
    ad market simulation, including the users,
    advertisers, and the various environments.
    ==========================================
"""

from market_simulation.objects.environment.surface_env_loader import (
    load_surface_env,
)
from market_simulation.objects.auction.auction_env_loader import (
    load_auction_env
)
from market_simulation.objects.person.user_factory import UserFactory
from market_simulation.config.market_config import MarketConfig
from market_simulation.objects.person.advertiser_factory import (
    AdvertiserFactory
)


def market_setup():
    market_config = MarketConfig.get_instance()
    market_config.setup('market_simulation/config/market_config.yaml')
    load_surface_env()
    load_auction_env()
    user_factory = UserFactory()
    user_factory.create_users(start=True)
    advertiser_factory = AdvertiserFactory()
    advertiser_factory.create_advertisers(start=True)
