import logging
from datetime import date
from decimal import Decimal

from app.fetchers.base import BaseFetcher
from app.fetchers.spot_util import fetch_futures_spot_map
from app.schemas.price import PriceRecordCreate
from app.seed_data import BASKET_SPOT_SYMBOLS

logger = logging.getLogger(__name__)

BASKET_ITEMS = {
    "basket_index": "macro_china_vegetable_basket",
    "agri_index": "macro_china_agricultural_product",
}


class BasketFetcher(BaseFetcher):
    def source_name(self) -> str:
        return "basket"

    def fetch(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        try:
            import akshare as ak

            for item_code, func_name in BASKET_ITEMS.items():
                try:
                    fetch_func = getattr(ak, func_name)
                    df = fetch_func()
                    if df is None or df.empty:
                        continue
                    latest = df.iloc[-1]
                    record_date = _parse_date(latest["日期"])
                    price = Decimal(str(latest["最新值"])).quantize(Decimal("0.0001"))
                    change_pct = Decimal(str(latest["涨跌幅"])).quantize(Decimal("0.0001"))
                    records.append(
                        PriceRecordCreate(
                            item_code=item_code,
                            record_date=record_date,
                            price=price,
                            change_pct=change_pct,
                        )
                    )
                except Exception as exc:
                    logger.warning("Basket fetch failed for %s: %s", item_code, exc)

            records.extend(self._fetch_pork())
            records.extend(fetch_futures_spot_map(BASKET_SPOT_SYMBOLS))
        except Exception as exc:
            logger.warning("Basket fetcher error: %s", exc)
        return records

    def _fetch_pork(self) -> list[PriceRecordCreate]:
        try:
            import akshare as ak

            df = ak.index_hog_spot_price()
            if df is None or df.empty:
                return []
            latest = df.iloc[-1]
            price_raw = latest.get("成交均价")
            if price_raw is None:
                return []
            price = Decimal(str(price_raw)).quantize(Decimal("0.0001"))
            change_pct = None
            if len(df) >= 2:
                prev = Decimal(str(df.iloc[-2]["成交均价"]))
                if prev:
                    change_pct = ((price - prev) / prev * 100).quantize(Decimal("0.0001"))
            return [
                PriceRecordCreate(
                    item_code="pork",
                    record_date=_parse_date(latest["日期"]),
                    price=price,
                    change_pct=change_pct,
                )
            ]
        except Exception as exc:
            logger.warning("Pork/hog fetch failed: %s", exc)
            return []


def _parse_date(value) -> date:
    if hasattr(value, "date"):
        return value.date()
    return date.fromisoformat(str(value)[:10])
