import logging
from datetime import date
from decimal import Decimal

from app.fetchers.base import BaseFetcher
from app.schemas.price import PriceRecordCreate
from app.seed_data import FX_COLUMNS

logger = logging.getLogger(__name__)


class ForexFetcher(BaseFetcher):
    def source_name(self) -> str:
        return "forex"

    def fetch(self) -> list[PriceRecordCreate]:
        try:
            import akshare as ak

            df = ak.currency_boc_safe()
            if df is None or df.empty:
                return []
            latest = df.iloc[-1]
            record_date = _parse_date(latest["日期"])
            records: list[PriceRecordCreate] = []
            for item_code, col in FX_COLUMNS.items():
                if col not in latest:
                    continue
                price = Decimal(str(latest[col])).quantize(Decimal("0.0001"))
                change_pct = None
                if len(df) >= 2 and col in df.columns:
                    prev = Decimal(str(df.iloc[-2][col]))
                    if prev:
                        change_pct = ((price - prev) / prev * 100).quantize(Decimal("0.0001"))
                records.append(
                    PriceRecordCreate(
                        item_code=item_code,
                        record_date=record_date,
                        price=price,
                        change_pct=change_pct,
                    )
                )
            return records
        except Exception as exc:
            logger.warning("Forex fetch failed: %s", exc)
            return []


def _parse_date(value) -> date:
    if hasattr(value, "date"):
        return value.date()
    return date.fromisoformat(str(value)[:10])
