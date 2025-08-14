"""
Pydantic schemas for MCP protocol messages and API validation.

These schemas define the structure of MCP v1 protocol messages,
API requests/responses, and internal data models.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MCPMessageType(str, Enum):
    """MCP protocol message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class ModelStatus(str, Enum):
    """Model status enumeration."""
    AVAILABLE = "available"
    LOADING = "loading"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class InferenceType(str, Enum):
    """Types of inference requests."""
    COMPLETION = "completion"
    CHAT = "chat"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"


# Base MCP Protocol Schemas
class MCPMessage(BaseModel):
    """Base MCP protocol message."""
    type: MCPMessageType
    id: Optional[str] = Field(default=None, description="Message ID for request/response correlation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MCPRequest(MCPMessage):
    """MCP protocol request message."""
    type: MCPMessageType = MCPMessageType.REQUEST
    method: str = Field(description="Request method name")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Request parameters")


class MCPResponse(MCPMessage):
    """MCP protocol response message."""
    type: MCPMessageType = MCPMessageType.RESPONSE
    result: Optional[Dict[str, Any]] = Field(default=None, description="Response result")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")


class MCPError(MCPMessage):
    """MCP protocol error message."""
    type: MCPMessageType = MCPMessageType.ERROR
    code: int = Field(description="Error code")
    message: str = Field(description="Error message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional error data")


# Model Management Schemas
class ModelInfo(BaseModel):
    """Model information and metadata."""
    id: str = Field(description="Unique model identifier")
    name: str = Field(description="Human-readable model name")
    description: Optional[str] = Field(default=None, description="Model description")
    backend_type: str = Field(description="Model backend type")
    version: Optional[str] = Field(default=None, description="Model version")
    status: ModelStatus = Field(default=ModelStatus.AVAILABLE)
    capabilities: List[InferenceType] = Field(default_factory=list, description="Supported inference types")
    context_length: int = Field(default=4096, description="Maximum context length")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional model metadata")


class ModelRegistrationRequest(BaseModel):
    """Request to register a new model."""
    name: str = Field(description="Model name")
    backend_type: str = Field(description="Backend type")
    config: Dict[str, Any] = Field(description="Model configuration")
    description: Optional[str] = Field(default=None)
    capabilities: List[InferenceType] = Field(default_factory=list)


# Inference Schemas
class InferenceRequest(BaseModel):
    """Base inference request."""
    model_id: str = Field(description="Model ID to use for inference")
    inference_type: InferenceType = Field(description="Type of inference")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID for isolation")
    user_id: Optional[str] = Field(default=None, description="User ID for context")


class CompletionRequest(InferenceRequest):
    """Text completion request."""
    inference_type: InferenceType = InferenceType.COMPLETION
    prompt: str = Field(description="Input prompt")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0, description="Top-p sampling")
    stop_sequences: Optional[List[str]] = Field(default=None, description="Stop sequences")


class ChatMessage(BaseModel):
    """Chat message."""
    role: str = Field(description="Message role (user, assistant, system)")
    content: str = Field(description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ChatRequest(InferenceRequest):
    """Chat completion request."""
    inference_type: InferenceType = InferenceType.CHAT
    messages: List[ChatMessage] = Field(description="Chat conversation history")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: Optional[bool] = Field(default=False, description="Enable streaming response")


class EmbeddingRequest(InferenceRequest):
    """Text embedding request."""
    inference_type: InferenceType = InferenceType.EMBEDDING
    text: Union[str, List[str]] = Field(description="Text to embed")
    normalize: Optional[bool] = Field(default=True, description="Normalize embeddings")


class InferenceResponse(BaseModel):
    """Base inference response."""
    request_id: str = Field(description="Request ID")
    model_id: str = Field(description="Model ID used")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usage: Optional[Dict[str, int]] = Field(default=None, description="Token usage statistics")


class CompletionResponse(InferenceResponse):
    """Text completion response."""
    text: str = Field(description="Generated text")
    finish_reason: Optional[str] = Field(default=None, description="Reason for completion finish")


class ChatResponse(InferenceResponse):
    """Chat completion response."""
    message: ChatMessage = Field(description="Generated message")
    finish_reason: Optional[str] = Field(default=None, description="Reason for completion finish")


class EmbeddingResponse(InferenceResponse):
    """Text embedding response."""
    embeddings: List[List[float]] = Field(description="Generated embeddings")
    dimensions: int = Field(description="Embedding dimensions")


# Health Check Schemas
class ModelHealthStatus(BaseModel):
    """Model health status."""
    model_id: str = Field(description="Model ID")
    status: ModelStatus = Field(description="Current model status")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = Field(default=None, description="Last response time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if unhealthy")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    models: List[ModelHealthStatus] = Field(description="Model health statuses")
    system_info: Optional[Dict[str, Any]] = Field(default=None, description="System information")


# API Response Schemas
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(description="Request success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(description="Response items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Page size")
    has_next: bool = Field(description="Has next page")