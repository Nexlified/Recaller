"""Simple integration test without complex array fields"""

def test_api_structure():
    """Test that we can import the main components without errors"""
    # Test that we can import all the key modules
    from app.main import app
    from app.models import contact, organization, social_group
    from app.crud import contact as contact_crud
    from app.schemas import contact as contact_schema
    
    # Basic validation that the app has the expected structure
    assert app is not None
    assert hasattr(contact, 'Contact')
    assert hasattr(organization, 'Organization')
    assert hasattr(social_group, 'SocialGroup')
    assert hasattr(contact_crud, 'contact')
    assert hasattr(contact_schema, 'ContactCreate')

def test_schema_validation():
    """Test that our Pydantic schemas work correctly"""
    from app.schemas.contact import ContactCreate, ContactIntelligenceUpdate
    from app.schemas.organization import OrganizationCreate
    
    # Test valid contact creation
    contact_data = ContactCreate(
        first_name="Test",
        last_name="User",
        email="test@example.com"
    )
    assert contact_data.first_name == "Test"
    assert contact_data.last_name == "User"
    
    # Test intelligence update
    intel_data = ContactIntelligenceUpdate(
        personality_type="extrovert",
        networking_value="high"
    )
    assert intel_data.personality_type == "extrovert"
    assert intel_data.networking_value == "high"
    
    # Test organization creation
    org_data = OrganizationCreate(
        name="Test Corp",
        organization_type="company"
    )
    assert org_data.name == "Test Corp"
    assert org_data.organization_type == "company"

def test_contact_model_basic():
    """Test basic contact model functionality without arrays"""
    from app.models.contact import Contact
    
    # Create a basic contact without array fields
    contact = Contact(
        first_name="Simple",
        last_name="Test",
        email="simple@example.com",
        tenant_id=1,
        connection_strength=7,
        networking_value="high",
        personality_type="extrovert"
    )
    
    assert contact.first_name == "Simple"
    assert contact.last_name == "Test"
    assert contact.connection_strength == 7
    assert contact.networking_value == "high"
    assert contact.personality_type == "extrovert"

def test_api_endpoint_availability():
    """Test that API endpoints are properly registered"""
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    
    # Test OpenAPI endpoint
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    assert "paths" in openapi_spec
    
    # Check that our contact endpoints are registered
    paths = openapi_spec["paths"]
    assert "/api/v1/contacts/" in paths
    assert "/api/v1/organizations/" in paths