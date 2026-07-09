from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    icon: str


class PriceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_date: date
    price: Decimal
    change_pct: Decimal | None = None

    @field_serializer("price", "change_pct")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    unit: str
    source: str
    region: str
    category_code: str
    category_name: str
    latest_price: Decimal | None = None
    change_pct: Decimal | None = None
    record_date: date | None = None

    @field_serializer("latest_price", "change_pct")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class ItemDetailOut(ItemOut):
    history: list[PriceRecordOut] = []


class DashboardCategorySummary(BaseModel):
    category_code: str
    category_name: str
    icon: str
    item_count: int
    sample_items: list[ItemOut]


class DashboardOut(BaseModel):
    categories: list[DashboardCategorySummary]
    updated_at: datetime | None = None


class PriceRecordCreate(BaseModel):
    item_code: str
    record_date: date
    price: Decimal
    change_pct: Decimal | None = None


class FetchResult(BaseModel):
    source: str
    success: bool
    records_count: int
    error: str | None = None
