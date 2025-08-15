# MCP Server Testing Guide

This guide provides comprehensive instructions for running and maintaining the test suite for the MCP (Model Context Protocol) server component of Recaller.

## Overview

The MCP server test suite covers:

- **Unit Tests**: Individual component testing (protocol handling, error handling, privacy enforcement)
- **Integration Tests**: API endpoint testing and inter-service communication
- **Tenant Isolation Tests**: Multi-tenancy security and data isolation
- **Privacy Enforcement Tests**: Data protection and external request blocking
- **Error Handling Tests**: Comprehensive error scenario coverage

## Test Structure

```
mcp_server/tests/
├── conftest.py                          # Test configuration and fixtures
├── test_mcp_protocol.py                 # MCP protocol unit tests
├── test_api_endpoints.py                # API integration tests
├── test_tenant_isolation_comprehensive.py # Tenant isolation tests
├── test_privacy_enforcement.py         # Privacy protection tests
└── test_error_handling.py              # Error handling tests
```

## Prerequisites

### Install Dependencies

```bash
cd mcp_server
pip install pytest pytest-asyncio fastapi uvicorn pydantic pydantic-settings websockets httpx
```

### Environment Setup

Ensure test environment variables are set:

```bash
export MCP_ENABLE_TENANT_ISOLATION=true
export BLOCK_EXTERNAL_REQUESTS=true
export ENFORCE_LOCAL_ONLY=true
export ANONYMIZE_LOGS=true
export ANONYMIZE_ERROR_MESSAGES=true
```

## Running Tests

### Run All Tests

```bash
cd mcp_server
python -m pytest tests/ -v
```

### Run Specific Test Categories

#### Unit Tests (MCP Protocol)
```bash
python -m pytest tests/test_mcp_protocol.py -v
```

#### Integration Tests (API Endpoints)
```bash
python -m pytest tests/test_api_endpoints.py -v
```

#### Tenant Isolation Tests
```bash
python -m pytest tests/test_tenant_isolation_comprehensive.py -v
```

#### Privacy Enforcement Tests
```bash
python -m pytest tests/test_privacy_enforcement.py -v
```

#### Error Handling Tests
```bash
python -m pytest tests/test_error_handling.py -v
```

### Run Tests with Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Run Tests in Parallel

```bash
pip install pytest-xdist
python -m pytest tests/ -n auto
```

## Test Categories

### 1. MCP Protocol Tests (`test_mcp_protocol.py`)

**Coverage:**
- Message parsing and validation
- Request/response handling
- Protocol error handling
- Message serialization/deserialization
- Async communication patterns

**Key Test Cases:**
- Valid request processing
- Invalid JSON handling
- Missing required fields
- Unknown method handling
- Protocol error propagation
- Request timeout handling

### 2. API Endpoint Tests (`test_api_endpoints.py`)

**Coverage:**
- Model management endpoints
- Inference endpoints
- Health check endpoints
- Authentication and authorization
- Request validation
- Response formatting

**Key Test Cases:**
- Model registration with tenant context
- Model listing with tenant filtering
- Successful inference operations
- Privacy validation in requests
- Error handling for missing models
- Rate limiting scenarios

### 3. Tenant Isolation Tests (`test_tenant_isolation_comprehensive.py`)

**Coverage:**
- Multi-tenant data separation
- Access control enforcement
- Cross-tenant access prevention
- Tenant context propagation
- Concurrent access scenarios

**Key Test Cases:**
- Model registration per tenant
- Tenant-filtered model listing
- Cross-tenant access denial
- Backend access control
- Concurrent tenant operations
- Audit logging for violations

### 4. Privacy Enforcement Tests (`test_privacy_enforcement.py`)

**Coverage:**
- External request blocking
- Sensitive data detection
- Data anonymization
- Model configuration validation
- Privacy compliance reporting

**Key Test Cases:**
- Blocking external API calls
- Detecting sensitive patterns
- Anonymizing logs and errors
- Validating model configurations
- Privacy status reporting
- Data retention enforcement

### 5. Error Handling Tests (`test_error_handling.py`)

**Coverage:**
- Protocol error handling
- API error responses
- Service failure scenarios
- Error context preservation
- Graceful degradation

**Key Test Cases:**
- MCP protocol errors
- Authentication failures
- Model unavailability
- Backend service errors
- Timeout handling
- Privacy violation errors

## Test Configuration

### Fixtures (`conftest.py`)

The test suite provides several fixtures:

#### Mock Tenants
```python
@pytest.fixture
def mock_tenant_1() -> TenantInfo:
    return TenantInfo(
        id="tenant-1",
        slug="tenant-1",
        name="Test Tenant 1",
        active=True
    )
```

#### Clean Model Registry
```python
@pytest.fixture
def clean_model_registry():
    # Provides a clean model registry for each test
    # Automatically restores state after test completion
```

#### Mock Model Backend
```python
@pytest.fixture
def mock_model_backend():
    # Provides a mock model backend for testing
    # Includes mocked inference methods
```

### Settings Reset
The test suite automatically resets MCP settings to secure defaults for each test, ensuring:
- Tenant isolation is enabled
- External requests are blocked
- Privacy protection is active
- Logging is anonymized

## Writing New Tests

### Test Naming Convention

