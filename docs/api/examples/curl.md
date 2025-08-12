# cURL Examples

This document provides comprehensive cURL examples for interacting with the Recaller API. All examples include complete commands with proper headers and error handling.

## Prerequisites

Before running these examples:

1. **Set Base URL**: Replace `http://localhost:8000` with your actual API base URL
2. **Obtain Token**: Use the login example to get an access token
3. **Set Variables**: Use environment variables for easier testing

### Environment Setup

```bash
# Set base URL
export RECALLER_API_URL="http://localhost:8000/api/v1"

# Set these after login
export ACCESS_TOKEN="your-jwt-token-here"
export TENANT_ID="your-tenant-id"  # Optional for multi-tenant setups
```

## Authentication

### User Registration

Create a new user account:

```bash
curl -X POST "${RECALLER_API_URL}/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "full_name": "John Doe",
    "password": "securepassword123"
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

**Expected Response (201):**
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

### User Login

Authenticate and get access token:

```bash
curl -X POST "${RECALLER_API_URL}/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser@example.com&password=securepassword123" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Extract Token for Future Use:**
```bash
# Store token in environment variable
export ACCESS_TOKEN=$(curl -s -X POST "${RECALLER_API_URL}/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser@example.com&password=securepassword123" \
  | jq -r '.access_token')

echo "Token stored: ${ACCESS_TOKEN:0:20}..."
```

## User Management

### Get Current User Profile

```bash
curl -X GET "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Update Current User Profile

```bash
curl -X PUT "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated Doe",
    "email": "john.updated@example.com"
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Change Password

```bash
curl -X PUT "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "newsecurepassword456"
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### List Users (with Pagination)

```bash
curl -X GET "${RECALLER_API_URL}/users?skip=0&limit=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Get Specific User by ID

```bash
curl -X GET "${RECALLER_API_URL}/users/123" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

## Organization Management

### List Organizations

Basic listing:
```bash
curl -X GET "${RECALLER_API_URL}/organizations?page=1&per_page=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

With filters:
```bash
curl -X GET "${RECALLER_API_URL}/organizations?organization_type=company&industry=Technology&is_active=true" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Search Organizations

```bash
curl -X GET "${RECALLER_API_URL}/organizations/search?query=tech&limit=5" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Create Organization

```bash
curl -X POST "${RECALLER_API_URL}/organizations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technology Corporation Inc.",
    "short_name": "TechCorp",
    "organization_type": "company",
    "industry": "Technology",
    "size_category": "large",
    "website": "https://www.techcorp.com",
    "email": "info@techcorp.com",
    "phone": "+1-800-555-0123",
    "address_street": "456 Innovation Drive",
    "address_city": "Palo Alto",
    "address_state": "California",
    "address_postal_code": "94301",
    "address_country_code": "US",
    "founded_year": 2010,
    "description": "A leading technology company specializing in innovative software solutions.",
    "employee_count": 5000
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Get Organization Details

```bash
curl -X GET "${RECALLER_API_URL}/organizations/456" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Update Organization

```bash
curl -X PUT "${RECALLER_API_URL}/organizations/456" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated: A leading technology company with expanded services.",
    "employee_count": 5500,
    "website": "https://www.newtechcorp.com"
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Delete Organization

```bash
curl -X DELETE "${RECALLER_API_URL}/organizations/456" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Organization Locations

Add location:
```bash
curl -X POST "${RECALLER_API_URL}/organizations/456/locations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "location_name": "San Francisco Office",
    "location_type": "branch",
    "address_street": "123 Market Street, Suite 456",
    "address_city": "San Francisco",
    "address_state": "California",
    "address_postal_code": "94105",
    "address_country_code": "US",
    "phone": "+1-415-555-0123",
    "email": "sf@techcorp.com",
    "employee_count": 150,
    "is_primary": false
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

List locations:
```bash
curl -X GET "${RECALLER_API_URL}/organizations/456/locations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Organization Aliases

Add alias:
```bash
curl -X POST "${RECALLER_API_URL}/organizations/456/aliases" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "alias_name": "TechCorp",
    "alias_type": "abbreviation"
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

## Social Groups

### List Social Groups

```bash
curl -X GET "${RECALLER_API_URL}/social-groups?skip=0&limit=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Search Social Groups

```bash
curl -X GET "${RECALLER_API_URL}/social-groups/search?query=book%20club" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Create Social Group

```bash
curl -X POST "${RECALLER_API_URL}/social-groups" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Book Club",
    "description": "A group for discussing technology books and trends",
    "group_type": "hobby",
    "is_active": true
  }' \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

## Analytics

### Get Analytics Overview

