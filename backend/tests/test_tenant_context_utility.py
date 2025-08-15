"""
Tests for the tenant context utility function.
"""
import pytest
from fastapi import HTTPException, Request
from app.api.deps import get_tenant_context


class MockState:
    """Mock state object that doesn't auto-create attributes"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockRequest:
    """Mock request object that doesn't auto-create attributes"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockTenant:
    """Mock tenant object"""
    def __init__(self, tenant_id=None):
        if tenant_id is not None:
            self.id = tenant_id


class TestGetTenantContext:
    """Test suite for get_tenant_context utility function"""

    def test_get_tenant_context_success(self):
        """Test successful tenant context retrieval"""
        # Create mock request with proper tenant context
        tenant = MockTenant(tenant_id=123)
        state = MockState(tenant=tenant)
        request = MockRequest(state=state)
        
        # Test the function
        tenant_id = get_tenant_context(request)
        
        # Assert correct tenant ID is returned
        assert tenant_id == 123
    
    def test_get_tenant_context_missing_tenant_state(self):
        """Test error when tenant is not in request state"""
        state = MockState()  # No tenant attribute
        request = MockRequest(state=state)
        
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_context(request)
        
        assert exc_info.value.status_code == 500
        assert "Tenant context not available" in exc_info.value.detail
    
    def test_get_tenant_context_none_tenant(self):
        """Test error when tenant is None"""
        state = MockState(tenant=None)
        request = MockRequest(state=state)
        
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_context(request)
        
        assert exc_info.value.status_code == 500
        assert "Tenant context not available" in exc_info.value.detail
    
    def test_get_tenant_context_missing_tenant_id(self):
        """Test error when tenant object has no id attribute"""
        tenant = MockTenant()  # No id set
        state = MockState(tenant=tenant)
        request = MockRequest(state=state)
        
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_context(request)
        
        assert exc_info.value.status_code == 500
        assert "Invalid tenant context" in exc_info.value.detail
    
    def test_get_tenant_context_none_tenant_id(self):
        """Test error when tenant id is None"""
        tenant = MockTenant(tenant_id=None)
        state = MockState(tenant=tenant)
        request = MockRequest(state=state)
        
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_context(request)
        
        assert exc_info.value.status_code == 500
        assert "Invalid tenant context" in exc_info.value.detail
    
    def test_get_tenant_context_no_state(self):
        """Test error when request has no state"""
        request = MockRequest()  # No state attribute
        
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_context(request)
        
        assert exc_info.value.status_code == 500
        assert "Tenant context not available" in exc_info.value.detail


if __name__ == "__main__":
    # Run tests if executed directly
    print("Running tenant context utility tests...")
    
    test_instance = TestGetTenantContext()
    
    test_methods = [
        test_instance.test_get_tenant_context_success,
        test_instance.test_get_tenant_context_missing_tenant_state,
        test_instance.test_get_tenant_context_none_tenant,
        test_instance.test_get_tenant_context_missing_tenant_id,
        test_instance.test_get_tenant_context_none_tenant_id,
        test_instance.test_get_tenant_context_no_state,
    ]
    
    for test_method in test_methods:
        try:
            print(f"  ✓ {test_method.__name__}")
            test_method()
        except Exception as e:
            print(f"  ❌ {test_method.__name__}: {e}")
            raise
    
    print("🎉 All tenant context utility tests passed!")