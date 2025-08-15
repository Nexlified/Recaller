# MCP Server Docker Setup - Quick Reference

This is a quick reference for the MCP Server Docker setup in Recaller.

## 📋 Summary

The MCP (Model Context Protocol) Server has been successfully integrated into Recaller's Docker Compose setup with:

✅ **Dockerfile**: `/mcp_server/Dockerfile`
✅ **Docker Compose Integration**: Updated `docker-compose.yml`
✅ **Production Ready**: `docker-compose.prod.yml`
✅ **Documentation**: Complete deployment guide
✅ **Security**: Non-root user, health checks, proper networking

## 🚀 Quick Start

```bash
# Development
git clone https://github.com/Nexlified/Recaller.git
cd Recaller
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

## 🔗 Service Details

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Frontend | 3000 | http://localhost:3000 | React UI |
| Backend | 8000 | http://localhost:8000 | FastAPI Backend |
| **MCP Server** | **8001** | **http://localhost:8001** | **LLM Integration** |
| PostgreSQL | 5432 | - | Database |
| Redis | 6379 | - | Cache/Queue |

## 🔍 Health Checks

```bash
# Verify MCP Server
curl http://localhost:8001/api/v1/health

# Check all services
docker compose ps
```

## 📁 Key Files

- `mcp_server/Dockerfile` - Container definition
- `docker-compose.yml` - Development setup
- `docker-compose.prod.yml` - Production setup
- `mcp_server/.env.example` - Environment template
- `.env.production.example` - Production environment template

## 🔧 Configuration

### Environment Variables
- `MCP_SERVER_PORT=8001` - Server port
- `BACKEND_API_URL=http://backend:8000` - Backend integration
- `MCP_ENABLE_TENANT_ISOLATION=true` - Multi-tenant support
- `MODEL_REGISTRY_PATH=/app/models` - Model storage

### Volume Mounts
- `mcp_models:/app/models` - Persistent model storage
- `./mcp_server:/app` - Development code mounting

## 🛡️ Security Features

- Non-root container user
- Secret key authentication
- Tenant isolation
- Privacy-first logging
- Resource limits

## 📚 Documentation

- [Complete Deployment Guide](./mcp-server-deployment.md)
- [Architecture Documentation](./mcp-server-architecture.md)
- [Setup Guide](./mcp-server-setup.md)

## 🐛 Troubleshooting

### Common Issues
1. **Port conflicts**: Change external port mapping
2. **Permission issues**: Check volume permissions
3. **Memory issues**: Reduce resource limits
4. **Connection issues**: Verify backend connectivity

### Debug Commands
```bash
# View logs
docker compose logs mcp_server

# Check container status
docker compose ps mcp_server

# Execute commands in container
docker compose exec mcp_server bash
```

## 🔄 Development Workflow

1. **Start services**: `docker compose up -d`
2. **View logs**: `docker compose logs -f mcp_server`
3. **Restart after changes**: `docker compose restart mcp_server`
4. **Stop services**: `docker compose down`

For detailed information, see the [MCP Server Deployment Guide](./mcp-server-deployment.md).