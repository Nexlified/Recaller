# System Architecture

Recaller follows a modern, scalable architecture designed for privacy, multi-tenancy, and extensibility. This document outlines the high-level system design and component interactions.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  React 19 + TypeScript + Tailwind CSS + Headless UI           │
│  • Financial Dashboard  • Task Management  • Contact Mgmt      │
│  • Budget Tracking     • Analytics       • AI Features        │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST API
┌─────────────────────────▼───────────────────────────────────────┐
│                       API Gateway Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI (Python) + Pydantic + OpenAPI                       │
│  • Authentication      • Rate Limiting    • CORS             │
│  • Request Validation  • Error Handling   • Documentation     │
└─────────────────────────┬───────────────────────┬───────────────┘
                          │                       │ MCP Protocol
                          │                       │
                          │               ┌───────▼───────┐
                          │               │   MCP Server   │
                          │               │  (Port 8001)   │
                          │               │ • Model Mgmt   │
                          │               │ • Inference    │
                          │               │ • AI Features  │
                          │               └───────┬───────┘
                          │                       │ Backend APIs
                          │                       │
                          │               ┌───────▼───────┐
                          │               │ LLM Backends   │
                          │               │ • Ollama       │
                          │               │ • HuggingFace  │
                          │               │ • OpenAI API   │
                          │               │ • Local Models │
                          │               └───────────────┘
                          │ Internal API Calls
┌─────────────────────────▼───────────────────────────────────────┐
│                      Business Logic Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Service Classes + Domain Logic                               │
│  • Financial Service   • Task Service     • User Service      │
│  • Analytics Service   • Notification Service                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Database Operations
┌─────────────────────────▼───────────────────────────────────────┐
│                       Data Access Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM + Alembic Migrations                          │
│  • CRUD Operations     • Query Optimization                   │
│  • Relationship Management • Transaction Handling             │
└─────────────────────────┬───────────────────────────────────────┘
                          │ SQL Queries
┌─────────────────────────▼───────────────────────────────────────┐
│                       Database Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL 15 + Redis 7                                      │
│  • Multi-tenant data   • Session storage   • Task queue       │
│  • ACID compliance     • Backup & recovery                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Background Processing                        │
├─────────────────────────────────────────────────────────────────┤
│  Celery + Redis + Flower                                      │
│  • Recurring transactions  • Email notifications              │
│  • Analytics computation   • Data cleanup                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### Frontend Layer (React + TypeScript)

**Technology Stack:**
- React 19+ with functional components and hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Headless UI for accessible components
- Axios for HTTP communication
- React Router for navigation

**Key Modules:**
- **Financial Dashboard**: Transaction management, budget tracking, analytics
- **Task Management**: To-dos, reminders, recurring tasks
- **Contact Management**: Personal and professional contacts
- **Analytics & Reporting**: Charts, trends, insights
- **Settings & Configuration**: User preferences, account settings

### API Gateway Layer (FastAPI)

**Technology Stack:**
- FastAPI framework with async/await support
- Pydantic for request/response validation
- OpenAPI/Swagger for documentation
- JWT authentication with refresh tokens
- CORS middleware for frontend communication

**Key Features:**
- **Multi-tenant middleware**: Automatic tenant context injection
- **Authentication**: JWT-based with role-based access control
- **Request validation**: Automatic input validation and sanitization
- **Error handling**: Consistent error responses and logging
- **Rate limiting**: API rate limiting to prevent abuse
- **API documentation**: Auto-generated OpenAPI documentation

### Business Logic Layer (Services)

**Service Architecture:**
```python
# Example service structure
class FinancialService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_crud = crud.transaction
        self.account_crud = crud.financial_account
    
    def create_transaction(self, user_id: int, tenant_id: int, data: TransactionCreate):
        # Business logic for transaction creation
        # Account balance updates
        # Validation rules
        # Audit logging
```

**Key Services:**
- **Financial Service**: Transaction processing, account management, budget tracking
- **Recurring Transaction Service**: Automated payment processing
- **Analytics Service**: Financial insights and reporting
- **Notification Service**: Email and in-app notifications
- **User Service**: User management and preferences
- **Task Service**: Task and reminder management

### Data Access Layer (SQLAlchemy ORM)

**Technology Stack:**
- SQLAlchemy Core and ORM
- Alembic for database migrations
- Connection pooling and query optimization
- Relationship management with lazy loading

**CRUD Pattern:**
```python
# Example CRUD implementation
class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    def get_by_user(
        self, 
        db: Session, 
        user_id: int, 
        tenant_id: int, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[Transaction]:
        # Multi-tenant filtered queries
        # Advanced filtering and sorting
        # Pagination support
```

### Database Layer (PostgreSQL + Redis)

**PostgreSQL Database:**
- **Primary storage**: All persistent data
- **Multi-tenant isolation**: Tenant-based data separation
- **ACID compliance**: Data consistency and reliability
- **Indexing strategy**: Optimized for query performance
- **Backup & recovery**: Regular backups and point-in-time recovery

**Redis Cache:**
- **Session storage**: User sessions and authentication tokens
- **Task queue**: Celery task management
- **Caching layer**: Frequently accessed data
- **Rate limiting**: API rate limit counters

### Background Processing (Celery)

**Task Categories:**
- **Recurring Transactions**: Daily processing of due payments
- **Email Notifications**: Reminder emails and alerts
- **Analytics Computation**: Financial insights and reporting
- **Data Maintenance**: Cleanup and optimization tasks

