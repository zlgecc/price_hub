"""Seed database with categories and price items."""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import PriceCategory, PriceItem, PriceRecord
from app.seed_data import SEED_CATEGORIES, SEED_DEMO_PRICES, SEED_ITEMS


def seed(db: Session) -> None:
    category_map: dict[str, PriceCategory] = {}

    for cat_data in SEED_CATEGORIES:
        existing = db.query(PriceCategory).filter_by(code=cat_data["code"]).first()
        if existing:
            existing.name = cat_data["name"]
            existing.icon = cat_data["icon"]
            category_map[cat_data["code"]] = existing
            continue
        category = PriceCategory(**cat_data)
        db.add(category)
        db.flush()
        category_map[cat_data["code"]] = category

    for item_data in SEED_ITEMS:
        category = category_map[item_data["category_code"]]
        existing = db.query(PriceItem).filter_by(code=item_data["code"]).first()
        if existing:
            existing.name = item_data["name"]
            existing.unit = item_data["unit"]
            existing.source = item_data["source"]
            existing.region = item_data["region"]
            existing.category_id = category.id
            continue
        db.add(
            PriceItem(
                category_id=category.id,
                code=item_data["code"],
                name=item_data["name"],
                unit=item_data["unit"],
                source=item_data["source"],
                region=item_data["region"],
            )
        )

    db.commit()


def seed_demo_prices(db: Session) -> int:
    today = date.today()
    count = 0

    for row in SEED_DEMO_PRICES:
        item = db.query(PriceItem).filter_by(code=row["item_code"]).first()
        if not item:
            continue

        existing = (
            db.query(PriceRecord).filter_by(item_id=item.id, record_date=today).first()
        )
        if existing:
            continue

        db.add(
            PriceRecord(
                item_id=item.id,
                record_date=today,
                price=Decimal(row["price"]),
                change_pct=Decimal(row["change_pct"]) if row.get("change_pct") is not None else None,
            )
        )
        count += 1

    db.commit()
    return count


if __name__ == "__main__":
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        seed(session)
        print("Seed completed.")
    finally:
        session.close()
