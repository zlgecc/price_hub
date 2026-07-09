"""Stocks, indices, and tech/semiconductor related prices."""

from __future__ import annotations

import logging

from app.fetchers.base import BaseFetcher
from app.fetchers.fred_util import calc_change_pct, fetch_fred_series_tail
from app.fetchers.sina_util import fetch_sina_quotes
from app.schemas.price import PriceRecordCreate
from app.seed_data import FRED_SERIES, SINA_MARKET_SYMBOLS

logger = logging.getLogger(__name__)

MARKET_FRED_ITEMS = (
    "idx_sp500",
    "idx_nasdaq100",
    "idx_djia",
    "semi_ppi",
    "semi_ip",
)


class MarketFetcher(BaseFetcher):
    def source_name(self) -> str:
        return "market"

    def fetch(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        records.extend(self._fetch_sina())
        records.extend(self._fetch_fred())
        return records

    def _fetch_sina(self) -> list[PriceRecordCreate]:
        symbols = list(SINA_MARKET_SYMBOLS.keys())
        quotes = fetch_sina_quotes(symbols)
        records: list[PriceRecordCreate] = []
        for symbol, item_code in SINA_MARKET_SYMBOLS.items():
            quote = quotes.get(symbol)
            if quote is None:
                logger.info("No Sina quote for %s (%s)", item_code, symbol)
                continue
            records.append(
                PriceRecordCreate(
                    item_code=item_code,
                    record_date=quote.record_date,
                    price=quote.price,
                    change_pct=quote.change_pct,
                )
            )
        return records

    def _fetch_fred(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        for item_code in MARKET_FRED_ITEMS:
            series_id = FRED_SERIES[item_code]
            try:
                points = fetch_fred_series_tail(series_id, limit=2)
                if not points:
                    logger.info("No FRED data for %s (%s)", item_code, series_id)
                    continue
                record_date, price = points[-1]
                prev = points[-2][1] if len(points) >= 2 else None
                records.append(
                    PriceRecordCreate(
                        item_code=item_code,
                        record_date=record_date,
                        price=price,
                        change_pct=calc_change_pct(price, prev),
                    )
                )
            except Exception as exc:
                logger.warning("Market FRED fetch failed for %s: %s", item_code, exc)
        return records
