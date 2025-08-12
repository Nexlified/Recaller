"""create event_tags table

Revision ID: 007_create_event_tags
Revises: 006_create_attendances
Create Date: 2025-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_create_event_tags'
down_revision = '006_create_attendances'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sa.String(100), nullable=False),
        sa.Column('tag_color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name=op.f('fk_event_tags_event_id_events')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'tag_name', name='uq_event_tag_name')
    )
    
    op.create_index(op.f('ix_event_tags_id'), 'event_tags', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_event_tags_id'), table_name='event_tags')
    op.drop_table('event_tags')