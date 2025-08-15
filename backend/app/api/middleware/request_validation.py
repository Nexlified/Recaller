"""
Request validation middleware for enforcing request size limits and basic security checks.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio


class RequestValidationMiddleware:
    """Middleware for validating request size and basic security."""
    
    def __init__(
        self,
        max_body_size: int = 10 * 1024 * 1024,  # 10MB
        max_query_length: int = 8192,  # 8KB
        max_header_size: int = 16384,  # 16KB
        max_url_length: int = 2048
    ):
        self.max_body_size = max_body_size
        self.max_query_length = max_query_length
        self.max_header_size = max_header_size
        self.max_url_length = max_url_length
    
    def validate_request_size(self, request: Request) -> Optional[dict]:
        """Validate request size limits."""
        # Check URL length
        if len(str(request.url)) > self.max_url_length:
            return {
                "error": "Request URL too long",
                "limit": self.max_url_length,
                "current": len(str(request.url))
            }
        
        # Check query string length
        if request.url.query and len(request.url.query) > self.max_query_length:
            return {
                "error": "Query string too long",
                "limit": self.max_query_length,
                "current": len(request.url.query)
            }
        
        # Check content length header
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_body_size:
                    return {
                        "error": "Request body too large",
                        "limit": self.max_body_size,
                        "current": size
                    }
            except ValueError:
                pass
        
        # Check total header size
        total_header_size = sum(
            len(name) + len(value) 
            for name, value in request.headers.items()
        )
        if total_header_size > self.max_header_size:
            return {
                "error": "Request headers too large",
                "limit": self.max_header_size,
                "current": total_header_size
            }
        
        return None
    
    def validate_request_security(self, request: Request) -> Optional[dict]:
        """Perform basic security validation."""
        # Check for suspicious headers
        suspicious_headers = [
            'x-forwarded-host',
            'x-original-url', 
            'x-rewrite-url'
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log suspicious activity but don't block
                print(f"Suspicious header detected: {header}")
        
        # Check for null bytes in URL (can cause issues)
        if '\x00' in str(request.url):
            return {
                "error": "Invalid characters in URL",
                "detail": "Null bytes are not allowed"
            }
        
        # Check for excessively long individual headers
        for name, value in request.headers.items():
            if len(value) > 4096:  # 4KB per header value
                return {
                    "error": f"Header '{name}' too long",
                    "limit": 4096,
                    "current": len(value)
                }
        
        return None


# Global middleware instance
request_validator = RequestValidationMiddleware()


async def request_validation_middleware(request: Request, call_next):
    """Request validation middleware function."""
    
    # Validate request size
    size_error = request_validator.validate_request_size(request)
    if size_error:
        return JSONResponse(
            status_code=413,
            content={
                "detail": size_error["error"],
                "limit": size_error["limit"],
                "current": size_error.get("current")
            }
        )
    
    # Validate request security
    security_error = request_validator.validate_request_security(request)
    if security_error:
        return JSONResponse(
            status_code=400,
            content={
                "detail": security_error["error"],
                "info": security_error.get("detail")
            }
        )
    
    # Process request
    response = await call_next(request)
    
    return response