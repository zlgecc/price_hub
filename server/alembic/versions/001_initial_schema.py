"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("icon", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_categories_code", "price_categories", ["code"], unique=True)

    op.create_table(
        "price_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["price_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_items_category_id", "price_items", ["category_id"])
    op.create_index("ix_price_items_code", "price_items", ["code"], unique=True)

    op.create_table(
        "price_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("change_pct", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["price_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "record_date", name="uq_item_record_date"),
    )
    op.create_index("ix_price_records_item_id", "price_records", ["item_id"])
    op.create_index("ix_price_records_record_date", "price_records", ["record_date"])


def downgrade() -> None:
    op.drop_table("price_records")
    op.drop_table("price_items")
    op.drop_table("price_categories")
