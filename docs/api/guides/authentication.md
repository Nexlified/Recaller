# Authentication Guide

This guide covers everything you need to know about authenticating with the Recaller API.

## Overview

Recaller uses **JWT (JSON Web Token) based authentication** with OAuth2-compatible endpoints. The authentication system is designed for security, scalability, and ease of integration.

## Authentication Flow

### 1. User Registration

First-time users need to register an account:

```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": null
}
```

### 2. Login & Token Acquisition

Use email and password to obtain an access token:

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE2NzM5NzI4MDB9.abc123...",
  "token_type": "bearer"
}
```

### 3. Making Authenticated Requests

Include the token in the `Authorization` header:

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Token Details

### JWT Structure

Recaller JWT tokens contain:

- **Header**: Algorithm and token type
- **Payload**: User ID, expiration, and tenant information
- **Signature**: Cryptographic signature for verification

Example decoded payload:
```json
{
  "sub": "123",           // User ID
  "exp": 1673972800,      // Expiration timestamp
  "iat": 1673969200,      // Issued at timestamp
  "tenant_id": 1          // Tenant identifier
}
```

### Token Expiration

- **Default Duration**: 30 minutes
- **Configurable**: Can be adjusted via `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Automatic Expiry**: Tokens become invalid after expiration
- **No Refresh**: Currently no refresh token mechanism (login again for new token)

## Security Features

### Password Security

- **Hashing**: Passwords are hashed using bcrypt with salt
- **Never Stored**: Plain text passwords are never saved
- **Minimum Length**: 8 character minimum requirement
- **Validation**: Server-side validation on registration and updates

### Token Security

- **Signed**: Tokens are cryptographically signed
- **Secret Key**: Server secret key prevents token forgery
- **Expiration**: Limited lifetime reduces exposure risk
- **Stateless**: No server-side session storage required

### Account Security

- **Active Status**: Inactive accounts cannot obtain tokens
- **Email Uniqueness**: One account per email address per tenant
- **Secure Headers**: Proper security headers in responses

## Multi-Tenant Authentication

### Tenant Context

In multi-tenant deployments, include the tenant ID:

```bash
curl -X GET "http://localhost:8000/api/v1/organizations" \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: your-tenant-id"
```

### Tenant Isolation

- **Automatic**: Middleware enforces tenant boundaries
- **User Binding**: Users belong to specific tenants
- **Data Isolation**: Users can only access their tenant's data
- **Cross-Tenant**: No cross-tenant data access allowed

## Implementation Examples

### JavaScript/TypeScript

```javascript
class RecallerAPI {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('recaller_token');
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('recaller_token', this.token);
      return data;
    } else {
      throw new Error('Login failed');
    }
  }

  async makeRequest(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`,
      ...options.headers
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Token expired or invalid
      this.logout();
      throw new Error('Authentication required');
    }

    return response;
  }

  logout() {
    this.token = null;
    localStorage.removeItem('recaller_token');
  }
}

// Usage
const api = new RecallerAPI();
await api.login('user@example.com', 'password');
const response = await api.makeRequest('/users/me');
```

### Python

```python
import requests
import json
from datetime import datetime, timedelta

class RecallerAPI:
    def __init__(self, base_url='http://localhost:8000/api/v1'):
        self.base_url = base_url
        self.token = None
        self.token_expires = None

    def login(self, email, password):
        """Login and store access token"""
        response = requests.post(
            f'{self.base_url}/login',
            data={
                'username': email,
                'password': password
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            # Assume 30 minute expiry
            self.token_expires = datetime.now() + timedelta(minutes=30)
            return data
        else:
            raise Exception(f"Login failed: {response.text}")

    def make_request(self, endpoint, method='GET', data=None, params=None):
        """Make authenticated API request"""
        if not self.token or datetime.now() >= self.token_expires:
            raise Exception("Token expired or not available")

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        response = requests.request(
            method=method,
            url=f'{self.base_url}{endpoint}',
            headers=headers,
            json=data,
            params=params
        )

        if response.status_code == 401:
            self.token = None
            raise Exception("Authentication required")

        return response

    def get_current_user(self):
        """Get current user profile"""
        response = self.make_request('/users/me')
        return response.json() if response.status_code == 200 else None

# Usage
api = RecallerAPI()
api.login('user@example.com', 'password')
user = api.get_current_user()
print(f"Logged in as: {user['full_name']}")
```

## Error Handling

### Authentication Errors

| Status Code | Error | Description | Solution |
|-------------|-------|-------------|----------|
| 400 | `Incorrect email or password` | Invalid credentials | Check email/password |
| 400 | `Inactive user` | Account disabled | Contact administrator |
| 401 | `Not authenticated` | Missing/invalid token | Login again |
| 422 | `Validation error` | Invalid request format | Check request format |

### Example Error Responses

**Invalid Credentials:**
```json
{
  "detail": "Incorrect email or password"
}
```

**Validation Error:**
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

## Best Practices

### Security

1. **Store Tokens Securely**: Use secure storage mechanisms
2. **Handle Expiration**: Implement automatic re-authentication
3. **HTTPS Only**: Always use HTTPS in production
4. **Token Rotation**: Login periodically for fresh tokens
5. **Logout Cleanup**: Clear tokens on logout

### Performance

1. **Reuse Tokens**: Don't login for every request
2. **Cache Wisely**: Store tokens appropriately for your platform
3. **Handle Errors**: Implement proper error handling and retries
4. **Connection Pooling**: Reuse HTTP connections when possible

### User Experience

1. **Persist Login**: Remember user sessions appropriately
2. **Clear Feedback**: Show authentication status to users
3. **Graceful Degradation**: Handle auth failures elegantly
4. **Loading States**: Show progress during authentication

## Troubleshooting

### Common Issues

**"Not authenticated" errors:**
- Check if token is included in Authorization header
- Verify token hasn't expired
- Ensure proper "Bearer " prefix

**Login failures:**
- Verify email and password are correct
- Check if account is active
- Ensure proper Content-Type header

**Token expiration:**
- Implement token refresh logic
- Login again to get new token
- Check system clock synchronization

### Debug Tips

1. **Decode JWT**: Use jwt.io to inspect token contents
2. **Check Headers**: Verify all required headers are present
3. **Server Logs**: Check server logs for detailed error messages
4. **Network Tools**: Use browser dev tools or Postman for debugging

---

**Next Steps:**
- Review [Multi-tenancy Guide](./multi-tenancy.md) for tenant concepts
- Check [Error Handling Guide](./error-handling.md) for comprehensive error management
- Explore [Code Examples](../examples/) for more implementation patterns