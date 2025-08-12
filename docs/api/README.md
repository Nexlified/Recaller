# Recaller API Documentation

Welcome to the comprehensive API documentation for Recaller, a privacy-first personal assistant application.

## Overview

The Recaller API is built with FastAPI and provides a complete REST API for managing personal relationships, organizations, social activities, and analytics. The API follows OpenAPI 3.1.0 standards and includes automatic interactive documentation.

## Base URL

```
Production: https://api.recaller.com/api/v1
Development: http://localhost:8000/api/v1
```

## Quick Start

1. **Authentication**: Obtain an access token using the `/login` endpoint
2. **Authorization**: Include the token in the `Authorization` header: `Bearer <token>`
3. **Tenant Context**: Include tenant ID in `X-Tenant-ID` header (if applicable)
4. **Make Requests**: Use the token to access protected endpoints

### Example Authentication Flow

```bash
# 1. Login to get access token
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# 2. Use token for API requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## API Features

### 🔐 Authentication & Security
- **JWT Token-based authentication**
- **OAuth2 compatible login flow**
- **Secure password hashing with bcrypt**
- **Token expiration and refresh**
- **Multi-tenant access control**

### 👥 User Management
- **User registration and profile management**
- **Role-based access control**
- **Active/inactive user status**
- **Profile updates and password changes**

### 🏢 Organization Management
- **Comprehensive organization profiles**
- **Multiple locations per organization**
- **Organization aliases and alternate names**
- **Industry and size categorization**
- **Search and filtering capabilities**

### 👥 Social Groups & Activities
- **Social group creation and management**
- **Activity planning and tracking**
- **Membership management**
- **Attendance tracking**
- **Group type categorization**

### 📊 Analytics & Insights
- **Network growth tracking**
- **Relationship health metrics**
- **Interaction analytics**
- **Performance indicators**
- **Custom reporting**

### ⚙️ Configuration Management
- **System configuration categories**
- **Reference data management**
- **Hierarchical configuration values**
- **Search and filtering**

## Interactive Documentation

The API provides interactive documentation through Swagger UI:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

## API Reference

### Core Endpoints

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Authentication](./endpoints/auth.md) | `/login`, `/register` | User authentication and registration |
| [Users](./endpoints/users.md) | `/users/*` | User profile management |
| [Organizations](./endpoints/organizations.md) | `/organizations/*` | Organization management |
| [Social Groups](./endpoints/social-groups.md) | `/social-groups/*` | Social group management |
| [Activities](./endpoints/activities.md) | `/social-groups/*/activities/*` | Activity management |
| [Analytics](./endpoints/analytics.md) | `/analytics/*` | Analytics and reporting |
| [Configuration](./endpoints/configuration.md) | `/config/*` | Configuration management |

### Data Models

- [Request Schemas](./schemas/requests.md) - Input data models
- [Response Schemas](./schemas/responses.md) - Output data models

## Guides & Best Practices

- [Authentication Guide](./guides/authentication.md) - Complete auth implementation
- [Multi-tenancy Guide](./guides/multi-tenancy.md) - Tenant isolation patterns
- [Pagination Guide](./guides/pagination.md) - Efficient data browsing
- [Error Handling](./guides/error-handling.md) - Error management
- [Best Practices](./guides/best-practices.md) - API usage recommendations

## Code Examples

- [cURL Examples](./examples/curl.md) - Command-line usage
- [JavaScript/TypeScript](./examples/javascript.md) - Frontend integration
- [Python Examples](./examples/python.md) - Backend integration

## Support & Resources

- **Interactive Testing**: Use the Swagger UI at `/docs` for live API testing
- **Schema Validation**: All requests and responses are validated against OpenAPI schemas
- **Error Messages**: Comprehensive error responses with helpful details
- **Rate Limiting**: Fair usage policies to ensure service availability

## API Versioning

The current API version is `v1`. All endpoints are prefixed with `/api/v1`.

Future versions will maintain backward compatibility when possible. Breaking changes will result in a new version (e.g., `/api/v2`).

## Multi-Tenancy

Recaller supports multi-tenant architecture:

- **Tenant Isolation**: Data is isolated by tenant
- **Automatic Enforcement**: Middleware ensures tenant boundaries
- **Header-based**: Use `X-Tenant-ID` header for tenant selection
- **Default Tenant**: Single-tenant deployments use default tenant

## Getting Help

- **Interactive Docs**: Use Swagger UI for endpoint testing
- **Schema Reference**: Check OpenAPI schema for detailed specifications
- **Error Codes**: Refer to error handling guide for troubleshooting
- **Examples**: Use provided code examples as starting points

---

**Next Steps:**
- Review [Authentication Guide](./guides/authentication.md) for setup
- Explore [Interactive Documentation](http://localhost:8000/docs)
- Check out [Code Examples](./examples/) for your preferred language