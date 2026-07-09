"""Shared helpers for domestic futures spot prices via AKShare."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal

from app.schemas.price import PriceRecordCreate

logger = logging.getLogger(__name__)


def fetch_futures_spot_map(
    symbol_to_items: dict[str, list[str]],
    lookback_days: int = 14,
) -> list[PriceRecordCreate]:
    """Fetch latest futures spot prices and map symbols to item codes."""
    try:
        import akshare as ak

        start = (date.today() - timedelta(days=lookback_days)).strftime("%Y%m%d")
        end = date.today().strftime("%Y%m%d")
        df = ak.futures_spot_price_daily(start_day=start, end_day=end)
        if df is None or df.empty:
            return []

        latest_date = df["date"].max()
        day_df = df[df["date"] == latest_date]
        record_date = _parse_date(latest_date)
        records: list[PriceRecordCreate] = []

        for symbol, item_codes in symbol_to_items.items():
            rows = day_df[day_df["symbol"].astype(str) == symbol]
            if rows.empty:
                continue
            price = Decimal(str(rows.iloc[0]["spot_price"])).quantize(Decimal("0.0001"))
            for item_code in item_codes:
                records.append(
                    PriceRecordCreate(
                        item_code=item_code,
                        record_date=record_date,
                        price=price,
                        change_pct=None,
                    )
                )
        return records
    except Exception as exc:
        logger.warning("Futures spot fetch failed: %s", exc)
        return []


def _parse_date(value) -> date:
    if hasattr(value, "date"):
        return value.date()
    text = str(value)
    if len(text) == 8 and text.isdigit():
        return date(int(text[:4]), int(text[4:6]), int(text[6:8]))
    return date.fromisoformat(text[:10])
