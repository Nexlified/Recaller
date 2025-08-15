# MCP Server Deployment Guide

This guide covers the deployment of the Recaller MCP (Model Context Protocol) Server using Docker and Docker Compose.

## Overview

The MCP Server provides a standardized interface for LLM integration in Recaller, supporting:
- Local and self-hosted LLM backends (Ollama, HuggingFace, etc.)
- Tenant isolation for multi-user deployments
- Privacy-first design with no external data sharing
- RESTful API for backend integration

## Quick Start with Docker Compose

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- Git
- At least 2GB available RAM
- 10GB available disk space

### Development Deployment

1. **Clone the repository:**
```bash
git clone https://github.com/Nexlified/Recaller.git
cd Recaller
```

2. **Start all services:**
```bash
docker compose up -d
```

3. **Verify MCP server is running:**
```bash
curl http://localhost:8001/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "models": []
}
```

### Production Deployment

1. **Create production environment:**
```bash
cp .env.production.example .env.production
```

2. **Edit production configuration:**
```bash
nano .env.production
```

Update the following critical settings:
- `POSTGRES_PASSWORD`: Strong database password
- `SECRET_KEY`: 64-character random string
- `MCP_SECRET_KEY`: 32-character random string
- `REACT_APP_API_URL`: Your domain URL

3. **Deploy with production settings:**
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

## Configuration

### Environment Variables

The MCP server accepts the following environment variables:

#### Server Configuration
- `MCP_SERVER_HOST`: Server bind address (default: 0.0.0.0)
- `MCP_SERVER_PORT`: Server port (default: 8001)
- `MCP_PROTOCOL_VERSION`: MCP protocol version (default: 1.0.0)

#### Security
- `MCP_SECRET_KEY`: Authentication secret key (required in production)
- `MCP_ENABLE_TENANT_ISOLATION`: Enable tenant isolation (default: true)
- `BACKEND_API_KEY`: Optional API key for backend communication

#### Backend Integration
- `BACKEND_API_URL`: FastAPI backend URL (default: http://backend:8000)

#### Resource Limits
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent model requests (default: 10)
- `MAX_CONTEXT_LENGTH`: Maximum context length for models (default: 4096)
- `MAX_RESPONSE_TOKENS`: Maximum response tokens (default: 1024)
- `REQUEST_TIMEOUT_SECONDS`: Request timeout (default: 120)

#### Privacy & Logging
- `ENABLE_REQUEST_LOGGING`: Enable request logging (default: false)
- `ANONYMIZE_LOGS`: Anonymize sensitive data in logs (default: true)
- `DATA_RETENTION_DAYS`: Data retention period (default: 0)

### Model Configuration

Models can be configured through:

1. **Environment variables** (for default models)
2. **API endpoints** (for dynamic registration)
3. **Configuration files** (for persistent setup)

Example model registration:
```bash
curl -X POST http://localhost:8001/api/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Llama",
    "backend_type": "ollama",
    "config": {
      "base_url": "http://localhost:11434",
      "model_name": "llama3.2:3b"
    },
    "capabilities": ["completion", "chat"]
  }'
```

## Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │────│     Backend     │────│   MCP Server    │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   LLM Backend   │
                       │   (Port 5432)   │    │  (Various)      │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │      Redis      │
                       │   (Port 6379)   │
                       └─────────────────┘
```

## Health Checks and Monitoring

### Health Check Endpoints

- **Overall health**: `GET /api/v1/health`
- **Model health**: `GET /api/v1/health/models/{model_id}`
- **Server info**: `GET /api/v1/info`
- **Statistics**: `GET /api/v1/stats`

### Monitoring with Docker

```bash
# Check service status
docker compose ps

# View MCP server logs
docker compose logs mcp_server

# Monitor resource usage
docker stats recaller-mcp_server-1
```

### Health Check Script

Create a monitoring script:
```bash
#!/bin/bash
# health-check.sh

MCP_URL="http://localhost:8001"

# Check overall health
response=$(curl -s -o /dev/null -w "%{http_code}" "$MCP_URL/api/v1/health")

if [ "$response" = "200" ]; then
    echo "✅ MCP Server is healthy"
    exit 0
else
    echo "❌ MCP Server is unhealthy (HTTP $response)"
    exit 1
fi
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
If port 8001 is already in use:
```bash
# Check what's using the port
sudo lsof -i :8001

# Change port in docker-compose.yml
ports:
  - "8002:8001"  # Use external port 8002
```

#### 2. Permission Issues
```bash
# Fix permission issues with volumes
sudo chown -R 1000:1000 ./mcp_server/models
```

#### 3. Memory Issues
Reduce resource limits in environment:
```bash
MAX_CONCURRENT_REQUESTS=3
MAX_CONTEXT_LENGTH=2048
```

#### 4. Connection Issues
Check network connectivity:
```bash
# Test backend connection
docker compose exec mcp_server curl http://backend:8000/health

# Test from host
curl http://localhost:8000/health
```

### Debugging

Enable debug logging:
```bash
# In .env file
LOG_LEVEL=DEBUG
ENABLE_REQUEST_LOGGING=true
```

View detailed logs:
```bash
docker compose logs -f mcp_server
```

## Scaling and Production Considerations

### Horizontal Scaling

For high-load deployments:

1. **Multiple MCP instances:**
```yaml
# docker-compose.scale.yml
services:
  mcp_server:
    # ... existing config
    deploy:
      replicas: 3
```

2. **Load balancer configuration:**
```nginx
upstream mcp_servers {
    server mcp_server_1:8001;
    server mcp_server_2:8001;
    server mcp_server_3:8001;
}
```

### Security Hardening

1. **Use secrets management:**
```yaml
secrets:
  mcp_secret_key:
    external: true
```

2. **Network isolation:**
```yaml
networks:
  internal:
    driver: bridge
    internal: true
```

3. **Resource limits:**
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

### Backup and Recovery

1. **Backup model configurations:**
```bash
# Backup model registry
docker compose exec mcp_server tar -czf /tmp/models-backup.tar.gz /app/models
docker cp recaller-mcp_server-1:/tmp/models-backup.tar.gz ./backups/
```

2. **Restore procedure:**
```bash
# Restore models
docker cp ./backups/models-backup.tar.gz recaller-mcp_server-1:/tmp/
docker compose exec mcp_server tar -xzf /tmp/models-backup.tar.gz -C /
```

## Integration Examples

### Adding Ollama Backend

1. **Add Ollama service to docker-compose:**
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

2. **Register Ollama model:**
```bash
curl -X POST http://localhost:8001/api/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Llama 3.2 3B",
    "backend_type": "ollama",
    "config": {
      "base_url": "http://ollama:11434",
      "model_name": "llama3.2:3b"
    }
  }'
```

### Custom Model Backends

For implementing custom model backends, see the [MCP Server Architecture Documentation](./mcp-server-architecture.md).

## Support

For deployment issues:
1. Check the [Troubleshooting Section](#troubleshooting)
2. Review logs with `docker compose logs mcp_server`
3. Open an issue on GitHub with deployment details
4. Consult the [MCP Server Setup Guide](./mcp-server-setup.md)

## Security Notice

⚠️ **Important**: Always change default passwords and secret keys in production deployments. Never expose the MCP server directly to the internet without proper authentication and TLS encryption.