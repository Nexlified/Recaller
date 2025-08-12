# Error Handling Guide

This guide provides comprehensive information about error handling in the Recaller API, including error codes, response formats, and best practices for handling different types of errors.

## Error Response Format

All API errors follow a consistent format based on FastAPI's error handling:

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Response

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Field-specific error message",
      "type": "error_type"
    }
  ]
}
```

## HTTP Status Codes

### 2xx Success Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content returned |

### 4xx Client Error Codes

| Code | Status | Description | Common Causes |
|------|--------|-------------|---------------|
| 400 | Bad Request | Invalid request data | Validation failures, business logic violations |
| 401 | Unauthorized | Authentication required | Missing token, expired token, invalid credentials |
| 403 | Forbidden | Access denied | Insufficient permissions, tenant restrictions |
| 404 | Not Found | Resource not found | Invalid ID, deleted resource |
| 422 | Unprocessable Entity | Validation error | Invalid data format, missing required fields |
| 429 | Too Many Requests | Rate limit exceeded | Too many requests in time window |

### 5xx Server Error Codes

| Code | Status | Description | Action |
|------|--------|-------------|--------|
| 500 | Internal Server Error | Server-side error | Retry request, contact support |
| 502 | Bad Gateway | Upstream service error | Retry request |
| 503 | Service Unavailable | Service temporarily unavailable | Retry with backoff |

## Error Categories

### Authentication Errors (401)

**Missing Token:**
```json
{
  "detail": "Not authenticated"
}
```

**Invalid Credentials:**
```json
{
  "detail": "Incorrect email or password"
}
```

**Inactive Account:**
```json
{
  "detail": "Inactive user"
}
```

**Example Handling:**
```javascript
if (response.status === 401) {
  // Clear stored token and redirect to login
  localStorage.removeItem('token');
  window.location.href = '/login';
}
```

### Authorization Errors (403)

**Insufficient Permissions:**
```json
{
  "detail": "The user doesn't have enough privileges"
}
```

**Tenant Access Denied:**
```json
{
  "detail": "Access denied for this tenant"
}
```

### Validation Errors (422)

**Single Field Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Multiple Field Errors:**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "organization_type"],
      "msg": "organization_type must be one of: company, school, nonprofit, government, healthcare, religious",
      "type": "value_error"
    }
  ]
}
```

### Business Logic Errors (400)

**Duplicate Resource:**
```json
{
  "detail": "The user with this email already exists in the system"
}
```

**Invalid State:**
```json
{
  "detail": "Cannot delete organization with active contacts"
}
```

**Constraint Violation:**
```json
{
  "detail": "Organization name must be unique within tenant"
}
```

### Resource Not Found (404)

**Simple Not Found:**
```json
{
  "detail": "User not found"
}
```

**Detailed Not Found:**
```json
{
  "detail": "The organization with id 123 does not exist in the system"
}
```

## Error Handling Patterns

### JavaScript/TypeScript Error Handling

```javascript
class APIError extends Error {
  constructor(status, detail, validationErrors = null) {
    super(detail);
    this.name = 'APIError';
    this.status = status;
    this.detail = detail;
    this.validationErrors = validationErrors;
  }
}

class RecallerAPI {
  async makeRequest(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        // Handle validation errors
        if (response.status === 422 && Array.isArray(errorData.detail)) {
          throw new APIError(
            response.status,
            'Validation failed',
            errorData.detail
          );
        }
        
        // Handle other errors
        throw new APIError(
          response.status,
          errorData.detail || 'An error occurred'
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Handle network errors
      throw new APIError(0, 'Network error occurred');
    }
  }

  // Helper method to extract validation errors
  getValidationErrors(error) {
    if (error.validationErrors) {
      const errors = {};
      error.validationErrors.forEach(validationError => {
        const field = validationError.loc[validationError.loc.length - 1];
        errors[field] = validationError.msg;
      });
      return errors;
    }
    return {};
  }
}

// Usage example
try {
  const user = await api.createUser({
    email: 'invalid-email',
    name: '',
    password: '123'
  });
} catch (error) {
  if (error.status === 422) {
    const fieldErrors = api.getValidationErrors(error);
    // Display field-specific errors in form
    Object.keys(fieldErrors).forEach(field => {
      showFieldError(field, fieldErrors[field]);
    });
  } else if (error.status === 401) {
    redirectToLogin();
  } else {
    showGeneralError(error.detail);
  }
}
```

