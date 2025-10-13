"""Create indices for existing tables

Revision ID: ad7d5c290705
Revises: 101ca36ec8bb
Create Date: 2025-10-06 08:24:20.959715

"""

from typing import Sequence, Union

from alembic.op import create_index, drop_index, alter_column

# revision identifiers, used by Alembic.
revision: str = "ad7d5c290705"
down_revision: Union[str, Sequence[str], None] = "101ca36ec8bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First of all, fix column name typo in policy table
    alter_column(
        "policy",
        "policyannualizedpremiium",
        new_column_name="policyannualizedpremium",
    )

    """Upgrade schema."""
    # 1. dim_region table indices
    create_index("idx_dim_region_region", "dim_region", ["region"])
    create_index("idx_dim_region_zone", "dim_region", ["zone"])

    # 2. dim_master_channel table index
    create_index(
        "idx_dim_master_channel_name", "dim_master_channel", ["master_channel_name"]
    )

    # 3. dim_sub_channel table index
    create_index(
        "idx_sub_channels_sub_channel_name", "dim_sub_channel", ["sub_channel_name"]
    )

    # 4. dim_product_broad_segment table index
    create_index(
        "idx_dim_product_broad_segment_broad_segment",
        "dim_product_broad_segment",
        ["broad_segment"],
    )

    # 5. dim_product table indices
    create_index("idx_dim_product_product_name", "dim_product", ["product_name"])
    create_index("idx_dim_product_lob", "dim_product", ["lob"])
    create_index(
        "idx_dim_product_prod_broad_seg_id", "dim_product", ["broad_segment_id"]
    )

    # 6. policy table indices
    create_index("idx_policy_productid", "policy", ["productid"])
    create_index("idx_policy_policycurrentstatus", "policy", ["policycurrentstatus"])
    create_index("idx_policy_policysumassured", "policy", ["policysumassured"])
    create_index(
        "idx_policy_policyannualizedpremium", "policy", ["policyannualizedpremium"]
    )

    # 7. fact_nbp_actual table indices
    create_index("idx_fact_nbp_actual_policy_id", "fact_nbp_actual", ["policy_id"])
    create_index(
        "idx_fact_nbp_actual_sub_channel_id", "fact_nbp_actual", ["sub_channel_id"]
    )
    create_index("idx_fact_nbp_actual_region_id", "fact_nbp_actual", ["region_id"])
    create_index("idx_fact_nbp_actual_date", "fact_nbp_actual", ["date"])

    # 8. fact_nbp_budget table indices
    create_index("idx_fact_nbp_budget_product_id", "fact_nbp_budget", ["product_id"])
    create_index(
        "idx_fact_nbp_budget_sub_channel_id", "fact_nbp_budget", ["sub_channel_id"]
    )
    create_index("idx_fact_nbp_budget_region_id", "fact_nbp_budget", ["region_id"])
    create_index(
        "idx_fact_nbp_budget_current_flag", "fact_nbp_budget", ["current_flag"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indices in reverse order
    # fact_nbp_budget table indices
    drop_index("idx_fact_nbp_budget_current_flag")
    drop_index("idx_fact_nbp_budget_region_id")
    drop_index("idx_fact_nbp_budget_sub_channel_id")
    drop_index("idx_fact_nbp_budget_product_id")

    # fact_nbp_actual table indices
    drop_index("idx_fact_nbp_actual_date")
    drop_index("idx_fact_nbp_actual_region_id")
    drop_index("idx_fact_nbp_actual_sub_channel_id")
    drop_index("idx_fact_nbp_actual_policy_id")

    # policy table indices
    drop_index("idx_policy_policyannualizedpremium")
    drop_index("idx_policy_policysumassured")
    drop_index("idx_policy_policycurrentstatus")
    drop_index("idx_policy_productid")

    # dim_product table indices
    drop_index("idx_dim_product_prod_broad_seg_id")
    drop_index("idx_dim_product_lob")
    drop_index("idx_dim_product_product_name")

    # dim_product_broad_segment table index
    drop_index("idx_dim_product_broad_segment_broad_segment")

    # dim_sub_channel table index
    drop_index("idx_sub_channels_sub_channel_name")

    # dim_master_channel table index
    drop_index("idx_dim_master_channel_name")

    # dim_region table indices
    drop_index("idx_dim_region_zone")
    drop_index("idx_dim_region_region")
