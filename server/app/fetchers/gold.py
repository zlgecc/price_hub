import logging
from datetime import date
from decimal import Decimal

import httpx

from app.fetchers.base import BaseFetcher
from app.schemas.price import PriceRecordCreate
from app.seed_data import SGE_SYMBOLS

logger = logging.getLogger(__name__)


class GoldFetcher(BaseFetcher):
    def source_name(self) -> str:
        return "gold"

    def fetch(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        records.extend(self._fetch_sge_all())
        records.extend(self._fetch_intl())
        return records

    def _fetch_sge_all(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        for item_code, symbol in SGE_SYMBOLS.items():
            try:
                import akshare as ak

                df = ak.spot_hist_sge(symbol=symbol)
                if df is None or df.empty:
                    continue
                latest = df.iloc[-1]
                record_date = _parse_date(latest.get("date") or latest.name)
                price = Decimal(str(latest["close"]))
                change_pct = _calc_change_pct(df["close"], price)
                records.append(
                    PriceRecordCreate(
                        item_code=item_code,
                        record_date=record_date,
                        price=price,
                        change_pct=change_pct,
                    )
                )
            except Exception as exc:
                logger.warning("SGE fetch failed for %s (%s): %s", item_code, symbol, exc)
        return records

    def _fetch_intl(self) -> list[PriceRecordCreate]:
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get("https://freegoldapi.com/data/latest.json")
                resp.raise_for_status()
                data = resp.json()
            if not data:
                return []
            latest = data[-1]
            record_date = date.fromisoformat(latest["date"][:10])
            price = Decimal(str(latest["price"]))
            change_pct = None
            if len(data) >= 2:
                prev = Decimal(str(data[-2]["price"]))
                if prev:
                    change_pct = ((price - prev) / prev * 100).quantize(Decimal("0.0001"))
            return [
                PriceRecordCreate(
                    item_code="gold_intl_usd",
                    record_date=record_date,
                    price=price,
                    change_pct=change_pct,
                )
            ]
        except Exception as exc:
            logger.warning("International gold fetch failed: %s", exc)
            return []


def _parse_date(value) -> date:
    if hasattr(value, "date"):
        return value.date()
    return date.fromisoformat(str(value)[:10])


def _calc_change_pct(series, current: Decimal) -> Decimal | None:
    if len(series) < 2:
        return None
    prev = Decimal(str(series.iloc[-2]))
    if not prev:
        return None
    return ((current - prev) / prev * 100).quantize(Decimal("0.0001"))
