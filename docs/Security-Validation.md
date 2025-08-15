# Request Validation and Security Features

This document describes the comprehensive request validation and input sanitization features implemented in the Recaller API.

## Overview

The Recaller API includes multiple layers of security validation to prevent common attacks and ensure data integrity:

1. **Input Sanitization** - Cleans and validates all user inputs
2. **Rate Limiting** - Prevents abuse and DoS attacks  
3. **Request Size Limits** - Protects against oversized requests
4. **Parameter Validation** - Enforces proper data types and constraints
5. **Security Pattern Detection** - Blocks XSS, SQL injection, and other attacks

## Input Sanitization

### InputSanitizer Class

The `InputSanitizer` class provides comprehensive input cleaning and validation:

```python
from app.core.validation import InputSanitizer

# Search query sanitization
clean_query = InputSanitizer.sanitize_search_query(user_input)

# Email validation and normalization  
clean_email = InputSanitizer.sanitize_email(email_input)

# Name field sanitization
clean_name = InputSanitizer.sanitize_name(name_input)

# Phone number cleaning
clean_phone = InputSanitizer.sanitize_phone(phone_input)

# URL validation
clean_url = InputSanitizer.sanitize_url(url_input)
```

### Security Features

#### XSS Prevention
- HTML escaping of all text inputs
- Detection and blocking of script tags
- Prevention of JavaScript execution patterns
- Blocking of dangerous HTML elements (iframe, object, embed)

#### SQL Injection Prevention  
- Detection of SQL keywords and patterns
- Blocking of dangerous characters (quotes, semicolons)
- Prevention of SQL comments and operators
- Protection against UNION and other injection techniques

#### Null Byte Injection Prevention
- Detection and rejection of null bytes (`\x00`)
- Protection against path traversal attacks
- Prevention of file system manipulation

#### Length Limits
- Search queries: 255 characters maximum
- Names: 255 characters maximum  
- Emails: 320 characters maximum (RFC compliant)
- Phone numbers: 20 characters maximum
- URLs: 2048 characters maximum
- Comments: 1000 characters maximum
- Descriptions: 2000 characters maximum

## Rate Limiting

### Redis-Based Rate Limiting

Rate limiting is implemented using Redis for distributed coordination:

```python
# Default limits (per IP or user)
- 60 requests per minute
- 1000 requests per hour  
- 10000 requests per day

# Auth endpoints (more restrictive)
- Login: 5/min, 50/hour, 100/day
- Register: 3/min, 20/hour, 50/day

# Search endpoints
- Search: 30/min, 500/hour, 5000/day
```

### Rate Limit Headers

Responses include rate limit information:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45  
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

When limits are exceeded:
```json
{
  "detail": "Rate limit exceeded",
  "limit": 60,
  "window": "requests_per_minute", 
  "retry_after": 60
}
```

## Request Size Limits

### Middleware Validation

Request validation middleware enforces size limits:

- **Request Body**: 10MB maximum
- **Query String**: 8KB maximum  
- **Headers Total**: 16KB maximum
- **Individual Header**: 4KB maximum
- **URL Length**: 2048 characters maximum

### Oversized Request Response

```json
{
  "detail": "Request body too large. Maximum size: 10485760 bytes",
  "limit": 10485760,
  "current": 15000000
}
```

## Parameter Validation

### Pagination Validation

```python
from app.core.validation import PaginationValidator

# Validates and sanitizes pagination parameters
page, per_page = PaginationValidator.validate_pagination(page, per_page)

# Limits:
# - page: minimum 1
# - per_page: 1-100 range
# - Default per_page: 20
```

### Query Parameter Validation

```python
from app.core.validation import QueryValidator

# Search query validation
clean_query = QueryValidator.validate_search_query(query)

# Sort field validation
sort_field = QueryValidator.validate_sort_field(field, allowed_fields)

# Sort direction validation  
direction = QueryValidator.validate_sort_direction(direction)  # 'asc' or 'desc'
```

## Endpoint Protection

### Protected Endpoints

The following endpoints include comprehensive validation:

#### Authentication
- `POST /api/v1/auth/register` - Email/name sanitization, password validation
- `POST /api/v1/auth/login` - Email sanitization

#### Search Endpoints  
- `GET /api/v1/contacts/search/` - Query sanitization, pagination validation
- `GET /api/v1/organizations/search` - Query/filter sanitization  
- `GET /api/v1/tasks/search/` - Search query sanitization