### Python Error Handling

```python
import requests
from typing import Dict, List, Optional

class APIError(Exception):
    def __init__(self, status_code: int, detail: str, validation_errors: Optional[List] = None):
        self.status_code = status_code
        self.detail = detail
        self.validation_errors = validation_errors or []
        super().__init__(detail)

class RecallerAPI:
    def make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> requests.Response:
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                method=method,
                url=f'{self.base_url}{endpoint}',
                headers=headers,
                **kwargs
            )
            
            if not response.ok:
                error_data = response.json()
                
                # Handle validation errors
                if response.status_code == 422 and isinstance(error_data.get('detail'), list):
                    raise APIError(
                        response.status_code,
                        'Validation failed',
                        error_data['detail']
                    )
                
                # Handle other errors
                raise APIError(
                    response.status_code,
                    error_data.get('detail', 'An error occurred')
                )
            
            return response
            
        except requests.RequestException as e:
            raise APIError(0, f'Network error: {str(e)}')
    
    def get_validation_errors(self, error: APIError) -> Dict[str, str]:
        """Extract field-specific validation errors"""
        errors = {}
        for validation_error in error.validation_errors:
            field = validation_error['loc'][-1]  # Get the field name
            errors[field] = validation_error['msg']
        return errors

# Usage example
api = RecallerAPI()

try:
    response = api.make_request('/users', method='POST', json={
        'email': 'invalid-email',
        'name': '',
        'password': '123'
    })
    user = response.json()
except APIError as e:
    if e.status_code == 422:
        field_errors = api.get_validation_errors(e)
        for field, message in field_errors.items():
            print(f"Error in {field}: {message}")
    elif e.status_code == 401:
        print("Authentication required")
        # Handle re-authentication
    else:
        print(f"API Error: {e.detail}")
```

## Retry Strategies

### Exponential Backoff

```javascript
class RetryableAPI {
  async makeRequestWithRetry(endpoint, options = {}, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await this.makeRequest(endpoint, options);
      } catch (error) {
        lastError = error;
        
        // Don't retry client errors (4xx) except 429
        if (error.status >= 400 && error.status < 500 && error.status !== 429) {
          throw error;
        }
        
        // Don't retry on last attempt
        if (attempt === maxRetries) {
          throw error;
        }
        
        // Calculate delay: 1s, 2s, 4s, 8s...
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError;
  }
}
```

### Rate Limit Handling

```javascript
async function makeRequestWithRateLimit(api, endpoint, options) {
  try {
    return await api.makeRequest(endpoint, options);
  } catch (error) {
    if (error.status === 429) {
      // Extract retry-after header if available
      const retryAfter = error.headers?.['retry-after'] || 60;
      
      console.log(`Rate limited. Retrying after ${retryAfter} seconds...`);
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      
      // Retry the request
      return await api.makeRequest(endpoint, options);
    }
    throw error;
  }
}
```

## Validation Error Examples

### Common Validation Patterns

**Required Field Missing:**
```json
{
  "loc": ["body", "name"],
  "msg": "field required",
  "type": "value_error.missing"
}
```

**Invalid Email Format:**
```json
{
  "loc": ["body", "email"],
  "msg": "value is not a valid email address",
  "type": "value_error.email"
}
```

