"""Add configuration management tables

Revision ID: 004_configuration_tables
Revises: 003_create_social_groups_tables
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_configuration_tables'
down_revision: Union[str, None] = '003_create_social_groups_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create configuration_categories table
    op.create_table('configuration_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('icon', sa.String(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_system', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_configuration_categories_id'), 'configuration_categories', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_categories_key'), 'configuration_categories', ['key'], unique=False)
    op.create_index(op.f('ix_configuration_categories_tenant_id'), 'configuration_categories', ['tenant_id'], unique=False)

    # Create configuration_types table
    op.create_table('configuration_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('data_type', sa.String(), nullable=True),
    sa.Column('validation_rules', sa.JSON(), nullable=True),
    sa.Column('default_value', sa.Text(), nullable=True),
    sa.Column('is_hierarchical', sa.Boolean(), nullable=True),
    sa.Column('is_translatable', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_system', sa.Boolean(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['configuration_categories.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_configuration_types_category_id'), 'configuration_types', ['category_id'], unique=False)
    op.create_index(op.f('ix_configuration_types_id'), 'configuration_types', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_types_key'), 'configuration_types', ['key'], unique=False)
    op.create_index(op.f('ix_configuration_types_tenant_id'), 'configuration_types', ['tenant_id'], unique=False)

    # Create configuration_values table
    op.create_table('configuration_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('path', sa.String(), nullable=True),
    sa.Column('value_metadata', sa.JSON(), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_system', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['configuration_values.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['configuration_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configuration_values_id'), 'configuration_values', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_values_key'), 'configuration_values', ['key'], unique=False)
    op.create_index(op.f('ix_configuration_values_parent_id'), 'configuration_values', ['parent_id'], unique=False)
    op.create_index(op.f('ix_configuration_values_path'), 'configuration_values', ['path'], unique=False)
    op.create_index(op.f('ix_configuration_values_tenant_id'), 'configuration_values', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_configuration_values_type_id'), 'configuration_values', ['type_id'], unique=False)

    # Create configuration_translations table
    op.create_table('configuration_translations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value_id', sa.Integer(), nullable=False),
    sa.Column('language_code', sa.String(length=5), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.ForeignKeyConstraint(['value_id'], ['configuration_values.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configuration_translations_id'), 'configuration_translations', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_translations_language_code'), 'configuration_translations', ['language_code'], unique=False)
    op.create_index(op.f('ix_configuration_translations_tenant_id'), 'configuration_translations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_configuration_translations_value_id'), 'configuration_translations', ['value_id'], unique=False)


def downgrade() -> None:
    op.drop_table('configuration_translations')
    op.drop_table('configuration_values')
    op.drop_table('configuration_types')
    op.drop_table('configuration_categories')