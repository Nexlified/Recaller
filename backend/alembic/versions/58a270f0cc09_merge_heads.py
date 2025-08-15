"""merge_heads

Revision ID: 58a270f0cc09
Revises: 015_add_journal_life_metrics, 25ac7038b3f4
Create Date: 2025-08-15 18:48:55.963006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58a270f0cc09'
down_revision = ('015_add_journal_life_metrics', '25ac7038b3f4')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
