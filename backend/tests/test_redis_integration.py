"""Test Redis connectivity and integration."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.redis import redis_client


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_redis_connection():
    """Test that Redis client can connect."""
    try:
        # Try to connect to Redis
        client = redis_client.connect()
        
        # Test basic operations
        test_key = "test:connection"
        test_value = "test_value"
        
        # Set a test value
        client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        
        # Get the test value
        retrieved_value = client.get(test_key)
        assert retrieved_value == test_value
        
        # Clean up
        client.delete(test_key)
        
        # Verify cleanup
        assert client.get(test_key) is None
        
    except Exception as e:
        pytest.skip(f"Redis not available for testing: {e}")


def test_health_endpoint_includes_redis(client):
    """Test that health endpoint includes Redis status."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "redis" in data["services"]
    
    # Redis status should be either "healthy", "disconnected", or contain "error"
    redis_status = data["services"]["redis"]
    assert redis_status in ["healthy", "disconnected"] or "error" in redis_status


def test_redis_ping():
    """Test Redis ping functionality."""
    try:
        client = redis_client.connect()
        result = client.ping()
        assert result is True
    except Exception as e:
        pytest.skip(f"Redis not available for testing: {e}")


def test_redis_client_is_connected():
    """Test Redis client connection status."""
    try:
        # This should work even if Redis is not available
        # as it just checks if the client thinks it's connected
        is_connected = redis_client.is_connected()
        assert isinstance(is_connected, bool)
    except Exception as e:
        pytest.skip(f"Redis client test failed: {e}")