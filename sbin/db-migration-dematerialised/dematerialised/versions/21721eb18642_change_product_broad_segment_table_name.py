"""Change product broad segment table name

Revision ID: 21721eb18642
Revises: aadacbda93b7
Create Date: 2025-09-26 18:34:19.606193

"""

from typing import Sequence, Union

from alembic.op import rename_table
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "21721eb18642"
down_revision: Union[str, Sequence[str], None] = "aadacbda93b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    rename_table("product_broad_segment", "dim_product_broad_segment")


def downgrade() -> None:
    """Downgrade schema."""
    rename_table("dim_product_broad_segment", "product_broad_segment")