#### List Endpoints
- `GET /api/v1/contacts/` - Pagination validation
- `GET /api/v1/organizations/` - Search/filter sanitization, pagination
- `GET /api/v1/users/` - Pagination validation

#### Update Endpoints
- `PUT /api/v1/users/me` - Email/name sanitization

### Validation Error Responses

When validation fails, endpoints return detailed error information:

```json
{
  "detail": "Invalid input: Search query contains prohibited patterns",
  "type": "validation_error",
  "field": "q"
}
```

## Configuration

### Environment Variables

Rate limiting and validation can be configured via environment variables:

```bash
# Redis configuration for rate limiting
REDIS_URL=redis://localhost:6379/0

# Request size limits  
MAX_REQUEST_BODY_SIZE=10485760  # 10MB
MAX_QUERY_STRING_LENGTH=8192   # 8KB
MAX_HEADER_SIZE=16384          # 16KB
MAX_URL_LENGTH=2048            # 2KB

# Rate limiting (per minute/hour/day)
DEFAULT_RATE_LIMIT_MINUTE=60
DEFAULT_RATE_LIMIT_HOUR=1000
DEFAULT_RATE_LIMIT_DAY=10000

AUTH_RATE_LIMIT_MINUTE=5
SEARCH_RATE_LIMIT_MINUTE=30
```

### Middleware Configuration

Validation middleware is configured in `app/main.py`:

```python
from app.api.middleware.rate_limit import rate_limit_middleware
from app.api.middleware.request_validation import request_validation_middleware

# Request validation (before rate limiting)
app.middleware("http")(request_validation_middleware)

# Rate limiting  
app.middleware("http")(rate_limit_middleware)
```

## Testing

### Unit Tests

Comprehensive test suites validate all security features:

- `tests/test_input_validation.py` - Input sanitization tests
- `tests/test_middleware_validation.py` - Middleware tests  
- `tests/test_journal_validation.py` - Legacy validation tests
- `tests/test_api_integration.py` - End-to-end integration tests

### Security Test Examples

```python
# XSS prevention test
malicious_input = "<script>alert('xss')</script>"
with pytest.raises(ValueError):
    InputSanitizer.sanitize_search_query(malicious_input)

# SQL injection prevention test  
sql_injection = "'; DROP TABLE users; --"
with pytest.raises(ValueError):
    InputSanitizer.sanitize_search_query(sql_injection)

# Length limit test
long_input = "a" * 1000
with pytest.raises(ValueError):
    InputSanitizer.sanitize_search_query(long_input)
```

### Running Security Tests

```bash
# Run all validation tests
pytest tests/test_input_validation.py -v

# Run middleware tests
pytest tests/test_middleware_validation.py -v  

# Run integration tests (requires database setup)
pytest tests/test_api_integration.py -v

# Run security-focused tests
pytest -k "security or validation or sanitiz" -v
```

## Best Practices

### For Developers

1. **Always use InputSanitizer** for any user input that will be stored or processed
2. **Apply rate limiting** to any endpoint that could be abused
3. **Validate pagination parameters** using PaginationValidator
4. **Use appropriate length limits** for different types of input
5. **Test with malicious inputs** to ensure validation is working

### For API Consumers

1. **Handle validation errors gracefully** with proper error messages
2. **Respect rate limits** to avoid being blocked
3. **Keep requests under size limits** to prevent rejection  
4. **Use proper pagination** for large data sets
5. **Sanitize inputs client-side** as an additional layer of protection

## Monitoring and Logging

### Security Events

The following security events are logged:

- Rate limit violations
- Oversized request attempts
- Malicious input detection  
- Suspicious header detection
- Validation failures

### Metrics

Key security metrics to monitor:

- Rate limit hit rate
- Validation error rate
- Request size distribution
- Attack pattern frequency
- Endpoint response times

### Alerts

Consider setting up alerts for:

- High rate limit violation rates
- Repeated malicious input attempts
- Unusual request size patterns
- High validation error rates from specific IPs

## Future Enhancements

Planned security improvements:

1. **Advanced threat detection** - Machine learning-based pattern recognition
2. **IP-based blocking** - Automatic blocking of malicious IPs
3. **Request fingerprinting** - Bot detection and blocking
4. **Content Security Policy** - Additional XSS protection headers
5. **OWASP compliance** - Full compliance with OWASP security standards