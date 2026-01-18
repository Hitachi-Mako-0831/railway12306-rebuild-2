"""Generic single-database configuration."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

