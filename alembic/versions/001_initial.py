"""Initial migration: pgvector extension, countries and climate_data tables

Revision ID: 001
Revises:
Create Date: 2026-02-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("iso_code", sa.String(2), nullable=False),
        sa.Column("iso3_code", sa.String(3), nullable=True),
        sa.Column("region", sa.String(255), nullable=True),
        sa.Column("capital_city", sa.String(255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("population", sa.Integer(), nullable=True),
    )
    op.create_index("ix_countries_iso_code", "countries", ["iso_code"], unique=True)

    op.create_table(
        "climate_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("country_id", sa.Integer(), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("metric_type", sa.String(100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
    )
    op.create_index("ix_climate_data_country_date", "climate_data", ["country_id", "date"])
    op.create_index("ix_climate_data_metric_type", "climate_data", ["metric_type"])


def downgrade() -> None:
    op.drop_table("climate_data")
    op.drop_table("countries")
    op.execute("DROP EXTENSION IF EXISTS vector")
