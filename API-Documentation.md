# API Documentation

Recaller provides a comprehensive REST API built with FastAPI, offering complete access to all financial management, task management, and personal assistant features. This documentation covers API endpoints, authentication, and usage examples.

## 🔗 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.your-domain.com`
- **API Version**: `v1` (all endpoints prefixed with `/api/v1/`)

## 📖 Interactive Documentation

Recaller automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔐 Authentication

### JWT Token Authentication

Recaller uses JWT (JSON Web Tokens) for authentication with access and refresh token mechanism.

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Using Tokens
Include the access token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Multi-Tenant Headers

For multi-tenant deployments, include the tenant ID in requests:

```http
X-Tenant-ID: default
```

## 💰 Financial Management API

### Transactions

#### Create Transaction
```http
POST /api/v1/transactions/
Content-Type: application/json
Authorization: Bearer <token>

{
  "type": "debit",
  "amount": 150.00,
  "currency": "USD",
  "description": "Grocery shopping",
  "transaction_date": "2025-08-13",
  "category_id": 1,
  "subcategory_id": 3,
  "account_id": 2,
  "metadata": {
    "location": "Whole Foods",
    "payment_method": "credit_card"
  }
}
```

#### List Transactions with Filtering
```http
GET /api/v1/transactions/?skip=0&limit=50&type=debit&date_from=2025-08-01&date_to=2025-08-31&category_id=1&search=grocery
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 123,
    "type": "debit",
    "amount": 150.00,
    "currency": "USD",
    "description": "Grocery shopping",
    "transaction_date": "2025-08-13",
    "category": {
      "id": 1,
      "name": "Food & Dining",
      "color": "#FF6B6B"
    },
    "subcategory": {
      "id": 3,
      "name": "Groceries"
    },
    "account": {
      "id": 2,
      "name": "Chase Credit Card",
      "account_type": "credit_card"
    },
    "is_recurring": false,
    "metadata": {
      "location": "Whole Foods",
      "payment_method": "credit_card"
    },
    "created_at": "2025-08-13T10:30:00Z",
    "updated_at": "2025-08-13T10:30:00Z"
  }
]
```

#### Get Monthly Summary
```http
GET /api/v1/transactions/summary/monthly?year=2025&month=8
Authorization: Bearer <token>
```

**Response:**
```json
{
  "year": 2025,
  "month": 8,
  "total_income": 5000.00,
  "total_expenses": 3200.00,
  "net_income": 1800.00,
  "transaction_count": 45,
  "category_breakdown": [
    {
      "category_name": "Food & Dining",
      "amount": 650.00,
      "percentage": 20.3
    }
  ]
}
```

#### Bulk Create Transactions
```http
POST /api/v1/transactions/bulk
Content-Type: application/json
Authorization: Bearer <token>

[
  {
    "type": "debit",
    "amount": 50.00,
    "description": "Coffee",
    "transaction_date": "2025-08-13",
    "category_id": 1
  },
  {
    "type": "credit",
    "amount": 5000.00,
    "description": "Salary",
    "transaction_date": "2025-08-01",
    "category_id": 5
  }
]
```

### Financial Accounts

#### Create Account
```http
POST /api/v1/financial-accounts/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Chase Checking",
  "account_type": "bank",
  "bank_name": "Chase Bank",
  "current_balance": 2500.00,
  "currency": "USD",
  "metadata": {
    "routing_number": "021000021",
    "account_features": ["online_banking", "mobile_deposit"]
  }
}
```

#### List Accounts with Summaries
```http
GET /api/v1/financial-accounts/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Chase Checking",
    "account_type": "bank",
    "bank_name": "Chase Bank",
    "current_balance": 2500.00,
    "currency": "USD",
    "is_active": true,
    "transaction_count_last_30_days": 25,
    "total_inflows_last_30_days": 5000.00,
    "total_outflows_last_30_days": 2500.00,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Recurring Transactions

#### Create Recurring Transaction
```http
POST /api/v1/recurring-transactions/
Content-Type: application/json
Authorization: Bearer <token>

