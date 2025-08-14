# MCP Server Architecture for Recaller

## Overview

The Model Context Protocol (MCP) server provides a standardized interface for Large Language Model (LLM) integration in Recaller. It implements MCP v1 protocol to enable secure, privacy-first connections with local or self-hosted LLMs while maintaining Recaller's multi-tenant architecture and privacy requirements.

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                     FastAPI Backend                            │
│                  (Recaller Main App)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP API / Internal Communication
┌─────────────────────────▼───────────────────────────────────────┐
│                       MCP Server                               │
├─────────────────────────────────────────────────────────────────┤
│  • Model Registry       • Inference Service                    │
│  • Protocol Handler     • Authentication                       │
│  • Tenant Isolation     • Health Monitoring                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP v1 Protocol
┌─────────────────────────▼───────────────────────────────────────┐
│                    Model Backends                              │
├─────────────────────────────────────────────────────────────────┤
│  • Ollama              • HuggingFace                           │
│  • OpenAI Compatible   • Local Models                          │
│  • Custom Backends     • Cloud APIs                            │
└─────────────────────────────────────────────────────────────────┘
```

### Service Boundaries

#### 1. **MCP Server Core** (`backend/mcp_server/`)
- **Responsibility**: MCP protocol implementation, request routing, and coordination
- **Key Components**:
  - Protocol handler for MCP v1 messages
  - Request/response lifecycle management
  - Error handling and validation
  - WebSocket/HTTP transport layers

#### 2. **Model Registry** (`backend/mcp_server/models/`)
- **Responsibility**: Model lifecycle management and discovery
- **Key Components**:
  - Model registration and configuration
  - Backend abstraction layer
  - Health monitoring and status tracking
  - Capability discovery and validation

#### 3. **Inference Service** (`backend/mcp_server/services/`)
- **Responsibility**: Request processing and inference coordination
- **Key Components**:
  - Rate limiting and resource management
  - Context validation and preprocessing
  - Backend-specific inference handling
  - Response formatting and post-processing

#### 4. **Authentication & Authorization** (`backend/mcp_server/services/auth.py`)
- **Responsibility**: Security and tenant isolation
- **Key Components**:
  - Tenant verification and context injection
  - API access control and permissions
  - Integration with main backend authentication
  - Privacy and security enforcement

#### 5. **Configuration Management** (`backend/mcp_server/config/`)
- **Responsibility**: Settings and configuration management
- **Key Components**:
  - Environment-based configuration
  - Model backend configurations
  - Security and privacy settings
  - Resource limits and constraints

## Directory Structure

```
backend/mcp_server/
├── __init__.py                 # Package initialization
├── main.py                     # FastAPI application and server startup
├── requirements.txt            # MCP server specific dependencies
├── Dockerfile                  # Container configuration
├── .env.example               # Environment configuration template
│
├── core/                      # Core MCP protocol implementation
│   ├── __init__.py
│   └── protocol.py            # MCP v1 protocol handler and server
│
├── models/                    # Model management and backends
│   ├── __init__.py
│   └── registry.py           # Model registry and backend abstractions
│
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── inference.py          # Inference processing service
│   └── auth.py               # Authentication and authorization
│
├── api/                       # REST API endpoints
│   ├── __init__.py
│   └── endpoints.py          # API route definitions
│
├── schemas/                   # Data models and validation
│   ├── __init__.py
│   └── mcp_schemas.py        # Pydantic schemas for MCP protocol
│
└── config/                    # Configuration management
    ├── __init__.py
    ├── settings.py           # Application settings
    └── models.example.json   # Example model configurations
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Framework**: FastAPI (async/await support)
- **Protocol**: MCP v1 (Model Context Protocol)
- **Transport**: WebSocket and HTTP
- **Validation**: Pydantic schemas
- **Documentation**: OpenAPI/Swagger

### Model Backend Support
- **Ollama**: Local LLM deployment platform
- **HuggingFace**: Transformers and model hub integration
- **OpenAI Compatible**: APIs following OpenAI format
- **Local Models**: Direct PyTorch/TensorFlow integration
- **Custom Backends**: Extensible backend architecture

### Integration Technologies
- **HTTP Client**: httpx for async backend communication
- **WebSockets**: websockets library for MCP protocol
- **Authentication**: JWT integration with main backend
- **Monitoring**: Built-in health checks and metrics

## Integration Points

### 1. **FastAPI Backend Integration**
- **Authentication**: Shares authentication context with main backend
- **Tenant Context**: Inherits tenant isolation from main application
- **Configuration**: Integrated configuration management
- **Monitoring**: Shared health check and monitoring infrastructure

