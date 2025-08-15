"""
Simple validation tests that don't require database setup.

Tests the validation middleware and input sanitization directly.
"""

import pytest
import html
from fastapi import FastAPI, Query, HTTPException
from fastapi.testclient import TestClient
from app.core.validation import InputSanitizer, PaginationValidator, QueryValidator
from app.api.middleware.request_validation import request_validation_middleware


# Create a simple test app for validation testing
test_app = FastAPI()
test_app.middleware("http")(request_validation_middleware)


@test_app.get("/test/search")
async def test_search(q: str = Query(..., min_length=1, max_length=255)):
    """Test endpoint that uses our validation."""
    try:
        sanitized_query = InputSanitizer.sanitize_search_query(q)
        return {"query": sanitized_query, "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@test_app.get("/test/pagination")
async def test_pagination(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)):
    """Test endpoint that uses pagination validation."""
    try:
        validated_page, validated_per_page = PaginationValidator.validate_pagination(page, per_page)
        return {"page": validated_page, "per_page": validated_per_page, "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@test_app.post("/test/email")
async def test_email(email: str):
    """Test endpoint that validates email."""
    try:
        sanitized_email = InputSanitizer.sanitize_email(email)
        return {"email": sanitized_email, "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


test_client = TestClient(test_app)


class TestValidationIntegration:
    """Test validation integration without database dependencies."""
    
    def test_search_validation_success(self):
        """Test successful search query validation."""
        response = test_client.get("/test/search?q=valid search")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["query"] == "valid search"
    
    def test_search_validation_failure_malicious(self):
        """Test search validation blocks malicious input."""
        malicious_queries = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "SELECT * FROM users"
        ]
        
        for query in malicious_queries:
            response = test_client.get(f"/test/search?q={query}")
            assert response.status_code == 400
            assert "prohibited patterns" in response.json()["detail"]
    
    def test_search_validation_failure_length(self):
        """Test search validation blocks oversized input."""
        long_query = "a" * 300
        response = test_client.get(f"/test/search?q={long_query}")
        assert response.status_code == 422  # FastAPI validation error for max_length
    
    def test_search_validation_failure_empty(self):
        """Test search validation blocks empty input."""
        response = test_client.get("/test/search?q=")
        assert response.status_code == 422  # FastAPI validation error for min_length
    
    def test_pagination_validation_success(self):
        """Test successful pagination validation."""
        response = test_client.get("/test/pagination?page=2&per_page=50")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 50
        assert data["status"] == "success"
    
    def test_pagination_validation_failure_invalid_page(self):
        """Test pagination validation blocks invalid page."""
        response = test_client.get("/test/pagination?page=0&per_page=20")
        assert response.status_code == 422  # FastAPI validation error for ge=1
    
    def test_pagination_validation_failure_invalid_per_page(self):
        """Test pagination validation blocks invalid per_page."""
        response = test_client.get("/test/pagination?page=1&per_page=200")
        assert response.status_code == 422  # FastAPI validation error for le=100
    
    def test_email_validation_success(self):
        """Test successful email validation."""
        response = test_client.post("/test/email", json="test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["status"] == "success"
    
    def test_email_validation_failure_invalid_format(self):
        """Test email validation blocks invalid formats."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "test<script>@example.com"
        ]
        
        for email in invalid_emails:
            response = test_client.post("/test/email", json=email)
            assert response.status_code == 400
            assert "Invalid email format" in response.json()["detail"] or "prohibited characters" in response.json()["detail"]
    
    def test_request_size_validation_large_query(self):
        """Test request validation blocks oversized query strings."""
        # Very large query parameter
        large_query = "q=" + "a" * 10000
        response = test_client.get(f"/test/search?{large_query}")
        assert response.status_code == 413  # Request entity too large
    
    def test_request_size_validation_very_long_url(self):
        """Test request validation blocks very long URLs."""
        # Create a very long URL path
        long_path = "/test/search/" + "a" * 3000
        response = test_client.get(long_path)
        assert response.status_code == 413  # Request entity too large


class TestInputSanitizerDirect:
    """Test InputSanitizer methods directly."""
    
    def test_search_query_sanitization_html_escape(self):
        """Test HTML escaping in search queries."""
        query = "hello & goodbye < >"
        result = InputSanitizer.sanitize_search_query(query)
        assert "&amp;" in result
        assert "&lt;" in result
        assert "&gt;" in result
    
    def test_email_sanitization_case_normalization(self):
        """Test email case normalization."""
        email = "TEST@EXAMPLE.COM"
        result = InputSanitizer.sanitize_email(email)
        assert result == "test@example.com"
    
    def test_name_sanitization_length_limit(self):
        """Test name length validation."""
        long_name = "a" * 300
        with pytest.raises(ValueError, match="exceeds maximum length"):
            InputSanitizer.sanitize_name(long_name)
    
    def test_phone_sanitization_character_removal(self):
        """Test phone number character filtering."""
        phone = "+1-555.123.4567 ext 123abc"
        result = InputSanitizer.sanitize_phone(phone)
        # Should keep only digits, +, -, (, ), and spaces
        assert "." not in result
        assert "ext" not in result
        assert "abc" not in result
        assert "+1-5551234567  123" == result
    
    def test_url_validation_protocol_checking(self):
        """Test URL protocol validation."""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.com/path?query=value"
        ]
        
        for url in valid_urls:
            result = InputSanitizer.sanitize_url(url)
            assert result == url
        
        invalid_urls = [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
            "ftp://example.com",
            "no-protocol.com"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_url(url)


class TestQueryValidator:
    """Test QueryValidator methods."""
    
    def test_sort_field_validation(self):
        """Test sort field validation."""
        allowed_fields = {"name", "email", "created_at"}
        
        # Valid field
        result = QueryValidator.validate_sort_field("name", allowed_fields)
        assert result == "name"
        
        # Invalid field
        with pytest.raises(ValueError, match="Invalid sort field"):
            QueryValidator.validate_sort_field("invalid_field", allowed_fields)
    
    def test_sort_direction_validation(self):
        """Test sort direction validation."""
        # Valid directions
        assert QueryValidator.validate_sort_direction("asc") == "asc"
        assert QueryValidator.validate_sort_direction("DESC") == "desc"
        
        # Invalid direction
        with pytest.raises(ValueError, match="must be 'asc' or 'desc'"):
            QueryValidator.validate_sort_direction("invalid")


class TestSecurityPatterns:
    """Test security pattern detection."""
    
    def test_xss_prevention(self):
        """Test XSS pattern detection and blocking."""
        xss_patterns = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "<iframe src=javascript:alert(1)></iframe>"
        ]
        
        for pattern in xss_patterns:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_search_query(pattern)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection pattern detection."""
        sql_patterns = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "SELECT password FROM users"
        ]
        
        for pattern in sql_patterns:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_search_query(pattern)
    
    def test_null_byte_prevention(self):
        """Test null byte injection prevention."""
        null_byte_inputs = [
            "test\x00.exe",
            "normal_text\x00<script>alert(1)</script>",
            "\x00DROP TABLE users;"
        ]
        
        for input_text in null_byte_inputs:
            with pytest.raises(ValueError, match="null bytes"):
                InputSanitizer.sanitize_search_query(input_text)
    
    def test_unicode_handling(self):
        """Test proper Unicode handling."""
        unicode_inputs = [
            "café",
            "naïve", 
            "你好世界",
            "Ñoño",
            "résumé"
        ]
        
        for text in unicode_inputs:
            # Should not raise errors
            result = InputSanitizer.sanitize_name(text)
            assert len(result) > 0
            # Should be HTML escaped
            assert html.escape(text, quote=True) == result or text == result


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])