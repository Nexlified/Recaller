# Authentication Integration Tests - Execution Guide

This document provides instructions for running the comprehensive integration tests for the authentication endpoints in the Recaller backend.

## Overview

The authentication integration tests validate the `/api/v1/auth/login` and `/api/v1/auth/register` endpoints with comprehensive coverage including:

- **Happy Path Testing**: Valid login and registration flows
- **Error Handling**: Invalid credentials, duplicate emails, validation errors
- **Security Testing**: Token validation, SQL injection protection, password hashing
- **Edge Cases**: Malformed data, inactive users, performance benchmarks
- **Multi-tenant Support**: Tenant context handling
- **Schema Validation**: Response structure compliance

## Test Files

### 1. `tests/test_auth_minimal.py`
Lightweight test suite with essential authentication test cases:
- Basic login and registration functionality
- Core error handling scenarios
- Token security validation
- Password hashing verification

### 2. `tests/test_auth_comprehensive.py`
Extensive test suite covering all requirements from the issue:
- Complete parameterized test coverage
- SQL injection protection tests
- Performance benchmarks
- Concurrent operation handling
- Response schema validation
- Edge case testing

## Prerequisites

### Required Dependencies
```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Install backend dependencies
pip install -r requirements.txt
```

### Database Setup
The tests use SQLite for isolated testing and automatically handle:
- Test database creation and teardown
- Test user data setup
- Cleanup between test runs

## Running Tests

### Quick Test Execution
```bash
# Run minimal test suite (fast validation)
python tests/test_auth_minimal.py

# Run minimal tests with pytest
python -m pytest tests/test_auth_minimal.py -v
```

### Comprehensive Test Execution
```bash
# Run all comprehensive tests
python -m pytest tests/test_auth_comprehensive.py -v

# Run specific test classes
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationLogin -v
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationRegistration -v
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationSecurity -v

# Run tests with shorter traceback for cleaner output
python -m pytest tests/test_auth_comprehensive.py -v --tb=short

# Run tests with coverage (if pytest-cov is installed)
python -m pytest tests/test_auth_comprehensive.py --cov=app.api.v1.endpoints.auth --cov-report=html
```

### Test Categories

#### 1. Login Endpoint Tests (`/api/v1/auth/login`)
```bash
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationLogin -v
```
Tests include:
- Valid credentials authentication
- Invalid email/password handling
- Inactive user account blocking
- Missing field validation
- SQL injection protection
- Performance benchmarks

#### 2. Registration Endpoint Tests (`/api/v1/auth/register`)
```bash
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationRegistration -v
```
Tests include:
- Valid user registration
- Duplicate email detection
- Email format validation
- Password strength requirements
- SQL injection protection
- Password hashing security

#### 3. Security Tests
```bash
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationSecurity -v
```
Tests include:
- JWT token structure validation
- Token expiration handling
- Secret key security
- Case sensitivity handling
- Large payload protection
- Concurrent request handling

#### 4. Schema Validation Tests
```bash
python -m pytest tests/test_auth_comprehensive.py::TestResponseSchemaValidation -v
```
Tests include:
- Login response schema compliance
- Registration response schema compliance
- Error response consistency
- Validation error structure

## Test Results Interpretation

### Success Indicators
- ✅ All tests pass (status code assertions)
- ✅ Response schemas match API documentation
- ✅ Security validations succeed
- ✅ Performance benchmarks meet requirements (<1s login, <2s registration)

### Expected Warnings
The following warnings are expected and do not indicate test failures:
- `PydanticDeprecatedSince20`: Pydantic v1 validators (existing codebase)
- `DeprecationWarning`: datetime.utcnow() usage (existing codebase)
- `MovedIn20Warning`: SQLAlchemy declarative usage (existing codebase)

### Failure Scenarios
Tests will fail if:
- Authentication logic is broken
- Password hashing is compromised
- Token generation fails
- SQL injection vulnerabilities exist
- Response schemas don't match specifications
- Performance requirements aren't met

## Continuous Integration Usage

### GitHub Actions Integration
```yaml
- name: Run Authentication Tests
  run: |
    cd backend
    python -m pytest tests/test_auth_comprehensive.py -v --tb=short
```

### Docker Testing
```bash
# Run tests in isolated container
docker run --rm -v $(pwd):/app -w /app/backend python:3.12 bash -c "
  pip install -r requirements.txt pytest pytest-asyncio httpx &&
  python -m pytest tests/test_auth_comprehensive.py -v
"
```

## Test Data Management

### Test Users
The tests automatically create and manage test users:
- `testuser@example.com` (active user for login tests)
- `inactive@example.com` (inactive user for access control tests)
- Dynamic users created/cleaned up during registration tests

### Database Isolation
- Each test run uses a fresh SQLite database
- Tests are isolated and can run independently
- Automatic cleanup prevents test data pollution

## Debugging Failed Tests

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Check SQLite permissions and cleanup
3. **Token Errors**: Verify JWT secret key configuration
4. **Performance Failures**: Check system load during test execution

### Debugging Commands
```bash
# Run single test with detailed output
python -m pytest tests/test_auth_comprehensive.py::TestAuthenticationLogin::test_login_valid_credentials_success -v -s

# Run tests with pdb debugging
python -m pytest tests/test_auth_comprehensive.py --pdb

# Generate test report
python -m pytest tests/test_auth_comprehensive.py --html=test_report.html --self-contained-html
```

## Coverage Requirements

The tests validate the following success criteria from the original issue:

- ✅ All authentication endpoints have comprehensive test coverage
- ✅ Tests include both positive and negative scenarios  
- ✅ Edge cases are covered (malformed tokens, expired sessions)
- ✅ Tests are isolated and can run independently
- ✅ Documentation includes test execution instructions
- ✅ SQL injection protection validated
- ✅ Input sanitization tested
- ✅ Rate limiting compliance (framework-level)
- ✅ Token expiration handling verified
- ✅ Performance benchmarks included
- ✅ Multi-tenant context support tested

## Performance Benchmarks

Expected performance thresholds:
- Login endpoint: < 1 second response time
- Registration endpoint: < 2 seconds response time (due to password hashing)
- Concurrent registrations: Should handle 5+ simultaneous requests

## Security Validations

The tests verify:
- Passwords are never stored in plaintext
- JWT tokens are properly signed and validated
- SQL injection attempts are safely handled
- Input validation prevents malformed data processing
- Inactive users cannot authenticate
- Token expiration is properly enforced

## Integration with Frontend

These backend tests validate the API contract that the frontend authentication system depends on:
- Token format and structure
- Error response formats
- Registration flow requirements
- Login validation rules

This ensures reliable integration between frontend and backend authentication components.