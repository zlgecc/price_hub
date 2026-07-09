"""Create schema and seed baseline data on first startup."""

import logging

from sqlalchemy import inspect

from app.database import Base, SessionLocal, engine
from app.models import PriceCategory
from app.seed import seed

logger = logging.getLogger(__name__)


def bootstrap_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if inspect(engine).has_table("price_categories") and db.query(PriceCategory).count() > 0:
            return

        seed(db)
        logger.info("Database bootstrapped with seed categories and items.")
