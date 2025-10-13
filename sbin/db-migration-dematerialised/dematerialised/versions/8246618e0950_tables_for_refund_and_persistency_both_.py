"""Tables for refund and persistency: both are materialised

Revision ID: 8246618e0950
Revises: ad7d5c290705
Create Date: 2025-10-06 08:46:58.743955

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8246618e0950"
down_revision: Union[str, Sequence[str], None] = "ad7d5c290705"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # create table nb_refund_aotg(
    #     as_on_date date not null,
    #     branch varchar(32) not null,
    #     broad_segment varchar(32) not null,
    #     channel varchar(32) not null,
    #     lob varchar(32) not null,
    #     product varchar(32) not null,
    #     region varchar(32) not null,
    #     zone varchar(32) not null,
    #     month varchar(6) not null,
    #     mtd_refund_amt numeric(13,2) not null
    # );

    # create table rolling_persistency_aotg(
    #     as_on_date date not null,
    #     branch varchar(32) not null,
    #     broad_segment varchar(32) not null,
    #     channel varchar(32) not null,
    #     lob varchar(32) not null,
    #     product varchar(32) not null,
    #     region varchar(32) not null,
    #     zone varchar(32) not null,
    #     month varchar(6) not null,
    #     period varchar(3) not null,
    #     cy_collectable numeric(13,2) not null,
    #     cy_collected numeric(13,2) not null
    # );
    # Create nb_refund_aotg table
    op.create_table(
        "nb_refund_aotg",
        sa.Column("as_on_date", sa.Date(), nullable=False),
        sa.Column("branch", sa.String(32), nullable=False),
        sa.Column("broad_segment", sa.String(32), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("lob", sa.String(32), nullable=False),
        sa.Column("product", sa.String(32), nullable=False),
        sa.Column("region", sa.String(32), nullable=False),
        sa.Column("zone", sa.String(32), nullable=False),
        sa.Column("month", sa.String(6), nullable=False),
        sa.Column("mtd_refund_amt", sa.Numeric(13, 2), nullable=False),
    )
    # Create indices for nb_refund_aotg table
    op.create_index("idx_nb_refund_aotg_month", "nb_refund_aotg", ["month"])
    op.create_index("idx_nb_refund_aotg_region", "nb_refund_aotg", ["region"])
    op.create_index("idx_nb_refund_aotg_zone", "nb_refund_aotg", ["zone"])
    op.create_index("idx_nb_refund_aotg_product", "nb_refund_aotg", ["product"])
    op.create_index("idx_nb_refund_aotg_lob", "nb_refund_aotg", ["lob"])
    op.create_index("idx_nb_refund_aotg_channel", "nb_refund_aotg", ["channel"])
    op.create_index(
        "idx_nb_refund_aotg_broad_segment", "nb_refund_aotg", ["broad_segment"]
    )
    op.create_index("idx_nb_refund_aotg_branch", "nb_refund_aotg", ["branch"])

    # Create rolling_persistency_aotg table
    op.create_table(
        "rolling_persistency_aotg",
        sa.Column("as_on_date", sa.Date(), nullable=False),
        sa.Column("branch", sa.String(32), nullable=False),
        sa.Column("broad_segment", sa.String(32), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("lob", sa.String(32), nullable=False),
        sa.Column("product", sa.String(32), nullable=False),
        sa.Column("region", sa.String(32), nullable=False),
        sa.Column("zone", sa.String(32), nullable=False),
        sa.Column("month", sa.String(6), nullable=False),
        sa.Column("period", sa.String(3), nullable=False),
        sa.Column("cy_collectable", sa.Numeric(13, 2), nullable=False),
        sa.Column("cy_collected", sa.Numeric(13, 2), nullable=False),
    )
    # Create indices for rolling_persistency_aotg table
    op.create_index(
        "idx_rolling_persistency_aotg_branch", "rolling_persistency_aotg", ["branch"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_broad_segment",
        "rolling_persistency_aotg",
        ["broad_segment"],
    )
    op.create_index(
        "idx_rolling_persistency_aotg_channel", "rolling_persistency_aotg", ["channel"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_lob", "rolling_persistency_aotg", ["lob"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_product", "rolling_persistency_aotg", ["product"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_region", "rolling_persistency_aotg", ["region"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_zone", "rolling_persistency_aotg", ["zone"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_month", "rolling_persistency_aotg", ["month"]
    )
    op.create_index(
        "idx_rolling_persistency_aotg_period", "rolling_persistency_aotg", ["period"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indices for rolling_persistency_aotg table
    op.drop_index("idx_rolling_persistency_aotg_period", "rolling_persistency_aotg")
    op.drop_index("idx_rolling_persistency_aotg_month", "rolling_persistency_aotg")
    op.drop_index("idx_rolling_persistency_aotg_zone", "rolling_persistency_aotg")
    op.drop_index("idx_rolling_persistency_aotg_region", "rolling_persistency_aotg")
    op.drop_index("idx_rolling_persistency_aotg_product", "rolling_persistency_aotg")
    op.drop_index("idx_rolling_persistency_aotg_lob", "rolling_persistency_aotg")
    op.drop_index("idx_rolling_persistency_aotg_channel", "rolling_persistency_aotg")
    op.drop_index(
        "idx_rolling_persistency_aotg_broad_segment", "rolling_persistency_aotg"
    )
    op.drop_index("idx_rolling_persistency_aotg_branch", "rolling_persistency_aotg")

    # Drop rolling_persistency_aotg table
    op.drop_table("rolling_persistency_aotg")

    # Drop indices for nb_refund_aotg table
    op.drop_index("idx_nb_refund_aotg_branch", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_broad_segment", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_channel", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_lob", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_product", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_zone", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_region", "nb_refund_aotg")
    op.drop_index("idx_nb_refund_aotg_month", "nb_refund_aotg")

    # Drop nb_refund_aotg table
    op.drop_table("nb_refund_aotg")
