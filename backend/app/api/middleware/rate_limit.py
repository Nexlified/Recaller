"""
Rate limiting middleware for API endpoints.

Provides configurable rate limiting based on IP address, user, and endpoint.
Uses Redis for distributed rate limiting across multiple server instances.
"""

import time
import json
from typing import Dict, Optional, Callable, Any
from functools import wraps
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from app.core.config import settings


class RateLimiter:
    """Rate limiter using Redis as backend."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.default_limits = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000
        }
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            '/api/v1/auth/login': {
                'requests_per_minute': 5,
                'requests_per_hour': 50,
                'requests_per_day': 100
            },
            '/api/v1/auth/register': {
                'requests_per_minute': 3,
                'requests_per_hour': 20,
                'requests_per_day': 50
            },
            # Search endpoints
            '/api/v1/contacts/search/': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'requests_per_day': 5000
            },
            '/api/v1/organizations/search/': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'requests_per_day': 5000
            },
            '/api/v1/tasks/search/': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'requests_per_day': 5000
            }
        }
    
    async def init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Could not connect to Redis for rate limiting: {e}")
            self.redis_client = None
    
    def get_client_id(self, request: Request) -> str:
        """Get unique client identifier for rate limiting."""
        # Try to get user ID first (for authenticated requests)
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def get_rate_limits(self, endpoint: str) -> Dict[str, int]:
        """Get rate limits for specific endpoint."""
        return self.endpoint_limits.get(endpoint, self.default_limits)
    
    async def is_rate_limited(self, request: Request) -> tuple[bool, Dict[str, Any]]:
        """Check if request should be rate limited."""
        if not self.redis_client:
            return False, {}
        
        client_id = self.get_client_id(request)
        endpoint = request.url.path
        limits = self.get_rate_limits(endpoint)
        
        current_time = int(time.time())
        
        # Check each time window
        for window, limit in limits.items():
            if window == 'requests_per_minute':
                window_seconds = 60
            elif window == 'requests_per_hour':
                window_seconds = 3600
            elif window == 'requests_per_day':
                window_seconds = 86400
            else:
                continue
            
            # Redis key for this client/endpoint/window
            key = f"rate_limit:{client_id}:{endpoint}:{window}"
            
            try:
                # Use Redis pipeline for atomic operations
                pipe = self.redis_client.pipeline()
                
                # Get current count
                pipe.get(key)
                
                # Increment counter
                pipe.incr(key)
                
                # Set expiration if key is new
                pipe.expire(key, window_seconds)
                
                results = await pipe.execute()
                current_count = int(results[1])  # Count after increment
                
                if current_count > limit:
                    # Rate limited
                    reset_time = current_time + window_seconds
                    return True, {
                        'error': 'Rate limit exceeded',
                        'limit': limit,
                        'window': window,
                        'current': current_count,
                        'reset_time': reset_time,
                        'retry_after': window_seconds
                    }
                
            except Exception as e:
                print(f"Redis error in rate limiting: {e}")
                # Fail open if Redis is unavailable
                return False, {}
        
        return False, {}
    
    async def add_rate_limit_headers(self, response: Response, request: Request):
        """Add rate limit headers to response."""
        if not self.redis_client:
            return
        
        client_id = self.get_client_id(request)
        endpoint = request.url.path
        limits = self.get_rate_limits(endpoint)
        
        try:
            # Add headers for the most restrictive limit (per minute)
            minute_limit = limits.get('requests_per_minute', self.default_limits['requests_per_minute'])
            key = f"rate_limit:{client_id}:{endpoint}:requests_per_minute"
            
            current_count = await self.redis_client.get(key)
            if current_count:
                remaining = max(0, minute_limit - int(current_count))
                response.headers["X-RateLimit-Limit"] = str(minute_limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        except Exception as e:
            print(f"Error adding rate limit headers: {e}")


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Initialize Redis connection if not done
    if rate_limiter.redis_client is None:
        await rate_limiter.init_redis()
    
    # Check rate limits
    is_limited, limit_info = await rate_limiter.is_rate_limited(request)
    
    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "detail": limit_info['error'],
                "limit": limit_info['limit'],
                "window": limit_info['window'],
                "retry_after": limit_info['retry_after']
            },
            headers={
                "Retry-After": str(limit_info['retry_after']),
                "X-RateLimit-Limit": str(limit_info['limit']),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(limit_info['reset_time'])
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    await rate_limiter.add_rate_limit_headers(response, request)
    
    return response


def rate_limit(
    requests_per_minute: Optional[int] = None,
    requests_per_hour: Optional[int] = None,
    requests_per_day: Optional[int] = None
):
    """Decorator for endpoint-specific rate limiting."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This decorator is mainly for documentation
            # The actual rate limiting is done in middleware
            return await func(*args, **kwargs)
        
        # Store rate limit info in function metadata
        wrapper._rate_limits = {
            'requests_per_minute': requests_per_minute,
            'requests_per_hour': requests_per_hour,
            'requests_per_day': requests_per_day
        }
        
        return wrapper
    return decorator