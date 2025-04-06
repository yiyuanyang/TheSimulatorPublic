"""
    =============== Auction Environment ================
    Auction environment, this is where the final layer
    of the recommendation system happen. All probability
    are multiplied by the ad's bid to get the final
    auction ranking. And the second price is calculated
    here as well.
    =====================================================
"""

from simulator_base.environment.environment import Environment
from simulator_base.orchestrator.orchestrator import get_orchestrator
from simulator_base.agent.agent import Agent
from market_simulation.config.market_config import get_config
from .ranking_environment import RankingEnvironment
from ..types.types import (
    AppSurfaceType,
    AuctionResults,
    AuctionResultFields,
    AuctionType,
)


class AuctionEnvironment(Environment):
    def __init__(self):
        super().__init__("AuctionEnvironment")
        self._ad_ranking = []

    def fetch_and_price_all_ads(
        self,
        user: Agent,
        surface: AppSurfaceType,
        ad_cnt: int = 0
    ) -> AuctionResults:
        """
            Obtaining scored ads from the ranking environment,
            order them via value of bid, and calculate the price
            based on the auction type.
        """
        # delete
        ranking_environment: RankingEnvironment = get_orchestrator() \
            .get_environment('RankingEnvironment')
        scored_ads = ranking_environment.fetch_and_rank_all_ads(
            user,
            surface
        )
        ad_candidates_with_bids = []
        for ad, prob in scored_ads:
            paced_bid = ad.paced_bid
            ad_candidates_with_bids.append(
                {
                    AuctionResultFields.AD: ad,
                    AuctionResultFields.BID: paced_bid * prob[1],
                    AuctionResultFields.PRICE: 0,
                    AuctionResultFields.PACED_BID: paced_bid,
                    AuctionResultFields.TRUE_PROBABILITY: prob[0],
                    AuctionResultFields.PREDICTED_PROBABILITY: prob[1],
                }
            )
        ranked_ads = sorted(
            ad_candidates_with_bids,
            key=lambda x: x[AuctionResultFields.BID],
            reverse=True
        )
        ranked_ads = ranked_ads[:ad_cnt] if ad_cnt > 0 else []

        # ================== Auction Price Calculation ==================
        market_config = get_config()
        delivery_config = market_config.get_delivery_config()
        auction_type = delivery_config['auction_config']['auction_type']
        for index, _ in enumerate(ranked_ads):
            # In GSP auction, every ad pays by the bid amount of the next
            # ad, and the last ad in the auction pays 0.
            if auction_type == AuctionType.GENERALIZED_SECOND_PRICE \
               and index != len(ranked_ads) - 1:
                price = ranked_ads[index + 1][AuctionResultFields.BID]
            # In GFP auction, every ad pays the bid amount of itself.
            elif auction_type == AuctionType.GENERALIZED_FIRST_PRICE:
                price = ranked_ads[index][AuctionResultFields.BID]
            else:
                price = 0
            ranked_ads[index][AuctionResultFields.PRICE] = price
        return ranked_ads
