"""Create journal tables

Revision ID: 012_create_journal_tables
Revises: 011_add_task_scheduler_fields
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012_create_journal_tables'
down_revision = '011_add_task_scheduler_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create journal_entries table
    op.create_table('journal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('mood', sa.String(length=20), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('weather', sa.String(length=100), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('entry_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_entry_id'], ['journal_entries.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for journal_entries
    op.create_index(op.f('ix_journal_entries_id'), 'journal_entries', ['id'])
    op.create_index(op.f('ix_journal_entries_tenant_id'), 'journal_entries', ['tenant_id'])
    op.create_index(op.f('ix_journal_entries_user_id'), 'journal_entries', ['user_id'])
    op.create_index(op.f('ix_journal_entries_entry_date'), 'journal_entries', ['entry_date'])
    op.create_index(op.f('ix_journal_entries_mood'), 'journal_entries', ['mood'])
    op.create_index(op.f('ix_journal_entries_is_archived'), 'journal_entries', ['is_archived'])
    op.create_index('ix_journal_entries_tenant_user_date', 'journal_entries', ['tenant_id', 'user_id', 'entry_date'])
    op.create_index('ix_journal_entries_user_archived', 'journal_entries', ['user_id', 'is_archived'])
    
    # Create journal_tags table
    op.create_table('journal_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('journal_entry_id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sa.String(length=50), nullable=False),
        sa.Column('tag_color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('journal_entry_id', 'tag_name', name='uq_journal_tags_entry_name')
    )
    
    # Create indexes for journal_tags
    op.create_index(op.f('ix_journal_tags_id'), 'journal_tags', ['id'])
    op.create_index(op.f('ix_journal_tags_journal_entry_id'), 'journal_tags', ['journal_entry_id'])
    op.create_index(op.f('ix_journal_tags_tag_name'), 'journal_tags', ['tag_name'])
    
    # Create journal_attachments table
    op.create_table('journal_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('journal_entry_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for journal_attachments
    op.create_index(op.f('ix_journal_attachments_id'), 'journal_attachments', ['id'])
    op.create_index(op.f('ix_journal_attachments_journal_entry_id'), 'journal_attachments', ['journal_entry_id'])


def downgrade():
    # Drop journal_attachments table
    op.drop_index(op.f('ix_journal_attachments_journal_entry_id'), table_name='journal_attachments')
    op.drop_index(op.f('ix_journal_attachments_id'), table_name='journal_attachments')
    op.drop_table('journal_attachments')
    
    # Drop journal_tags table
    op.drop_index(op.f('ix_journal_tags_tag_name'), table_name='journal_tags')
    op.drop_index(op.f('ix_journal_tags_journal_entry_id'), table_name='journal_tags')
    op.drop_index(op.f('ix_journal_tags_id'), table_name='journal_tags')
    op.drop_table('journal_tags')
    
    # Drop journal_entries table
    op.drop_index('ix_journal_entries_user_archived', table_name='journal_entries')
    op.drop_index('ix_journal_entries_tenant_user_date', table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_is_archived'), table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_mood'), table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_entry_date'), table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_user_id'), table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_tenant_id'), table_name='journal_entries')
    op.drop_index(op.f('ix_journal_entries_id'), table_name='journal_entries')
    op.drop_table('journal_entries')