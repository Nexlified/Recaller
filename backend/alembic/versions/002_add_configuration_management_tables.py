"""add configuration management tables

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
    op.create_table(
        'config_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('config_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_key', name='uq_config_categories_category_key')
    )
    op.create_index('ix_config_categories_category_key', 'config_categories', ['category_key'], unique=False)
    op.create_index('ix_config_categories_id', 'config_categories', ['id'], unique=False)
    op.create_index('ix_config_categories_is_active', 'config_categories', ['is_active'], unique=False)
    op.create_index('ix_config_categories_sort_order', 'config_categories', ['sort_order'], unique=False)

    # Create config_types table
    op.create_table(
        'config_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('type_key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(length=20), nullable=True, server_default='enum'),
        sa.Column('max_level', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('allows_custom_values', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_system', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_version', sa.String(length=50), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('config_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['config_categories.id'], name='fk_config_types_category_id_config_categories', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_config_types_data_type', 'config_types', ['data_type'], unique=False)
    op.create_index('ix_config_types_id', 'config_types', ['id'], unique=False)
    op.create_index('ix_config_types_is_active', 'config_types', ['is_active'], unique=False)
    op.create_index('uq_config_types_category_key', 'config_types', ['category_id', 'type_key'], unique=True)

    # Create config_values table
    op.create_table(
        'config_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('config_type_id', sa.Integer(), nullable=False),
        sa.Column('value_key', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_value_id', sa.Integer(), nullable=True),
        sa.Column('hierarchy_path', sa.String(length=500), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('has_children', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('children_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('value_metadata', sa.JSON(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('custom_properties', sa.JSON(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_system', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_custom', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('sync_version', sa.String(length=50), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['config_type_id'], ['config_types.id'], name='fk_config_values_config_type_id_config_types', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_config_values_created_by_users'),
        sa.ForeignKeyConstraint(['parent_value_id'], ['config_values.id'], name='fk_config_values_parent_value_id_config_values', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_config_values_tenant_id_tenants', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_config_values_updated_by_users'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_config_values_custom_props', 'config_values', ['custom_properties'], unique=False, postgresql_using='gin')
    op.create_index('idx_config_values_hierarchy_path', 'config_values', ['hierarchy_path'], unique=False)
    op.create_index('idx_config_values_value_metadata', 'config_values', ['value_metadata'], unique=False, postgresql_using='gin')
    op.create_index('ix_config_values_id', 'config_values', ['id'], unique=False)
    op.create_index('ix_config_values_is_active', 'config_values', ['is_active'], unique=False)
    op.create_index('ix_config_values_is_custom', 'config_values', ['is_custom'], unique=False)
    op.create_index('ix_config_values_level', 'config_values', ['level'], unique=False)
    op.create_index('ix_config_values_sort_order', 'config_values', ['sort_order'], unique=False)
    op.create_index('ix_config_values_tags', 'config_values', ['tags'], unique=False)
    op.create_index('uq_config_values_type_key_tenant', 'config_values', ['config_type_id', 'value_key', 'tenant_id'], unique=True)

    # Create config_value_translations table
    op.create_table(
        'config_value_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_value_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('translated_by', sa.Integer(), nullable=True),
        sa.Column('translation_quality', sa.String(length=20), nullable=True, server_default='manual'),
        sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['config_value_id'], ['config_values.id'], name='fk_config_value_translations_config_value_id_config_values', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['translated_by'], ['users.id'], name='fk_config_value_translations_translated_by_users'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_config_value_translations_id', 'config_value_translations', ['id'], unique=False)
    op.create_index('ix_config_value_translations_language_code', 'config_value_translations', ['language_code'], unique=False)
    op.create_index('ix_config_value_translations_translation_quality', 'config_value_translations', ['translation_quality'], unique=False)
    op.create_index('uq_config_translations_value_lang', 'config_value_translations', ['config_value_id', 'language_code'], unique=True)

    # Create config_value_dependencies table
    op.create_table(
        'config_value_dependencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_value_id', sa.Integer(), nullable=False),
        sa.Column('target_value_id', sa.Integer(), nullable=False),
        sa.Column('dependency_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dependency_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_value_id'], ['config_values.id'], name='fk_config_value_dependencies_source_value_id_config_values', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_value_id'], ['config_values.id'], name='fk_config_value_dependencies_target_value_id_config_values', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_config_value_dependencies_dependency_type', 'config_value_dependencies', ['dependency_type'], unique=False)
    op.create_index('ix_config_value_dependencies_id', 'config_value_dependencies', ['id'], unique=False)
    op.create_index('uq_config_dependencies_source_target_type', 'config_value_dependencies', ['source_value_id', 'target_value_id', 'dependency_type'], unique=True)

    # Create config_sync_history table
    op.create_table(
        'config_sync_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_session_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=True),
        sa.Column('config_type_id', sa.Integer(), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=False),
        sa.Column('sync_action', sa.String(length=20), nullable=False),
        sa.Column('sync_status', sa.String(length=20), nullable=False),
        sa.Column('changes_summary', sa.JSON(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_created', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_updated', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_deleted', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_skipped', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('source_version', sa.String(length=50), nullable=True),
        sa.Column('target_version', sa.String(length=50), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('memory_usage_mb', sa.Integer(), nullable=True),
        sa.Column('triggered_by', sa.String(length=50), nullable=True),
        sa.Column('triggered_by_user_id', sa.Integer(), nullable=True),
        sa.Column('execution_context', sa.JSON(), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['config_type_id'], ['config_types.id'], name='fk_config_sync_history_config_type_id_config_types', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by_user_id'], ['users.id'], name='fk_config_sync_history_triggered_by_user_id_users'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_config_sync_history_executed_at', 'config_sync_history', ['executed_at'], unique=False)
    op.create_index('ix_config_sync_history_id', 'config_sync_history', ['id'], unique=False)
    op.create_index('ix_config_sync_history_source_file', 'config_sync_history', ['source_file'], unique=False)
    op.create_index('ix_config_sync_history_sync_action', 'config_sync_history', ['sync_action'], unique=False)
    op.create_index('ix_config_sync_history_sync_session_id', 'config_sync_history', ['sync_session_id'], unique=False)
    op.create_index('ix_config_sync_history_sync_status', 'config_sync_history', ['sync_status'], unique=False)

    # Create config_change_log table
    op.create_table(
        'config_change_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_history_id', sa.Integer(), nullable=False),
        sa.Column('config_value_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('value_key', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['config_value_id'], ['config_values.id'], name='fk_config_change_log_config_value_id_config_values', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sync_history_id'], ['config_sync_history.id'], name='fk_config_change_log_sync_history_id_config_sync_history', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_config_change_log_tenant_id_tenants'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_config_change_log_action', 'config_change_log', ['action'], unique=False)
    op.create_index('ix_config_change_log_created_at', 'config_change_log', ['created_at'], unique=False)
    op.create_index('ix_config_change_log_id', 'config_change_log', ['id'], unique=False)

    # Create config_usage_stats table
    op.create_table(
        'config_usage_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_value_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('context_type', sa.String(length=50), nullable=True),
        sa.Column('context_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('daily_usage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('weekly_usage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('monthly_usage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['config_value_id'], ['config_values.id'], name='fk_config_usage_stats_config_value_id_config_values', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_config_usage_stats_tenant_id_tenants', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_config_usage_stats_context_type', 'config_usage_stats', ['context_type'], unique=False)
    op.create_index('ix_config_usage_stats_id', 'config_usage_stats', ['id'], unique=False)
    op.create_index('ix_config_usage_stats_last_used_at', 'config_usage_stats', ['last_used_at'], unique=False)
    op.create_index('uq_usage_stats_value_tenant_context', 'config_usage_stats', ['config_value_id', 'tenant_id', 'context_type'], unique=True)


def downgrade():
    # Drop tables in reverse order of creation to handle foreign key dependencies
    op.drop_table('config_usage_stats')
    op.drop_table('config_change_log')
    op.drop_table('config_sync_history')
    op.drop_table('config_value_dependencies')
    op.drop_table('config_value_translations')
    op.drop_table('config_values')
    op.drop_table('config_types')
    op.drop_table('config_categories')