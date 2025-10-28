"""change_dim_product_column

Revision ID: 101ca36ec8bb
Revises: 21721eb18642
Create Date: 2025-09-29 08:01:33.173165

"""

from typing import Sequence, Union

from alembic.op import alter_column
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "101ca36ec8bb"
down_revision: Union[str, Sequence[str], None] = "21721eb18642"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    alter_column("dim_product", "prod_broad_seg_id", new_column_name="broad_segment_id")


def downgrade() -> None:
    """Downgrade schema."""
    alter_column("dim_product", "broad_segment_id", new_column_name="prod_broad_seg_id")