**Configuration:**
```python
# Celery beat schedule
beat_schedule = {
    'process-recurring-transactions': {
        'task': 'app.services.background_tasks.process_all_recurring_transactions',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
    'send-recurring-reminders': {
        'task': 'app.services.background_tasks.send_recurring_transaction_reminders',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
}
```

### AI/LLM Integration Layer (MCP Server)

**Technology Stack:**
- Model Context Protocol (MCP) v1 implementation
- FastAPI server with async processing (Port 8001)
- Multi-backend model support (Ollama, HuggingFace, OpenAI-compatible)
- Privacy-first on-device processing

**Key Features:**
- **Model management**: Registration, discovery, and lifecycle management
- **Inference processing**: Text completion, chat, embeddings
- **Tenant isolation**: Secure multi-tenant AI processing
- **Privacy protection**: On-device processing with zero-retention options
- **Backend abstraction**: Pluggable model backend architecture
- **Health monitoring**: Model availability and performance tracking

**Service Architecture:**
```python
# MCP Server integration
class AIService:
    async def get_financial_insights(self, user_context, query):
        response = await mcp_client.inference.chat(
            model_id="local_llama",
            messages=[{"role": "user", "content": query}],
            tenant_id=user_context.tenant_id
        )
        return response.message.content
```

## 🏢 Multi-Tenant Architecture

### Tenant Isolation Strategy

**Database Level:**
- Every table includes `tenant_id` foreign key
- All queries automatically filtered by tenant
- Cross-tenant data access prevention

**API Level:**
- Tenant context injected via middleware
- Request headers validate tenant access
- Response data filtered by tenant

**Background Tasks:**
- Tenant-aware processing
- Isolated task execution
- Tenant-specific configurations

### Tenant Middleware Flow

```python
# Tenant middleware implementation
class TenantMiddleware:
    async def __call__(self, request: Request, call_next):
        # Extract tenant from header or user context
        tenant_id = self.get_tenant_from_request(request)
        
        # Validate tenant access
        if not self.validate_tenant_access(request.user, tenant_id):
            raise HTTPException(status_code=403, detail="Tenant access denied")
        
        # Inject tenant into request state
        request.state.tenant = tenant
        
        # Process request
        response = await call_next(request)
        return response
```

## 🔐 Security Architecture

### Authentication & Authorization

**JWT Token Flow:**
1. User login with credentials
2. Server validates and issues JWT access token + refresh token
3. Client includes access token in API requests
4. Server validates token and extracts user/tenant context
5. Refresh token used to obtain new access tokens

**Role-Based Access Control:**
- **User**: Standard user with access to own data
- **Admin**: Tenant administrator with user management capabilities
- **Super Admin**: System administrator with cross-tenant access

### Data Protection

**Encryption:**
- Sensitive data encrypted at rest (account numbers, personal info)
- TLS/HTTPS for data in transit
- Environment variables for secrets management

**Privacy Measures:**
- No third-party data sharing
- On-device AI processing
- User data ownership and control
- GDPR compliance ready

## 📊 Data Flow Architecture

### Transaction Processing Flow

```
User Input → Frontend Validation → API Request → Authentication Check 
    ↓
Tenant Validation → Business Logic → Database Update → Account Balance Update
    ↓
Response Generation → Frontend Update → Background Task Trigger (if needed)
```

### Recurring Transaction Flow

```
Scheduled Task → Fetch Due Transactions → Validate Business Rules
    ↓
Generate Transactions → Update Account Balances → Send Notifications
    ↓
Update Next Due Dates → Log Processing Results → Error Handling
```

## 🚀 Scalability Considerations

### Horizontal Scaling

**Application Layer:**
- Stateless API servers for load balancing
- Container orchestration with Docker Swarm/Kubernetes
- Microservices architecture for independent scaling

**Database Layer:**
- Read replicas for query performance
- Connection pooling and query optimization
- Tenant-based sharding strategy

**Background Processing:**
- Multiple Celery workers for parallel processing
- Queue prioritization for critical tasks
- Auto-scaling based on queue length

### Performance Optimization

**Database Optimization:**
- Strategic indexing on frequently queried columns
- Query optimization and N+1 problem prevention
- Connection pooling and prepared statements

**Caching Strategy:**
- Redis for session and frequently accessed data
- Application-level caching for expensive computations
- CDN for static assets

**API Optimization:**
- Response pagination for large datasets
- Field selection to reduce payload size
- Compression for API responses

## 🔄 Development Workflow

### Environment Setup

```yaml
# docker-compose.yml structure
services:
  backend:          # FastAPI application
  frontend:         # React application
  db:              # PostgreSQL database
  redis:           # Redis cache
  celery_worker:   # Background task worker
  celery_beat:     # Task scheduler
  celery_flower:   # Task monitoring
```

### CI/CD Pipeline

**Development Flow:**
1. Feature development in feature branches
2. Automated testing (unit, integration, end-to-end)
3. Code review and quality checks
4. Merge to main branch
5. Automated deployment to staging
6. Manual approval for production deployment

**Testing Strategy:**
- **Unit Tests**: Individual component testing
- **Integration Tests**: API and database integration
- **End-to-End Tests**: Complete user workflow testing
- **Performance Tests**: Load and stress testing

## 📈 Monitoring & Observability

### Application Monitoring

**Metrics Collection:**
- API response times and error rates
- Database query performance
- Background task success/failure rates
- User activity and feature usage

**Logging Strategy:**
- Structured logging with correlation IDs
- Error tracking and alerting
- Audit trails for financial transactions
- Performance profiling

**Health Checks:**
- API endpoint health monitoring
- Database connection health
- Background task processing status
- External service dependencies

---

*This architecture supports Recaller's core principles of privacy, security, and user control while providing a foundation for scalable growth.*