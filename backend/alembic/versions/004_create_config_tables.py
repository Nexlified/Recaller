"""Create configuration management tables

Revision ID: 004_create_config_tables
Revises: 003_create_social_groups_tables
Create Date: 2025-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_create_config_tables'
down_revision = '003_create_social_groups_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create config_types table
    op.create_table(
        'config_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('schema_version', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_checksum', sa.String(), nullable=True),
        sa.Column('config_file_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_config_types_tenant_id_tenants')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_types_id'), 'config_types', ['id'], unique=False)
    op.create_index(op.f('ix_config_types_tenant_id'), 'config_types', ['tenant_id'], unique=False)

    # Create config_values table
    op.create_table(
        'config_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('config_type_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_value_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=True),
        sa.Column('config_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['config_type_id'], ['config_types.id'], name=op.f('fk_config_values_config_type_id_config_types')),
        sa.ForeignKeyConstraint(['parent_value_id'], ['config_values.id'], name=op.f('fk_config_values_parent_value_id_config_values')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_config_values_tenant_id_tenants')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_values_id'), 'config_values', ['id'], unique=False)
    op.create_index(op.f('ix_config_values_tenant_id'), 'config_values', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_config_values_config_type_id'), 'config_values', ['config_type_id'], unique=False)

    # Create config_sync_sessions table
    op.create_table(
        'config_sync_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sync_type', sa.String(), nullable=False),
        sa.Column('files_processed', sa.Integer(), nullable=True),
        sa.Column('changes_made', sa.Integer(), nullable=True),
        sa.Column('errors_count', sa.Integer(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_config_sync_sessions_tenant_id_tenants')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id', name=op.f('uq_config_sync_sessions_session_id'))
    )
    op.create_index(op.f('ix_config_sync_sessions_id'), 'config_sync_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_config_sync_sessions_tenant_id'), 'config_sync_sessions', ['tenant_id'], unique=False)

    # Create config_changes table
    op.create_table(
        'config_changes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('sync_session_id', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=True),
        sa.Column('field_name', sa.String(), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('config_file_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sync_session_id'], ['config_sync_sessions.id'], name=op.f('fk_config_changes_sync_session_id_config_sync_sessions')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_config_changes_tenant_id_tenants')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_changes_id'), 'config_changes', ['id'], unique=False)
    op.create_index(op.f('ix_config_changes_tenant_id'), 'config_changes', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_config_changes_sync_session_id'), 'config_changes', ['sync_session_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_config_changes_sync_session_id'), table_name='config_changes')
    op.drop_index(op.f('ix_config_changes_tenant_id'), table_name='config_changes')
    op.drop_index(op.f('ix_config_changes_id'), table_name='config_changes')
    op.drop_table('config_changes')
    
    op.drop_index(op.f('ix_config_sync_sessions_tenant_id'), table_name='config_sync_sessions')
    op.drop_index(op.f('ix_config_sync_sessions_id'), table_name='config_sync_sessions')
    op.drop_table('config_sync_sessions')
    
    op.drop_index(op.f('ix_config_values_config_type_id'), table_name='config_values')
    op.drop_index(op.f('ix_config_values_tenant_id'), table_name='config_values')
    op.drop_index(op.f('ix_config_values_id'), table_name='config_values')
    op.drop_table('config_values')
    
    op.drop_index(op.f('ix_config_types_tenant_id'), table_name='config_types')
    op.drop_index(op.f('ix_config_types_id'), table_name='config_types')
    op.drop_table('config_types')