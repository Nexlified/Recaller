"""
Unit tests for MCP protocol implementation.

These tests verify the core MCP protocol message handling,
request/response processing, and error handling mechanisms.
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.protocol import (
    MCPProtocolHandler, MCPProtocolError, MCPErrorCodes, MCPServer
)
from schemas.mcp_schemas import (
    MCPRequest, MCPResponse, MCPError, MCPMessageType, 
    ModelInfo, ModelStatus, InferenceType
)


class TestMCPProtocolError:
    """Test MCP protocol error handling."""

    def test_protocol_error_creation(self):
        """Test that MCPProtocolError is created correctly."""
        error = MCPProtocolError(
            code=MCPErrorCodes.INVALID_REQUEST,
            message="Invalid request format",
            data={"field": "missing_param"}
        )
        
        assert error.code == MCPErrorCodes.INVALID_REQUEST
        assert error.message == "Invalid request format"
        assert error.data == {"field": "missing_param"}
        assert "MCP Error -32600" in str(error)

    def test_protocol_error_without_data(self):
        """Test MCPProtocolError without additional data."""
        error = MCPProtocolError(
            code=MCPErrorCodes.METHOD_NOT_FOUND,
            message="Method not found"
        )
        
        assert error.code == MCPErrorCodes.METHOD_NOT_FOUND
        assert error.message == "Method not found"
        assert error.data is None

    def test_error_codes_constants(self):
        """Test that error code constants are properly defined."""
        assert MCPErrorCodes.PARSE_ERROR == -32700
        assert MCPErrorCodes.INVALID_REQUEST == -32600
        assert MCPErrorCodes.METHOD_NOT_FOUND == -32601
        assert MCPErrorCodes.INVALID_PARAMS == -32602
        assert MCPErrorCodes.INTERNAL_ERROR == -32603
        assert MCPErrorCodes.MODEL_NOT_AVAILABLE == -32001
        assert MCPErrorCodes.CONTEXT_TOO_LONG == -32002
        assert MCPErrorCodes.RATE_LIMIT_EXCEEDED == -32003
        assert MCPErrorCodes.TENANT_ACCESS_DENIED == -32004


class TestMCPProtocolHandler:
    """Test MCP protocol message handling."""

    def setup_method(self):
        """Set up test protocol handler."""
        self.handler = MCPProtocolHandler()

    @pytest.mark.asyncio
    async def test_process_valid_request(self):
        """Test processing a valid MCP request."""
        request_data = {
            "type": "request",
            "id": "test-123",
            "method": "models.list",
            "params": {}
        }
        
        # Mock the method handler
        mock_response = {"models": []}
        with patch.object(self.handler, '_handle_request', return_value=mock_response):
            result = await self.handler.process_message(json.dumps(request_data))
            
            response = json.loads(result)
            assert response["type"] == "response"
            assert response["id"] == "test-123"
            assert response["result"] == mock_response

    @pytest.mark.asyncio
    async def test_process_invalid_json(self):
        """Test processing invalid JSON message."""
        invalid_json = "{ invalid json"
        
        result = await self.handler.process_message(invalid_json)
        
        response = json.loads(result)
        assert response["type"] == "error"
        assert response["code"] == MCPErrorCodes.PARSE_ERROR
        assert "JSON parse error" in response["message"]

    @pytest.mark.asyncio
    async def test_process_missing_required_fields(self):
        """Test processing message with missing required fields."""
        invalid_request = {
            "type": "request",
            # Missing 'method' field
            "id": "test-123"
        }
        
        result = await self.handler.process_message(json.dumps(invalid_request))
        
        response = json.loads(result)
        assert response["type"] == "error"
        assert response["code"] == MCPErrorCodes.INVALID_REQUEST

    @pytest.mark.asyncio
    async def test_process_unknown_method(self):
        """Test processing request with unknown method."""
        request_data = {
            "type": "request",
            "id": "test-123",
            "method": "unknown.method",
            "params": {}
        }
        
        result = await self.handler.process_message(json.dumps(request_data))
        
        response = json.loads(result)
        assert response["type"] == "error"
        assert response["code"] == MCPErrorCodes.METHOD_NOT_FOUND
        assert "unknown.method" in response["message"]

    @pytest.mark.asyncio
    async def test_handle_protocol_error(self):
        """Test handling of MCPProtocolError during request processing."""
        request_data = {
            "type": "request",
            "id": "test-123",
            "method": "models.list",
            "params": {}
        }
        
        # Mock the method handler to raise MCPProtocolError
        with patch.object(self.handler, '_handle_request') as mock_handler:
            mock_handler.side_effect = MCPProtocolError(
                code=MCPErrorCodes.TENANT_ACCESS_DENIED,
                message="Tenant access denied",
                data={"tenant_id": "test"}
            )
            
            result = await self.handler.process_message(json.dumps(request_data))
            
            response = json.loads(result)
            assert response["type"] == "error"
            assert response["code"] == MCPErrorCodes.TENANT_ACCESS_DENIED
            assert response["message"] == "Tenant access denied"
            assert response["data"] == {"tenant_id": "test"}

    @pytest.mark.asyncio
    async def test_handle_unexpected_error(self):
        """Test handling of unexpected errors during request processing."""
        request_data = {
            "type": "request",
            "id": "test-123",
            "method": "models.list",
            "params": {}
        }
        
        # Mock the method handler to raise unexpected error
        with patch.object(self.handler, '_handle_request') as mock_handler:
            mock_handler.side_effect = ValueError("Unexpected error")
            
            result = await self.handler.process_message(json.dumps(request_data))
            
            response = json.loads(result)
            assert response["type"] == "error"
            assert response["code"] == MCPErrorCodes.INTERNAL_ERROR
            assert response["message"] == "Internal error"
            assert response["data"]["error_type"] == "ValueError"

    @pytest.mark.asyncio
    async def test_send_request_with_response(self):
        """Test sending a request and receiving a response."""
        mock_transport = AsyncMock()
        self.handler._transport = mock_transport
        
        # Simulate receiving a response
        response_data = {
            "type": "response",
            "id": "test-request-1",
            "result": {"status": "success"}
        }
        
        # Create a task that will resolve the pending request
        async def simulate_response():
            await asyncio.sleep(0.1)  # Small delay
            await self.handler._handle_response(response_data)
        
        response_task = asyncio.create_task(simulate_response())
        
        # Send the request
        result = await self.handler.send_request("test.method", {"param": "value"})
        
        await response_task
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_send_request_timeout(self):
        """Test request timeout handling."""
        mock_transport = AsyncMock()
        self.handler._transport = mock_transport
        
        # Test timeout
        with pytest.raises(MCPProtocolError, match="Request timeout"):
            await self.handler.send_request("test.method", timeout=0.1)

    @pytest.mark.asyncio
    async def test_handle_error_response(self):
        """Test handling of error response."""
        mock_transport = AsyncMock()
        self.handler._transport = mock_transport
        
        # Simulate receiving an error response
        error_data = {
            "type": "error",
            "id": "test-request-1",
            "code": MCPErrorCodes.MODEL_NOT_AVAILABLE,
            "message": "Model not available"
        }
        
        # Create a task that will resolve the pending request with error
        async def simulate_error():
            await asyncio.sleep(0.1)  # Small delay
            await self.handler._handle_error(error_data)
        
        error_task = asyncio.create_task(simulate_error())
        
        # Send the request and expect it to raise an error
        with pytest.raises(MCPProtocolError) as exc_info:
            await self.handler.send_request("test.method", {"param": "value"})
        
        await error_task
        assert exc_info.value.code == MCPErrorCodes.MODEL_NOT_AVAILABLE
        assert exc_info.value.message == "Model not available"


class TestMCPServer:
    """Test MCP server functionality."""

    def setup_method(self):
        """Set up test MCP server."""
        self.server = MCPServer(host="localhost", port=8001)

    def test_server_initialization(self):
        """Test MCP server initialization."""
        assert self.server.host == "localhost"
        assert self.server.port == 8001
        assert self.server._running is False

    @pytest.mark.asyncio
    async def test_server_start_stop(self):
        """Test server start and stop lifecycle."""
        # Mock the transport server
        with patch('asyncio.start_server') as mock_start_server:
            mock_server = MagicMock()
            mock_start_server.return_value = mock_server
            
            # Start the server
            await self.server.start()
            assert self.server._running is True
            
            # Stop the server
            await self.server.stop()
            assert self.server._running is False
            mock_server.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_client_connection(self):
        """Test handling client connections."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        
        # Mock message from client
        mock_reader.readline.return_value = b'{"type": "request", "id": "1", "method": "ping"}\n'
        
        # Mock the protocol handler
        with patch.object(self.server._protocol_handler, 'process_message') as mock_process:
            mock_process.return_value = '{"type": "response", "id": "1", "result": "pong"}'
            
            # Handle the connection
            await self.server._handle_client(mock_reader, mock_writer)
            
            # Verify the response was written
            mock_writer.write.assert_called()
            mock_writer.drain.assert_called()

    @pytest.mark.asyncio
    async def test_handle_client_connection_error(self):
        """Test handling client connection errors."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        
        # Mock connection error
        mock_reader.readline.side_effect = ConnectionResetError("Connection lost")
        
        # Should handle the error gracefully
        await self.server._handle_client(mock_reader, mock_writer)
        
        # Writer should be closed
        mock_writer.close.assert_called()


class TestMCPMessageValidation:
    """Test MCP message schema validation."""

    def test_valid_request_creation(self):
        """Test creating valid MCP request."""
        request = MCPRequest(
            id="test-123",
            method="models.list",
            params={"filter": "available"}
        )
        
        assert request.type == MCPMessageType.REQUEST
        assert request.id == "test-123"
        assert request.method == "models.list"
        assert request.params == {"filter": "available"}
        assert isinstance(request.timestamp, datetime)

    def test_valid_response_creation(self):
        """Test creating valid MCP response."""
        response = MCPResponse(
            id="test-123",
            result={"models": ["model1", "model2"]}
        )
        
        assert response.type == MCPMessageType.RESPONSE
        assert response.id == "test-123"
        assert response.result == {"models": ["model1", "model2"]}

    def test_valid_error_creation(self):
        """Test creating valid MCP error."""
        error = MCPError(
            id="test-123",
            code=MCPErrorCodes.INVALID_PARAMS,
            message="Invalid parameters",
            data={"param": "missing"}
        )
        
        assert error.type == MCPMessageType.ERROR
        assert error.id == "test-123"
        assert error.code == MCPErrorCodes.INVALID_PARAMS
        assert error.message == "Invalid parameters"
        assert error.data == {"param": "missing"}

    def test_message_serialization(self):
        """Test MCP message serialization to JSON."""
        request = MCPRequest(
            id="test-123",
            method="models.list"
        )
        
        # Convert to dict for JSON serialization
        request_dict = request.dict()
        
        assert request_dict["type"] == "request"
        assert request_dict["id"] == "test-123"
        assert request_dict["method"] == "models.list"
        
        # Should be JSON serializable
        json_str = json.dumps(request_dict)
        assert json_str is not None
        
        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["id"] == "test-123"