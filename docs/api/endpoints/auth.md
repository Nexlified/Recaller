# Authentication Endpoints

This document provides detailed information about authentication-related endpoints in the Recaller API.

## Base URL

All authentication endpoints are available at:
```
{base_url}/api/v1/
```

## Endpoints Overview

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/login` | POST | Authenticate user and get access token | No |
| `/register` | POST | Create new user account | No |

---

## POST /login

Authenticate a user with email and password to obtain an access token.

### Request

**URL:** `POST /api/v1/login`

**Content-Type:** `application/x-www-form-urlencoded`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | User's email address |
| `password` | string | Yes | User's password |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=user@example.com&password=securepassword123'
});

const data = await response.json();
```

**Python Example:**

```python
import requests

response = requests.post(
  'http://localhost:8000/api/v1/login',
  data={
    'username': 'user@example.com',
    'password': 'securepassword123'
  },
  headers={
    'Content-Type': 'application/x-www-form-urlencoded'
  }
)

data = response.json()
```

### Response

**Success Response (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE2NzM5NzI4MDB9.abc123...",
  "token_type": "bearer"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token for API authentication |
| `token_type` | string | Token type, always "bearer" |

### Error Responses

**Invalid Credentials (400):**

```json
{
  "detail": "Incorrect email or password"
}
```

**Inactive User (400):**

```json
{
  "detail": "Inactive user"
}
```

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Usage Notes

- **OAuth2 Compatible**: This endpoint follows OAuth2 password flow standards
- **Token Expiration**: Tokens expire after 30 minutes by default
- **Security**: Passwords are verified against bcrypt hashes
- **Rate Limiting**: Multiple failed attempts may be rate limited

---

## POST /register

Create a new user account in the system.

### Request

**URL:** `POST /api/v1/register`

**Content-Type:** `application/json`

**Body Parameters:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `email` | string | Yes | User's email address | Valid email format, unique |
| `full_name` | string | No | User's full name | Max 100 characters |
| `password` | string | Yes | User's password | Min 8 characters, max 100 |
| `is_active` | boolean | No | Account active status | Default: true |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "full_name": "John Doe",
    "password": "securepassword123"
  }'
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'newuser@example.com',
    full_name: 'John Doe',
    password: 'securepassword123'
  })
});

const user = await response.json();
```

**Python Example:**

```python
import requests

response = requests.post(
  'http://localhost:8000/api/v1/register',
  json={
    'email': 'newuser@example.com',
    'full_name': 'John Doe',
    'password': 'securepassword123'
  }
)

user = response.json()
```

### Response

**Success Response (201):**

```json
{
  "id": 123,
  "email": "newuser@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": null
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique user identifier |
| `email` | string | User's email address |
| `full_name` | string | User's full name |
| `is_active` | boolean | Account active status |
| `created_at` | datetime | Account creation timestamp |
| `updated_at` | datetime | Last update timestamp (null for new accounts) |

### Error Responses

**Email Already Exists (400):**

```json
{
  "detail": "The user with this email already exists in the system"
}
```

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Usage Notes

- **Email Uniqueness**: Email addresses must be unique within each tenant
- **Password Security**: Passwords are hashed with bcrypt before storage
- **Auto-Activation**: New accounts are active by default
- **Tenant Assignment**: Users are assigned to the default tenant
- **No Auto-Login**: Use `/login` endpoint after registration to get a token

---

## Common Authentication Patterns

### Complete Registration + Login Flow

```javascript
async function registerAndLogin(userData) {
  try {
    // 1. Register new user
    const registerResponse = await fetch('/api/v1/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    
    if (!registerResponse.ok) {
      throw new Error('Registration failed');
    }
    
    const user = await registerResponse.json();
    console.log('User registered:', user);
    
    // 2. Login to get token
    const loginResponse = await fetch('/api/v1/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${userData.email}&password=${userData.password}`
    });
    
    if (!loginResponse.ok) {
      throw new Error('Login failed');
    }
    
    const tokens = await loginResponse.json();
    console.log('Login successful:', tokens);
    
    // Store token for future requests
    localStorage.setItem('access_token', tokens.access_token);
    
    return { user, tokens };
    
  } catch (error) {
    console.error('Registration/Login error:', error);
    throw error;
  }
}

// Usage
const result = await registerAndLogin({
  email: 'user@example.com',
  full_name: 'John Doe',
  password: 'securepassword123'
});
```

### Token Validation

```javascript
async function validateToken(token) {
  try {
    const response = await fetch('/api/v1/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const user = await response.json();
      return { valid: true, user };
    } else {
      return { valid: false, error: 'Token invalid or expired' };
    }
  } catch (error) {
    return { valid: false, error: 'Network error' };
  }
}
```

### Automatic Token Refresh

```javascript
class AuthManager {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.loginTime = localStorage.getItem('login_time');
  }
  
  isTokenExpired() {
    if (!this.loginTime) return true;
    
    const tokenAge = Date.now() - parseInt(this.loginTime);
    const thirtyMinutes = 30 * 60 * 1000; // 30 minutes in milliseconds
    
    return tokenAge > thirtyMinutes;
  }
  
  async ensureValidToken() {
    if (!this.token || this.isTokenExpired()) {
      // Redirect to login or show login modal
      this.redirectToLogin();
      return false;
    }
    return true;
  }
  
  async login(email, password) {
    const response = await fetch('/api/v1/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${email}&password=${password}`
    });
    
    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      this.loginTime = Date.now().toString();
      
      localStorage.setItem('access_token', this.token);
      localStorage.setItem('login_time', this.loginTime);
      
      return data;
    } else {
      throw new Error('Login failed');
    }
  }
  
  logout() {
    this.token = null;
    this.loginTime = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('login_time');
  }
  
  redirectToLogin() {
    this.logout();
    window.location.href = '/login';
  }
}
```

## Security Considerations

### Password Requirements

- **Minimum Length**: 8 characters
- **Maximum Length**: 100 characters
- **Hashing**: bcrypt with salt
- **Storage**: Plain text passwords are never stored

### Token Security

- **Expiration**: 30 minutes default lifetime
- **Signing**: HMAC-SHA256 signature
- **Payload**: Contains user ID and tenant information
- **Validation**: Verified on each request

### Best Practices

1. **HTTPS Only**: Always use HTTPS in production
2. **Secure Storage**: Store tokens securely (HttpOnly cookies or secure storage)
3. **Token Rotation**: Re-login periodically for fresh tokens
4. **Logout Cleanup**: Clear tokens on logout
5. **Error Handling**: Handle authentication errors gracefully

---

**Related Documentation:**
- [Authentication Guide](../guides/authentication.md) - Complete authentication implementation
- [Error Handling](../guides/error-handling.md) - Error management patterns
- [User Management Endpoints](./users.md) - User profile management