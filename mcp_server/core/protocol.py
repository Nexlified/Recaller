"""
Core MCP protocol implementation and message handling.

This module implements the Model Context Protocol v1 specification,
providing standardized communication between the MCP server and LLMs.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
import uuid

from ..schemas.mcp_schemas import (
    MCPMessage, MCPRequest, MCPResponse, MCPError, MCPMessageType
)


logger = logging.getLogger(__name__)


class MCPProtocolError(Exception):
    """MCP protocol specific error."""
    def __init__(self, code: int, message: str, data: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {code}: {message}")


class MCPProtocolHandler:
    """
    MCP Protocol v1 message handler.
    
    Implements the core protocol logic for handling MCP messages,
    routing requests, and managing the request/response lifecycle.
    """
    
    def __init__(self):
        self._methods: Dict[str, Callable] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._message_handlers: Dict[MCPMessageType, Callable] = {
            MCPMessageType.REQUEST: self._handle_request,
            MCPMessageType.RESPONSE: self._handle_response,
            MCPMessageType.ERROR: self._handle_error,
            MCPMessageType.NOTIFICATION: self._handle_notification
        }
    
    def register_method(self, method_name: str, handler: Callable):
        """Register a method handler for MCP requests."""
        self._methods[method_name] = handler
        logger.info(f"Registered MCP method: {method_name}")
    
    async def process_message(self, message_data: str) -> Optional[str]:
        """
        Process an incoming MCP message.
        
        Args:
            message_data: JSON string containing the MCP message
            
        Returns:
            Optional JSON string response
        """
        try:
            # Parse the message
            data = json.loads(message_data)
            message_type = MCPMessageType(data.get("type"))
            
            # Route to appropriate handler
            handler = self._message_handlers.get(message_type)
            if not handler:
                raise MCPProtocolError(
                    code=-32601,
                    message=f"Unknown message type: {message_type}"
                )
            
            response = await handler(data)
            return json.dumps(response.dict()) if response else None
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MCP message: {e}")
            error_response = MCPError(
                code=-32700,
                message="Parse error",
                data={"original_error": str(e)}
            )
            return json.dumps(error_response.dict())
            
        except MCPProtocolError as e:
            logger.error(f"MCP protocol error: {e}")
            error_response = MCPError(
                id=data.get("id"),
                code=e.code,
                message=e.message,
                data=e.data
            )
            return json.dumps(error_response.dict())
            
        except Exception as e:
            logger.error(f"Unexpected error processing MCP message: {e}")
            error_response = MCPError(
                id=data.get("id"),
                code=-32603,
                message="Internal error",
                data={"error_type": type(e).__name__}
            )
            return json.dumps(error_response.dict())
    
    async def _handle_request(self, data: Dict[str, Any]) -> Optional[MCPResponse]:
        """Handle MCP request messages."""
        try:
            request = MCPRequest(**data)
            
            # Find the method handler
            handler = self._methods.get(request.method)
            if not handler:
                raise MCPProtocolError(
                    code=-32601,
                    message=f"Method not found: {request.method}"
                )
            
            # Execute the handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request.params or {})
            else:
                result = handler(request.params or {})
            
            # Return response
            return MCPResponse(
                id=request.id,
                result=result
            )
            
        except MCPProtocolError:
            raise
        except Exception as e:
            raise MCPProtocolError(
                code=-32603,
                message="Internal error",
                data={"error": str(e)}
            )
    
    async def _handle_response(self, data: Dict[str, Any]) -> None:
        """Handle MCP response messages."""
        response = MCPResponse(**data)
        
        # Resolve pending request if exists
        if response.id and response.id in self._pending_requests:
            future = self._pending_requests.pop(response.id)
            if not future.cancelled():
                future.set_result(response)
    
    async def _handle_error(self, data: Dict[str, Any]) -> None:
        """Handle MCP error messages."""
        error = MCPError(**data)
        
        # Resolve pending request with error if exists
        if error.id and error.id in self._pending_requests:
            future = self._pending_requests.pop(error.id)
            if not future.cancelled():
                future.set_exception(MCPProtocolError(error.code, error.message, error.data))
        
        logger.error(f"Received MCP error: {error.code} - {error.message}")
    
    async def _handle_notification(self, data: Dict[str, Any]) -> None:
        """Handle MCP notification messages."""
        # Notifications don't require responses
        logger.info(f"Received MCP notification: {data}")
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None, 
                          timeout: float = 30.0) -> Any:
        """
        Send an MCP request and wait for response.
        
        Args:
            method: Request method name
            params: Request parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response result
        """
        request_id = str(uuid.uuid4())
        request = MCPRequest(
            id=request_id,
            method=method,
            params=params
        )
        
        # Create future for response
        future = asyncio.Future()
        self._pending_requests[request_id] = future
        
        try:
            # Send request (implementation depends on transport layer)
            await self._send_message(request)
            
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            
            if response.error:
                raise MCPProtocolError(
                    code=response.error.get("code", -32603),
                    message=response.error.get("message", "Unknown error"),
                    data=response.error.get("data")
                )
            
            return response.result
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise MCPProtocolError(
                code=-32000,
                message=f"Request timeout after {timeout} seconds"
            )
        except Exception as e:
            self._pending_requests.pop(request_id, None)
            raise
    
    async def _send_message(self, message: MCPMessage) -> None:
        """
        Send a message via the transport layer.
        
        This is a placeholder that should be implemented by the transport layer.
        """
        raise NotImplementedError("Transport layer not implemented")


class MCPServer:
    """
    MCP Server implementation.
    
    Provides the main server interface for handling MCP connections
    and managing the protocol lifecycle.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        self.host = host
        self.port = port
        self.protocol_handler = MCPProtocolHandler()
        self._server = None
        self._connections = set()
    
    def register_method(self, method_name: str, handler: Callable):
        """Register a method handler."""
        self.protocol_handler.register_method(method_name, handler)
    
    async def start(self) -> None:
        """Start the MCP server."""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        # Implementation depends on chosen transport (WebSocket, HTTP, etc.)
        # This is a placeholder for the actual server implementation
        pass
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        logger.info("Stopping MCP server")
        
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        # Close all connections
        for connection in self._connections:
            await connection.close()
        
        self._connections.clear()
    
    async def handle_connection(self, websocket, path):
        """Handle a new WebSocket connection."""
        self._connections.add(websocket)
        logger.info(f"New MCP connection from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                response = await self.protocol_handler.process_message(message)
                if response:
                    await websocket.send(response)
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            self._connections.discard(websocket)
            logger.info(f"MCP connection closed for {websocket.remote_address}")


# Protocol constants
MCP_VERSION = "1.0.0"
MCP_SPEC_URL = "https://modelcontext.org/"

# Standard error codes
class MCPErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # Custom error codes (application specific)
    MODEL_NOT_AVAILABLE = -32001
    CONTEXT_TOO_LONG = -32002
    RATE_LIMIT_EXCEEDED = -32003
    TENANT_ACCESS_DENIED = -32004