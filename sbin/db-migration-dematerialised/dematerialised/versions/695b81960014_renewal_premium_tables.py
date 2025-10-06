"""Renewal Premium tables

Revision ID: 695b81960014
Revises: 8246618e0950
Create Date: 2025-10-06 10:55:22.728831

"""

from typing import Sequence, Union

from alembic.op import create_table, drop_table, create_index, drop_index
from sqlalchemy import Column, Date, Numeric, String


# revision identifiers, used by Alembic.
revision: str = "695b81960014"
down_revision: Union[str, Sequence[str], None] = "8246618e0950"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_table(
        "fact_rp_budget",
        Column("rp_budget_id", Numeric, primary_key=True),
        Column("current_flag", Numeric),
        Column("product_id", Numeric),
        Column("region_id", Numeric),
        Column("sub_channel_id", Numeric),
        Column("rp", Numeric(32, 8)),
    )

    # Create indices
    create_index("idx_fact_rp_budget_product_id", "fact_rp_budget", ["product_id"])
    create_index("idx_fact_rp_budget_region_id", "fact_rp_budget", ["region_id"])
    create_index(
        "idx_fact_rp_budget_sub_channel_id", "fact_rp_budget", ["sub_channel_id"]
    )
    create_index("idx_fact_rp_budget_current_flag", "fact_rp_budget", ["current_flag"])

    create_table(
        "fact_rp_actual",
        Column("rp_actual_id", Numeric, primary_key=True),
        Column("date", Date),
        Column("region_id", Numeric),
        Column("sub_channel_id", Numeric),
        Column("policytechnicalid", String(50)),
        Column("rp_premium", Numeric(32, 8)),
        Column("rp_cancellations_amount", Numeric(32, 8)),
        Column("rp_gross", Numeric(32, 8)),
        Column("rp_service_tax", Numeric(32, 8)),
        Column("rp_entry_fee", Numeric(32, 8)),
        Column("rated_rp", Numeric(32, 8)),
        Column("rated_rp_gross", Numeric(32, 8)),
        Column("rated_rp_service_tax", Numeric(32, 8)),
        Column("rated_rp_entry_fee", Numeric(32, 8)),
    )

    # Create indices
    create_index("idx_fact_rp_actual_date", "fact_rp_actual", ["date"])
    create_index("idx_fact_rp_actual_region_id", "fact_rp_actual", ["region_id"])
    create_index(
        "idx_fact_rp_actual_sub_channel_id", "fact_rp_actual", ["sub_channel_id"]
    )
    create_index(
        "idx_fact_rp_actual_policytechnicalid", "fact_rp_actual", ["policytechnicalid"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indices
    drop_index("idx_fact_rp_budget_current_flag", "fact_rp_budget")
    drop_index("idx_fact_rp_budget_sub_channel_id", "fact_rp_budget")
    drop_index("idx_fact_rp_budget_region_id", "fact_rp_budget")
    drop_index("idx_fact_rp_budget_product_id", "fact_rp_budget")

    # Drop table
    drop_table("fact_rp_budget")

    # Drop indices
    drop_index("idx_fact_rp_actual_policytechnicalid", "fact_rp_actual")
    drop_index("idx_fact_rp_actual_sub_channel_id", "fact_rp_actual")
    drop_index("idx_fact_rp_actual_region_id", "fact_rp_actual")
    drop_index("idx_fact_rp_actual_date", "fact_rp_actual")

    # Drop table
    drop_table("fact_rp_actual")
