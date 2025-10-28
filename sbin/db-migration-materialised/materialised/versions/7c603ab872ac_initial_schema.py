"""Initial Schema

Revision ID: 7c603ab872ac
Revises:
Create Date: 2025-09-30 13:44:12.311962

"""

from typing import Sequence, Union

from alembic.op import create_table, drop_table
from sqlalchemy import Column, Integer, String, Date, Float


# revision identifiers, used by Alembic.
revision: str = "7c603ab872ac"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_table(
        "nb_refund_aotg",
        Column("as_on_date", Date, nullable=False),
        Column("branch", String(32), nullable=False),
        Column("broad_segment", String(32), nullable=False),
        Column("channel", String(32), nullable=False),
        Column("lob", String(32), nullable=False),
        Column("product", String(32), nullable=False),
        Column("region", String(32), nullable=False),
        Column("zone", String(32), nullable=False),
        Column("month", String(6), nullable=False),
        Column("mtd_refund_amt", Float(precision=2), nullable=False),
    )

    create_table(
        "rolling_persistency_aotg",
        Column("as_on_date", Date, nullable=False),
        Column("branch", String(32), nullable=False),
        Column("broad_segment", String(32), nullable=False),
        Column("channel", String(32), nullable=False),
        Column("lob", String(32), nullable=False),
        Column("product", String(32), nullable=False),
        Column("region", String(32), nullable=False),
        Column("zone", String(32), nullable=False),
        Column("month", String(6), nullable=False),
        Column("period", String(3), nullable=False),
        Column("cy_collectable", Float(precision=2), nullable=False),
        Column("cy_collected", Float(precision=2), nullable=False),
    )

    create_table(
        "v_realtime_cashiering",
        Column("as_on_date", Date, nullable=False),
        Column("branch", String(32), nullable=False),
        Column("broad_segment", String(32), nullable=False),
        Column("channel", String(32), nullable=False),
        Column("lob", String(32), nullable=False),
        Column("product", String(32), nullable=False),
        Column("region", String(32), nullable=False),
        Column("zone", String(32), nullable=False),
        Column("month", String(6), nullable=False),
        Column("nb_realtime_cash_act", Float(precision=2), nullable=False),
        Column("nb_realtime_cash_rtd", Float(precision=2), nullable=False),
        Column("rp_reatime_cash", Float(precision=2), nullable=False),
    )

    create_table(
        "budget_achievement",
        Column("channel", String(32), nullable=False),
        Column("region", String(32), nullable=False),
        Column("lob", String(32), nullable=False),
        Column("broad_segment", String(32), nullable=False),
        Column("as_on_date", Date, nullable=False),
        Column("month", String(6), nullable=False),
        Column("cy_mtd_bud", Float(precision=2), nullable=False),
        Column("cy_mtd_bud_rtd", Float(precision=2), nullable=False),
        Column("cy_mtd_act", Float(precision=2), nullable=False),
        Column("cy_mtd_rtd", Float(precision=2), nullable=False),
        Column("cy_mtd_act_cash", Float(precision=2), nullable=False),
        Column("cy_mtd_rtd_cash", Float(precision=2), nullable=False),
        Column("cy_ytd_bud", Float(precision=2), nullable=False),
        Column("cy_ytd_bud_rtd", Float(precision=2), nullable=False),
        Column("cy_ytd_act", Float(precision=2), nullable=False),
        Column("cy_ytd_rtd", Float(precision=2), nullable=False),
        Column("cy_ytd_act_cash", Float(precision=2), nullable=False),
        Column("cy_ytd_rtd_cash", Float(precision=2), nullable=False),
        Column("ly_mtd_act", Float(precision=2), nullable=False),
        Column("ly_mtd_rtd", Float(precision=2), nullable=False),
        Column("ly_mtd_act_cash", Float(precision=2), nullable=False),
        Column("ly_mtd_rtd_cash", Float(precision=2), nullable=False),
        Column("ly_ytd_act", Float(precision=2), nullable=False),
        Column("ly_ytd_rtd", Float(precision=2), nullable=False),
        Column("ly_ytd_act_cash", Float(precision=2), nullable=False),
        Column("ly_ytd_rtd_cash", Float(precision=2), nullable=False),
        Column("ytd_shortfall", Float(precision=2), nullable=False),
        Column("ytd_shortfall_rtd", Float(precision=2), nullable=False),
        Column("ytd_cash_shortfall", Float(precision=2), nullable=False),
        Column("ytd_cash_shortfall_rtd", Float(precision=2), nullable=False),
        Column("mtd_shortfall", Float(precision=2), nullable=False),
        Column("mtd_shortfall_rtd", Float(precision=2), nullable=False),
        Column("mtd_cash_shortfall", Float(precision=2), nullable=False),
        Column("mtd_cash_shortfall_rtd", Float(precision=2), nullable=False),
        Column("ren_cy_mtd_bud", Float(precision=2), nullable=False),
        Column("ren_cy_mtd_act", Float(precision=2), nullable=False),
        Column("ren_ly_mtd_act", Float(precision=2), nullable=False),
        Column("ren_mtd_shortfall", Float(precision=2), nullable=False),
        Column("ren_mtd_budget_ach", Float(precision=2), nullable=False),
        Column("ren_cy_ytd_bud", Float(precision=2), nullable=False),
        Column("ren_cy_ytd_act", Float(precision=2), nullable=False),
        Column("ren_ly_ytd_act", Float(precision=2), nullable=False),
        Column("ren_ytd_shortfall", Float(precision=2), nullable=False),
        Column("ren_ytd_budget_ach", Float(precision=2), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    drop_table("nb_refund_aotg")
    drop_table("rolling_persistency_aotg")
    drop_table("v_realtime_cashiering")
    drop_table("budget_achievement")