### 2. **LLM Model Integration**
- **Protocol Standardization**: MCP v1 for consistent communication
- **Backend Abstraction**: Pluggable backend architecture
- **Capability Discovery**: Automatic detection of model capabilities
- **Health Monitoring**: Continuous model availability checks

### 3. **Database Integration**
- **Model Registry**: Persistent model configuration storage
- **Tenant Data**: Respects existing tenant isolation
- **Configuration**: Shared database for model metadata
- **Audit Logs**: Optional request/response logging

## Security and Privacy Features

### Tenant Isolation
- **Request Context**: All requests include tenant identification
- **Data Separation**: No cross-tenant data access
- **Model Access**: Tenant-specific model permissions
- **Resource Limits**: Per-tenant rate limiting and quotas

### Privacy Protection
- **On-Device Processing**: Local model execution preferred
- **No Data Retention**: Optional zero-retention policy
- **Request Anonymization**: Optional log anonymization
- **Secure Communication**: TLS/HTTPS for all communications

### Access Control
- **API Authentication**: Token-based access control
- **Model Permissions**: Fine-grained model access control
- **Rate Limiting**: Protection against abuse
- **Resource Quotas**: CPU/memory usage limits

## Configuration

### Environment Variables
Key configuration options for the MCP server:

```bash
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
MCP_PROTOCOL_VERSION=1.0.0

# Security
MCP_SECRET_KEY=your-secret-key
MCP_ENABLE_TENANT_ISOLATION=true

# Backend Integration
BACKEND_API_URL=http://backend:8000
BACKEND_API_KEY=optional-api-key

# Resource Limits
MAX_CONCURRENT_REQUESTS=10
MAX_CONTEXT_LENGTH=4096
MAX_RESPONSE_TOKENS=1024

# Privacy
ENABLE_REQUEST_LOGGING=false
ANONYMIZE_LOGS=true
DATA_RETENTION_DAYS=0
```

### Model Configuration
Models are configured through JSON files or API registration:

```json
{
  "name": "Llama 3.2 3B",
  "backend_type": "ollama",
  "config": {
    "base_url": "http://localhost:11434",
    "model_name": "llama3.2:3b"
  },
  "capabilities": ["completion", "chat"]
}
```

## Deployment

### Docker Compose Integration
The MCP server is integrated into the existing docker-compose setup:

```yaml
mcp_server:
  build: ./backend/mcp_server
  ports:
    - "8001:8001"
  environment:
    - BACKEND_API_URL=http://backend:8000
    - MCP_ENABLE_TENANT_ISOLATION=true
  depends_on:
    - backend
    - redis
```

### Standalone Deployment
For development or testing:

```bash
cd backend/mcp_server
pip install -r requirements.txt
python main.py
```

## API Endpoints

### Model Management
- `POST /api/v1/models/register` - Register new model
- `GET /api/v1/models` - List available models
- `GET /api/v1/models/{id}` - Get model information
- `DELETE /api/v1/models/{id}` - Unregister model

### Inference
- `POST /api/v1/inference/completion` - Text completion
- `POST /api/v1/inference/chat` - Chat completion
- `POST /api/v1/inference/embedding` - Text embeddings

### Health and Monitoring
- `GET /api/v1/health` - Overall health check
- `GET /api/v1/health/models/{id}` - Model-specific health
- `GET /api/v1/stats` - Server statistics
- `GET /api/v1/info` - Server information

## Extensibility

### Adding New Backends
1. Implement the `ModelBackend` interface
2. Register in `_backend_classes` mapping
3. Add configuration schema
4. Implement health checks and inference methods

### Custom Inference Types
1. Add new `InferenceType` enum value
2. Create request/response schemas
3. Implement service logic
4. Add API endpoint

### Protocol Extensions
1. Extend MCP schemas for new message types
2. Register handlers in protocol manager
3. Update API documentation
4. Maintain backward compatibility

## Future Considerations

### Scalability
- **Horizontal Scaling**: Load balancing across multiple instances
- **Model Sharding**: Distribute models across servers
- **Caching**: Response caching for repeated requests
- **Queue Management**: Async request processing

### Advanced Features
- **Model Versioning**: Support for multiple model versions
- **A/B Testing**: Model comparison and testing
- **Fine-tuning**: Support for model customization
- **Federated Learning**: Multi-tenant model training

### Integration Enhancements
- **Real-time Streaming**: WebSocket streaming responses
- **Batch Processing**: Bulk inference requests
- **Model Marketplace**: Community model sharing
- **Plugin System**: Third-party extensions