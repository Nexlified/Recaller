"""
Comprehensive tests for tenant isolation to ensure no cross-tenant data access.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_context
from app.core.security import create_access_token
from app.crud import user as user_crud
from app.schemas.user import UserCreate


class TestTenantIsolationComprehensive:
    """Test cases to verify complete tenant isolation cannot be bypassed."""
    
    def test_user_authentication_respects_tenant_isolation(self, client: TestClient, db_session: Session):
        """Test that user authentication properly enforces tenant isolation."""
        
        # Create two tenants 
        from app.models.tenant import Tenant
        tenant1 = Tenant(id=1, name="Tenant 1", slug="tenant-1", is_active=True)
        tenant2 = Tenant(id=2, name="Tenant 2", slug="tenant-2", is_active=True)
        db_session.add(tenant1)
        db_session.add(tenant2)
        db_session.commit()
        
        # Create users in different tenants with same email
        user1_data = UserCreate(
            email="user@example.com",
            full_name="User in Tenant 1",
            password="password123",
            is_active=True
        )
        user2_data = UserCreate(
            email="user@example.com",  # Same email, different tenant
            full_name="User in Tenant 2", 
            password="password123",
            is_active=True
        )
        
        user1 = user_crud.create_user(db_session, obj_in=user1_data, tenant_id=1)
        user2 = user_crud.create_user(db_session, obj_in=user2_data, tenant_id=2)
        
        # Test that each user can only be fetched with their correct tenant_id
        fetched_user1 = user_crud.get_user_by_id(db_session, user_id=user1.id, tenant_id=1)
        fetched_user2 = user_crud.get_user_by_id(db_session, user_id=user2.id, tenant_id=2)
        
        assert fetched_user1 is not None
        assert fetched_user1.id == user1.id
        assert fetched_user1.tenant_id == 1
        
        assert fetched_user2 is not None
        assert fetched_user2.id == user2.id
        assert fetched_user2.tenant_id == 2
        
        # Test cross-tenant access is blocked
        cross_fetch1 = user_crud.get_user_by_id(db_session, user_id=user1.id, tenant_id=2)
        cross_fetch2 = user_crud.get_user_by_id(db_session, user_id=user2.id, tenant_id=1)
        
        assert cross_fetch1 is None, "User from tenant 1 should not be accessible via tenant 2"
        assert cross_fetch2 is None, "User from tenant 2 should not be accessible via tenant 1"
    
    def test_user_listing_respects_tenant_isolation(self, client: TestClient, db_session: Session):
        """Test that user listing only returns users from the correct tenant."""
        
        # Create tenants
        from app.models.tenant import Tenant
        tenant1 = Tenant(id=1, name="Tenant 1", slug="tenant-1", is_active=True)
        tenant2 = Tenant(id=2, name="Tenant 2", slug="tenant-2", is_active=True)
        db_session.add(tenant1)
        db_session.add(tenant2)
        db_session.commit()
        
        # Create multiple users in each tenant
        tenant1_users = []
        tenant2_users = []
        
        for i in range(3):
            user1_data = UserCreate(
                email=f"user{i}@tenant1.com",
                full_name=f"User {i} Tenant 1",
                password="password123",
                is_active=True
            )
            user2_data = UserCreate(
                email=f"user{i}@tenant2.com",
                full_name=f"User {i} Tenant 2",
                password="password123", 
                is_active=True
            )
            
            user1 = user_crud.create_user(db_session, obj_in=user1_data, tenant_id=1)
            user2 = user_crud.create_user(db_session, obj_in=user2_data, tenant_id=2)
            
            tenant1_users.append(user1)
            tenant2_users.append(user2)
        
        # Test that listing users respects tenant isolation
        tenant1_listed = user_crud.get_users(db_session, tenant_id=1)
        tenant2_listed = user_crud.get_users(db_session, tenant_id=2)
        
        # Verify tenant 1 users are returned for tenant 1
        tenant1_ids = {user.id for user in tenant1_listed}
        expected_tenant1_ids = {user.id for user in tenant1_users}
        assert expected_tenant1_ids.issubset(tenant1_ids), "All tenant 1 users should be returned"
        
        # Verify tenant 2 users are returned for tenant 2
        tenant2_ids = {user.id for user in tenant2_listed}
        expected_tenant2_ids = {user.id for user in tenant2_users}
        assert expected_tenant2_ids.issubset(tenant2_ids), "All tenant 2 users should be returned"
        
        # Verify no cross-tenant leakage
        assert tenant1_ids.isdisjoint(expected_tenant2_ids), "Tenant 1 listing should not contain tenant 2 users"
        assert tenant2_ids.isdisjoint(expected_tenant1_ids), "Tenant 2 listing should not contain tenant 1 users"
    
    def test_authentication_with_tenant_isolation(self, client: TestClient, db_session: Session):
        """Test that authentication properly uses tenant context."""
        
        # Create tenants
        from app.models.tenant import Tenant
        tenant1 = Tenant(id=1, name="Tenant 1", slug="tenant-1", is_active=True)
        tenant2 = Tenant(id=2, name="Tenant 2", slug="tenant-2", is_active=True)
        db_session.add(tenant1)
        db_session.add(tenant2)
        db_session.commit()
        
        # Create user in tenant 1
        user_data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="password123",
            is_active=True
        )
        user = user_crud.create_user(db_session, obj_in=user_data, tenant_id=1)
        
        # Test authentication with correct tenant
        authenticated_user = user_crud.authenticate(
            db_session, 
            email="test@example.com", 
            password="password123", 
            tenant_id=1
        )
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.tenant_id == 1
        
        # Test authentication with wrong tenant should fail
        wrong_tenant_auth = user_crud.authenticate(
            db_session,
            email="test@example.com",
            password="password123", 
            tenant_id=2
        )
        assert wrong_tenant_auth is None, "Authentication should fail with wrong tenant"
    
    def test_tenant_context_utility_integration(self):
        """Test that the tenant context utility function works correctly."""
        
        # Test successful case
        class MockTenant:
            def __init__(self, tenant_id):
                self.id = tenant_id
        
        class MockState:
            def __init__(self, tenant):
                self.tenant = tenant
        
        class MockRequest:
            def __init__(self, state):
                self.state = state
        
        # Test with valid tenant context
        tenant = MockTenant(123)
        state = MockState(tenant)
        request = MockRequest(state)
        
        tenant_id = get_tenant_context(request)
        assert tenant_id == 123
        
        # Test error cases are handled by existing test_tenant_context_utility.py


if __name__ == "__main__":
    print("Running comprehensive tenant isolation tests...")
    
    # These tests need a proper test environment with database
    # Run with: PYTHONPATH=/path/to/backend python -m pytest tests/test_tenant_isolation_comprehensive.py -v
    
    print("Please run with pytest for full integration testing.")