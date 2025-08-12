"""Create configuration management tables

Revision ID: 006_create_configuration
Revises: 005_create_analytics
Create Date: 2025-08-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_create_configuration'
down_revision = '005_create_analytics'
branch_labels = None
depends_on = None


def upgrade():
    # Create configuration_categories table
    op.create_table(
        'configuration_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uq_configuration_categories_key')
    )
    op.create_index(op.f('ix_configuration_categories_id'), 'configuration_categories', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_categories_key'), 'configuration_categories', ['key'], unique=False)

    # Create configuration_types table
    op.create_table(
        'configuration_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(50), nullable=False, server_default='string'),
        sa.Column('is_hierarchical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_multi_select', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['configuration_categories.id'], name=op.f('fk_configuration_types_category_id_configuration_categories')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uq_configuration_types_key')
    )
    op.create_index(op.f('ix_configuration_types_id'), 'configuration_types', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_types_category_id'), 'configuration_types', ['category_id'], unique=False)
    op.create_index(op.f('ix_configuration_types_key'), 'configuration_types', ['key'], unique=False)

    # Create configuration_values table
    op.create_table(
        'configuration_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['type_id'], ['configuration_types.id'], name=op.f('fk_configuration_values_type_id_configuration_types')),
        sa.ForeignKeyConstraint(['parent_id'], ['configuration_values.id'], name=op.f('fk_configuration_values_parent_id_configuration_values')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type_id', 'key', name='uq_configuration_values_type_key')
    )
    op.create_index(op.f('ix_configuration_values_id'), 'configuration_values', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_values_type_id'), 'configuration_values', ['type_id'], unique=False)
    op.create_index(op.f('ix_configuration_values_parent_id'), 'configuration_values', ['parent_id'], unique=False)
    op.create_index(op.f('ix_configuration_values_key'), 'configuration_values', ['key'], unique=False)

    # Create config_categories table (for reference data API)
    op.create_table(
        'config_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uq_config_categories_key')
    )
    op.create_index(op.f('ix_config_categories_id'), 'config_categories', ['id'], unique=False)

    # Create config_types table
    op.create_table(
        'config_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(50), nullable=False, server_default='string'),
        sa.Column('is_hierarchical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['config_categories.id'], name=op.f('fk_config_types_category_id_config_categories')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uq_config_types_key')
    )
    op.create_index(op.f('ix_config_types_id'), 'config_types', ['id'], unique=False)
    op.create_index(op.f('ix_config_types_category_id'), 'config_types', ['category_id'], unique=False)

    # Create config_values table
    op.create_table(
        'config_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['type_id'], ['config_types.id'], name=op.f('fk_config_values_type_id_config_types')),
        sa.ForeignKeyConstraint(['parent_id'], ['config_values.id'], name=op.f('fk_config_values_parent_id_config_values')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type_id', 'key', name='uq_config_values_type_key')
    )
    op.create_index(op.f('ix_config_values_id'), 'config_values', ['id'], unique=False)
    op.create_index(op.f('ix_config_values_type_id'), 'config_values', ['type_id'], unique=False)
    op.create_index(op.f('ix_config_values_parent_id'), 'config_values', ['parent_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_config_values_parent_id'), table_name='config_values')
    op.drop_index(op.f('ix_config_values_type_id'), table_name='config_values')
    op.drop_index(op.f('ix_config_values_id'), table_name='config_values')
    op.drop_table('config_values')
    
    op.drop_index(op.f('ix_config_types_category_id'), table_name='config_types')
    op.drop_index(op.f('ix_config_types_id'), table_name='config_types')
    op.drop_table('config_types')
    
    op.drop_index(op.f('ix_config_categories_id'), table_name='config_categories')
    op.drop_table('config_categories')
    
    op.drop_index(op.f('ix_configuration_values_key'), table_name='configuration_values')
    op.drop_index(op.f('ix_configuration_values_parent_id'), table_name='configuration_values')
    op.drop_index(op.f('ix_configuration_values_type_id'), table_name='configuration_values')
    op.drop_index(op.f('ix_configuration_values_id'), table_name='configuration_values')
    op.drop_table('configuration_values')
    
    op.drop_index(op.f('ix_configuration_types_key'), table_name='configuration_types')
    op.drop_index(op.f('ix_configuration_types_category_id'), table_name='configuration_types')
    op.drop_index(op.f('ix_configuration_types_id'), table_name='configuration_types')
    op.drop_table('configuration_types')
    
    op.drop_index(op.f('ix_configuration_categories_key'), table_name='configuration_categories')
    op.drop_index(op.f('ix_configuration_categories_id'), table_name='configuration_categories')
    op.drop_table('configuration_categories')
