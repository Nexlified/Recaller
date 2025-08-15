# Recaller MCP Server

A Model Context Protocol (MCP) v1 compliant server for secure, privacy-first LLM integration with Recaller.

## Overview

The Recaller MCP Server provides a standardized interface for Large Language Model integration while maintaining Recaller's core principles of privacy, multi-tenancy, and on-device AI processing. It implements the MCP v1 protocol to enable secure communication with various LLM backends.

## Features

- **MCP v1 Protocol**: Full compliance with Model Context Protocol specification
- **Multi-Backend Support**: Ollama, HuggingFace, OpenAI-compatible APIs, and custom backends
- **Tenant Isolation**: Complete data separation and access control per tenant
- **Privacy-First**: On-device processing with optional zero-retention policies
- **Extensible Architecture**: Plugin-based backend system for easy expansion
- **Health Monitoring**: Comprehensive health checks and performance monitoring
- **Resource Management**: Rate limiting, context validation, and resource quotas

## Quick Start

### Docker Compose (Recommended)

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Verify MCP server is running**:
   ```bash
   curl http://localhost:8080/api/v1/health
   ```

3. **Set up a model backend** (e.g., Ollama):
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model
   ollama pull llama3.2:3b
   
   # Register with MCP server
   curl -X POST http://localhost:8080/api/v1/models/register \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: default" \
     -d '{
       "name": "Llama 3.2 3B",
       "backend_type": "ollama",
       "capabilities": ["completion", "chat"],
       "config": {
         "base_url": "http://localhost:11434",
         "model_name": "llama3.2:3b"
       }
     }'
   ```

4. **Test inference**:
   ```bash
   curl -X POST http://localhost:8080/api/v1/inference/chat \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: default" \
     -d '{
       "model_id": "ollama_llama_3_2_3b",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

### Standalone Development

1. **Setup environment**:
   ```bash
   cd mcp_server
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start server**:
   ```bash
   python main.py
   ```

## Architecture

### Directory Structure

```
mcp_server/
├── main.py                     # FastAPI application
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container configuration
├── .env.example               # Environment template
│
├── core/                      # Core MCP protocol
│   └── protocol.py            # Protocol implementation
│
├── models/                    # Model management
│   └── registry.py           # Model registry and backends
│
├── services/                  # Business logic
│   ├── inference.py          # Inference processing
│   └── auth.py               # Authentication
│
├── api/                       # REST API
│   └── endpoints.py          # API routes
│
├── schemas/                   # Data validation
│   └── mcp_schemas.py        # Pydantic models
│
└── config/                    # Configuration
    ├── settings.py           # Application settings
    └── models.example.json   # Model configuration examples
```

### Core Components

1. **Protocol Handler**: MCP v1 message processing and routing
2. **Model Registry**: Backend abstraction and lifecycle management
3. **Inference Service**: Request processing and response handling
4. **Auth Service**: Tenant isolation and access control
5. **API Layer**: REST endpoints for integration

## Supported Backends

### Ollama
- **Use Case**: Local LLM deployment with full API integration
- **Models**: Llama, Mistral, CodeLlama, etc.
- **Features**: Completion, chat, streaming, automatic model pulling
- **Implementation**: Complete with real API calls and health monitoring

### HuggingFace
- **Use Case**: Transformer models and embeddings
- **Models**: BERT, RoBERTa, sentence-transformers, DialoGPT
- **Features**: Embeddings, classification, completion, chat
- **Implementation**: Extensible framework (placeholder with examples)

### OpenAI Compatible
- **Use Case**: Any API following OpenAI format
- **Examples**: LocalAI, Oobabooga, vLLM, text-generation-webui
- **Features**: Full OpenAI API compatibility
- **Implementation**: Complete example backend with real API integration

### Custom Backends
- **Extensible**: Plugin architecture for custom implementations
- **Interface**: Simple ModelBackend interface to implement
- **Examples**: Direct PyTorch, TensorFlow, or custom inference engines
- **Documentation**: Comprehensive guide for creating new backends

## API Endpoints

### Model Management
- `POST /api/v1/models/register` - Register new model
- `GET /api/v1/models` - List available models
- `GET /api/v1/models/{id}` - Get model details
- `DELETE /api/v1/models/{id}` - Unregister model

### Inference
- `POST /api/v1/inference/completion` - Text completion
- `POST /api/v1/inference/chat` - Chat completion
- `POST /api/v1/inference/embedding` - Text embeddings

### Health & Monitoring
- `GET /api/v1/health` - System health check
- `GET /api/v1/stats` - Server statistics
- `GET /api/v1/info` - Server information

## Configuration

### Environment Variables

```bash
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001

