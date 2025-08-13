"""
Simple integration tests for user management endpoints.

This is a focused test suite that tests the core user endpoints without
complex model dependencies.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestGetCurrentUserSimple:
    """Test cases for GET /api/v1/users/me endpoint."""
    
    def test_get_current_user_success(self, client: TestClient, auth_headers, test_user):
        """Test successful retrieval of current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate response schema and data
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "is_active" in data
        assert "created_at" in data
        
        # Validate actual data matches test user
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["is_active"] == test_user.is_active
        
        # Ensure sensitive data is not included
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Test GET /me without authentication token."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
    
    def test_get_current_user_invalid_token(self, client: TestClient, invalid_auth_headers):
        """Test GET /me with invalid authentication token."""
        response = client.get("/api/v1/users/me", headers=invalid_auth_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data


class TestUpdateCurrentUserSimple:
    """Test cases for PUT /api/v1/users/me endpoint."""
    
    def test_update_current_user_full_name(self, client: TestClient, auth_headers, test_user):
        """Test updating current user's full name."""
        update_data = {"full_name": "Updated Test User"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate the update was successful
        assert data["full_name"] == "Updated Test User"
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email  # Email should remain unchanged
    
    def test_update_current_user_email(self, client: TestClient, auth_headers, test_user):
        """Test updating current user's email."""
        update_data = {"email": "newemail@example.com"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate the update was successful
        assert data["email"] == "newemail@example.com"
        assert data["id"] == test_user.id
        assert data["full_name"] == test_user.full_name  # Name should remain unchanged
    
    def test_update_current_user_invalid_email_format(self, client: TestClient, auth_headers):
        """Test updating with invalid email format."""
        update_data = {"email": "invalid-email-format"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        # Validate error details for email validation
        errors = data["detail"]
        assert any("email" in str(error) for error in errors)
    
    def test_update_current_user_unauthenticated(self, client: TestClient):
        """Test updating user profile without authentication."""
        update_data = {"full_name": "Should Not Work"}
        
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestResponseSchemasSimple:
    """Test cases to validate response schemas and data types."""
    
    def test_user_response_schema(self, client: TestClient, auth_headers, test_user):
        """Test that user response matches expected schema."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate required fields and their types
        assert isinstance(data["id"], int)
        assert isinstance(data["email"], str)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["created_at"], str)
        
        # Validate optional fields
        if data.get("full_name") is not None:
            assert isinstance(data["full_name"], str)
        if data.get("updated_at") is not None:
            assert isinstance(data["updated_at"], str)
        
        # Ensure sensitive fields are not present
        assert "password" not in data
        assert "hashed_password" not in data
        assert "tenant_id" not in data  # Internal field should not be exposed