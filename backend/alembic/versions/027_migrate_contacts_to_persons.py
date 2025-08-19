"""Migrate data from contacts to person tables

Revision ID: 027_migrate_contacts_to_persons
Revises: 026_create_person_tables
Create Date: 2025-01-19 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '027_migrate_contacts_to_persons'
down_revision = '026_create_person_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    connection = op.get_bind()
    
    # 1. Migrate basic contact information to person_profiles
    connection.execute(text("""
        INSERT INTO person_profiles (
            id, tenant_id, created_by_user_id, first_name, last_name, gender, notes, 
            visibility, is_active, created_at, updated_at
        )
        SELECT 
            id, tenant_id, created_by_user_id, first_name, last_name, gender, notes,
            visibility, is_active, created_at, updated_at
        FROM contacts
        WHERE is_active = true
    """))
    
    # 2. Migrate contact information (email, phone) to person_contact_info
    # Migrate email addresses
    connection.execute(text("""
        INSERT INTO person_contact_info (
            person_id, contact_type, contact_value, contact_label, privacy_level, 
            is_primary, is_active, created_at
        )
        SELECT 
            id as person_id,
            'email' as contact_type,
            email as contact_value,
            'primary' as contact_label,
            CASE 
                WHEN visibility = 'public' THEN 'public'
                ELSE 'private'
            END as privacy_level,
            true as is_primary,
            true as is_active,
            created_at
        FROM contacts
        WHERE email IS NOT NULL AND email != '' AND is_active = true
    """))
    
    # Migrate phone numbers
    connection.execute(text("""
        INSERT INTO person_contact_info (
            person_id, contact_type, contact_value, contact_label, privacy_level, 
            is_primary, is_active, created_at
        )
        SELECT 
            id as person_id,
            'phone' as contact_type,
            phone as contact_value,
            'primary' as contact_label,
            CASE 
                WHEN visibility = 'public' THEN 'public'
                ELSE 'private'
            END as privacy_level,
            true as is_primary,
            true as is_active,
            created_at
        FROM contacts
        WHERE phone IS NOT NULL AND phone != '' AND is_active = true
    """))
    
    # 3. Migrate professional information to person_professional_info
    connection.execute(text("""
        INSERT INTO person_professional_info (
            person_id, organization_id, job_title, is_current_position, 
            is_active, created_at
        )
        SELECT 
            id as person_id,
            organization_id,
            job_title,
            true as is_current_position,  -- Assume current position
            true as is_active,
            created_at
        FROM contacts
        WHERE (job_title IS NOT NULL AND job_title != '') 
           OR organization_id IS NOT NULL
           AND is_active = true
    """))
    
    # 4. Migrate personal information to person_personal_info
    connection.execute(text("""
        INSERT INTO person_personal_info (
            person_id, date_of_birth, anniversary_date, maiden_name, family_nickname,
            is_emergency_contact, privacy_level, is_active, created_at
        )
        SELECT 
            id as person_id,
            date_of_birth,
            anniversary_date,
            maiden_name,
            family_nickname,
            is_emergency_contact,
            CASE 
                WHEN visibility = 'public' THEN 'public'
                ELSE 'private'
            END as privacy_level,
            true as is_active,
            created_at
        FROM contacts
        WHERE (date_of_birth IS NOT NULL 
            OR anniversary_date IS NOT NULL 
            OR maiden_name IS NOT NULL 
            OR family_nickname IS NOT NULL
            OR is_emergency_contact = true)
           AND is_active = true
    """))
    
    # 5. Migrate birthday and anniversary to life events
    # Migrate birthdays
    connection.execute(text("""
        INSERT INTO person_life_events (
            person_id, event_type, event_date, event_title, importance_level,
            is_recurring, recurring_pattern, should_remind, privacy_level,
            is_active, created_at
        )
        SELECT 
            id as person_id,
            'birthday' as event_type,
            date_of_birth as event_date,
            first_name || COALESCE(' ' || last_name, '') || '''s Birthday' as event_title,
            5 as importance_level,  -- High importance
            true as is_recurring,
            'yearly' as recurring_pattern,
            true as should_remind,
            CASE 
                WHEN visibility = 'public' THEN 'public'
                ELSE 'private'
            END as privacy_level,
            true as is_active,
            created_at
        FROM contacts
        WHERE date_of_birth IS NOT NULL AND is_active = true
    """))
    
    # Migrate anniversaries
    connection.execute(text("""
        INSERT INTO person_life_events (
            person_id, event_type, event_date, event_title, importance_level,
            is_recurring, recurring_pattern, should_remind, privacy_level,
            is_active, created_at
        )
        SELECT 
            id as person_id,
            'anniversary' as event_type,
            anniversary_date as event_date,
            first_name || COALESCE(' ' || last_name, '') || '''s Anniversary' as event_title,
            4 as importance_level,  -- High importance
            true as is_recurring,
            'yearly' as recurring_pattern,
            true as should_remind,
            CASE 
                WHEN visibility = 'public' THEN 'public'
                ELSE 'private'
            END as privacy_level,
            true as is_active,
            created_at
        FROM contacts
        WHERE anniversary_date IS NOT NULL AND is_active = true
    """))
    
    print("Migration completed: Data moved from contacts to person tables")


def downgrade():
    # In downgrade, we would need to restore data back to contacts table
    # This is complex and would require recreating the contacts table first
    # For now, we'll just clear the person tables
    connection = op.get_bind()
    
    # Clear person tables in reverse dependency order
    connection.execute(text("DELETE FROM person_life_events"))
    connection.execute(text("DELETE FROM person_personal_info"))
    connection.execute(text("DELETE FROM person_professional_info"))
    connection.execute(text("DELETE FROM person_contact_info"))
    connection.execute(text("DELETE FROM person_profiles"))
    
    print("Downgrade completed: Person tables cleared")