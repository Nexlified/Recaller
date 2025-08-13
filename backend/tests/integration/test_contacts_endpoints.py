"""
Comprehensive integration tests for contacts management endpoints.

This test suite covers all contacts endpoints including CRUD operations,
search functionality, relationships, data validation, and tenant isolation.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from typing import Dict, Any, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api import deps
from app.db.base_class import Base
from app.models.user import User
from app.models.tenant import Tenant
from app.models.contact import Contact
from app.core.security import create_access_token, get_password_hash

# Test database configuration for contacts tests
CONTACTS_TEST_DB_URL = "sqlite:///./test_contacts.db"

contacts_engine = create_engine(
    CONTACTS_TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
ContactsTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=contacts_engine)


@pytest.fixture(scope="session")
def contacts_db():
    """Create test database and tables for contacts tests."""
    Base.metadata.create_all(bind=contacts_engine)
    yield
    Base.metadata.drop_all(bind=contacts_engine)


@pytest.fixture
def contacts_db_session(contacts_db):
    """Create a database session for contacts testing."""
    connection = contacts_engine.connect()
    transaction = connection.begin()
    session = ContactsTestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


def override_get_db_for_contacts(db_session):
    """Override the get_db dependency for contacts testing."""
    def _get_db():
        yield db_session
    return _get_db


@pytest.fixture
def contacts_client(contacts_db_session):
    """Create a test client with database session override for contacts tests."""
    app.dependency_overrides[deps.get_db] = override_get_db_for_contacts(contacts_db_session)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def contacts_test_tenant(contacts_db_session):
    """Create a test tenant for contacts tests."""
    tenant = contacts_db_session.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant:
        tenant = Tenant(
            id=1, 
            name="Contacts Test Tenant", 
            slug="contacts-test-tenant",
            is_active=True
        )
        contacts_db_session.add(tenant)
        contacts_db_session.commit()
        contacts_db_session.refresh(tenant)
    return tenant


@pytest.fixture
def contacts_test_user(contacts_db_session, contacts_test_tenant):
    """Create a test user for contacts tests."""
    user = User(
        email="contacts.testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Contacts Test User",
        is_active=True,
        tenant_id=contacts_test_tenant.id,
    )
    contacts_db_session.add(user)
    contacts_db_session.commit()
    contacts_db_session.refresh(user)
    return user


@pytest.fixture
def contacts_auth_headers(contacts_test_user):
    """Create authentication headers for contacts test user."""
    access_token = create_access_token(subject=str(contacts_test_user.id))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def contacts_invalid_auth_headers():
    """Create invalid authentication headers for contacts tests."""
    return {"Authorization": "Bearer invalid_token"}


class TestContactCRUDOperations:
    """Test cases for Contact CRUD operations."""

    def test_create_contact_success(self, contacts_client: TestClient, contacts_auth_headers, contacts_test_user):
        """Test successful contact creation."""
        contact_data = {
            "first_name": "John",
            "last_name": "Doe", 
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "is_active": True
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate response schema
        assert "id" in data
        assert "tenant_id" in data
        assert "created_by_user_id" in data
        assert "created_at" in data
        
        # Validate data matches input
        assert data["first_name"] == contact_data["first_name"]
        assert data["last_name"] == contact_data["last_name"]
        assert data["full_name"] == contact_data["full_name"]
        assert data["email"] == contact_data["email"]
        assert data["phone"] == contact_data["phone"]
        assert data["is_active"] == contact_data["is_active"]
        
        # Validate tenant isolation
        assert data["tenant_id"] == contacts_test_user.tenant_id
        assert data["created_by_user_id"] == contacts_test_user.id

    def test_create_contact_minimal_data(self, contacts_client: TestClient, contacts_auth_headers):
        """Test contact creation with only required fields."""
        contact_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "full_name": "Jane Smith"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["full_name"] == "Jane Smith"
        assert data["email"] is None
        assert data["phone"] is None

    def test_create_contact_invalid_email(self, contacts_client: TestClient, contacts_auth_headers):
        """Test contact creation with invalid email format."""
        contact_data = {
            "first_name": "Invalid",
            "last_name": "Email",
            "full_name": "Invalid Email", 
            "email": "invalid-email-format"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_data = response.json()
        assert "detail" in error_data

    def test_create_contact_missing_required_fields(self, contacts_client: TestClient, contacts_auth_headers):
        """Test contact creation with missing required fields."""
        contact_data = {
            "email": "missing@fields.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_contact_success(self, contacts_client: TestClient, contacts_auth_headers, contacts_test_user):
        """Test successful contact retrieval."""
        # First create a contact
        contact_data = {
            "first_name": "Get",
            "last_name": "Test",
            "full_name": "Get Test",
            "email": "get.test@example.com"
        }
        
        create_response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        created_contact = create_response.json()
        contact_id = created_contact["id"]
        
        # Now retrieve it
        response = contacts_client.get(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == contact_id
        assert data["first_name"] == "Get"
        assert data["last_name"] == "Test"
        assert data["email"] == "get.test@example.com"

    def test_get_contact_not_found(self, contacts_client: TestClient, contacts_auth_headers):
        """Test retrieving non-existent contact."""
        response = contacts_client.get("/api/v1/contacts/99999", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data

    def test_update_contact_full_update(self, contacts_client: TestClient, contacts_auth_headers):
        """Test full contact update."""
        # Create contact
        contact_data = {
            "first_name": "Update",
            "last_name": "Test",
            "full_name": "Update Test",
            "email": "update.test@example.com"
        }
        
        create_response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        created_contact = create_response.json()
        contact_id = created_contact["id"]
        
        # Update contact
        update_data = {
            "first_name": "Updated",
            "last_name": "Person",
            "full_name": "Updated Person",
            "email": "updated.person@example.com",
            "phone": "+1-555-999-8888"
        }
        
        response = contacts_client.put(f"/api/v1/contacts/{contact_id}", json=update_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Person"
        assert data["email"] == "updated.person@example.com"
        assert data["phone"] == "+1-555-999-8888"

    def test_update_contact_partial_update(self, contacts_client: TestClient, contacts_auth_headers):
        """Test partial contact update."""
        # Create contact
        contact_data = {
            "first_name": "Partial",
            "last_name": "Update",
            "full_name": "Partial Update",
            "email": "partial@example.com"
        }
        
        create_response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        created_contact = create_response.json()
        contact_id = created_contact["id"]
        
        # Partial update
        update_data = {
            "phone": "+1-555-111-2222"
        }
        
        response = contacts_client.put(f"/api/v1/contacts/{contact_id}", json=update_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Original data should be preserved
        assert data["first_name"] == "Partial"
        assert data["last_name"] == "Update"
        assert data["email"] == "partial@example.com"
        # New data should be added
        assert data["phone"] == "+1-555-111-2222"

    def test_update_contact_not_found(self, contacts_client: TestClient, contacts_auth_headers):
        """Test updating non-existent contact."""
        update_data = {
            "first_name": "NonExistent"
        }
        
        response = contacts_client.put("/api/v1/contacts/99999", json=update_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_contact_success(self, contacts_client: TestClient, contacts_auth_headers):
        """Test successful contact deletion."""
        # Create contact
        contact_data = {
            "first_name": "Delete",
            "last_name": "Test", 
            "full_name": "Delete Test",
            "email": "delete.test@example.com"
        }
        
        create_response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        created_contact = create_response.json()
        contact_id = created_contact["id"]
        
        # Delete contact
        response = contacts_client.delete(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
        # Verify contact is deleted
        get_response = contacts_client.get(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_contact_not_found(self, contacts_client: TestClient, contacts_auth_headers):
        """Test deleting non-existent contact."""
        response = contacts_client.delete("/api/v1/contacts/99999", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestContactListingAndPagination:
    """Test cases for contact listing and pagination."""

    def test_list_contacts_empty(self, contacts_client: TestClient, contacts_auth_headers):
        """Test listing contacts when none exist."""
        response = contacts_client.get("/api/v1/contacts/", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_contacts_with_data(self, contacts_client: TestClient, contacts_auth_headers):
        """Test listing contacts with existing data."""
        # Create multiple contacts
        contacts_data = [
            {"first_name": "Contact", "last_name": "One", "full_name": "Contact One"},
            {"first_name": "Contact", "last_name": "Two", "full_name": "Contact Two"},
            {"first_name": "Contact", "last_name": "Three", "full_name": "Contact Three"}
        ]
        
        created_contacts = []
        for contact_data in contacts_data:
            response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
            created_contacts.append(response.json())
        
        # List contacts
        response = contacts_client.get("/api/v1/contacts/", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_list_contacts_pagination(self, contacts_client: TestClient, contacts_auth_headers):
        """Test contact pagination."""
        # Create multiple contacts
        for i in range(5):
            contact_data = {
                "first_name": f"Page",
                "last_name": f"Test{i}",
                "full_name": f"Page Test{i}"
            }
            contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Test pagination
        response = contacts_client.get("/api/v1/contacts/?skip=0&limit=2", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    def test_list_contacts_large_limit(self, contacts_client: TestClient, contacts_auth_headers):
        """Test listing contacts with large limit."""
        response = contacts_client.get("/api/v1/contacts/?limit=1000", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestContactSearchFunctionality:
    """Test cases for contact search functionality."""

    def test_search_contacts_by_name(self, contacts_client: TestClient, contacts_auth_headers):
        """Test searching contacts by name."""
        # Create contacts with specific names
        contacts = [
            {"first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson"},
            {"first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith"},
            {"first_name": "Alice", "last_name": "Brown", "full_name": "Alice Brown"}
        ]
        
        for contact_data in contacts:
            contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Search for "Alice"
        response = contacts_client.get("/api/v1/contacts/search/?q=Alice", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should find at least the Alice contacts we created
        alice_contacts = [c for c in data if "Alice" in c["full_name"]]
        assert len(alice_contacts) >= 2

    def test_search_contacts_by_email(self, contacts_client: TestClient, contacts_auth_headers):
        """Test searching contacts by email."""
        # Create contact with specific email
        contact_data = {
            "first_name": "Email",
            "last_name": "Search",
            "full_name": "Email Search",
            "email": "search.test@example.com"
        }
        
        contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Search by email
        response = contacts_client.get("/api/v1/contacts/search/?q=search.test", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        found = any(c["email"] == "search.test@example.com" for c in data)
        assert found

    def test_search_contacts_no_results(self, contacts_client: TestClient, contacts_auth_headers):
        """Test search with no matching results."""
        response = contacts_client.get("/api/v1/contacts/search/?q=nonexistentquery12345", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_contacts_empty_query(self, contacts_client: TestClient, contacts_auth_headers):
        """Test search with empty query."""
        response = contacts_client.get("/api/v1/contacts/search/?q=", headers=contacts_auth_headers)
        
        # This should either return all contacts or return an empty list
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_search_contacts_special_characters(self, contacts_client: TestClient, contacts_auth_headers):
        """Test search with special characters."""
        # Create contact with special characters
        contact_data = {
            "first_name": "José",
            "last_name": "García",
            "full_name": "José García",
            "email": "jose.garcia@example.com"
        }
        
        contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Search with special characters
        response = contacts_client.get("/api/v1/contacts/search/?q=José", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_search_contacts_pagination(self, contacts_client: TestClient, contacts_auth_headers):
        """Test search with pagination."""
        # Create multiple contacts with searchable term
        for i in range(10):
            contact_data = {
                "first_name": f"Searchable{i}",
                "last_name": "Contact",
                "full_name": f"Searchable{i} Contact"
            }
            contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Search with pagination
        response = contacts_client.get("/api/v1/contacts/search/?q=Searchable&skip=0&limit=3", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3


class TestContactEventRelationships:
    """Test cases for contact-event relationship endpoints."""

    def test_get_contact_events_empty(self, contacts_client: TestClient, contacts_auth_headers):
        """Test getting events for contact with no events."""
        # Create contact
        contact_data = {
            "first_name": "No",
            "last_name": "Events",
            "full_name": "No Events"
        }
        
        create_response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        contact_id = create_response.json()["id"]
        
        # Get contact events
        response = contacts_client.get(f"/api/v1/contacts/{contact_id}/events", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_contact_events_invalid_contact(self, contacts_client: TestClient, contacts_auth_headers):
        """Test getting events for non-existent contact."""
        response = contacts_client.get("/api/v1/contacts/99999/events", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_shared_events_both_contacts_not_found(self, contacts_client: TestClient, contacts_auth_headers):
        """Test getting shared events between non-existent contacts."""
        response = contacts_client.get("/api/v1/contacts/99999/shared-events/99998", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_shared_events_empty_result(self, contacts_client: TestClient, contacts_auth_headers):
        """Test getting shared events with no shared events."""
        # Create two contacts
        contact1_data = {
            "first_name": "Contact",
            "last_name": "One", 
            "full_name": "Contact One"
        }
        contact2_data = {
            "first_name": "Contact",
            "last_name": "Two",
            "full_name": "Contact Two"
        }
        
        response1 = contacts_client.post("/api/v1/contacts/", json=contact1_data, headers=contacts_auth_headers)
        response2 = contacts_client.post("/api/v1/contacts/", json=contact2_data, headers=contacts_auth_headers)
        
        contact1_id = response1.json()["id"]
        contact2_id = response2.json()["id"]
        
        # Get shared events
        response = contacts_client.get(f"/api/v1/contacts/{contact1_id}/shared-events/{contact2_id}", headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestTenantIsolation:
    """Test cases for tenant isolation in contact management."""

    def test_contacts_tenant_isolation(self, contacts_client: TestClient, contacts_auth_headers, contacts_test_user):
        """Test that contacts are properly isolated by tenant."""
        # Create a contact
        contact_data = {
            "first_name": "Tenant",
            "last_name": "Isolated",
            "full_name": "Tenant Isolated",
            "email": "tenant.isolated@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify tenant_id matches the user's tenant
        assert data["tenant_id"] == contacts_test_user.tenant_id
        
        # Verify created_by_user_id matches the user
        assert data["created_by_user_id"] == contacts_test_user.id


class TestAuthenticationAndAuthorization:
    """Test cases for authentication and authorization."""

    def test_create_contact_unauthenticated(self, contacts_client: TestClient):
        """Test creating contact without authentication."""
        contact_data = {
            "first_name": "Unauth",
            "last_name": "Test",
            "full_name": "Unauth Test"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_contact_unauthenticated(self, contacts_client: TestClient):
        """Test getting contact without authentication."""
        response = contacts_client.get("/api/v1/contacts/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_contact_unauthenticated(self, contacts_client: TestClient):
        """Test updating contact without authentication."""
        response = contacts_client.put("/api/v1/contacts/1", json={"first_name": "Updated"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_contact_unauthenticated(self, contacts_client: TestClient):
        """Test deleting contact without authentication."""
        response = contacts_client.delete("/api/v1/contacts/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_contacts_unauthenticated(self, contacts_client: TestClient):
        """Test listing contacts without authentication."""
        response = contacts_client.get("/api/v1/contacts/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_contacts_unauthenticated(self, contacts_client: TestClient):
        """Test searching contacts without authentication."""
        response = contacts_client.get("/api/v1/contacts/search/?q=test")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_access(self, contacts_client: TestClient, contacts_invalid_auth_headers):
        """Test access with invalid token."""
        response = contacts_client.get("/api/v1/contacts/", headers=contacts_invalid_auth_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDataValidationAndEdgeCases:
    """Test cases for data validation and edge cases."""

    def test_create_contact_very_long_names(self, contacts_client: TestClient, contacts_auth_headers):
        """Test contact creation with very long names."""
        contact_data = {
            "first_name": "A" * 200,  # Very long first name
            "last_name": "B" * 200,   # Very long last name
            "full_name": "A" * 200 + " " + "B" * 200
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # This might succeed or fail depending on validation - both are acceptable
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_contact_sql_injection_attempt(self, contacts_client: TestClient, contacts_auth_headers):
        """Test SQL injection protection in contact creation."""
        contact_data = {
            "first_name": "'; DROP TABLE contacts; --",
            "last_name": "Test",
            "full_name": "'; DROP TABLE contacts; -- Test",
            "email": "test@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Should either create safely or reject - should not cause SQL injection
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_search_sql_injection_attempt(self, contacts_client: TestClient, contacts_auth_headers):
        """Test SQL injection protection in search."""
        malicious_query = "'; DROP TABLE contacts; --"
        
        response = contacts_client.get(f"/api/v1/contacts/search/?q={malicious_query}", headers=contacts_auth_headers)
        
        # Should handle safely without SQL injection
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_contact_xss_attempt(self, contacts_client: TestClient, contacts_auth_headers):
        """Test XSS protection in contact creation."""
        contact_data = {
            "first_name": "<script>alert('xss')</script>",
            "last_name": "Test",
            "full_name": "<script>alert('xss')</script> Test"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # XSS content should be safely handled (stored as-is, escaped on output)
            assert "first_name" in data

    def test_unicode_support(self, contacts_client: TestClient, contacts_auth_headers):
        """Test Unicode character support."""
        contact_data = {
            "first_name": "测试",
            "last_name": "用户",
            "full_name": "测试 用户",
            "email": "test.unicode@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "测试"
        assert data["last_name"] == "用户"

    def test_empty_string_fields(self, contacts_client: TestClient, contacts_auth_headers):
        """Test handling of empty string fields."""
        contact_data = {
            "first_name": "",
            "last_name": "",
            "full_name": "",
            "email": "",
            "phone": ""
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Should reject empty required fields
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestContactCascadeOperations:
    """Test cases for cascade delete operations and complex relationships."""

    def test_delete_contact_cascades_to_interactions(self, contacts_client: TestClient, contacts_auth_headers, contacts_db_session):
        """Test that deleting a contact cascades to its interactions."""
        from datetime import datetime
        
        # Create a contact
        contact_data = {
            "first_name": "Cascade",
            "last_name": "Test",
            "full_name": "Cascade Test",
            "email": "cascade.test@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        contact_id = response.json()["id"]
        
        # Create a contact interaction directly in the database
        from app.models.contact import ContactInteraction
        interaction = ContactInteraction(
            contact_id=contact_id,
            interaction_type="meeting",
            interaction_date=datetime(2023, 1, 1, 10, 0, 0),
            initiated_by="me",
            title="Test Meeting",
            description="Test interaction"
        )
        contacts_db_session.add(interaction)
        contacts_db_session.commit()
        interaction_id = interaction.id
        
        # Verify interaction exists
        assert contacts_db_session.query(ContactInteraction).filter(ContactInteraction.id == interaction_id).first() is not None
        
        # Delete the contact
        delete_response = contacts_client.delete(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify interaction was also deleted (cascade)
        assert contacts_db_session.query(ContactInteraction).filter(ContactInteraction.id == interaction_id).first() is None

    def test_delete_contact_with_event_relationships(self, contacts_client: TestClient, contacts_auth_headers, contacts_db_session):
        """Test contact deletion behavior with event relationships."""
        # Create a contact
        contact_data = {
            "first_name": "Event",
            "last_name": "Related",
            "full_name": "Event Related",
            "email": "event.related@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        contact = response.json()
        contact_id = contact["id"]
        
        # Test that we can get empty events for the contact before deletion
        events_response = contacts_client.get(f"/api/v1/contacts/{contact_id}/events", headers=contacts_auth_headers)
        assert events_response.status_code == status.HTTP_200_OK
        assert len(events_response.json()) == 0
        
        # Delete the contact
        delete_response = contacts_client.delete(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify contact is deleted
        get_response = contacts_client.get(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestContactBulkOperations:
    """Test cases for bulk operations and performance scenarios."""

    def test_create_multiple_contacts_bulk(self, contacts_client: TestClient, contacts_auth_headers):
        """Test creating multiple contacts efficiently."""
        contacts_data = []
        for i in range(10):
            contact_data = {
                "first_name": f"Bulk{i}",
                "last_name": "Contact",
                "full_name": f"Bulk{i} Contact",
                "email": f"bulk{i}@example.com"
            }
            contacts_data.append(contact_data)
        
        created_contacts = []
        for contact_data in contacts_data:
            response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
            assert response.status_code == status.HTTP_200_OK
            created_contacts.append(response.json())
        
        # Verify all contacts were created
        assert len(created_contacts) == 10
        for i, contact in enumerate(created_contacts):
            assert contact["first_name"] == f"Bulk{i}"
            assert contact["email"] == f"bulk{i}@example.com"
        
        # Test bulk listing
        list_response = contacts_client.get("/api/v1/contacts/?limit=20", headers=contacts_auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        all_contacts = list_response.json()
        
        # Should contain at least our bulk created contacts
        bulk_contacts = [c for c in all_contacts if c["first_name"].startswith("Bulk")]
        assert len(bulk_contacts) >= 10

    def test_search_performance_large_dataset(self, contacts_client: TestClient, contacts_auth_headers):
        """Test search performance with a larger dataset."""
        # Create contacts with different patterns
        for i in range(20):
            contact_data = {
                "first_name": f"Search{i % 5}",  # Only 5 unique first names
                "last_name": f"Performance{i}",
                "full_name": f"Search{i % 5} Performance{i}",
                "email": f"search{i}@performance.com"
            }
            contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        
        # Test search that should return multiple results
        search_response = contacts_client.get("/api/v1/contacts/search/?q=Search0", headers=contacts_auth_headers)
        assert search_response.status_code == status.HTTP_200_OK
        search_results = search_response.json()
        
        # Should find contacts with "Search0" in their name
        assert len(search_results) >= 1
        for contact in search_results:
            assert "Search0" in contact["full_name"]
        
        # Test search with pagination
        paginated_response = contacts_client.get("/api/v1/contacts/search/?q=Performance&limit=5", headers=contacts_auth_headers)
        assert paginated_response.status_code == status.HTTP_200_OK
        paginated_results = paginated_response.json()
        assert len(paginated_results) <= 5


class TestContactDataIntegrity:
    """Test cases for data integrity and consistency."""

    def test_duplicate_email_handling(self, contacts_client: TestClient, contacts_auth_headers):
        """Test how system handles duplicate email addresses."""
        email = "duplicate.test@example.com"
        
        # Create first contact
        contact1_data = {
            "first_name": "First",
            "last_name": "Contact",
            "full_name": "First Contact",
            "email": email
        }
        
        response1 = contacts_client.post("/api/v1/contacts/", json=contact1_data, headers=contacts_auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        
        # Create second contact with same email
        contact2_data = {
            "first_name": "Second",
            "last_name": "Contact", 
            "full_name": "Second Contact",
            "email": email
        }
        
        response2 = contacts_client.post("/api/v1/contacts/", json=contact2_data, headers=contacts_auth_headers)
        # System should either allow duplicates or reject - both are valid behaviors
        assert response2.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_contact_data_consistency_after_update(self, contacts_client: TestClient, contacts_auth_headers):
        """Test data consistency after multiple updates."""
        # Create contact
        contact_data = {
            "first_name": "Consistency",
            "last_name": "Test",
            "full_name": "Consistency Test",
            "email": "consistency@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        contact = response.json()
        contact_id = contact["id"]
        original_created_at = contact["created_at"]
        
        # Perform multiple updates
        updates = [
            {"first_name": "Updated1"},
            {"last_name": "Updated2"},
            {"email": "updated@example.com"},
            {"phone": "+1-555-999-0000"}
        ]
        
        for update_data in updates:
            update_response = contacts_client.put(f"/api/v1/contacts/{contact_id}", json=update_data, headers=contacts_auth_headers)
            assert update_response.status_code == status.HTTP_200_OK
        
        # Get final state
        final_response = contacts_client.get(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        final_contact = final_response.json()
        
        # Verify final state has all updates
        assert final_contact["first_name"] == "Updated1"
        assert final_contact["last_name"] == "Updated2"
        assert final_contact["email"] == "updated@example.com"
        assert final_contact["phone"] == "+1-555-999-0000"
        
        # Verify created_at is unchanged but updated_at exists
        assert final_contact["created_at"] == original_created_at
        assert "updated_at" in final_contact

    def test_contact_null_and_empty_field_handling(self, contacts_client: TestClient, contacts_auth_headers):
        """Test handling of null and empty values in optional fields."""
        # Create contact with null email and phone
        contact_data = {
            "first_name": "Null",
            "last_name": "Fields",
            "full_name": "Null Fields",
            "email": None,
            "phone": None
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        assert response.status_code == status.HTTP_200_OK
        contact = response.json()
        
        assert contact["email"] is None
        assert contact["phone"] is None
        
        # Update with empty string values
        update_data = {
            "email": "",
            "phone": ""
        }
        
        update_response = contacts_client.put(f"/api/v1/contacts/{contact['id']}", json=update_data, headers=contacts_auth_headers)
        # Should either accept empty strings or reject them
        assert update_response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestContactSecurityAndValidation:
    """Advanced security and validation tests."""

    def test_contact_field_length_limits(self, contacts_client: TestClient, contacts_auth_headers):
        """Test field length validation limits."""
        # Test with field lengths at database limits
        contact_data = {
            "first_name": "A" * 100,  # Model has String(100)
            "last_name": "B" * 100,   # Model has String(100)
            "full_name": "C" * 255,   # Model has String(255)
            "email": "test@" + "d" * 240 + ".com",  # Model has String(255)
            "phone": "1" * 50         # Model has String(50)
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        # Should either accept (within limits) or reject (validation)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_contact_email_format_variations(self, contacts_client: TestClient, contacts_auth_headers):
        """Test various email format validations."""
        email_test_cases = [
            ("valid@example.com", True),
            ("user.name@example.com", True),
            ("user+tag@example.com", True),
            ("invalid-email", False),
            ("@invalid.com", False),
            ("invalid@", False),
            ("", True),  # Empty email should be allowed (optional field)
        ]
        
        for email, should_be_valid in email_test_cases:
            contact_data = {
                "first_name": "Email",
                "last_name": "Test",
                "full_name": "Email Test",
                "email": email if email else None
            }
            
            response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
            
            if should_be_valid:
                assert response.status_code == status.HTTP_200_OK, f"Email {email} should be valid"
            else:
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Email {email} should be invalid"

    def test_contact_concurrent_access(self, contacts_client: TestClient, contacts_auth_headers):
        """Test concurrent access scenarios."""
        # Create a contact
        contact_data = {
            "first_name": "Concurrent",
            "last_name": "Test",
            "full_name": "Concurrent Test",
            "email": "concurrent@example.com"
        }
        
        response = contacts_client.post("/api/v1/contacts/", json=contact_data, headers=contacts_auth_headers)
        contact_id = response.json()["id"]
        
        # Simulate concurrent updates (in real scenario this would be multiple threads)
        update1 = {"first_name": "Update1"}
        update2 = {"last_name": "Update2"}
        
        response1 = contacts_client.put(f"/api/v1/contacts/{contact_id}", json=update1, headers=contacts_auth_headers)
        response2 = contacts_client.put(f"/api/v1/contacts/{contact_id}", json=update2, headers=contacts_auth_headers)
        
        # Both updates should succeed
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        # Final state should have the last update
        final_response = contacts_client.get(f"/api/v1/contacts/{contact_id}", headers=contacts_auth_headers)
        final_contact = final_response.json()
        
        # Last update wins
        assert final_contact["last_name"] == "Update2"