{
  "type": "debit",
  "amount": 1200.00,
  "currency": "USD",
  "description": "Rent Payment",
  "frequency": "monthly",
  "interval_count": 1,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "category_id": 2,
  "account_id": 1,
  "metadata": {
    "landlord": "Property Management Co",
    "property_address": "123 Main St"
  }
}
```

#### Get Due Reminders
```http
GET /api/v1/recurring-transactions/due-reminders?days_ahead=7
Authorization: Bearer <token>
```

#### Process Due Recurring Transactions
```http
POST /api/v1/recurring-transactions/process-all-due
Authorization: Bearer <token>
```

### Budgets

#### Create Budget
```http
POST /api/v1/budgets/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Monthly Food Budget",
  "category_id": 1,
  "amount": 800.00,
  "currency": "USD",
  "period": "monthly",
  "start_date": "2025-08-01",
  "end_date": "2025-08-31",
  "alert_threshold": 0.8
}
```

#### Get Budget Alerts
```http
GET /api/v1/budgets/alerts
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "budget_id": 1,
    "budget_name": "Monthly Food Budget",
    "budgeted_amount": 800.00,
    "spent_amount": 720.00,
    "percentage_used": 0.9,
    "alert_type": "over_threshold",
    "days_remaining": 18
  }
]
```

### Financial Analytics

#### Dashboard Summary
```http
GET /api/v1/financial-analytics/dashboard-summary
Authorization: Bearer <token>
```

**Response:**
```json
{
  "current_month": {
    "total_income": 5000.00,
    "total_expenses": 3200.00,
    "net_income": 1800.00
  },
  "account_balances": {
    "total_balance": 15000.00,
    "by_account_type": {
      "bank": 8000.00,
      "credit_card": -2000.00,
      "investment": 9000.00
    }
  },
  "upcoming_recurring": [
    {
      "description": "Rent Payment",
      "amount": 1200.00,
      "due_date": "2025-09-01"
    }
  ],
  "budget_alerts": 2,
  "recent_transactions": 15
}
```

#### Cash Flow Analysis
```http
GET /api/v1/financial-analytics/cash-flow?months=6
Authorization: Bearer <token>
```

#### Spending Trends
```http
GET /api/v1/financial-analytics/spending-trends?period=monthly&months=12
Authorization: Bearer <token>
```

## 📋 Task Management API

### Tasks

#### Create Task
```http
POST /api/v1/tasks/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Buy groceries",
  "description": "Get items for weekly meal prep",
  "due_date": "2025-08-15",
  "priority": "medium",
  "category_id": 1,
  "tags": ["shopping", "food"],
  "metadata": {
    "shopping_list": ["milk", "bread", "eggs"]
  }
}
```

#### List Tasks with Filtering
```http
GET /api/v1/tasks/?status=pending&priority=high&due_date_from=2025-08-13&due_date_to=2025-08-20
Authorization: Bearer <token>
```

### Task Categories

#### Create Task Category
```http
POST /api/v1/task-categories/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Personal",
  "description": "Personal tasks and reminders",
  "color": "#4ECDC4",
  "icon": "user"
}
```

## 👥 Contact Management API

### Contacts

#### Create Contact
```http
POST /api/v1/contacts/
Content-Type: application/json
Authorization: Bearer <token>

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567",
  "relationship": "friend",
  "tags": ["college", "tech"],
  "metadata": {
    "birthday": "1990-05-15",
    "company": "Tech Corp",
    "notes": "Met at conference 2023"
  }
}
```

## ⚙️ Background Tasks API

### Task Management

#### Trigger Recurring Transaction Processing
```http
POST /api/v1/background-tasks/recurring-transactions/process?dry_run=false
Authorization: Bearer <token>
```

#### Send Reminders
```http
POST /api/v1/background-tasks/recurring-transactions/send-reminders
Authorization: Bearer <token>
```

#### Check Task Status
```http
GET /api/v1/background-tasks/tasks/{task_id}/status
Authorization: Bearer <token>
```

## 📊 Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "amount": ["Amount must be greater than 0"],
    "email": ["Invalid email format"]
  },
  "timestamp": "2025-08-13T10:30:00Z"
}
```

### Common HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## 🔄 Pagination

List endpoints support pagination with standard parameters:

```http
GET /api/v1/transactions/?skip=0&limit=50
```

**Response includes pagination metadata:**
```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 50,
  "has_next": true,
  "has_previous": false
}
```

## 🎯 Rate Limiting

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour
- **Rate limit headers** included in responses:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 999
  X-RateLimit-Reset: 1692024000
  ```

## 📝 Request/Response Examples

### cURL Examples

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Create transaction
curl -X POST "http://localhost:8000/api/v1/transactions/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "type": "debit",
    "amount": 50.00,
    "description": "Coffee",
    "transaction_date": "2025-08-13"
  }'

# Get transactions
curl -X GET "http://localhost:8000/api/v1/transactions/?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### JavaScript/Axios Examples

```javascript
// API client setup
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Create transaction
const createTransaction = async (transactionData) => {
  try {
    const response = await api.post('/transactions/', transactionData);
    return response.data;
  } catch (error) {
    console.error('Error creating transaction:', error.response.data);
    throw error;
  }
};

// Get transactions
const getTransactions = async (filters = {}) => {
  try {
    const response = await api.get('/transactions/', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Error fetching transactions:', error.response.data);
    throw error;
  }
};
```

### Python/Requests Examples

```python
import requests

# API client class
class RecallerAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def login(self, email, password):
        response = self.session.post(f"{self.base_url}/auth/login", 
                                   json={"email": email, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        return response.json()
    
    def create_transaction(self, transaction_data):
        response = self.session.post(f"{self.base_url}/transactions/", 
                                   json=transaction_data)
        return response.json()
    
    def get_transactions(self, **filters):
        response = self.session.get(f"{self.base_url}/transactions/", 
                                  params=filters)
        return response.json()

# Usage
api = RecallerAPI()
api.login("user@example.com", "password")

# Create transaction
transaction = api.create_transaction({
    "type": "debit",
    "amount": 150.00,
    "description": "Grocery shopping",
    "transaction_date": "2025-08-13"
})

# Get transactions
transactions = api.get_transactions(limit=50, type="debit")
```

## 🔍 API Testing

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" and enter your bearer token
3. Expand any endpoint section
4. Click "Try it out"
5. Fill in parameters and request body
6. Click "Execute" to test the endpoint

### Postman Collection

A Postman collection is available for easy API testing:

1. Import the collection from `/docs/postman/Recaller-API.postman_collection.json`
2. Set up environment variables for base URL and tokens
3. Run individual requests or entire collections

---

*For more detailed examples and advanced usage, see the [GitHub repository](https://github.com/Nexlified/Recaller) and [interactive documentation](http://localhost:8000/docs).*