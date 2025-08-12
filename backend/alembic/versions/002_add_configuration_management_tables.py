"""Add configuration management tables

Revision ID: 002
Revises: 001
Create Date: 2025-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create config_categories table
    op.create_table('config_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_key')
    )
    op.create_index(op.f('ix_config_categories_category_key'), 'config_categories', ['category_key'], unique=False)
    op.create_index(op.f('ix_config_categories_id'), 'config_categories', ['id'], unique=False)

    # Create config_types table
    op.create_table('config_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('type_key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(length=20), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['config_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_id', 'type_key')
    )
    op.create_index(op.f('ix_config_types_id'), 'config_types', ['id'], unique=False)
    op.create_index(op.f('ix_config_types_type_key'), 'config_types', ['type_key'], unique=False)

    # Create config_values table
    op.create_table('config_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('config_type_id', sa.Integer(), nullable=False),
        sa.Column('value_key', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_value_id', sa.Integer(), nullable=True),
        sa.Column('hierarchy_path', sa.String(length=500), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('extra_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('sync_version', sa.String(length=50), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['config_type_id'], ['config_types.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_value_id'], ['config_values.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_type_id', 'value_key', 'tenant_id')
    )
    op.create_index(op.f('ix_config_values_hierarchy_path'), 'config_values', ['hierarchy_path'], unique=False)
    op.create_index(op.f('ix_config_values_id'), 'config_values', ['id'], unique=False)
    op.create_index(op.f('ix_config_values_parent_value_id'), 'config_values', ['parent_value_id'], unique=False)
    op.create_index(op.f('ix_config_values_tenant_id'), 'config_values', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_config_values_value_key'), 'config_values', ['value_key'], unique=False)

    # Create config_value_translations table
    op.create_table('config_value_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_value_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['config_value_id'], ['config_values.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_value_id', 'language_code')
    )
    op.create_index(op.f('ix_config_value_translations_id'), 'config_value_translations', ['id'], unique=False)
    op.create_index(op.f('ix_config_value_translations_language_code'), 'config_value_translations', ['language_code'], unique=False)

    # Create config_sync_history table
    op.create_table('config_sync_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('config_type_id', sa.Integer(), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=False),
        sa.Column('sync_action', sa.String(length=20), nullable=False),
        sa.Column('sync_status', sa.String(length=20), nullable=False),
        sa.Column('changes_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('records_created', sa.Integer(), nullable=True),
        sa.Column('records_updated', sa.Integer(), nullable=True),
        sa.Column('records_deleted', sa.Integer(), nullable=True),
        sa.Column('errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('warnings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_version', sa.String(length=50), nullable=True),
        sa.Column('target_version', sa.String(length=50), nullable=True),
        sa.Column('triggered_by', sa.String(length=50), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['config_type_id'], ['config_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_sync_history_executed_at'), 'config_sync_history', ['executed_at'], unique=False)
    op.create_index(op.f('ix_config_sync_history_id'), 'config_sync_history', ['id'], unique=False)
    op.create_index(op.f('ix_config_sync_history_sync_session_id'), 'config_sync_history', ['sync_session_id'], unique=False)


def downgrade():
    op.drop_table('config_sync_history')
    op.drop_table('config_value_translations')
    op.drop_table('config_values')
    op.drop_table('config_types')
    op.drop_table('config_categories')