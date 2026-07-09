import logging

from app.fetchers.base import BaseFetcher
from app.fetchers.fred_util import calc_change_pct, fetch_fred_series_tail
from app.fetchers.spot_util import fetch_futures_spot_map
from app.schemas.price import PriceRecordCreate
from app.seed_data import COMMODITY_SPOT_SYMBOLS, FRED_SERIES

logger = logging.getLogger(__name__)

# FRED series that belong to commodity category (exclude energy)
COMMODITY_FRED_ITEMS = (
    "copper",
    "aluminum",
    "wheat",
    "corn",
    "soybean",
    "palm_oil_intl",
)


class CommodityFetcher(BaseFetcher):
    def source_name(self) -> str:
        return "commodity"

    def fetch(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        records.extend(self._fetch_fred())
        records.extend(fetch_futures_spot_map(COMMODITY_SPOT_SYMBOLS))
        return records

    def _fetch_fred(self) -> list[PriceRecordCreate]:
        records: list[PriceRecordCreate] = []
        for item_code in COMMODITY_FRED_ITEMS:
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
                logger.warning("Commodity FRED fetch failed for %s: %s", item_code, exc)
        return records
