"""Configuration import system setup

Revision ID: 023_configuration_import_system
Revises: 022_add_relationship_fields
Create Date: 2025-01-15 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '023_configuration_import_system'
down_revision = '022_add_relationship_fields'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add configuration import tracking table
    op.create_table(
        'configuration_imports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_type', sa.String(100), nullable=False),
        sa.Column('config_version', sa.String(50), nullable=False),
        sa.Column('source_file', sa.String(255), nullable=False),
        sa.Column('import_status', sa.String(50), nullable=False),  # pending, success, failed
        sa.Column('import_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('records_imported', sa.Integer(), default=0),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_configuration_imports_config_type', 'configuration_imports', ['config_type'])
    op.create_index('ix_configuration_imports_tenant_id', 'configuration_imports', ['tenant_id'])
    
    # Add configuration source tracking to existing tables
    op.add_column('configuration_values', sa.Column('source', sa.String(50), default='manual'))
    op.add_column('configuration_values', sa.Column('source_version', sa.String(50), nullable=True))
    op.add_column('configuration_values', sa.Column('import_id', sa.Integer(), 
                                                   sa.ForeignKey('configuration_imports.id'), nullable=True))

def downgrade() -> None:
    op.drop_column('configuration_values', 'import_id')
    op.drop_column('configuration_values', 'source_version')
    op.drop_column('configuration_values', 'source')
    op.drop_index('ix_configuration_imports_tenant_id')
    op.drop_index('ix_configuration_imports_config_type')
    op.drop_table('configuration_imports')