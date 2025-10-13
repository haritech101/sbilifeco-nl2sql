"""Ground 0 schema

Revision ID: aadacbda93b7
Revises:
Create Date: 2025-09-26 10:28:11.341465

"""

from random import choice, randint
from typing import Sequence, Union

from alembic.op import create_table, drop_table, create_primary_key, bulk_insert
from sqlalchemy import Column, Integer, String, ForeignKey, Date, table, column
from faker import Faker


# revision identifiers, used by Alembic.
revision: str = "aadacbda93b7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    the_faker = Faker()
    the_faker.seed_instance(42)

    # Regions
    regions_table = create_table(
        "dim_region",
        Column("region_id", Integer, primary_key=True, autoincrement=True),
        Column("region", String(64), nullable=False, unique=True),
        Column("zone", String(64)),
    )

    bulk_insert(
        regions_table,
        [
            {"region": "Ahmedabad", "zone": "West"},
            {"region": "Andhra Pradesh", "zone": "South"},
            {"region": "Bengaluru", "zone": "South"},
            {"region": "Bhopal", "zone": "Central"},
            {"region": "Bhubaneswar", "zone": "East"},
            {"region": "Chandigarh", "zone": "North"},
            {"region": "Chennai", "zone": "South"},
            {"region": "Data Centre", "zone": None},
            {"region": "Delhi", "zone": "North"},
            {"region": "Jaipur", "zone": "North"},
            {"region": "Kerala", "zone": "South"},
            {"region": "Lucknow", "zone": "North"},
            {"region": "Maharashtra", "zone": "West"},
            {"region": "Mumbai Metro", "zone": "West"},
            {"region": "North East", "zone": "East"},
            {"region": "Patna", "zone": "East"},
            {"region": "Telangana", "zone": "South"},
            {"region": "West Bengal", "zone": "East"},
        ],
        multiinsert=False,
    )

    master_channel_table = create_table(
        "dim_master_channel",
        Column("masterchannel_id", Integer, primary_key=True, autoincrement=True),
        Column("master_channel_name", String(64), nullable=False, unique=True),
    )
    bulk_insert(master_channel_table, [{"master_channel_name": "Root"}])

    sub_channels_table = create_table(
        "dim_sub_channel",
        Column("subchannel_id", Integer, primary_key=True, autoincrement=True),
        Column("sub_channel_name", String(64), nullable=False, unique=True),
        Column(
            "master_channel_id",
            Integer,
            ForeignKey("dim_master_channel.masterchannel_id"),
            nullable=False,
        ),
    )
    bulk_insert(
        sub_channels_table,
        [
            {"sub_channel_name": channel, "master_channel_id": 1}
            for channel in [
                "SBI",
                "RRB",
                "Retail Agency",
                "Institutional Alliances",
                "Emerging Business",
                "Corporate Solutions",
                "Others",
            ]
        ],
    )

    segments_table = create_table(
        "product_broad_segment",
        Column("prod_broad_seg_id", Integer, primary_key=True, autoincrement=True),
        Column("broad_segment", String(64), nullable=False, unique=True),
    )
    bulk_insert(
        segments_table,
        [
            {"broad_segment": segment}
            for segment in [
                "ULIP",
                "Par",
                "Non Par - Protection",
                "Non Par - Annuity",
                "Non Par - Others",
                "Credit Life",
                "Group Annuity",
                "Group Others",
                "PMJJBY",
                "GTI - Others",
                "FMC",
            ]
        ],
    )

    products_table = create_table(
        "dim_product",
        Column("product_id", Integer, primary_key=True, autoincrement=True),
        Column("product_name", String(128), nullable=False, unique=True),
        Column(
            "prod_broad_seg_id",
            Integer,
            ForeignKey("product_broad_segment.prod_broad_seg_id"),
            nullable=False,
        ),
        Column("lob", String(64), nullable=False),
    )

    num_products = randint(25, 50)
    bulk_insert(
        products_table,
        [
            {
                "product_name": f"{the_faker.word()} {the_faker.word()}",
                "prod_broad_seg_id": randint(1, 11),
                "lob": choice(["Individual", "Group", "Group Corporate"]),
            }
            for _ in range(num_products)
        ],
    )

    create_table(
        "policy",
        Column("policytechnicalid", String(64)),
        Column("policycurrentstatus", String(32)),
        Column("policysumassured", Integer, nullable=False, default=0),
        Column(
            "productid", Integer, ForeignKey("dim_product.product_id"), nullable=False
        ),
        Column("policyannualizedpremiium", Integer, nullable=False, default=0),
    )
    create_primary_key(
        constraint_name="pk_policytechnicalid",
        table_name="policy",
        columns=["policytechnicalid"],
    )

    create_table(
        "fact_nbp_actual",
        Column("nbp_actual_id", Integer, primary_key=True, autoincrement=True),
        Column("nbp", Integer, nullable=False, default=0),
        Column("rated_nbp", Integer, nullable=False, default=0),
        Column("nbp_gross", Integer, nullable=False, default=0),
        Column("rated_nbp_gross", Integer, nullable=False, default=0),
        Column("policy_id", String(64), ForeignKey("policy.policytechnicalid")),
        Column("sub_channel_id", Integer, ForeignKey("dim_sub_channel.subchannel_id")),
        Column("region_id", Integer, ForeignKey("dim_region.region_id")),
        Column("date", Date, nullable=False),
    )

    create_table(
        "fact_nbp_budget",
        Column("nbp_budget_id", Integer, primary_key=True, autoincrement=True),
        Column("nbp", Integer, nullable=False, default=0),
        Column("rated_nbp", Integer, nullable=False, default=0),
        Column("nbp_gross", Integer, nullable=False, default=0),
        Column("rated_nbp_gross", Integer, nullable=False, default=0),
        Column("product_id", Integer, ForeignKey("dim_product.product_id")),
        Column("sub_channel_id", Integer, ForeignKey("dim_sub_channel.subchannel_id")),
        Column("region_id", Integer, ForeignKey("dim_region.region_id")),
        Column("current_flag", Integer, nullable=False, default=0),
    )


def downgrade() -> None:
    """Downgrade schema."""
    drop_table("fact_nbp_actual")
    drop_table("fact_nbp_budget")
    drop_table("dim_region")
    drop_table("policy")
    drop_table("dim_product")
    drop_table("product_broad_segment")
    drop_table("dim_sub_channel")
    drop_table("dim_master_channel")
