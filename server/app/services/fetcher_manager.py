import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.fetchers import (
    BasketFetcher,
    CommodityFetcher,
    ForexFetcher,
    GoldFetcher,
    MarketFetcher,
    OilFetcher,
)
from app.fetchers.base import BaseFetcher
from app.models import PriceItem, PriceRecord
from app.schemas.price import FetchResult, PriceRecordCreate

logger = logging.getLogger(__name__)


class FetcherManager:
    def __init__(self) -> None:
        self.fetchers: list[BaseFetcher] = [
            GoldFetcher(),
            OilFetcher(),
            BasketFetcher(),
            CommodityFetcher(),
            ForexFetcher(),
            MarketFetcher(),
        ]

    async def run_all(self, db: Session) -> list[FetchResult]:
        results: list[FetchResult] = []
        for fetcher in self.fetchers:
            source = fetcher.source_name()
            try:
                records = await asyncio.to_thread(fetcher.fetch)
                count = self._upsert_records(db, records)
                db.commit()
                results.append(FetchResult(source=source, success=True, records_count=count))
                logger.info("Fetcher %s: %d records upserted", source, count)
            except Exception as exc:
                db.rollback()
                logger.exception("Fetcher %s failed", source)
                results.append(
                    FetchResult(source=source, success=False, records_count=0, error=str(exc))
                )
        return results

    def _upsert_records(self, db: Session, records: list[PriceRecordCreate]) -> int:
        count = 0
        item_cache: dict[str, PriceItem | None] = {}
        for record in records:
            if record.item_code not in item_cache:
                item_cache[record.item_code] = (
                    db.query(PriceItem).filter_by(code=record.item_code).first()
                )
            item = item_cache[record.item_code]
            if not item:
                logger.warning("Unknown item code: %s", record.item_code)
                continue

            existing = (
                db.query(PriceRecord)
                .filter_by(item_id=item.id, record_date=record.record_date)
                .first()
            )
            if existing:
                existing.price = record.price
                existing.change_pct = record.change_pct
                existing.fetched_at = datetime.utcnow()
            else:
                db.add(
                    PriceRecord(
                        item_id=item.id,
                        record_date=record.record_date,
                        price=record.price,
                        change_pct=record.change_pct,
                        fetched_at=datetime.utcnow(),
                    )
                )
            count += 1
        return count
