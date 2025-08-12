import pytest
from app.models.contact import Contact
from app.models.organization import Organization
from app.models.social_group import SocialGroup
from app.models.contact_interaction import ContactInteraction
from app.models.contact_ai_insight import ContactAIInsight
from app.models.contact_relationship_score import ContactRelationshipScore

def test_create_contact(db_session):
    """Test creating a contact in the database"""
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        tenant_id=1,
        connection_strength=7,
        networking_value="high"
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    
    assert contact.id is not None
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.connection_strength == 7
    assert contact.networking_value == "high"

def test_create_organization(db_session):
    """Test creating an organization"""
    org = Organization(
        name="Tech Corp",
        organization_type="company",
        industry="technology",
        tenant_id=1
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    assert org.id is not None
    assert org.name == "Tech Corp"
    assert org.organization_type == "company"
    assert org.industry == "technology"

def test_contact_organization_relationship(db_session):
    """Test the relationship between contacts and organizations"""
    # Create organization
    org = Organization(
        name="Test Company",
        organization_type="company",
        tenant_id=1
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    # Create contact with organization
    contact = Contact(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        current_organization_id=org.id,
        tenant_id=1
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    
    # Test relationship
    assert contact.current_organization_id == org.id
    assert contact.current_organization.name == "Test Company"

def test_contact_interaction_creation(db_session):
    """Test creating contact interactions"""
    # Create contact first
    contact = Contact(
        first_name="Bob",
        last_name="Wilson",
        tenant_id=1
    )
    db_session.add(contact)
    db_session.commit()
    
    # Create interaction
    interaction = ContactInteraction(
        contact_id=contact.id,
        user_id=1,
        interaction_type="call",
        interaction_method="phone",
        interaction_quality=8,
        summary="Great conversation about project collaboration"
    )
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    
    assert interaction.id is not None
    assert interaction.contact_id == contact.id
    assert interaction.interaction_type == "call"
    assert interaction.interaction_quality == 8

def test_contact_ai_insight_creation(db_session):
    """Test creating AI insights for contacts"""
    # Create contact first
    contact = Contact(
        first_name="Alice",
        last_name="Johnson",
        tenant_id=1
    )
    db_session.add(contact)
    db_session.commit()
    
    # Create AI insight
    insight = ContactAIInsight(
        contact_id=contact.id,
        insight_type="follow_up_suggestion",
        title="Good time to reconnect",
        description="It's been 30 days since last contact",
        priority="medium",
        confidence_score=0.85,
        insight_date="2025-01-01"
    )
    db_session.add(insight)
    db_session.commit()
    db_session.refresh(insight)
    
    assert insight.id is not None
    assert insight.contact_id == contact.id
    assert insight.insight_type == "follow_up_suggestion"
    assert insight.confidence_score == 0.85