"""
Integration tests for API endpoints with validation and rate limiting.

Tests that validation and security features work end-to-end.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestEndpointValidation:
    """Test endpoint validation integration."""
    
    def test_contacts_search_validation(self):
        """Test contacts search endpoint with validation."""
        # Valid search (should work even without auth for validation test)
        response = client.get("/api/v1/contacts/search/?q=test")
        # Should fail with 401 (auth required) but not 400 (validation error)
        assert response.status_code in [401, 422]  # Depends on auth middleware order
        
        # Invalid search query (too long)
        long_query = "a" * 300
        response = client.get(f"/api/v1/contacts/search/?q={long_query}")
        assert response.status_code == 422  # Validation error
        assert "exceeds maximum length" in response.text
        
        # Invalid search query (SQL injection)
        malicious_query = "'; DROP TABLE users; --"
        response = client.get(f"/api/v1/contacts/search/?q={malicious_query}")
        assert response.status_code == 422  # Validation error
    
    def test_organizations_search_validation(self):
        """Test organizations search endpoint with validation."""
        # Valid search
        response = client.get("/api/v1/organizations/search?query=test")
        assert response.status_code in [401, 422]  # Auth required but validation passed
        
        # Invalid search query (empty)
        response = client.get("/api/v1/organizations/search?query=")
        assert response.status_code == 422  # Validation error
        
        # Invalid search query (XSS attempt)
        xss_query = "<script>alert('xss')</script>"
        response = client.get(f"/api/v1/organizations/search?query={xss_query}")
        assert response.status_code == 422  # Validation error
    
    def test_tasks_search_validation(self):
        """Test tasks search endpoint with validation."""
        # Valid search
        response = client.get("/api/v1/tasks/search/?q=test")
        assert response.status_code in [401, 422]  # Auth required but validation passed
        
        # Invalid search query (too short)
        response = client.get("/api/v1/tasks/search/?q=")
        assert response.status_code == 422  # Validation error
        
        # Invalid search query (malicious)
        malicious_query = "javascript:alert(1)"
        response = client.get(f"/api/v1/tasks/search/?q={malicious_query}")
        assert response.status_code == 422  # Validation error
    
    def test_pagination_validation(self):
        """Test pagination parameter validation."""
        # Invalid page number
        response = client.get("/api/v1/contacts/?skip=0&limit=0")
        assert response.status_code == 422
        
        # Invalid limit (too high)
        response = client.get("/api/v1/contacts/?skip=0&limit=200")
        assert response.status_code == 422
    
    def test_auth_register_validation(self):
        """Test registration endpoint validation."""
        # Valid registration data
        valid_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=valid_data)
        # Should work (assuming email not already taken)
        assert response.status_code in [201, 400, 422]  # Could be success or business logic error
        
        # Invalid email format
        invalid_data = {
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Password too short
        short_password_data = {
            "email": "test2@example.com",
            "password": "123",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=short_password_data)
        assert response.status_code == 422  # Validation error
        
        # Malicious full name
        malicious_data = {
            "email": "test3@example.com",
            "password": "password123",
            "full_name": "<script>alert('xss')</script>"
        }
        response = client.post("/api/v1/auth/register", json=malicious_data)
        assert response.status_code == 422  # Validation error


class TestRequestSizeLimits:
    """Test request size validation middleware."""
    
    def test_large_query_string(self):
        """Test large query string rejection."""
        # Very large query string
        large_query = "q=" + "a" * 10000
        response = client.get(f"/api/v1/contacts/search/?{large_query}")
        # Should be rejected by request validation middleware
        assert response.status_code == 413  # Request entity too large
    
    def test_large_request_body(self):
        """Test large request body rejection."""
        # Very large request body
        large_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "a" * 1000000  # 1MB of text
        }
        response = client.post("/api/v1/auth/register", json=large_data)
        # Should be rejected by request validation middleware
        assert response.status_code in [413, 422]  # Too large or validation error
    
    def test_very_long_url(self):
        """Test very long URL rejection."""
        # Very long URL path
        long_path = "/api/v1/contacts/" + "a" * 3000
        response = client.get(long_path)
        # Should be rejected by request validation middleware
        assert response.status_code == 413  # Request entity too large


class TestSecurityHeaders:
    """Test security-related request handling."""
    
    def test_null_bytes_in_url(self):
        """Test null byte injection in URL."""
        # URL with null bytes
        response = client.get("/api/v1/contacts/search/?q=test\x00malicious")
        # Should be rejected by request validation middleware
        assert response.status_code == 400  # Bad request
    
    def test_suspicious_headers(self):
        """Test handling of suspicious headers."""
        headers = {
            "X-Forwarded-Host": "malicious.com",
            "X-Original-URL": "/admin/secret"
        }
        response = client.get("/api/v1/contacts/", headers=headers)
        # Should log but not necessarily block (depends on implementation)
        # Just ensure it doesn't crash
        assert response.status_code != 500


class TestEndToEndSecurity:
    """Test end-to-end security scenarios."""
    
    def test_multiple_attack_vectors(self):
        """Test multiple security attack vectors combined."""
        # Combined XSS + SQL injection attempt
        malicious_query = "'; DROP TABLE users; --<script>alert(1)</script>"
        response = client.get(f"/api/v1/contacts/search/?q={malicious_query}")
        assert response.status_code == 422  # Should be blocked by validation
    
    def test_encoded_attacks(self):
        """Test URL-encoded attack attempts."""
        # URL-encoded XSS attempt
        encoded_xss = "%3Cscript%3Ealert(1)%3C/script%3E"
        response = client.get(f"/api/v1/contacts/search/?q={encoded_xss}")
        # Should be handled safely
        assert response.status_code in [401, 422]  # Auth or validation error
    
    def test_unicode_attacks(self):
        """Test Unicode-based attack attempts."""
        # Unicode XSS attempt
        unicode_xss = "\u003cscript\u003ealert(1)\u003c/script\u003e"
        response = client.get(f"/api/v1/contacts/search/?q={unicode_xss}")
        # Should be handled safely
        assert response.status_code in [401, 422]  # Auth or validation error


class TestAPISecurity:
    """Test overall API security features."""
    
    def test_cors_headers(self):
        """Test CORS configuration with security restrictions."""
        # Test allowed origin
        response = client.options("/api/v1/contacts/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        # Should have CORS headers for allowed origin
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        
        # Test restricted origin (should not be allowed)
        response = client.options("/api/v1/contacts/", headers={"Origin": "https://malicious.com"})
        # Should not have CORS headers for disallowed origin
        cors_origin = response.headers.get("access-control-allow-origin")
        assert cors_origin != "https://malicious.com"
        
    def test_cors_methods_restricted(self):
        """Test CORS methods are restricted to allowed methods only."""
        response = client.options("/api/v1/contacts/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        assert response.status_code == 200
        
        # Should have allowed methods header
        methods_header = response.headers.get("access-control-allow-methods", "")
        allowed_methods = [method.strip() for method in methods_header.split(",")]
        
        # Should include standard methods
        for method in ["GET", "POST", "PUT", "DELETE", "OPTIONS"]:
            assert method in allowed_methods, f"Method {method} should be allowed"
        
        # Should not include dangerous methods
        dangerous_methods = ["TRACE", "CONNECT", "PATCH"]
        for method in dangerous_methods:
            assert method not in allowed_methods, f"Method {method} should not be allowed"
    
    def test_cors_headers_restricted(self):
        """Test CORS headers are restricted to necessary headers only."""
        response = client.options("/api/v1/contacts/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        })
        assert response.status_code == 200
        
        # Should have allowed headers
        headers_value = response.headers.get("access-control-allow-headers", "")
        allowed_headers = [header.strip().lower() for header in headers_value.split(",")]
        
        # Should include necessary headers
        required_headers = ["content-type", "authorization", "x-tenant-id"]
        for header in required_headers:
            assert header in allowed_headers, f"Header {header} should be allowed"
        
        # Should not include wildcard
        assert "*" not in allowed_headers, "Wildcard headers should not be allowed"
    
    def test_health_endpoint_accessibility(self):
        """Test that health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "degraded"]
    
    def test_openapi_docs_accessibility(self):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_api_versioning(self):
        """Test API version prefix handling."""
        response = client.get("/api/v1/")
        # Should either redirect or give 404/405, but not crash
        assert response.status_code != 500