"""
Main MCP Server application.

This module provides the main FastAPI application for the MCP server,
including startup/shutdown logic, middleware configuration, and route registration.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

try:
    # Try relative imports first (when run as module)
    from .config.settings import mcp_settings
    from .api.endpoints import router as api_router
    from .models.registry import model_registry
    from .services.auth import auth_service
    from .core.protocol import MCPProtocolError
    from . import __version__, __description__
except ImportError:
    # Fall back to absolute imports (when run directly)
    from config.settings import mcp_settings
    from api.endpoints import router as api_router
    from models.registry import model_registry
    from services.auth import auth_service
    from core.protocol import MCPProtocolError
    import __init__
    __version__ = __init__.__version__
    __description__ = __init__.__description__


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting MCP Server...")
    
    try:
        # Initialize model registry
        await model_registry.initialize()
        logger.info("Model registry initialized")
        
        # Start MCP protocol server (WebSocket/HTTP)
        # This would start the actual MCP protocol server
        # Implementation depends on chosen transport
        
        logger.info(f"MCP Server started on {mcp_settings.MCP_SERVER_HOST}:{mcp_settings.MCP_SERVER_PORT}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start MCP Server: {e}")
        raise
    finally:
        logger.info("Shutting down MCP Server...")
        
        # Cleanup auth service
        await auth_service.cleanup()
        
        logger.info("MCP Server shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Recaller MCP Server",
    description=__description__,
    version=__version__,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(MCPProtocolError)
async def mcp_exception_handler(request: Request, exc: MCPProtocolError):
    """Handle MCP protocol errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "data": exc.data
            }
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": -32601,
                "message": "Endpoint not found",
                "data": {"path": str(request.url.path)}
            }
        }
    )


# Middleware for request logging (if enabled)
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log requests if enabled in settings."""
    if mcp_settings.ENABLE_REQUEST_LOGGING:
        start_time = asyncio.get_event_loop().time()
        
        # Log request (anonymize if configured)
        if mcp_settings.ANONYMIZE_LOGS:
            logger.info(f"Request: {request.method} {request.url.path}")
        else:
            logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response time
        process_time = asyncio.get_event_loop().time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
        
        return response
    else:
        return await call_next(request)


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Recaller MCP Server",
        "version": __version__,
        "description": __description__,
        "protocol_version": mcp_settings.MCP_PROTOCOL_VERSION,
        "endpoints": {
            "api": "/api/v1",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/api/v1/health"
        }
    }


# Development server runner
def run_dev_server():
    """Run development server."""
    uvicorn.run(
        "mcp_server.main:app",
        host=mcp_settings.MCP_SERVER_HOST,
        port=mcp_settings.MCP_SERVER_PORT,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    run_dev_server()