```bash
curl -X GET "${RECALLER_API_URL}/analytics/overview" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Get Network Analytics

```bash
curl -X GET "${RECALLER_API_URL}/analytics/network/overview" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Get Interaction Analytics

```bash
curl -X GET "${RECALLER_API_URL}/analytics/interactions/overview" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

## Configuration

### List Configuration Categories

```bash
curl -X GET "${RECALLER_API_URL}/config/categories" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

### Get Configuration Types

```bash
curl -X GET "${RECALLER_API_URL}/config/types" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

## Advanced Examples

### Batch Operations with JSON File

Create organizations from file:
```bash
# organizations.json
[
  {
    "name": "Company A",
    "organization_type": "company",
    "industry": "Technology"
  },
  {
    "name": "Company B", 
    "organization_type": "company",
    "industry": "Healthcare"
  }
]

# Upload each organization
jq -c '.[]' organizations.json | while read org; do
  curl -X POST "${RECALLER_API_URL}/organizations" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$org" \
    -w "\nStatus: %{http_code}\n"
  sleep 1  # Rate limiting
done
```

### Error Handling with jq

```bash
# Check for errors and extract relevant information
response=$(curl -s -X GET "${RECALLER_API_URL}/organizations/999" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n%{http_code}")

# Split response and status code
status_code=$(echo "$response" | tail -n1)
json_response=$(echo "$response" | head -n -1)

if [ "$status_code" -eq 200 ]; then
  echo "Success:"
  echo "$json_response" | jq '.'
elif [ "$status_code" -eq 404 ]; then
  echo "Not found:"
  echo "$json_response" | jq -r '.detail'
else
  echo "Error ($status_code):"
  echo "$json_response" | jq '.'
fi
```

### Pagination Loop

```bash
# Fetch all organizations using pagination
page=1
per_page=10
total_fetched=0

while true; do
  echo "Fetching page $page..."
  
  response=$(curl -s -X GET "${RECALLER_API_URL}/organizations?page=$page&per_page=$per_page" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json")
  
  # Check if response contains data
  data_count=$(echo "$response" | jq '.data | length')
  total=$(echo "$response" | jq '.pagination.total')
  
  if [ "$data_count" -eq 0 ]; then
    echo "No more data found"
    break
  fi
  
  echo "Found $data_count organizations on page $page"
  echo "$response" | jq '.data[].name'
  
  total_fetched=$((total_fetched + data_count))
  
  if [ "$total_fetched" -ge "$total" ]; then
    echo "All $total organizations fetched"
    break
  fi
  
  page=$((page + 1))
done
```

### Multi-tenant Requests

```bash
# Set tenant context
export TENANT_ID="tenant-123"

curl -X GET "${RECALLER_API_URL}/organizations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "X-Tenant-ID: ${TENANT_ID}" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

## Testing & Debugging

### Verbose Output

```bash
# Enable verbose output for debugging
curl -v -X GET "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Timing Information

```bash
# Get detailed timing information
curl -X GET "${RECALLER_API_URL}/organizations" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nTiming:\n--------\nDNS Lookup: %{time_namelookup}s\nConnect: %{time_connect}s\nSSL: %{time_appconnect}s\nPre-transfer: %{time_pretransfer}s\nRedirect: %{time_redirect}s\nStart Transfer: %{time_starttransfer}s\nTotal: %{time_total}s\nHTTP Code: %{http_code}\n"
```

### Save Response Headers

```bash
# Save response headers to file
curl -X GET "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -D response_headers.txt \
  -o response_body.json

echo "Headers saved to response_headers.txt"
echo "Body saved to response_body.json"
```

## Common Issues & Solutions

### Token Expired
```bash
# Check if token is expired
if curl -s -X GET "${RECALLER_API_URL}/users/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | grep -q "Not authenticated"; then
  echo "Token expired, please login again"
  # Re-run login command
fi
```

### Rate Limiting
```bash
# Add delays between requests
for i in {1..5}; do
  curl -X GET "${RECALLER_API_URL}/organizations?page=$i" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}"
  sleep 1  # Wait 1 second between requests
done
```

### JSON Validation
```bash
# Validate JSON before sending
json_data='{
  "name": "Test Organization",
  "organization_type": "company"
}'

if echo "$json_data" | jq . > /dev/null 2>&1; then
  echo "JSON is valid"
  curl -X POST "${RECALLER_API_URL}/organizations" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$json_data"
else
  echo "Invalid JSON format"
fi
```

---

**Related Documentation:**
- [Authentication Guide](../guides/authentication.md) - Authentication implementation
- [Error Handling](../guides/error-handling.md) - Error management
- [API Endpoints](../endpoints/) - Detailed endpoint documentation