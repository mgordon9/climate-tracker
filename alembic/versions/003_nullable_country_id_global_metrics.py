"""Make climate_data.country_id nullable to support global metrics

Revision ID: 003
Revises: 002
Create Date: 2026-03-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("climate_data", "country_id", nullable=True)


def downgrade() -> None:
    # Rows with NULL country_id must be removed before downgrading
    op.execute("DELETE FROM climate_data WHERE country_id IS NULL")
    op.alter_column("climate_data", "country_id", nullable=False)
