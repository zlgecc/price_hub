from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import PriceCategory, PriceItem, PriceRecord
from app.schemas.price import (
    CategoryOut,
    DashboardCategorySummary,
    DashboardOut,
    ItemDetailOut,
    ItemOut,
    PriceRecordOut,
)


def list_categories(db: Session) -> list[CategoryOut]:
    categories = db.query(PriceCategory).order_by(PriceCategory.id).all()
    return [CategoryOut.model_validate(c) for c in categories]


def list_items(
    db: Session,
    category: str | None = None,
    region: str | None = None,
    search: str | None = None,
) -> list[ItemOut]:
    query = db.query(PriceItem).options(joinedload(PriceItem.category))
    if category:
        query = query.join(PriceCategory).filter(PriceCategory.code == category)
    if region:
        query = query.filter(PriceItem.region == region)
    if search:
        query = query.filter(PriceItem.name.ilike(f"%{search}%"))
    items = query.order_by(PriceItem.id).all()
    return [_item_to_out(db, item) for item in items]


def get_item_detail(db: Session, code: str, days: int = 30) -> ItemDetailOut | None:
    item = (
        db.query(PriceItem)
        .options(joinedload(PriceItem.category))
        .filter(PriceItem.code == code)
        .first()
    )
    if not item:
        return None
    since = date.today() - timedelta(days=days)
    records = (
        db.query(PriceRecord)
        .filter(PriceRecord.item_id == item.id, PriceRecord.record_date >= since)
        .order_by(PriceRecord.record_date)
        .all()
    )
    base = _item_to_out(db, item)
    return ItemDetailOut(
        **base.model_dump(),
        history=[PriceRecordOut.model_validate(r) for r in records],
    )


def get_dashboard(db: Session) -> DashboardOut:
    categories = db.query(PriceCategory).order_by(PriceCategory.id).all()
    summaries: list[DashboardCategorySummary] = []
    latest_fetch: datetime | None = None

    max_fetched = db.query(func.max(PriceRecord.fetched_at)).scalar()
    if max_fetched:
        latest_fetch = max_fetched

    for cat in categories:
        items = (
            db.query(PriceItem)
            .options(joinedload(PriceItem.category))
            .filter(PriceItem.category_id == cat.id)
            .order_by(PriceItem.id)
            .all()
        )
        item_outs = [_item_to_out(db, item) for item in items]
        # Prefer items that already have a latest price so empty Key-only
        # placeholders (e.g. provincial oil) do not dominate the dashboard.
        with_price = [item for item in item_outs if item.latest_price is not None]
        without_price = [item for item in item_outs if item.latest_price is None]
        sample_items = (with_price + without_price)[:5]
        summaries.append(
            DashboardCategorySummary(
                category_code=cat.code,
                category_name=cat.name,
                icon=cat.icon,
                item_count=len(item_outs),
                sample_items=sample_items,
            )
        )

    return DashboardOut(categories=summaries, updated_at=latest_fetch)


def _item_to_out(db: Session, item: PriceItem) -> ItemOut:
    latest = (
        db.query(PriceRecord)
        .filter(PriceRecord.item_id == item.id)
        .order_by(PriceRecord.record_date.desc())
        .first()
    )
    return ItemOut(
        id=item.id,
        code=item.code,
        name=item.name,
        unit=item.unit,
        source=item.source,
        region=item.region,
        category_code=item.category.code,
        category_name=item.category.name,
        latest_price=latest.price if latest else None,
        change_pct=latest.change_pct if latest else None,
        record_date=latest.record_date if latest else None,
    )
