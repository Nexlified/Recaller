"""
Tests for rate limiting and request validation middleware.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.api.middleware.rate_limit import RateLimiter, rate_limit_middleware
from app.api.middleware.request_validation import (
    RequestValidationMiddleware, request_validation_middleware
)


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_init(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter()
        assert limiter.redis_client is None
        assert limiter.default_limits['requests_per_minute'] == 60
        assert '/api/v1/auth/login' in limiter.endpoint_limits
    
    def test_get_client_id_with_user(self):
        """Test client ID generation with authenticated user."""
        limiter = RateLimiter()
        
        # Mock request with user ID
        request = Mock()
        request.state.user_id = 123
        
        client_id = limiter.get_client_id(request)
        assert client_id == "user:123"
    
    def test_get_client_id_with_ip(self):
        """Test client ID generation with IP address."""
        limiter = RateLimiter()
        
        # Mock request without user ID
        request = Mock()
        request.state = Mock()
        request.state.user_id = None
        request.client.host = "192.168.1.1"
        request.headers = {}
        
        client_id = limiter.get_client_id(request)
        assert client_id == "ip:192.168.1.1"
    
    def test_get_client_id_with_forwarded_for(self):
        """Test client ID generation with X-Forwarded-For header."""
        limiter = RateLimiter()
        
        # Mock request with forwarded IP
        request = Mock()
        request.state = Mock()
        request.state.user_id = None
        request.client.host = "127.0.0.1"
        request.headers = {"X-Forwarded-For": "203.0.113.1, 192.168.1.1"}
        
        client_id = limiter.get_client_id(request)
        assert client_id == "ip:203.0.113.1"
    
    def test_get_rate_limits_default(self):
        """Test getting default rate limits."""
        limiter = RateLimiter()
        limits = limiter.get_rate_limits("/api/v1/unknown")
        assert limits == limiter.default_limits
    
    def test_get_rate_limits_auth_endpoint(self):
        """Test getting rate limits for auth endpoints."""
        limiter = RateLimiter()
        limits = limiter.get_rate_limits("/api/v1/auth/login")
        assert limits['requests_per_minute'] == 5
        assert limits['requests_per_hour'] == 50
    
    @pytest.mark.asyncio
    async def test_is_rate_limited_no_redis(self):
        """Test rate limiting when Redis is not available."""
        limiter = RateLimiter()
        limiter.redis_client = None
        
        request = Mock()
        request.url.path = "/api/v1/test"
        
        is_limited, info = await limiter.is_rate_limited(request)
        assert not is_limited
        assert info == {}
    
    @pytest.mark.asyncio
    async def test_is_rate_limited_within_limits(self):
        """Test rate limiting when within limits."""
        limiter = RateLimiter()
        
        # Mock Redis client
        redis_mock = AsyncMock()
        redis_mock.pipeline.return_value.__aenter__.return_value.execute.return_value = [None, 1]
        limiter.redis_client = redis_mock
        
        request = Mock()
        request.url.path = "/api/v1/test"
        request.state = Mock()
        request.state.user_id = None
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        is_limited, info = await limiter.is_rate_limited(request)
        assert not is_limited
    
    @pytest.mark.asyncio
    async def test_is_rate_limited_exceeds_limit(self):
        """Test rate limiting when exceeding limits."""
        limiter = RateLimiter()
        
        # Mock Redis client to return count exceeding limit
        redis_mock = AsyncMock()
        redis_mock.pipeline.return_value.__aenter__.return_value.execute.return_value = [None, 100]
        limiter.redis_client = redis_mock
        
        request = Mock()
        request.url.path = "/api/v1/test"
        request.state = Mock()
        request.state.user_id = None
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        is_limited, info = await limiter.is_rate_limited(request)
        assert is_limited
        assert info['error'] == 'Rate limit exceeded'
        assert 'limit' in info
        assert 'retry_after' in info


class TestRequestValidationMiddleware:
    """Test request validation middleware."""
    
    def test_middleware_init(self):
        """Test middleware initialization."""
        middleware = RequestValidationMiddleware()
        assert middleware.max_body_size == 10 * 1024 * 1024
        assert middleware.max_query_length == 8192
        assert middleware.max_header_size == 16384
        assert middleware.max_url_length == 2048
    
    def test_validate_url_length(self):
        """Test URL length validation."""
        middleware = RequestValidationMiddleware(max_url_length=100)
        
        # Mock request with long URL
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/" + "a" * 200)
        request.url.query = ""
        request.headers = {}
        
        error = middleware.validate_request_size(request)
        assert error is not None
        assert error['error'] == "Request URL too long"
    
    def test_validate_query_length(self):
        """Test query string length validation."""
        middleware = RequestValidationMiddleware(max_query_length=50)
        
        # Mock request with long query string
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/")
        request.url.query = "q=" + "a" * 100
        request.headers = {}
        
        error = middleware.validate_request_size(request)
        assert error is not None
        assert error['error'] == "Query string too long"
    
    def test_validate_content_length(self):
        """Test content length validation."""
        middleware = RequestValidationMiddleware(max_body_size=1000)
        
        # Mock request with large body
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/")
        request.url.query = ""
        request.headers = {"content-length": "2000"}
        
        error = middleware.validate_request_size(request)
        assert error is not None
        assert error['error'] == "Request body too large"
    
    def test_validate_header_size(self):
        """Test header size validation."""
        middleware = RequestValidationMiddleware(max_header_size=100)
        
        # Mock request with large headers
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/")
        request.url.query = ""
        request.headers = {
            "very-long-header-name": "very-long-header-value" * 10,
            "another-header": "another-value"
        }
        
        error = middleware.validate_request_size(request)
        assert error is not None
        assert error['error'] == "Request headers too large"
    
    def test_validate_null_bytes_in_url(self):
        """Test null byte detection in URL."""
        middleware = RequestValidationMiddleware()
        
        # Mock request with null bytes
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/test\x00.exe")
        request.headers = {}
        
        error = middleware.validate_request_security(request)
        assert error is not None
        assert error['error'] == "Invalid characters in URL"
    
    def test_validate_suspicious_headers(self):
        """Test detection of suspicious headers."""
        middleware = RequestValidationMiddleware()
        
        # Mock request with suspicious headers
        request = Mock()
        request.headers = {"x-forwarded-host": "malicious.com"}
        
        # This should log but not block
        error = middleware.validate_request_security(request)
        assert error is None  # Suspicious headers are logged but not blocked
    
    def test_validate_oversized_header_value(self):
        """Test detection of oversized individual header values."""
        middleware = RequestValidationMiddleware()
        
        # Mock request with oversized header value
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/")
        request.headers = {"normal-header": "a" * 5000}
        
        error = middleware.validate_request_security(request)
        assert error is not None
        assert "Header 'normal-header' too long" in error['error']
    
    @pytest.mark.asyncio
    async def test_request_validation_middleware_success(self):
        """Test successful request validation."""
        # Mock a valid request
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/api/test")
        request.url.query = "q=test"
        request.headers = {"content-type": "application/json", "content-length": "100"}
        
        # Mock call_next
        call_next = AsyncMock()
        mock_response = Mock()
        call_next.return_value = mock_response
        
        response = await request_validation_middleware(request, call_next)
        assert response == mock_response
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_request_validation_middleware_size_error(self):
        """Test request validation with size error."""
        # Mock an oversized request
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/" + "a" * 3000)
        request.url.query = ""
        request.headers = {}
        
        # Mock call_next (should not be called)
        call_next = AsyncMock()
        
        response = await request_validation_middleware(request, call_next)
        
        # Should return JSONResponse with error
        assert isinstance(response, JSONResponse)
        assert response.status_code == 413
        call_next.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_request_validation_middleware_security_error(self):
        """Test request validation with security error."""
        # Mock a request with null bytes
        request = Mock()
        request.url = Mock()
        request.url.__str__ = Mock(return_value="https://example.com/test\x00")
        request.headers = {}
        
        # Mock call_next (should not be called)
        call_next = AsyncMock()
        
        response = await request_validation_middleware(request, call_next)
        
        # Should return JSONResponse with error
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        call_next.assert_not_called()


class TestIntegrationSecurity:
    """Test integration scenarios for security validation."""
    
    def test_combined_attack_vectors(self):
        """Test multiple attack vectors combined."""
        from app.core.validation import InputSanitizer
        
        # Combined SQL injection + XSS
        malicious_input = "'; DROP TABLE users; --<script>alert(1)</script>"
        
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_search_query(malicious_input)
    
    def test_encoding_bypass_attempts(self):
        """Test various encoding bypass attempts."""
        from app.core.validation import InputSanitizer
        
        # URL encoded attempts
        encoded_payloads = [
            "%3Cscript%3Ealert(1)%3C/script%3E",
            "%27%20OR%20%271%27%3D%271",
            "java%0ascript:alert(1)"
        ]
        
        for payload in encoded_payloads:
            # Our sanitizer should either reject or safely handle these
            try:
                result = InputSanitizer.sanitize_search_query(payload)
                # If not rejected, should be safely escaped
                assert "<script>" not in result
                assert "javascript:" not in result.lower()
            except ValueError:
                # Rejection is also acceptable
                pass
    
    def test_unicode_bypass_attempts(self):
        """Test Unicode-based bypass attempts."""
        from app.core.validation import InputSanitizer
        
        # Unicode-based XSS attempts
        unicode_payloads = [
            "\u003cscript\u003ealert(1)\u003c/script\u003e",
            "\u0022\u003e\u003cscript\u003ealert(1)\u003c/script\u003e"
        ]
        
        for payload in unicode_payloads:
            try:
                result = InputSanitizer.sanitize_search_query(payload)
                # Should be safely handled
                assert "<script>" not in result
            except ValueError:
                # Rejection is also acceptable
                pass