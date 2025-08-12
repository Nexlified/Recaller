"""Create contacts and organizations tables

Revision ID: 003_create_contacts_org
Revises: 002_create_users
Create Date: 2025-08-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_create_contacts_org'
down_revision = '002_create_users'
branch_labels = None
depends_on = None


def upgrade():
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        
        # Basic Information
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('short_name', sa.String(100), nullable=True),
        sa.Column('organization_type', sa.String(50), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('size_category', sa.String(20), nullable=True),
        
        # Contact Information
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        
        # Address
        sa.Column('address_street', sa.Text(), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(100), nullable=True),
        sa.Column('address_postal_code', sa.String(20), nullable=True),
        sa.Column('address_country_code', sa.String(2), nullable=True),
        
        # Metadata
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_organizations_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_organizations_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_tenant_id'), 'organizations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_organization_type'), 'organizations', ['organization_type'], unique=False)
    op.create_index(op.f('ix_organizations_industry'), 'organizations', ['industry'], unique=False)

    # Create organization_aliases table
    op.create_table(
        'organization_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.String(255), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_organization_aliases_organization_id_organizations'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'alias', name='uq_organization_aliases_organization_alias')
    )
    op.create_index(op.f('ix_organization_aliases_id'), 'organization_aliases', ['id'], unique=False)
    op.create_index(op.f('ix_organization_aliases_organization_id'), 'organization_aliases', ['organization_id'], unique=False)
    op.create_index(op.f('ix_organization_aliases_alias'), 'organization_aliases', ['alias'], unique=False)

    # Create organization_locations table
    op.create_table(
        'organization_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('location_type', sa.String(50), nullable=False),
        sa.Column('address_street', sa.Text(), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(100), nullable=True),
        sa.Column('address_postal_code', sa.String(20), nullable=True),
        sa.Column('address_country_code', sa.String(2), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_organization_locations_organization_id_organizations'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_locations_id'), 'organization_locations', ['id'], unique=False)
    op.create_index(op.f('ix_organization_locations_organization_id'), 'organization_locations', ['organization_id'], unique=False)
    op.create_index(op.f('ix_organization_locations_location_type'), 'organization_locations', ['location_type'], unique=False)

    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('job_title', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_contacts_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_contacts_created_by_user_id_users')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_contacts_organization_id_organizations')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_tenant_id'), 'contacts', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=False)
    op.create_index(op.f('ix_contacts_first_name'), 'contacts', ['first_name'], unique=False)
    op.create_index(op.f('ix_contacts_last_name'), 'contacts', ['last_name'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_contacts_last_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_first_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_tenant_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_table('contacts')
    
    op.drop_index(op.f('ix_organization_locations_location_type'), table_name='organization_locations')
    op.drop_index(op.f('ix_organization_locations_organization_id'), table_name='organization_locations')
    op.drop_index(op.f('ix_organization_locations_id'), table_name='organization_locations')
    op.drop_table('organization_locations')
    
    op.drop_index(op.f('ix_organization_aliases_alias'), table_name='organization_aliases')
    op.drop_index(op.f('ix_organization_aliases_organization_id'), table_name='organization_aliases')
    op.drop_index(op.f('ix_organization_aliases_id'), table_name='organization_aliases')
    op.drop_table('organization_aliases')
    
    op.drop_index(op.f('ix_organizations_industry'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_organization_type'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_tenant_id'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')