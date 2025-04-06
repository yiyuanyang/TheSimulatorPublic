"""
    ============= Auction Env Loader ===============
    Load up the few auction environments for ranking
    ===============================================
"""

from simulator_base.environment.environment import Environment
from .auction_environment import AuctionEnvironment
from .all_ads_environment import AllAdsEnvironment
from ..state.all_active_ads_state import AllActiveAdsState
from .ranking_environment import RankingEnvironment
from .targeting_environment import TargetingEnvironment
from market_simulation.config.market_config import get_config
from datetime import timedelta
from typing import List


def load_auction_env(start: bool = True) -> List[Environment]:
    auction_env = AuctionEnvironment()
    all_ads_env = AllAdsEnvironment()
    env_config = get_config().get_environment_config()
    ads_scanning_period = env_config['ads_scanning_period']
    period_timedelta = timedelta(minutes=ads_scanning_period)
    all_ads_state = AllActiveAdsState(period_timedelta)
    all_ads_env.add_object(all_ads_state)
    ranking_env = RankingEnvironment()
    targeting_env = TargetingEnvironment()
    if start:
        auction_env.start()
        all_ads_env.start()
        ranking_env.start()
        targeting_env.start()
    return [
        auction_env,
        all_ads_env,
        ranking_env,
        targeting_env
    ]
