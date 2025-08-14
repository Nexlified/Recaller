# MCP Server Setup and Integration Guide

## Overview

This guide provides step-by-step instructions for setting up and integrating the MCP (Model Context Protocol) server with Recaller. The MCP server enables secure, privacy-first LLM integration while maintaining tenant isolation and data privacy.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.11 or higher
- **Docker**: 20.10+ with Docker Compose
- **Memory**: Minimum 4GB RAM (8GB+ recommended for local models)
- **Storage**: 10GB+ available space for models

### Optional Model Backends
- **Ollama**: For local LLM deployment
- **CUDA**: For GPU acceleration (if using local models)
- **HuggingFace Account**: For accessing gated models

## Installation Methods

### Method 1: Docker Compose (Recommended)

#### 1. Clone and Setup
```bash
git clone https://github.com/Nexlified/Recaller.git
cd Recaller
```

#### 2. Configure Environment
```bash
# Copy MCP server environment template
cp backend/mcp_server/.env.example backend/mcp_server/.env

# Edit configuration
nano backend/mcp_server/.env
```

Key settings to configure:
```bash
# Generate a secure secret key
MCP_SECRET_KEY=your-secure-32-character-secret-key

# Configure backend integration
BACKEND_API_URL=http://backend:8000

# Set resource limits based on your hardware
MAX_CONCURRENT_REQUESTS=5
MAX_CONTEXT_LENGTH=4096
```

#### 3. Start Services
```bash
# Start all services including MCP server
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### 4. Verify Installation
```bash
# Check MCP server health
curl http://localhost:8001/api/v1/health

# Check server info
curl http://localhost:8001/api/v1/info
```

### Method 2: Standalone Development Setup

#### 1. Setup Python Environment
```bash
cd backend/mcp_server

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r ../requirements.txt
```

#### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Ensure backend is accessible
# Update BACKEND_API_URL if needed
```

#### 3. Start Services
```bash
# Start main backend first
cd ../
docker-compose up -d backend db redis

# Start MCP server
cd mcp_server
python main.py
```

## Model Backend Setup

### Ollama Integration

#### 1. Install Ollama
```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download/windows
```

#### 2. Configure Models
```bash
# Pull a model (this may take several minutes)
ollama pull llama3.2:3b

# Verify model is available
ollama list
```

#### 3. Register Model with MCP Server
```bash
curl -X POST http://localhost:8001/api/v1/models/register \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "name": "Llama 3.2 3B",
    "backend_type": "ollama",
    "description": "Local Llama 3.2 3B model",
    "capabilities": ["completion", "chat"],
    "config": {
      "base_url": "http://localhost:11434",
      "model_name": "llama3.2:3b"
    }
  }'
```

### HuggingFace Integration

#### 1. Install Dependencies
```bash
# In MCP server virtual environment
pip install transformers torch sentence-transformers
```

#### 2. Register Embedding Model
```bash
curl -X POST http://localhost:8001/api/v1/models/register \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "name": "BERT Embeddings",
    "backend_type": "huggingface",
    "description": "BERT-based text embeddings",
    "capabilities": ["embedding"],
    "config": {
      "model_name": "sentence-transformers/all-MiniLM-L6-v2",
      "device": "cpu"
    }
  }'
```

## Configuration

### Environment Configuration

The MCP server uses environment variables for configuration. Key settings include:

```bash
# Server Settings
MCP_SERVER_HOST=0.0.0.0        # Server bind address
MCP_SERVER_PORT=8001           # Server port
MCP_PROTOCOL_VERSION=1.0.0     # MCP protocol version

# Security
MCP_SECRET_KEY=your-secret-key              # JWT signing key
MCP_ENABLE_TENANT_ISOLATION=true           # Enable multi-tenancy
MCP_ACCESS_TOKEN_EXPIRE_MINUTES=30         # Token expiration

# Backend Integration
BACKEND_API_URL=http://backend:8000         # Main backend URL
BACKEND_API_KEY=                           # Optional API key

# Resource Limits
MAX_CONCURRENT_REQUESTS=10                  # Concurrent request limit
MAX_CONTEXT_LENGTH=4096                    # Maximum context tokens
MAX_RESPONSE_TOKENS=1024                   # Maximum response tokens
REQUEST_TIMEOUT_SECONDS=120                # Request timeout

# Privacy Settings
ENABLE_REQUEST_LOGGING=false               # Log requests (privacy impact)
ANONYMIZE_LOGS=true                        # Anonymize sensitive data
DATA_RETENTION_DAYS=0                      # Data retention (0 = no retention)

# Health Monitoring
HEALTH_CHECK_INTERVAL=30                   # Health check frequency
MODEL_HEALTH_CHECK_ENABLED=true           # Enable model health checks
```

### Model Configuration

Models can be configured via JSON files or API registration:

#### File-based Configuration
Create `backend/mcp_server/config/models.json`:
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

