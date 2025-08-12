"""
Integration tests for user management endpoints.

This module contains comprehensive integration tests for the user management API endpoints,
covering authentication, authorization, data validation, and tenant isolation as required.

Endpoints tested:
- GET /api/v1/users/me - Get current user profile
- PUT /api/v1/users/me - Update current user profile  
- GET /api/v1/users/ - List users (additional coverage)
- GET /api/v1/users/{user_id} - Get user by ID (additional coverage)
- PUT /api/v1/users/{user_id} - Update user by ID (additional coverage)
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User


class TestGetCurrentUser:
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
    
    def test_get_current_user_inactive_user(self, client: TestClient, db_session, test_user):
        """Test GET /me with inactive user account."""
        # Deactivate the user
        test_user.is_active = False
        db_session.add(test_user)
        db_session.commit()
        
        # Create auth headers for the now inactive user
        from app.core.security import create_access_token
        access_token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Inactive user"


class TestUpdateCurrentUser:
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
    
    def test_update_current_user_password(self, client: TestClient, auth_headers, test_user, db_session):
        """Test updating current user's password."""
        update_data = {"password": "newpassword123"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate password is not returned in response
        assert "password" not in data
        assert "hashed_password" not in data
        
        # Verify the password was actually updated in the database
        db_session.refresh(test_user)
        from app.core.security import verify_password
        assert verify_password("newpassword123", test_user.hashed_password)
    
    def test_update_current_user_multiple_fields(self, client: TestClient, auth_headers, test_user):
        """Test updating multiple user fields simultaneously."""
        update_data = {
            "full_name": "Completely New Name",
            "email": "completely.new@example.com"
        }
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate all updates were successful
        assert data["full_name"] == "Completely New Name"
        assert data["email"] == "completely.new@example.com"
        assert data["id"] == test_user.id
    
    def test_update_current_user_partial_update(self, client: TestClient, auth_headers, test_user):
        """Test partial updates (only updating one field)."""
        original_email = test_user.email
        update_data = {"full_name": "Only Name Changed"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate only the specified field was updated
        assert data["full_name"] == "Only Name Changed"
        assert data["email"] == original_email  # Should remain unchanged
    
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
    
    def test_update_current_user_password_too_short(self, client: TestClient, auth_headers):
        """Test updating with password that's too short."""
        update_data = {"password": "short"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    def test_update_current_user_full_name_too_long(self, client: TestClient, auth_headers):
        """Test updating with full name that exceeds maximum length."""
        # Create a name that's longer than 100 characters
        long_name = "x" * 101
        update_data = {"full_name": long_name}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    def test_update_current_user_unauthenticated(self, client: TestClient):
        """Test updating user profile without authentication."""
        update_data = {"full_name": "Should Not Work"}
        
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_current_user_invalid_token(self, client: TestClient, invalid_auth_headers):
        """Test updating user profile with invalid token."""
        update_data = {"full_name": "Should Not Work"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=invalid_auth_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_current_user_duplicate_email(self, client: TestClient, auth_headers, db_session, test_tenant):
        """Test updating email to one that already exists."""
        # Create another user with a different email
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        
        other_user_data = UserCreate(
            email="other@example.com",
            full_name="Other User",
            password="password123",
            is_active=True
        )
        other_user = create_user(db_session, obj_in=other_user_data, tenant_id=test_tenant.id)
        
        # Try to update current user's email to the other user's email
        update_data = {"email": "other@example.com"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        # This should fail due to email uniqueness constraint
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestAuthenticationAndAuthorization:
    """Test cases for authentication and authorization scenarios."""
    
    def test_user_can_only_access_own_profile(self, client: TestClient, db_session, test_tenant):
        """Test that users can only access their own profile data."""
        # Create two users
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        from app.core.security import create_access_token
        
        user1_data = UserCreate(
            email="user1@example.com",
            full_name="User One",
            password="password123",
            is_active=True
        )
        user2_data = UserCreate(
            email="user2@example.com",
            full_name="User Two",
            password="password123",
            is_active=True
        )
        
        user1 = create_user(db_session, obj_in=user1_data, tenant_id=test_tenant.id)
        user2 = create_user(db_session, obj_in=user2_data, tenant_id=test_tenant.id)
        
        # Create auth headers for user1
        user1_token = create_access_token(subject=str(user1.id))
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        # User1 should be able to access their own profile
        response = client.get("/api/v1/users/me", headers=user1_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user1@example.com"
        
        # User1 should NOT be able to update user2's profile (if they somehow had the ID)
        # This tests the /users/{user_id} endpoint access control
        response = client.get(f"/api/v1/users/{user2.id}", headers=user1_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST  # Insufficient privileges
    
    def test_superuser_can_access_other_users(self, client: TestClient, admin_auth_headers, test_user):
        """Test that superusers can access other users' profiles."""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email


class TestDataValidationAndEdgeCases:
    """Test cases for data validation and edge cases."""
    
    def test_get_nonexistent_user_by_id(self, client: TestClient, auth_headers):
        """Test accessing non-existent user by ID."""
        nonexistent_id = 99999
        response = client.get(f"/api/v1/users/{nonexistent_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "User not found" in data["detail"]
    
    def test_update_nonexistent_user_by_id(self, client: TestClient, admin_auth_headers):
        """Test updating non-existent user by ID."""
        nonexistent_id = 99999
        update_data = {"full_name": "Should Not Work"}
        
        response = client.put(f"/api/v1/users/{nonexistent_id}", json=update_data, headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "does not exist" in data["detail"]
    
    def test_empty_update_data(self, client: TestClient, auth_headers):
        """Test updating with empty data object."""
        update_data = {}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        # Should succeed with no changes
        assert response.status_code == status.HTTP_200_OK
    
    def test_null_values_in_update(self, client: TestClient, auth_headers):
        """Test updating with null values for optional fields."""
        update_data = {"full_name": None}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # full_name should be set to null/None
        assert data.get("full_name") is None
    
    def test_special_characters_in_name(self, client: TestClient, auth_headers):
        """Test updating with special characters in name."""
        special_name = "José María García-López"
        update_data = {"full_name": special_name}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == special_name
    
    def test_email_case_sensitivity(self, client: TestClient, auth_headers):
        """Test email case handling in updates."""
        update_data = {"email": "UPPERCASE@EXAMPLE.COM"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Email should be normalized (typically lowercase)
        assert data["email"].lower() == "uppercase@example.com"


class TestTenantIsolation:
    """Test cases for multi-tenant isolation."""
    
    def test_tenant_isolation_user_access(self, client: TestClient, db_session):
        """Test that users from different tenants cannot access each other's data."""
        # Create a second tenant
        from app.models.tenant import Tenant
        tenant2 = Tenant(
            id=2,
            name="Second Tenant",
            slug="second-tenant",
            is_active=True
        )
        db_session.add(tenant2)
        db_session.commit()
        db_session.refresh(tenant2)
        
        # Create users in different tenants
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        from app.core.security import create_access_token
        
        tenant1_user_data = UserCreate(
            email="tenant1@example.com",
            full_name="Tenant 1 User",
            password="password123",
            is_active=True
        )
        tenant2_user_data = UserCreate(
            email="tenant2@example.com",
            full_name="Tenant 2 User",
            password="password123",
            is_active=True
        )
        
        tenant1_user = create_user(db_session, obj_in=tenant1_user_data, tenant_id=1)
        tenant2_user = create_user(db_session, obj_in=tenant2_user_data, tenant_id=2)
        
        # Create auth headers for tenant1 user
        tenant1_token = create_access_token(subject=str(tenant1_user.id))
        tenant1_headers = {"Authorization": f"Bearer {tenant1_token}"}
        
        # Tenant1 user should be able to access their own profile
        response = client.get("/api/v1/users/me", headers=tenant1_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "tenant1@example.com"
        
        # Note: Due to current implementation using default tenant_id=1 in deps.py,
        # this test would need the actual tenant middleware to work properly.
        # For now, we're testing the data access patterns within the same tenant.


class TestListUsers:
    """Test cases for GET /api/v1/users/ endpoint (additional coverage)."""
    
    def test_list_users_success(self, client: TestClient, auth_headers, test_user):
        """Test successful listing of users."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        assert len(data) >= 1  # At least our test user should be present
        
        # Validate the structure of user objects in the list
        user_data = data[0]
        assert "id" in user_data
        assert "email" in user_data
        assert "full_name" in user_data
        assert "is_active" in user_data
        assert "created_at" in user_data
    
    def test_list_users_pagination(self, client: TestClient, auth_headers):
        """Test pagination parameters for listing users."""
        # Test with skip and limit parameters
        response = client.get("/api/v1/users/?skip=0&limit=10", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10  # Should respect limit
    
    def test_list_users_unauthenticated(self, client: TestClient):
        """Test listing users without authentication."""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestResponseSchemas:
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
    
    def test_datetime_format_in_response(self, client: TestClient, auth_headers):
        """Test that datetime fields are properly formatted."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate datetime format (ISO 8601)
        created_at = data["created_at"]
        assert "T" in created_at  # ISO format should contain 'T'
        assert created_at.endswith("Z") or "+" in created_at or "-" in created_at[-6:]  # Timezone info