# GitHub Copilot Instructions for Recaller

## Project Overview

**Recaller** is a privacy-first, open-source personal assistant app that helps users manage their finances, communications, social activities, belongings, and recurring payments. The application is powered by on-device/self-hosted AI and follows a multi-tenant architecture.

## Architecture

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication
- **API Version**: v1 at `/api/v1/`
- **Multi-tenancy**: Tenant-based isolation using middleware
- **Migrations**: Alembic for database schema management

### Frontend (Nextjs + TypeScript)
- **Framework**: Nextjs + with TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios for API communication
- **Routing**: Next.js built-in routing
- **UI Components**: Headless UI, Heroicons
- **Notifications**: React Hot Toast

### Development Environment
- **Containerization**: Docker Compose with services for backend, frontend, db
- **Database**: PostgreSQL 15
- **Backend Port**: 8000
- **Frontend Port**: 3000
- **Database Port**: 5432

## Multi-Tenancy & Access Control

### Tenant Model
- Users belong to tenants (organizations/groups)
- Tenant isolation is enforced at the database and API level
- Default tenant handling for single-tenant deployments
- Tenant identification via `X-Tenant-ID` header

### User Access Rights
- **Same Tenancy Access**: All users within the same tenant have equal access rights
- **Content Ownership**: Users can only manage their own content
- **No Admin Features**: Frontend is user-facing without administrative functionality
- **Self-Service**: Users manage their own data and settings

## Code Patterns & Conventions

### Backend Patterns

#### API Structure
```python
# API endpoints follow this pattern:
# /api/v1/{resource}/{action}
# Example: /api/v1/users/me, /api/v1/auth/login

# All endpoints should include tenant context
from fastapi import Depends, Request
from app.api.deps import get_current_user, get_db

@router.get("/")
async def get_items(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Access tenant via request.state.tenant
    tenant_id = request.state.tenant.id
```

#### Database Models
```python
# All models should inherit from Base and include tenant_id
from app.db.base_class import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    # ... other fields
```

#### CRUD Operations
```python
# CRUD operations should filter by tenant_id
def get_user_items(db: Session, user_id: int, tenant_id: int):
    return db.query(Model).filter(
        Model.user_id == user_id,
        Model.tenant_id == tenant_id
    ).all()
```

### Frontend Patterns

#### API Calls
```typescript
// Use axios for API calls with base URL configuration
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Always include tenant and auth headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  const tenantId = localStorage.getItem('tenantId') || 'default';
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  
  return config;
});
```

#### Component Structure
```typescript
// Components should be functional with TypeScript
import React from 'react';
import { User } from '../types/User';

interface UserProfileProps {
  user: User;
  onUpdate: (user: User) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ user, onUpdate }) => {
  // Component logic here
  return (
    <div className="bg-white shadow rounded-lg p-6">
      {/* User profile content */}
    </div>
  );
};
```

## Environment Configuration

### Backend Environment Variables
```bash
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=recaller
POSTGRES_PASSWORD=recaller
POSTGRES_DB=recaller
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
PROJECT_NAME=Recaller
VERSION=1.0.0
API_V1_STR=/api/v1
```

### Frontend Environment Variables
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
```

## Development Workflow

### Setup Commands
```bash
# Full stack development
docker-compose up --build

# Backend only
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend only
cd frontend
npm install
npm start
```

### Database Operations
```bash
# Run migrations
cd backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Security Considerations

- **JWT Tokens**: Use secure secret keys in production
- **CORS**: Configured for development; restrict in production
- **Tenant Isolation**: Always filter queries by tenant_id
- **User Data**: Users can only access their own data within their tenant
- **Environment Variables**: Use .env files for sensitive configuration

## Key Files and Directories

### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── api.py          # Main API router
│   │   │   └── endpoints/      # API endpoints
│   │   ├── deps.py             # Dependencies
│   │   └── middleware/
│   │       └── tenant.py       # Tenant middleware
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # Security utilities
│   ├── crud/                   # Database operations
│   ├── db/                     # Database setup
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/             # React components
│   ├── pages/                  # Page components
│   ├── services/               # API services
│   ├── types/                  # TypeScript types
│   └── utils/                  # Utility functions
├── public/                     # Static assets
└── package.json
```

## Coding Guidelines

1. **Type Safety**: Use TypeScript for frontend and Pydantic for backend
2. **Error Handling**: Implement proper error handling and user feedback
3. **Tenant Awareness**: Always consider tenant context in data operations
4. **User Privacy**: Ensure users can only access their own data
5. **Environment Config**: Use environment variables for configuration
6. **API Consistency**: Follow RESTful API conventions
7. **Component Reusability**: Create reusable UI components
8. **Database Integrity**: Use proper foreign keys and constraints
9. **Authentication**: Protect all API endpoints requiring user access
10. **Documentation**: Include inline comments for complex business logic

## Common Tasks

### Adding a New API Endpoint
1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Add to router in `backend/app/api/v1/api.py`
3. Ensure tenant filtering in database queries
4. Add corresponding frontend service call

### Adding a New Database Model
1. Create model in `backend/app/models/`
2. Include `tenant_id` foreign key
3. Create Pydantic schemas in `backend/app/schemas/`
4. Add CRUD operations in `backend/app/crud/`
5. Generate and run Alembic migration

### Adding a New Frontend Component
1. Create component in `frontend/src/components/`
2. Use TypeScript interfaces for props
3. Style with Tailwind CSS classes
4. Handle API calls with proper error handling
5. Include in routing if it's a page component

## Privacy & Self-Hosting

- **On-Device AI**: No user data sent to third-party AI services
- **Self-Hosted**: Designed for self-hosting and privacy
- **Open Source**: Extensible and community-driven
- **Data Ownership**: Users maintain full control of their data
- **Local Processing**: AI features run locally when possible