from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PriceCategory(Base):
    __tablename__ = "price_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(20), default="📊")

    items: Mapped[list["PriceItem"]] = relationship(back_populates="category")


class PriceItem(Base):
    __tablename__ = "price_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("price_categories.id"), index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str] = mapped_column(String(50), default="")
    source: Mapped[str] = mapped_column(String(100), default="")
    region: Mapped[str] = mapped_column(String(50), default="全国")

    category: Mapped["PriceCategory"] = relationship(back_populates="items")
    records: Mapped[list["PriceRecord"]] = relationship(back_populates="item")


class PriceRecord(Base):
    __tablename__ = "price_records"
    __table_args__ = (UniqueConstraint("item_id", "record_date", name="uq_item_record_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("price_items.id"), index=True)
    record_date: Mapped[date] = mapped_column(Date, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    change_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    item: Mapped["PriceItem"] = relationship(back_populates="records")