#### API-based Registration
```bash
# Register via API
curl -X POST http://localhost:8001/api/v1/models/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My Model", "backend_type": "ollama", ...}'
```

## Integration with Recaller Backend

### 1. Authentication Integration

The MCP server integrates with Recaller's authentication system:

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

### 2. Tenant Isolation

The MCP server respects tenant boundaries:

```python
# Tenant context is automatically injected
# Users can only access models within their tenant
# No cross-tenant data leakage
```

### 3. Error Handling

Implement proper error handling for MCP integration:

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

## Testing and Validation

### 1. Health Checks

Verify all components are working:

```bash
# Check overall health
curl http://localhost:8001/api/v1/health

# Check specific model
curl http://localhost:8001/api/v1/health/models/ollama_llama_3_2_3b
```

### 2. Basic Inference Tests

Test different inference types:

```bash
# Text completion
curl -X POST http://localhost:8001/api/v1/inference/completion \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "model_id": "ollama_llama_3_2_3b",
    "prompt": "The capital of France is",
    "max_tokens": 50
  }'

# Chat completion
curl -X POST http://localhost:8001/api/v1/inference/chat \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "model_id": "ollama_llama_3_2_3b",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'

# Text embeddings
curl -X POST http://localhost:8001/api/v1/inference/embedding \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: default" \
  -d '{
    "model_id": "huggingface_bert_embeddings",
    "text": "Hello world"
  }'
```

### 3. Load Testing

Test performance under load:

```bash
# Install apache bench
sudo apt-get install apache2-utils

# Test concurrent requests
ab -n 100 -c 10 -H "X-Tenant-ID: default" \
  -p test_data.json -T application/json \
  http://localhost:8001/api/v1/inference/completion
```

## Monitoring and Maintenance

### 1. Log Monitoring

Monitor MCP server logs:

```bash
# Docker logs
docker-compose logs -f mcp_server

# Standalone logs
tail -f logs/mcp_server.log
```

### 2. Performance Monitoring

Track key metrics:

```bash
# Server statistics
curl http://localhost:8001/api/v1/stats

# Model performance
curl http://localhost:8001/api/v1/health
```

### 3. Model Management

Manage registered models:

```bash
# List models
curl http://localhost:8001/api/v1/models

# Update model status
curl -X PUT http://localhost:8001/api/v1/models/model_id/status \
  -d '{"status": "maintenance"}'

# Unregister model
curl -X DELETE http://localhost:8001/api/v1/models/model_id
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
```bash
# Check if MCP server is running
docker-compose ps mcp_server

# Check port binding
netstat -tlnp | grep 8001
```

#### 2. Model Not Available
```bash
# Verify model registration
curl http://localhost:8001/api/v1/models

# Check model health
curl http://localhost:8001/api/v1/health/models/model_id
```

#### 3. Authentication Errors
```bash
# Verify backend connection
curl http://localhost:8001/api/v1/info

# Check tenant configuration
curl -H "X-Tenant-ID: your-tenant" http://localhost:8001/api/v1/models
```

#### 4. Resource Exhaustion
```bash
# Check resource usage
docker stats mcp_server

# Monitor active requests
curl http://localhost:8001/api/v1/stats
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in .env file
LOG_LEVEL=DEBUG
```

### Performance Tuning

Optimize for your hardware:

```bash
# Adjust resource limits
MAX_CONCURRENT_REQUESTS=5     # Lower for limited resources
MAX_CONTEXT_LENGTH=2048       # Reduce for faster inference
REQUEST_TIMEOUT_SECONDS=60    # Shorter timeout for responsiveness
```

## Security Considerations

### 1. Network Security
- Use HTTPS in production
- Restrict network access to MCP server
- Implement firewall rules

### 2. Authentication
- Use strong secret keys
- Rotate tokens regularly
- Implement proper RBAC

### 3. Privacy
- Disable request logging in production
- Use data retention policies
- Implement audit trails

### 4. Model Security
- Verify model integrity
- Use trusted model sources
- Implement model sandboxing

## Production Deployment

### 1. Environment Preparation
```bash
# Use production environment
cp .env.example .env.production

# Update for production
MCP_SECRET_KEY=production-secret-key
ENABLE_REQUEST_LOGGING=false
ANONYMIZE_LOGS=true
```

### 2. Scaling Considerations
- Use load balancers for multiple instances
- Implement model caching
- Monitor resource usage
- Plan for model updates

### 3. Backup and Recovery
- Backup model configurations
- Implement disaster recovery
- Document rollback procedures

## Support and Documentation

### Resources
- [MCP Protocol Specification](https://modelcontext.org/)
- [Recaller Documentation](../README.md)
- [API Documentation](http://localhost:8001/docs)

### Getting Help
- Check server logs for errors
- Review health check endpoints
- Consult troubleshooting section
- Submit issues to project repository