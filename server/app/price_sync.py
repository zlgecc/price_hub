"""Ensure price records exist by fetching live data or seeding demo values."""

import asyncio
import logging

from app.database import SessionLocal
from app.models import PriceRecord
from app.seed import seed_demo_prices
from app.services.fetcher_manager import FetcherManager

logger = logging.getLogger(__name__)
_lock = asyncio.Lock()


def has_price_records() -> bool:
    with SessionLocal() as db:
        return db.query(PriceRecord).count() > 0


async def ensure_price_data() -> None:
    if has_price_records():
        return

    async with _lock:
        if has_price_records():
            return

        with SessionLocal() as db:
            count = seed_demo_prices(db)
            logger.info("Seeded %d demo price records for first load", count)

        try:
            with SessionLocal() as db:
                manager = FetcherManager()
                results = await manager.run_all(db)
                logger.info("Auto price fetch completed: %s", results)
        except Exception:
            logger.exception("Auto price fetch failed; demo prices remain available")