**Value Out of Range:**
```json
{
  "loc": ["body", "page"],
  "msg": "ensure this value is greater than 0",
  "type": "value_error.number.not_gt"
}
```

**String Too Long:**
```json
{
  "loc": ["body", "description"],
  "msg": "ensure this value has at most 2000 characters",
  "type": "value_error.any_str.max_length"
}
```

**Invalid Choice:**
```json
{
  "loc": ["body", "organization_type"],
  "msg": "organization_type must be one of: company, school, nonprofit, government, healthcare, religious",
  "type": "value_error"
}
```

## Error Recovery Strategies

### Form Validation

```javascript
function handleFormErrors(error, formElement) {
  // Clear previous errors
  clearFormErrors(formElement);
  
  if (error.status === 422) {
    // Handle field-specific validation errors
    const fieldErrors = api.getValidationErrors(error);
    
    Object.keys(fieldErrors).forEach(fieldName => {
      const field = formElement.querySelector(`[name="${fieldName}"]`);
      if (field) {
        showFieldError(field, fieldErrors[fieldName]);
      }
    });
  } else {
    // Show general error message
    showFormError(formElement, error.detail);
  }
}

function showFieldError(field, message) {
  field.classList.add('error');
  
  // Create or update error message
  let errorElement = field.parentNode.querySelector('.error-message');
  if (!errorElement) {
    errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    field.parentNode.appendChild(errorElement);
  }
  errorElement.textContent = message;
}
```

### Global Error Handler

```javascript
// Set up global error handler
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason instanceof APIError) {
    // Handle API errors globally
    if (event.reason.status === 401) {
      redirectToLogin();
    } else if (event.reason.status >= 500) {
      showNotification('Server error occurred. Please try again later.', 'error');
    }
    
    // Prevent the error from being logged to console
    event.preventDefault();
  }
});
```

## Best Practices

### Error Handling

1. **Always Handle Errors**: Never ignore error responses
2. **Specific Handling**: Handle different error types appropriately
3. **User-Friendly Messages**: Convert technical errors to user-friendly text
4. **Logging**: Log errors for debugging and monitoring
5. **Graceful Degradation**: Provide fallbacks when possible

### User Experience

1. **Clear Feedback**: Show specific error messages to users
2. **Form Validation**: Highlight problematic fields
3. **Retry Options**: Offer retry buttons for recoverable errors
4. **Loading States**: Show loading indicators during requests
5. **Offline Handling**: Handle network connectivity issues

### Development

1. **Error Boundaries**: Implement error boundaries in React applications
2. **Centralized Handling**: Create centralized error handling utilities
3. **Type Safety**: Use TypeScript for better error handling
4. **Testing**: Test error scenarios thoroughly
5. **Monitoring**: Implement error tracking and monitoring

## Testing Error Scenarios

### Mock Error Responses

```javascript
// Jest test example
describe('Error Handling', () => {
  test('should handle validation errors', async () => {
    const mockError = {
      status: 422,
      detail: [
        {
          loc: ['body', 'email'],
          msg: 'value is not a valid email address',
          type: 'value_error.email'
        }
      ]
    };
    
    fetch.mockRejectOnce(new APIError(422, 'Validation failed', mockError.detail));
    
    try {
      await api.createUser({ email: 'invalid' });
    } catch (error) {
      expect(error.status).toBe(422);
      expect(error.validationErrors).toHaveLength(1);
    }
  });
  
  test('should handle authentication errors', async () => {
    fetch.mockRejectOnce(new APIError(401, 'Not authenticated'));
    
    try {
      await api.getCurrentUser();
    } catch (error) {
      expect(error.status).toBe(401);
      expect(error.detail).toBe('Not authenticated');
    }
  });
});
```

---

**Next Steps:**
- Review [Authentication Guide](./authentication.md) for auth-specific error handling
- Check [Best Practices Guide](./best-practices.md) for overall API usage recommendations
- Explore [Code Examples](../examples/) for implementation patterns