# Security
MCP_SECRET_KEY=your-secret-key
MCP_ENABLE_TENANT_ISOLATION=true

# Backend Integration
BACKEND_API_URL=http://backend:8000

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

Models can be registered via API or configuration files:

```json
{
  "name": "Local Llama",
  "backend_type": "ollama",
  "config": {
    "base_url": "http://localhost:11434",
    "model_name": "llama3.2:3b"
  },
  "capabilities": ["completion", "chat"]
}
```

## Security & Privacy

### Tenant Isolation
- Complete data separation between tenants
- Tenant-specific model access controls
- Isolated request processing

### Privacy Features
- On-device model execution
- Optional zero data retention
- Request anonymization
- No third-party data sharing

### Access Control
- JWT-based authentication
- API rate limiting
- Resource quotas
- Model permissions

## Integration

### With Recaller Backend

The MCP server integrates seamlessly with the main Recaller application:

```python
# In Recaller backend
async def get_ai_insights(user_context, query):
    response = await mcp_client.inference.chat(
        model_id="local_llama",
        messages=[{"role": "user", "content": query}],
        tenant_id=user_context.tenant_id
    )
    return response.message.content
```

### Authentication Flow

1. User authenticates with main Recaller backend
2. Backend forwards requests to MCP server with tenant context
3. MCP server validates tenant access and processes request
4. Response returned to backend and user

## Deployment

### Production Checklist

- [ ] Generate secure secret keys
- [ ] Configure HTTPS/TLS
- [ ] Set up monitoring and logging
- [ ] Configure resource limits
- [ ] Test backup and recovery
- [ ] Review security settings

### Scaling Considerations

- **Horizontal Scaling**: Multiple MCP server instances behind load balancer
- **Model Distribution**: Different models on different servers
- **Caching**: Response caching for repeated requests
- **Resource Management**: GPU/CPU allocation per model

## Monitoring

### Health Checks

```bash
# Overall health
curl http://localhost:8001/api/v1/health

# Model-specific health
curl http://localhost:8001/api/v1/health/models/model_id

# Server statistics
curl http://localhost:8001/api/v1/stats
```

### Metrics

- Request latency and throughput
- Model availability and response times
- Resource usage (CPU, memory, GPU)
- Error rates and types
- Tenant usage patterns

## Development

### Adding New Backends

The MCP server supports a fully extensible backend architecture. Creating new backends is straightforward:

1. **Implement Backend Interface**:
   ```python
   from backends.base_backend import ModelBackend
   
   class CustomBackend(ModelBackend):
       async def initialize(self): ...
       async def health_check(self): ...
       def get_capabilities(self): ...
       async def generate_completion(self, prompt, **kwargs): ...
       async def generate_chat_response(self, messages, **kwargs): ...
   ```

2. **Register Backend**:
   ```python
   # In models/registry.py
   self._backend_classes["custom"] = CustomBackend
   ```

3. **Configure Model**:
   ```json
   {
     "name": "My Custom Model",
     "backend_type": "custom",
     "config": {
       "api_url": "https://your-api.com",
       "model_name": "your-model"
     }
   }
   ```

4. **Test Integration**:
   ```bash
   python test_extensibility.py
   ```

For detailed instructions, see [Backend Extension Guide](../docs/mcp-backend-extension-guide.md).

### Example Backends

- **Ollama Backend**: Complete implementation with API integration ([backends/ollama_backend.py](backends/ollama_backend.py))
- **HuggingFace Backend**: Extensible framework with examples ([backends/huggingface_backend.py](backends/huggingface_backend.py))
- **OpenAI Compatible**: Example for API-based backends ([examples/openai_compatible_backend.py](examples/openai_compatible_backend.py))

### Testing New Backends

```bash
# Test the extensibility system
python test_extensibility.py

# Run specific backend tests
pytest tests/test_custom_backend.py -v

# Test with real services (if available)
python examples/test_ollama_integration.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=mcp_server tests/
```

## Documentation

- [Architecture Overview](../../docs/mcp-server-architecture.md)
- [Setup Guide](../../docs/mcp-server-setup.md)
- [API Documentation](http://localhost:8001/docs) (when server is running)
- [MCP Protocol Specification](https://modelcontext.org/)

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if server is running and port is accessible
2. **Model Not Available**: Verify model registration and backend status
3. **Authentication Errors**: Check tenant configuration and tokens
4. **Performance Issues**: Review resource limits and concurrent requests

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Getting Help

- Check server logs: `docker-compose logs mcp_server`
- Review health endpoints: `/api/v1/health`
- Consult documentation links above
- Submit issues to project repository

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

This project is licensed under the same license as the main Recaller project.