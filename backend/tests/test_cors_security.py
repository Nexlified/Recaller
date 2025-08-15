"""
CORS Security Tests

Tests to verify that CORS configuration is secure and restricts access appropriately.
These tests ensure that the CORS configuration does not use wildcard permissions
that could compromise security.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


class TestCORSSecurity:
    """Test CORS security configuration."""
    
    def test_cors_no_wildcards_in_config(self):
        """Test that configuration doesn't contain dangerous wildcards."""
        # Verify settings don't contain wildcards
        origins = settings.get_cors_origins()
        methods = settings.get_cors_methods()
        headers = settings.get_cors_headers()
        
        assert "*" not in origins, "CORS origins should not include wildcard"
        assert "*" not in methods, "CORS methods should not include wildcard" 
        assert "*" not in headers, "CORS headers should not include wildcard"
        
        # Verify we have specific allowed origins
        assert len(origins) > 0, "Should have specific allowed origins"
        assert all(origin.startswith("http") for origin in origins), "Origins should be full URLs"
    
    def test_cors_allowed_origin_gets_headers(self):
        """Test that requests from allowed origins get CORS headers."""
        allowed_origin = settings.get_cors_origins()[0]
        
        response = client.options("/api/v1/contacts/", headers={
            "Origin": allowed_origin
        })
        
        # Should get CORS headers for allowed origin
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == allowed_origin
    
    def test_cors_disallowed_origin_blocked(self):
        """Test that requests from disallowed origins are properly handled."""
        malicious_origins = [
            "https://malicious.com",
            "http://attacker.evil",
            "https://phishing-site.com"
        ]
        
        for origin in malicious_origins:
            response = client.options("/api/v1/contacts/", headers={
                "Origin": origin
            })
            
            # Should not get CORS headers for disallowed origin
            cors_origin = response.headers.get("access-control-allow-origin")
            assert cors_origin != origin, f"Origin {origin} should not be allowed"
    
    def test_cors_methods_restricted(self):
        """Test that only allowed HTTP methods are permitted."""
        allowed_origin = settings.get_cors_origins()[0]
        
        response = client.options("/api/v1/contacts/", headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "GET"
        })
        
        if response.status_code == 200:
            methods_header = response.headers.get("access-control-allow-methods", "")
            allowed_methods = [method.strip() for method in methods_header.split(",")]
            
            # Should include standard safe methods
            expected_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            for method in expected_methods:
                assert method in allowed_methods, f"Method {method} should be allowed"
            
            # Should not include dangerous methods
            dangerous_methods = ["TRACE", "CONNECT"]
            for method in dangerous_methods:
                assert method not in allowed_methods, f"Dangerous method {method} should not be allowed"
            
            # Should not include wildcard
            assert "*" not in allowed_methods, "Wildcard methods should not be allowed"
    
    def test_cors_headers_restricted(self):
        """Test that only necessary headers are allowed."""
        allowed_origin = settings.get_cors_origins()[0]
        
        # Test with a common header request
        response = client.options("/api/v1/contacts/", headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        })
        
        # Check that response doesn't include wildcard headers
        headers_value = response.headers.get("access-control-allow-headers", "")
        if headers_value:
            allowed_headers = [header.strip() for header in headers_value.split(",")]
            assert "*" not in allowed_headers, "Wildcard headers should not be allowed"
    
    def test_cors_credentials_configured(self):
        """Test that credentials policy is properly configured."""
        allowed_origin = settings.get_cors_origins()[0]
        
        response = client.options("/api/v1/contacts/", headers={
            "Origin": allowed_origin
        })
        
        # Should have credentials policy set (either true or false, but not wildcard)
        credentials = response.headers.get("access-control-allow-credentials")
        if credentials:
            assert credentials.lower() in ["true", "false"], "Credentials should be explicit boolean"
    
    def test_cors_preflight_request(self):
        """Test CORS preflight request handling."""
        allowed_origin = settings.get_cors_origins()[0]
        
        # Simulate a preflight request
        response = client.options("/api/v1/contacts/", headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        })
        
        # Preflight should be handled (200 or 405 is acceptable)
        assert response.status_code in [200, 405], "Preflight request should be handled"
        
        # If successful, should have proper CORS headers
        if response.status_code == 200:
            assert "access-control-allow-origin" in response.headers
            assert response.headers["access-control-allow-origin"] == allowed_origin


class TestCORSConfiguration:
    """Test CORS configuration values."""
    
    def test_cors_config_methods(self):
        """Test that CORS configuration methods work correctly."""
        # Test get_cors_origins
        origins = settings.get_cors_origins()
        assert isinstance(origins, list), "get_cors_origins should return a list"
        assert len(origins) > 0, "Should have at least one allowed origin"
        
        # Test get_cors_methods  
        methods = settings.get_cors_methods()
        assert isinstance(methods, list), "get_cors_methods should return a list"
        assert "GET" in methods, "GET method should be allowed"
        assert "POST" in methods, "POST method should be allowed"
        
        # Test get_cors_headers
        headers = settings.get_cors_headers()
        assert isinstance(headers, list), "get_cors_headers should return a list"
        assert any("content-type" in h.lower() for h in headers), "Content-Type should be allowed"
    
    def test_cors_environment_override(self):
        """Test that CORS can be configured via environment variables."""
        # This test verifies the configuration structure supports environment overrides
        # The actual values are tested in other tests
        
        assert hasattr(settings, 'CORS_ALLOWED_ORIGINS'), "Should have CORS_ALLOWED_ORIGINS setting"
        assert hasattr(settings, 'CORS_ALLOWED_METHODS'), "Should have CORS_ALLOWED_METHODS setting"
        assert hasattr(settings, 'CORS_ALLOWED_HEADERS'), "Should have CORS_ALLOWED_HEADERS setting"
        assert hasattr(settings, 'CORS_ALLOW_CREDENTIALS'), "Should have CORS_ALLOW_CREDENTIALS setting"


# Security-focused markers for pytest
pytestmark = pytest.mark.security