- Test files: `test_<component>.py`
- Test classes: `Test<Component><Aspect>`
- Test methods: `test_<specific_behavior>`

### Example Test Structure

```python
class TestModelManagement:
    """Test model management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    @patch('api.endpoints.get_current_tenant')
    @patch('api.endpoints.model_registry')
    def test_model_registration_success(self, mock_registry, mock_get_tenant):
        """Test successful model registration."""
        # Arrange
        mock_tenant = TenantInfo(id="test-tenant", slug="test-tenant", name="Test Tenant")
        mock_get_tenant.return_value = mock_tenant
        mock_registry.register_model = AsyncMock(return_value="model_id")
        
        # Act
        response = self.client.post("/api/v1/models/register", json={...})
        
        # Assert
        assert response.status_code == 200
        assert response.json()["success"] is True
```

### Testing Async Code

Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_operation(self):
    """Test an async operation."""
    result = await some_async_function()
    assert result is not None
```

### Mocking External Dependencies

Always mock external dependencies:

```python
@patch('services.auth.httpx.AsyncClient')
async def test_with_external_service(self, mock_client):
    """Test with mocked external service."""
    mock_client.return_value.get.return_value.status_code = 200
    # Test implementation
```

## Continuous Integration

### GitHub Actions Integration

The test suite is designed to run in CI environments. Add to `.github/workflows/test-mcp-server.yml`:

```yaml
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd mcp_server
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: |
        cd mcp_server
        python -m pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./mcp_server/coverage.xml
```

## Performance Testing

### Load Testing

For performance testing, use the concurrent test patterns:

```python
def test_concurrent_requests(self):
    """Test performance under concurrent load."""
    import threading
    import time
    
    results = []
    
    def make_request():
        response = self.client.get("/api/v1/models")
        results.append(response.status_code)
    
    # Create multiple threads
    threads = [threading.Thread(target=make_request) for _ in range(10)]
    
    start_time = time.time()
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    assert all(result == 200 for result in results)
    assert end_time - start_time < 2.0  # Should complete quickly
```

## Troubleshooting

### Common Issues

#### Import Errors
- Ensure `sys.path` is correctly configured in test files
- Verify all dependencies are installed
- Check for circular imports

#### Async Test Failures
- Use `@pytest.mark.asyncio` for async tests
- Ensure proper async/await usage
- Mock async dependencies correctly

#### Fixture Issues
- Check fixture scope (function, class, module, session)
- Verify fixture dependencies
- Ensure proper cleanup in fixtures

#### Mock Problems
- Use `patch` decorators correctly
- Return appropriate mock values
- Verify mock method calls with assertions

### Debugging Tests

#### Verbose Output
```bash
python -m pytest tests/ -v -s
```

#### Debug Specific Test
```bash
python -m pytest tests/test_api_endpoints.py::TestModelManagementEndpoints::test_register_model_success -v -s
```

#### Capture Logs
```bash
python -m pytest tests/ --log-cli-level=DEBUG
```

## Security Testing

### Tenant Isolation Verification

Ensure all tests validate:
- Cross-tenant data access is prevented
- Tenant context is properly enforced
- Admin access works when appropriate

### Privacy Protection Verification

Ensure all tests validate:
- External requests are blocked
- Sensitive data is anonymized
- Privacy settings are respected

### Example Security Test

```python
def test_cross_tenant_access_blocked(self, mock_tenant_1, mock_tenant_2):
    """Verify cross-tenant access is completely blocked."""
    # Create model for tenant 1
    model = create_test_model(tenant_id=mock_tenant_1.id)
    
    # Attempt access from tenant 2
    result = registry.get_model(model.id, mock_tenant_2.id)
    
    # Should be blocked
    assert result is None
```

## Maintenance

### Regular Test Updates

- Update tests when adding new features
- Ensure test coverage remains high (>90%)
- Remove obsolete tests
- Update mocks when dependencies change

### Test Performance Monitoring

- Monitor test execution time
- Identify slow tests and optimize
- Use parallel execution for large test suites
- Profile tests to find bottlenecks

### Documentation Updates

- Keep this guide updated with new test categories
- Document new fixtures and utilities
- Update examples when patterns change
- Maintain troubleshooting section

## Best Practices

1. **Write Tests First**: Use TDD approach when possible
2. **Keep Tests Simple**: One concept per test
3. **Use Descriptive Names**: Test names should explain behavior
4. **Mock External Dependencies**: Always mock external services
5. **Test Error Cases**: Don't just test happy paths
6. **Maintain Test Data**: Keep test data minimal and focused
7. **Clean Up**: Ensure tests don't affect each other
8. **Document Complex Tests**: Add comments for complex test logic

## Integration with Development Workflow

### Pre-commit Hooks

Set up pre-commit hooks to run tests:

```bash
pip install pre-commit
# Add to .pre-commit-config.yaml
```

### IDE Integration

Configure your IDE to run tests:
- VS Code: Python Test Explorer
- PyCharm: Built-in test runner
- Vim: vim-test plugin

### Code Quality

Combine testing with code quality tools:
```bash
pip install black flake8 mypy
black mcp_server/tests/
flake8 mcp_server/tests/
mypy mcp_server/tests/
```

This comprehensive testing approach ensures the MCP server maintains high quality, security, and reliability standards while supporting the multi-tenant, privacy-focused architecture of Recaller.