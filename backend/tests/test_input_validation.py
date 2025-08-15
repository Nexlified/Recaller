"""
Tests for general input validation and sanitization functionality.

Tests the new InputSanitizer class and request validation middleware.
"""

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.core.validation import (
    InputSanitizer, PaginationValidator, QueryValidator
)


class TestInputSanitizer:
    """Test the general input sanitizer functionality."""
    
    def test_sanitize_search_query_valid(self):
        """Test sanitization of valid search queries."""
        query = "hello world"
        result = InputSanitizer.sanitize_search_query(query)
        assert result == "hello world"
        
        # Test with HTML that should be escaped
        query = "search <term>"
        result = InputSanitizer.sanitize_search_query(query)
        assert result == "search &lt;term&gt;"
    
    def test_sanitize_search_query_malicious(self):
        """Test rejection of malicious search queries."""
        malicious_queries = [
            "'; DROP TABLE users; --",
            "SELECT * FROM users",
            "INSERT INTO table",
            "UPDATE users SET",
            "DELETE FROM users",
            "EXEC sp_",
            "javascript:alert(1)",
            "onload=alert(1)",
            "@@version"
        ]
        
        for query in malicious_queries:
            with pytest.raises(ValueError, match="prohibited patterns"):
                InputSanitizer.sanitize_search_query(query)
    
    def test_sanitize_search_query_length_limit(self):
        """Test search query length validation."""
        long_query = "a" * 300
        with pytest.raises(ValueError, match="exceeds maximum length"):
            InputSanitizer.sanitize_search_query(long_query)
    
    def test_sanitize_email_valid(self):
        """Test email sanitization with valid emails."""
        email = "test@example.com"
        result = InputSanitizer.sanitize_email(email)
        assert result == "test@example.com"
        
        # Test case normalization
        email = "TEST@EXAMPLE.COM"
        result = InputSanitizer.sanitize_email(email)
        assert result == "test@example.com"
    
    def test_sanitize_email_invalid(self):
        """Test rejection of invalid emails."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "test<script>@example.com",
            "test@example.com; DROP TABLE users;"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_email(email)
    
    def test_sanitize_email_length_limit(self):
        """Test email length validation."""
        long_email = "a" * 350 + "@example.com"  # Make it longer than 320 chars
        with pytest.raises(ValueError, match="exceeds maximum length"):
            InputSanitizer.sanitize_email(long_email)
    
    def test_sanitize_phone_valid(self):
        """Test phone number sanitization."""
        phone = "+1 (555) 123-4567"
        result = InputSanitizer.sanitize_phone(phone)
        assert result == "+1 (555) 123-4567"
        
        # Test with extra characters removed (note: . gets removed)
        phone = "+1-555.123.4567 ext 123abc"
        result = InputSanitizer.sanitize_phone(phone)
        assert result == "+1-5551234567  123"  # Dots and letters removed
    
    def test_sanitize_phone_length_limit(self):
        """Test phone number length validation."""
        long_phone = "1" * 30
        with pytest.raises(ValueError, match="exceeds maximum length"):
            InputSanitizer.sanitize_phone(long_phone)
    
    def test_sanitize_url_valid(self):
        """Test URL sanitization."""
        url = "https://example.com"
        result = InputSanitizer.sanitize_url(url)
        assert result == "https://example.com"
        
        url = "http://subdomain.example.com/path?query=value"
        result = InputSanitizer.sanitize_url(url)
        assert result == url
    
    def test_sanitize_url_malicious(self):
        """Test rejection of malicious URLs."""
        malicious_urls = [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "vbscript:msgbox(1)",
            "file:///etc/passwd",
            "ftp://malicious.com",
            "no-protocol.com"
        ]
        
        for url in malicious_urls:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_url(url)
    
    def test_sanitize_url_length_limit(self):
        """Test URL length validation."""
        long_url = "https://example.com/" + "a" * 3000
        with pytest.raises(ValueError, match="exceeds maximum length"):
            InputSanitizer.sanitize_url(long_url)
    
    def test_sanitize_name_valid(self):
        """Test name sanitization."""
        name = "John Doe"
        result = InputSanitizer.sanitize_name(name)
        assert result == "John Doe"
        
        # Test HTML escaping
        name = "John <script>alert(1)</script> Doe"
        with pytest.raises(ValueError, match="malicious script patterns"):
            InputSanitizer.sanitize_name(name)


class TestPaginationValidator:
    """Test pagination validation."""
    
    def test_valid_pagination(self):
        """Test valid pagination parameters."""
        page, per_page = PaginationValidator.validate_pagination(1, 20)
        assert page == 1
        assert per_page == 20
        
        page, per_page = PaginationValidator.validate_pagination(5, 50)
        assert page == 5
        assert per_page == 50
    
    def test_invalid_page(self):
        """Test invalid page numbers."""
        with pytest.raises(ValueError, match="must be at least"):
            PaginationValidator.validate_pagination(0, 20)
        
        with pytest.raises(ValueError, match="must be at least"):
            PaginationValidator.validate_pagination(-1, 20)
    
    def test_invalid_per_page(self):
        """Test invalid per_page values."""
        with pytest.raises(ValueError, match="cannot exceed"):
            PaginationValidator.validate_pagination(1, 200)
        
        with pytest.raises(ValueError, match="must be at least 1"):
            PaginationValidator.validate_pagination(1, 0)


class TestQueryValidator:
    """Test query parameter validation."""
    
    def test_validate_search_query(self):
        """Test search query validation."""
        # Valid query
        result = QueryValidator.validate_search_query("hello world")
        assert result == "hello world"
        
        # Empty query
        result = QueryValidator.validate_search_query("")
        assert result is None
        
        result = QueryValidator.validate_search_query(None)
        assert result is None
        
        # Whitespace only
        result = QueryValidator.validate_search_query("   ")
        assert result is None
    
    def test_validate_sort_field(self):
        """Test sort field validation."""
        allowed_fields = {"name", "email", "created_at"}
        
        # Valid field
        result = QueryValidator.validate_sort_field("name", allowed_fields)
        assert result == "name"
        
        # Invalid field
        with pytest.raises(ValueError, match="Invalid sort field"):
            QueryValidator.validate_sort_field("invalid_field", allowed_fields)
        
        # None value
        result = QueryValidator.validate_sort_field(None, allowed_fields)
        assert result is None
    
    def test_validate_sort_direction(self):
        """Test sort direction validation."""
        # Valid directions
        result = QueryValidator.validate_sort_direction("asc")
        assert result == "asc"
        
        result = QueryValidator.validate_sort_direction("DESC")
        assert result == "desc"
        
        # Invalid direction
        with pytest.raises(ValueError, match="must be 'asc' or 'desc'"):
            QueryValidator.validate_sort_direction("invalid")
        
        # None value
        result = QueryValidator.validate_sort_direction(None)
        assert result is None


class TestSecurityValidation:
    """Test security-focused validation scenarios."""
    
    def test_xss_prevention_search(self):
        """Test XSS prevention in search queries."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "onmouseover=alert(1)",
            "<iframe src=javascript:alert(1)></iframe>"
        ]
        
        for payload in xss_payloads:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_search_query(payload)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "admin'--",
            "' OR 1=1#"
        ]
        
        for payload in sql_payloads:
            with pytest.raises(ValueError):
                InputSanitizer.sanitize_search_query(payload)
    
    def test_null_byte_injection(self):
        """Test null byte injection prevention."""
        malicious_inputs = [
            "test\x00.exe",
            "normal_text\x00<script>alert(1)</script>",
            "\x00DROP TABLE users;"
        ]
        
        for payload in malicious_inputs:
            # Search query sanitizer should reject null bytes
            with pytest.raises(ValueError, match="null bytes"):
                InputSanitizer.sanitize_search_query(payload)
    
    def test_unicode_normalization(self):
        """Test proper Unicode handling."""
        unicode_inputs = [
            "café",
            "naïve",
            "你好世界",
            "Ñoño",
            "résumé"
        ]
        
        for text in unicode_inputs:
            # These should not raise errors for names
            result = InputSanitizer.sanitize_name(text)
            assert len(result) > 0
    
    def test_length_limit_dos_prevention(self):
        """Test DoS prevention through length limits."""
        # Test various fields with extremely long inputs
        long_text = "a" * 100000
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_search_query(long_text)
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_name(long_text)
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_email(long_text + "@example.com")