import pytest
from app.crud.contact import contact
from app.crud.organization import organization
from app.schemas.contact import ContactCreate, ContactIntelligenceUpdate
from app.schemas.organization import OrganizationCreate

def test_create_contact_crud(db_session):
    """Test creating a contact using CRUD operations"""
    contact_data = ContactCreate(
        first_name="Test",
        last_name="User",
        email="test.user@example.com"
    )
    
    db_contact = contact.create_with_tenant(
        db=db_session, 
        obj_in=contact_data, 
        tenant_id=1
    )
    
    assert db_contact.first_name == "Test"
    assert db_contact.last_name == "User"
    assert db_contact.email == "test.user@example.com"
    assert db_contact.tenant_id == 1

def test_get_contact_by_email(db_session):
    """Test retrieving a contact by email"""
    # First create a contact
    contact_data = ContactCreate(
        first_name="Email",
        last_name="Test",
        email="email.test@example.com"
    )
    
    created_contact = contact.create_with_tenant(
        db=db_session, 
        obj_in=contact_data, 
        tenant_id=1
    )
    
    # Now retrieve by email
    found_contact = contact.get_by_email(
        db=db_session, 
        email="email.test@example.com", 
        tenant_id=1
    )
    
    assert found_contact is not None
    assert found_contact.id == created_contact.id
    assert found_contact.email == "email.test@example.com"

def test_update_contact_intelligence(db_session):
    """Test updating contact intelligence fields"""
    # Create contact
    contact_data = ContactCreate(
        first_name="Intelligence",
        last_name="Test",
        email="intel.test@example.com"
    )
    
    db_contact = contact.create_with_tenant(
        db=db_session, 
        obj_in=contact_data, 
        tenant_id=1
    )
    
    # Update intelligence
    intelligence_data = ContactIntelligenceUpdate(
        personality_type="extrovert",
        communication_preference="video_call",
        networking_value="high",
        connection_strength=8
    )
    
    updated_contact = contact.update_intelligence(
        db=db_session,
        db_obj=db_contact,
        obj_in=intelligence_data
    )
    
    assert updated_contact.personality_type == "extrovert"
    assert updated_contact.communication_preference == "video_call"
    assert updated_contact.networking_value == "high"
    assert updated_contact.connection_strength == 8

def test_create_organization_crud(db_session):
    """Test creating an organization using CRUD operations"""
    org_data = OrganizationCreate(
        name="CRUD Test Corp",
        organization_type="company",
        industry="software"
    )
    
    db_org = organization.create_with_tenant(
        db=db_session,
        obj_in=org_data,
        tenant_id=1
    )
    
    assert db_org.name == "CRUD Test Corp"
    assert db_org.organization_type == "company"
    assert db_org.industry == "software"
    assert db_org.tenant_id == 1

def test_get_contacts_by_networking_value(db_session):
    """Test retrieving contacts by networking value"""
    # Create contacts with different networking values
    high_value_contact = contact.create_with_tenant(
        db=db_session,
        obj_in=ContactCreate(
            first_name="High",
            last_name="Value",
            email="high.value@example.com"
        ),
        tenant_id=1
    )
    
    # Update networking value
    contact.update_intelligence(
        db=db_session,
        db_obj=high_value_contact,
        obj_in=ContactIntelligenceUpdate(networking_value="high")
    )
    
    medium_value_contact = contact.create_with_tenant(
        db=db_session,
        obj_in=ContactCreate(
            first_name="Medium",
            last_name="Value",
            email="medium.value@example.com"
        ),
        tenant_id=1
    )
    
    # Get high networking value contacts
    high_contacts = contact.get_by_networking_value(
        db=db_session,
        tenant_id=1,
        networking_value="high"
    )
    
    assert len(high_contacts) == 1
    assert high_contacts[0].first_name == "High"
    assert high_contacts[0].networking_value == "high"