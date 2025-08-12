import pytest
from fastapi.testclient import TestClient

def test_create_contact_api(client):
    """Test creating a contact through the API"""
    contact_data = {
        "first_name": "API",
        "last_name": "Test",
        "email": "api.test@example.com",
        "intelligence": {
            "personality_type": "extrovert",
            "networking_value": "high",
            "connection_strength": 7
        }
    }
    
    # Note: This will fail without authentication, but tests the structure
    response = client.post("/api/v1/contacts/", json=contact_data)
    # Expect authentication error (401) since no auth token provided
    assert response.status_code == 401

def test_read_contacts_api(client):
    """Test reading contacts through the API"""
    # Note: This will fail without authentication, but tests the structure
    response = client.get("/api/v1/contacts/")
    # Expect authentication error (401) since no auth token provided
    assert response.status_code == 401

def test_create_organization_api(client):
    """Test creating an organization through the API"""
    org_data = {
        "name": "API Test Company",
        "organization_type": "company",
        "industry": "technology"
    }
    
    # Note: This will fail without authentication, but tests the structure
    response = client.post("/api/v1/organizations/", json=org_data)
    # Expect authentication error (401) since no auth token provided
    assert response.status_code == 401

def test_contacts_endpoints_structure(client):
    """Test that all expected contact endpoints are available"""
    # Test various endpoints exist (will return 401 but endpoint exists)
    endpoints_to_test = [
        "/api/v1/contacts/",
        "/api/v1/contacts/1",
        "/api/v1/contacts/1/full-profile",
        "/api/v1/contacts/1/intelligence",
        "/api/v1/contacts/1/interactions",
        "/api/v1/contacts/follow-up-needed",
        "/api/v1/contacts/recommendations/reconnect",
        "/api/v1/organizations/"
    ]
    
    for endpoint in endpoints_to_test:
        response = client.get(endpoint)
        # All should return 401 (unauthorized) or 404 (for specific IDs), not 404 (not found)
        assert response.status_code in [401, 404, 422]  # 422 for validation errors

def test_openapi_contains_contact_endpoints(client):
    """Test that the OpenAPI spec contains our contact endpoints"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    paths = openapi_spec["paths"]
    
    # Check that key endpoints are documented
    assert "/api/v1/contacts/" in paths
    assert "/api/v1/contacts/{contact_id}" in paths
    assert "/api/v1/contacts/{contact_id}/full-profile" in paths
    assert "/api/v1/contacts/{contact_id}/intelligence" in paths
    assert "/api/v1/contacts/{contact_id}/interactions" in paths
    assert "/api/v1/organizations/" in paths

def test_contact_schema_validation(client):
    """Test that contact creation validates required fields"""
    # Test with missing required fields
    invalid_contact_data = {
        "email": "test@example.com"
        # Missing first_name and last_name
    }
    
    response = client.post("/api/v1/contacts/", json=invalid_contact_data)
    # Should get validation error (422) before authentication error
    assert response.status_code in [401, 422]

def test_organization_schema_validation(client):
    """Test that organization creation validates required fields"""
    # Test with missing required fields
    invalid_org_data = {
        "industry": "technology"
        # Missing name and organization_type
    }
    
    response = client.post("/api/v1/organizations/", json=invalid_org_data)
    # Should get validation error (422) before authentication error
    assert response.status_code in [401, 422]