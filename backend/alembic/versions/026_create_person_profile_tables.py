"""026_create_person_profile_tables

Create normalized person profile tables for relationship management

Revision ID: 026_create_person_profile_tables
Revises: 025_create_gift_tables
Create Date: 2025-01-17 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '026_create_person_profile_tables'
down_revision: Union[str, None] = '025_create_gift_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create person_profiles table
    op.create_table(
        'person_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_profiles_id'), 'person_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_person_profiles_tenant_id'), 'person_profiles', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_person_profiles_visibility'), 'person_profiles', ['visibility'], unique=False)

    # Create person_contact_info table
    op.create_table(
        'person_contact_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('contact_type', sa.String(20), nullable=False, server_default='personal'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_emergency_contact', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_contact_info_email'), 'person_contact_info', ['email'], unique=False)
    op.create_index(op.f('ix_person_contact_info_tenant_id'), 'person_contact_info', ['tenant_id'], unique=False)

    # Create person_professional_info table
    op.create_table(
        'person_professional_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('job_title', sa.String(255), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('organization_name', sa.String(255), nullable=True),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('salary_range', sa.String(50), nullable=True),
        sa.Column('work_location', sa.String(255), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_professional_info_tenant_id'), 'person_professional_info', ['tenant_id'], unique=False)

    # Create person_personal_info table
    op.create_table(
        'person_personal_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('anniversary_date', sa.Date(), nullable=True),
        sa.Column('maiden_name', sa.String(255), nullable=True),
        sa.Column('family_nickname', sa.String(100), nullable=True),
        sa.Column('preferred_name', sa.String(255), nullable=True),
        sa.Column('favorite_color', sa.String(50), nullable=True),
        sa.Column('favorite_food', sa.String(255), nullable=True),
        sa.Column('dietary_restrictions', sa.Text(), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('personality_notes', sa.Text(), nullable=True),
        sa.Column('interests_hobbies', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_personal_info_tenant_id'), 'person_personal_info', ['tenant_id'], unique=False)

    # Create person_life_events table
    op.create_table(
        'person_life_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('my_role', sa.String(100), nullable=True),
        sa.Column('significance', sa.Integer(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_life_events_tenant_id'), 'person_life_events', ['tenant_id'], unique=False)

    # Create person_belongings table
    op.create_table(
        'person_belongings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('brand', sa.String(100), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('estimated_value', sa.String(50), nullable=True),
        sa.Column('acquisition_date', sa.Date(), nullable=True),
        sa.Column('acquisition_method', sa.String(50), nullable=True),
        sa.Column('relationship_context', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_belongings_tenant_id'), 'person_belongings', ['tenant_id'], unique=False)

    # Create person_relationships table
    op.create_table(
        'person_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('person_a_id', sa.Integer(), nullable=False),
        sa.Column('person_b_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('relationship_category', sa.String(20), nullable=False),
        sa.Column('relationship_strength', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('how_we_met', sa.Text(), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_mutual', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_a_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['person_b_id'], ['person_profiles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_relationships_tenant_id'), 'person_relationships', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_person_relationships_person_a_id'), 'person_relationships', ['person_a_id'], unique=False)
    op.create_index(op.f('ix_person_relationships_person_b_id'), 'person_relationships', ['person_b_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order of creation to avoid foreign key constraint issues
    op.drop_table('person_relationships')
    op.drop_table('person_belongings')
    op.drop_table('person_life_events')
    op.drop_table('person_personal_info')
    op.drop_table('person_professional_info')
    op.drop_table('person_contact_info')
    op.drop_table('person_profiles')