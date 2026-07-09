from app.fetchers.basket import BasketFetcher
from app.fetchers.base import BaseFetcher
from app.fetchers.commodity import CommodityFetcher
from app.fetchers.forex import ForexFetcher
from app.fetchers.gold import GoldFetcher
from app.fetchers.market import MarketFetcher
from app.fetchers.oil import OilFetcher

__all__ = [
    "BaseFetcher",
    "GoldFetcher",
    "OilFetcher",
    "BasketFetcher",
    "CommodityFetcher",
    "ForexFetcher",
    "MarketFetcher",
]
