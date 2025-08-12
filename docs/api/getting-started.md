# Getting Started with Recaller API

This guide will help you get up and running with the Recaller API quickly. Follow these steps to authenticate and make your first API calls.

## Prerequisites

- **API Access**: Ensure you have access to a Recaller API instance
- **HTTP Client**: Use curl, Postman, or any HTTP client library
- **JSON Knowledge**: Basic understanding of JSON format

## Quick Setup

### 1. Set Environment Variables

```bash
# Set your API base URL
export RECALLER_API_URL="http://localhost:8000/api/v1"

# These will be set after authentication
export ACCESS_TOKEN=""
export USER_ID=""
```

### 2. Test API Connectivity

```bash
# Test basic connectivity
curl -X GET "http://localhost:8000/" \
  -H "Content-Type: application/json"

# Expected response:
# {
#   "message": "Welcome to Recaller API!",
#   "documentation": "/docs",
#   "openapi": "/api/v1/openapi.json"
# }
```

### 3. Access Interactive Documentation

Visit the interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication Flow

### Step 1: Register a New User

```bash
curl -X POST "${RECALLER_API_URL}/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "full_name": "Demo User",
    "password": "demopassword123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "email": "demo@example.com",
  "full_name": "Demo User",
  "is_active": true,
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": null
}
```

### Step 2: Login and Get Access Token

```bash
curl -X POST "${RECALLER_API_URL}/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demopassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 3: Store Token for Future Use

```bash
# Extract and store the token
export ACCESS_TOKEN=$(curl -s -X POST "${RECALLER_API_URL}/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demopassword123" \
  | jq -r '.access_token')

echo "Token stored successfully"
```

## First API Calls

### Get Your User Profile

```bash
curl -X GET "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Create Your First Organization

```bash
curl -X POST "${RECALLER_API_URL}/organizations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Organization",
    "organization_type": "company",
    "industry": "Technology",
    "description": "A sample organization for testing",
    "website": "https://example.com"
  }'
```

### List Organizations

```bash
curl -X GET "${RECALLER_API_URL}/organizations?page=1&per_page=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

## Language-Specific Examples

### JavaScript/Node.js

```javascript
// Install axios: npm install axios
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api/v1';

class RecallerAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = null;
  }

  async register(userData) {
    const response = await axios.post(`${this.baseURL}/register`, userData);
    return response.data;
  }

  async login(email, password) {
    const response = await axios.post(`${this.baseURL}/login`, 
      `username=${email}&password=${password}`,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    
    this.token = response.data.access_token;
    return response.data;
  }

  async getCurrentUser() {
    const response = await axios.get(`${this.baseURL}/users/me`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return response.data;
  }

  async createOrganization(orgData) {
    const response = await axios.post(`${this.baseURL}/organizations`, orgData, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  }
}

// Usage
async function quickStart() {
  const api = new RecallerAPI();
  
  try {
    // Register new user
    const user = await api.register({
      email: 'demo@example.com',
      full_name: 'Demo User',
      password: 'demopassword123'
    });
    console.log('User registered:', user);

    // Login
    const tokens = await api.login('demo@example.com', 'demopassword123');
    console.log('Login successful');

    // Get current user
    const currentUser = await api.getCurrentUser();
    console.log('Current user:', currentUser);

    // Create organization
    const org = await api.createOrganization({
      name: 'My First Organization',
      organization_type: 'company',
      industry: 'Technology'
    });
    console.log('Organization created:', org);

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

quickStart();
```

### Python

```python
# Install requests: pip install requests
import requests
import json

API_BASE_URL = 'http://localhost:8000/api/v1'

class RecallerAPI:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None

    def register(self, user_data):
        response = requests.post(f'{self.base_url}/register', json=user_data)
        response.raise_for_status()
        return response.json()

    def login(self, email, password):
        response = requests.post(
            f'{self.base_url}/login',
            data={'username': email, 'password': password},
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data['access_token']
        return data

    def get_current_user(self):
        response = requests.get(
            f'{self.base_url}/users/me',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

    def create_organization(self, org_data):
        response = requests.post(
            f'{self.base_url}/organizations',
            json=org_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

# Usage
def quick_start():
    api = RecallerAPI()
    
    try:
        # Register new user
        user = api.register({
            'email': 'demo@example.com',
            'full_name': 'Demo User',
            'password': 'demopassword123'
        })
        print('User registered:', user['email'])

        # Login
        tokens = api.login('demo@example.com', 'demopassword123')
        print('Login successful')

        # Get current user
        current_user = api.get_current_user()
        print('Current user:', current_user['full_name'])

        # Create organization
        org = api.create_organization({
            'name': 'My First Organization',
            'organization_type': 'company',
            'industry': 'Technology'
        })
        print('Organization created:', org['name'])

    except requests.RequestException as e:
        print('Error:', e)

if __name__ == '__main__':
    quick_start()
```

## Common Workflows

### 1. User Registration & Profile Setup

```bash
# 1. Register
curl -X POST "${RECALLER_API_URL}/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'

# 2. Login
export ACCESS_TOKEN=$(curl -s -X POST "${RECALLER_API_URL}/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123" \
  | jq -r '.access_token')

# 3. Update profile
curl -X PUT "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Updated Doe"}'
```

### 2. Organization Management

```bash
# Create organization
ORG_ID=$(curl -s -X POST "${RECALLER_API_URL}/organizations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Startup Inc.",
    "organization_type": "company",
    "industry": "Technology",
    "size_category": "startup"
  }' | jq -r '.id')

# Add location
curl -X POST "${RECALLER_API_URL}/organizations/${ORG_ID}/locations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "location_name": "Headquarters",
    "address_city": "San Francisco",
    "address_state": "California",
    "is_primary": true
  }'

# Add alias
curl -X POST "${RECALLER_API_URL}/organizations/${ORG_ID}/aliases" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "alias_name": "TechStart",
    "alias_type": "abbreviation"
  }'
```

### 3. Data Browsing

```bash
# Browse organizations with filters
curl -X GET "${RECALLER_API_URL}/organizations?organization_type=company&industry=Technology&page=1&per_page=5" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"

# Search organizations
curl -X GET "${RECALLER_API_URL}/organizations/search?query=tech&limit=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"

# Get analytics overview
curl -X GET "${RECALLER_API_URL}/analytics/overview" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

## Next Steps

### 1. Explore Interactive Documentation

Visit `http://localhost:8000/docs` to:
- Browse all available endpoints
- Test API calls directly in your browser
- View request/response schemas
- Copy working code examples

### 2. Read Detailed Guides

- [Authentication Guide](./guides/authentication.md) - Complete auth implementation
- [Error Handling](./guides/error-handling.md) - Robust error management
- [Multi-tenancy Guide](./guides/multi-tenancy.md) - Multi-tenant patterns

### 3. Check Code Examples

- [cURL Examples](./examples/curl.md) - Command-line usage
- [JavaScript Examples](./examples/javascript.md) - Frontend integration
- [Python Examples](./examples/python.md) - Backend integration

### 4. Understand Data Models

- [Request Schemas](./schemas/requests.md) - Input data models
- [Response Schemas](./schemas/responses.md) - Output data models

## Support

### Getting Help

1. **Interactive Docs**: Test endpoints at `/docs`
2. **Error Messages**: Check response details for specific guidance
3. **Status Codes**: Use HTTP status codes for debugging
4. **Examples**: Reference provided code examples

### Common Issues

**Authentication Problems:**
- Ensure token is included in Authorization header
- Check token hasn't expired (30 minutes default)
- Verify proper "Bearer " prefix

**Validation Errors:**
- Check required fields are provided
- Validate data types and formats
- Review field length constraints

**Permission Issues:**
- Ensure user account is active
- Check user has appropriate permissions
- Verify tenant context if applicable

---

**Ready to dive deeper?** Check out the [complete API documentation](./README.md) for comprehensive information about all endpoints and features.