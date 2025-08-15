# MCP Server Integration Guide

**Recaller MCP Server** enables secure, privacy-first integration with Large Language Models (LLMs) while maintaining tenant isolation and on-device processing.

## 🔄 Quick Start

### 1. Start MCP Server
```bash
# Using Docker Compose (Recommended)
docker compose up -d

# Verify server is running
curl http://localhost:8001/api/v1/health
```

### 2. Set Up Model Backend

#### Option A: Ollama (Local LLMs)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2:3b

# Register with MCP server
curl -X POST http://localhost:8001/api/v1/models/register \
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

#### Option B: HuggingFace Models
```bash
# Register embedding model
curl -X POST http://localhost:8001/api/v1/models/register \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "name": "BERT Embeddings",
    "backend_type": "huggingface",
    "capabilities": ["embedding"],
    "config": {
      "model_name": "sentence-transformers/all-MiniLM-L6-v2",
      "device": "cpu"
    }
  }'
```

### 3. Test Inference
```bash
# Text completion
curl -X POST http://localhost:8001/api/v1/inference/completion \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "model_id": "your-model-id",
    "prompt": "Explain the benefits of privacy-first AI:",
    "max_tokens": 100
  }'

# Chat completion
curl -X POST http://localhost:8001/api/v1/inference/chat \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "model_id": "your-model-id",
    "messages": [
      {"role": "user", "content": "How can I manage my finances better?"}
    ]
  }'
```

## 🔧 API Endpoints

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

## ⚙️ Configuration

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

### Model Configuration File
Create `config/models.json`:
```json
{
  "models": [
    {
      "name": "Local Llama",
      "backend_type": "ollama",
      "config": {
        "base_url": "http://localhost:11434",
        "model_name": "llama3.2:3b"
      },
      "capabilities": ["completion", "chat"]
    }
  ]
}
```

## 🏗️ Backend Integration

### Authentication Integration
```python
# In your Recaller backend code
import httpx

async def call_mcp_inference(tenant_id: str, user_token: str, request_data: dict):
    """Call MCP server for inference"""
    headers = {
        "Authorization": f"Bearer {user_token}",
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://mcp_server:8001/api/v1/inference/chat",
            headers=headers,
            json=request_data
        )
        return response.json()
```

### Error Handling
```python
try:
    response = await call_mcp_inference(tenant_id, token, request)
    return response
except httpx.HTTPStatusError as e:
    if e.response.status_code == 403:
        raise AuthenticationError("MCP access denied")
    elif e.response.status_code == 404:
        raise NotFoundError("Model not available")
    else:
        raise InferenceError("MCP inference failed")
```

## 🚀 Deployment

### Docker Compose
```yaml
services:
  mcp_server:
    build: ./mcp_server
    ports:
      - "8001:8001"
    environment:
      - MCP_SECRET_KEY=${MCP_SECRET_KEY}
      - BACKEND_API_URL=http://backend:8000
    volumes:
      - ./mcp_server/config:/app/config
    depends_on:
      - backend
```

### Production Considerations
- Use reverse proxy (nginx) for SSL termination
- Set up proper logging and monitoring
- Configure resource limits based on hardware
- Use external model backends for scalability
- Implement backup strategies for model configurations

## 🔒 Security & Privacy

### Tenant Isolation
- Complete data separation per tenant
- API-level access control
- Model access restrictions by tenant

### Privacy Features
- On-device processing (no external calls)
- Configurable data retention (default: 0 days)
- Anonymized logging
- No telemetry or tracking

### Security Best Practices
- Use strong secret keys
- Enable HTTPS in production
- Regular security updates
- Monitor access logs

## 📊 Monitoring

### Health Checks
```bash
# System health
curl http://localhost:8001/api/v1/health

# Model-specific health
curl http://localhost:8001/api/v1/health/models/model_id

# Server statistics
curl http://localhost:8001/api/v1/stats
```

### Log Monitoring
```bash
# Docker logs
docker compose logs -f mcp_server

# Server statistics
curl http://localhost:8001/api/v1/stats
```

## 🛠️ Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if MCP server is running
docker compose ps mcp_server

# Check port binding
netstat -tlnp | grep 8001
```

#### Model Not Available
```bash
# Verify model registration
curl http://localhost:8001/api/v1/models

# Check model health
curl http://localhost:8001/api/v1/health/models/model_id
```

#### Authentication Errors
```bash
# Verify backend connection
curl http://localhost:8001/api/v1/info

# Check tenant configuration
curl -H "X-Tenant-ID: your-tenant" http://localhost:8001/api/v1/models
```

## 📚 Additional Resources

- [Detailed Setup Guide](docs/mcp-server-setup.md)
- [Production Deployment Guide](docs/mcp-server-deployment.md)
- [Architecture Documentation](docs/mcp-server-architecture.md)
- [MCP Protocol Specification](https://modelcontext.org/)
- [Technical README](mcp_server/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

---

*For detailed technical documentation, see the [mcp_server/README.md](mcp_server/README.md) and [docs/](docs/) directory.*