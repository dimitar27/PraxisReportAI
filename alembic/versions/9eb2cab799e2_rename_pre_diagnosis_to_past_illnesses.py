"""Rename pre_diagnosis to past_illnesses

Revision ID: 9eb2cab799e2
Revises: 40eff33fb950
Create Date: 2025-06-11 11:23:57.250201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9eb2cab799e2'
down_revision: Union[str, None] = '40eff33fb950'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename pre_diagnosis → past_illnesses column in patients table."""
    op.alter_column('patients', 'pre_diagnosis', new_column_name='past_illnesses')


def downgrade() -> None:
    """Revert past_illnesses → pre_diagnosis rename in patients table."""
    op.alter_column('patients', 'past_illnesses', new_column_name='pre_diagnosis')
