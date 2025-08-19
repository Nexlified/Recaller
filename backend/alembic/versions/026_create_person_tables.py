"""Create person tables to replace contacts

Revision ID: 026_create_person_tables
Revises: 025_create_gift_tables
Create Date: 2025-01-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '026_create_person_tables'
down_revision = '025_create_gift_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create person_profiles table (core profile information)
    op.create_table(
        'person_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('visibility', sa.String(10), nullable=False, server_default='private'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_person_profiles_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_person_profiles_created_by_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_profiles'))
    )
    op.create_index(op.f('ix_person_profiles_id'), 'person_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_person_profiles_tenant_id'), 'person_profiles', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_person_profiles_first_name'), 'person_profiles', ['first_name'], unique=False)
    op.create_index(op.f('ix_person_profiles_last_name'), 'person_profiles', ['last_name'], unique=False)
    op.create_index(op.f('ix_person_profiles_visibility'), 'person_profiles', ['visibility'], unique=False)
    op.create_index('idx_person_profiles_tenant_active', 'person_profiles', ['tenant_id', 'is_active'], unique=False)
    op.create_index('idx_person_profiles_name', 'person_profiles', ['first_name', 'last_name'], unique=False)

    # Create person_contact_info table (email, phone, addresses with privacy settings)
    op.create_table(
        'person_contact_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('contact_type', sa.String(20), nullable=False),
        sa.Column('contact_value', sa.String(500), nullable=False),
        sa.Column('contact_label', sa.String(100), nullable=True),
        sa.Column('privacy_level', sa.String(10), nullable=False, server_default='private'),
        sa.Column('address_street', sa.String(255), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(100), nullable=True),
        sa.Column('address_postal_code', sa.String(20), nullable=True),
        sa.Column('address_country_code', sa.String(2), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], name=op.f('fk_person_contact_info_person_id_person_profiles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_contact_info'))
    )
    op.create_index(op.f('ix_person_contact_info_id'), 'person_contact_info', ['id'], unique=False)
    op.create_index(op.f('ix_person_contact_info_person_id'), 'person_contact_info', ['person_id'], unique=False)
    op.create_index('idx_person_contact_info_person_type', 'person_contact_info', ['person_id', 'contact_type'], unique=False)
    op.create_index('idx_person_contact_info_primary', 'person_contact_info', ['person_id', 'is_primary', 'contact_type'], unique=False)

    # Create person_professional_info table (job history, organizations, work details)
    op.create_table(
        'person_professional_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('job_title', sa.String(255), nullable=True),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('is_current_position', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('work_email', sa.String(255), nullable=True),
        sa.Column('work_phone', sa.String(50), nullable=True),
        sa.Column('work_address', sa.Text(), nullable=True),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('responsibilities', sa.JSON(), nullable=True),
        sa.Column('skills_used', sa.JSON(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('manager_person_id', sa.Integer(), nullable=True),
        sa.Column('reporting_structure', sa.Text(), nullable=True),
        sa.Column('can_be_reference', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reference_notes', sa.Text(), nullable=True),
        sa.Column('linkedin_profile', sa.String(500), nullable=True),
        sa.Column('other_profiles', sa.JSON(), nullable=True),
        sa.Column('salary_range', sa.String(100), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], name=op.f('fk_person_professional_info_person_id_person_profiles')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_person_professional_info_organization_id_organizations')),
        sa.ForeignKeyConstraint(['manager_person_id'], ['person_profiles.id'], name=op.f('fk_person_professional_info_manager_person_id_person_profiles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_professional_info'))
    )
    op.create_index(op.f('ix_person_professional_info_id'), 'person_professional_info', ['id'], unique=False)
    op.create_index(op.f('ix_person_professional_info_person_id'), 'person_professional_info', ['person_id'], unique=False)
    op.create_index('idx_person_professional_person_current', 'person_professional_info', ['person_id', 'is_current_position'], unique=False)
    op.create_index('idx_person_professional_org', 'person_professional_info', ['organization_id'], unique=False)

    # Create person_personal_info table (birthday, preferences, family information)
    op.create_table(
        'person_personal_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('anniversary_date', sa.Date(), nullable=True),
        sa.Column('maiden_name', sa.String(255), nullable=True),
        sa.Column('family_nickname', sa.String(100), nullable=True),
        sa.Column('is_emergency_contact', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('emergency_contact_priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('preferred_communication', sa.JSON(), nullable=True),
        sa.Column('communication_notes', sa.Text(), nullable=True),
        sa.Column('marital_status', sa.String(20), nullable=True),
        sa.Column('spouse_partner_person_id', sa.Integer(), nullable=True),
        sa.Column('children_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cultural_background', sa.String(100), nullable=True),
        sa.Column('languages_spoken', sa.JSON(), nullable=True),
        sa.Column('religion', sa.String(100), nullable=True),
        sa.Column('dietary_restrictions', sa.JSON(), nullable=True),
        sa.Column('hobbies_interests', sa.JSON(), nullable=True),
        sa.Column('favorite_activities', sa.JSON(), nullable=True),
        sa.Column('privacy_level', sa.String(10), nullable=False, server_default='private'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], name=op.f('fk_person_personal_info_person_id_person_profiles')),
        sa.ForeignKeyConstraint(['spouse_partner_person_id'], ['person_profiles.id'], name=op.f('fk_person_personal_info_spouse_partner_person_id_person_profiles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_personal_info'))
    )
    op.create_index(op.f('ix_person_personal_info_id'), 'person_personal_info', ['id'], unique=False)
    op.create_index(op.f('ix_person_personal_info_person_id'), 'person_personal_info', ['person_id'], unique=False)
    op.create_index(op.f('ix_person_personal_info_is_emergency_contact'), 'person_personal_info', ['is_emergency_contact'], unique=False)
    op.create_index('idx_person_personal_person', 'person_personal_info', ['person_id'], unique=False)
    op.create_index('idx_person_personal_emergency', 'person_personal_info', ['is_emergency_contact', 'emergency_contact_priority'], unique=False)
    op.create_index('idx_person_personal_birth_month', 'person_personal_info', ['date_of_birth'], unique=False)

    # Create person_life_events table (important dates, milestones, life tracking)
    op.create_table(
        'person_life_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(30), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('importance_level', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurring_pattern', sa.String(20), nullable=True),
        sa.Column('should_remind', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('reminder_days_before', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('participants', sa.JSON(), nullable=True),
        sa.Column('related_organization_id', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('privacy_level', sa.String(10), nullable=False, server_default='private'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], name=op.f('fk_person_life_events_person_id_person_profiles')),
        sa.ForeignKeyConstraint(['related_organization_id'], ['organizations.id'], name=op.f('fk_person_life_events_related_organization_id_organizations')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_life_events'))
    )
    op.create_index(op.f('ix_person_life_events_id'), 'person_life_events', ['id'], unique=False)
    op.create_index(op.f('ix_person_life_events_person_id'), 'person_life_events', ['person_id'], unique=False)
    op.create_index('idx_person_life_events_person_date', 'person_life_events', ['person_id', 'event_date'], unique=False)
    op.create_index('idx_person_life_events_type_date', 'person_life_events', ['event_type', 'event_date'], unique=False)
    op.create_index('idx_person_life_events_remind', 'person_life_events', ['should_remind', 'event_date'], unique=False)

    # Create person_belongings table (items, possessions, relationship context)
    op.create_table(
        'person_belongings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('belonging_type', sa.String(20), nullable=False),
        sa.Column('item_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_value', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('sentimental_value', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('date_acquired', sa.Date(), nullable=True),
        sa.Column('occasion', sa.String(255), nullable=True),
        sa.Column('related_person_id', sa.Integer(), nullable=True),
        sa.Column('relationship_context', sa.Text(), nullable=True),
        sa.Column('brand', sa.String(100), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('condition', sa.String(20), nullable=True),
        sa.Column('current_location', sa.String(255), nullable=True),
        sa.Column('is_borrowed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('borrowed_to_person_id', sa.Integer(), nullable=True),
        sa.Column('borrowed_date', sa.Date(), nullable=True),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.Column('receipts', sa.JSON(), nullable=True),
        sa.Column('documents', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('privacy_level', sa.String(10), nullable=False, server_default='private'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['person_id'], ['person_profiles.id'], name=op.f('fk_person_belongings_person_id_person_profiles')),
        sa.ForeignKeyConstraint(['related_person_id'], ['person_profiles.id'], name=op.f('fk_person_belongings_related_person_id_person_profiles')),
        sa.ForeignKeyConstraint(['borrowed_to_person_id'], ['person_profiles.id'], name=op.f('fk_person_belongings_borrowed_to_person_id_person_profiles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_belongings'))
    )
    op.create_index(op.f('ix_person_belongings_id'), 'person_belongings', ['id'], unique=False)
    op.create_index(op.f('ix_person_belongings_person_id'), 'person_belongings', ['person_id'], unique=False)
    op.create_index('idx_person_belongings_person_type', 'person_belongings', ['person_id', 'belonging_type'], unique=False)
    op.create_index('idx_person_belongings_borrowed', 'person_belongings', ['is_borrowed', 'borrowed_date'], unique=False)
    op.create_index('idx_person_belongings_category', 'person_belongings', ['category', 'subcategory'], unique=False)

    # Create person_relationships table (rich bidirectional relationship mapping)
    op.create_table(
        'person_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('person_a_id', sa.Integer(), nullable=False),
        sa.Column('person_b_id', sa.Integer(), nullable=False),
        sa.Column('relationship_a_to_b', sa.String(50), nullable=False),
        sa.Column('relationship_b_to_a', sa.String(50), nullable=False),
        sa.Column('relationship_status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('closeness_level', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('interaction_frequency', sa.String(20), nullable=True),
        sa.Column('how_they_met', sa.Text(), nullable=True),
        sa.Column('relationship_context', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('relationship_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('relationship_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('auto_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('manual_override', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('original_relationship_type', sa.String(50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('privacy_level', sa.String(10), nullable=False, server_default='private'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_person_relationships_tenant_id_tenants')),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_person_relationships_created_by_user_id_users')),
        sa.ForeignKeyConstraint(['person_a_id'], ['person_profiles.id'], name=op.f('fk_person_relationships_person_a_id_person_profiles')),
        sa.ForeignKeyConstraint(['person_b_id'], ['person_profiles.id'], name=op.f('fk_person_relationships_person_b_id_person_profiles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_person_relationships'))
    )
    op.create_index(op.f('ix_person_relationships_id'), 'person_relationships', ['id'], unique=False)
    op.create_index(op.f('ix_person_relationships_tenant_id'), 'person_relationships', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_person_relationships_person_a_id'), 'person_relationships', ['person_a_id'], unique=False)
    op.create_index(op.f('ix_person_relationships_person_b_id'), 'person_relationships', ['person_b_id'], unique=False)
    op.create_index('idx_person_relationships_persons', 'person_relationships', ['person_a_id', 'person_b_id'], unique=False)
    op.create_index('idx_person_relationships_tenant', 'person_relationships', ['tenant_id', 'is_active'], unique=False)
    op.create_index('idx_person_relationships_a_type', 'person_relationships', ['person_a_id', 'relationship_a_to_b'], unique=False)
    op.create_index('idx_person_relationships_b_type', 'person_relationships', ['person_b_id', 'relationship_b_to_a'], unique=False)
    op.create_index('idx_person_relationships_unique', 'person_relationships', ['person_a_id', 'person_b_id'], unique=True)


def downgrade():
    # Drop person tables in reverse order
    op.drop_table('person_relationships')
    op.drop_table('person_belongings')
    op.drop_table('person_life_events')
    op.drop_table('person_personal_info')
    op.drop_table('person_professional_info')
    op.drop_table('person_contact_info')
    op.drop_table('person_profiles')