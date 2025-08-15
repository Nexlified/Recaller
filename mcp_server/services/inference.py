"""
Inference service for handling model inference requests.

This module provides the business logic for processing different types
of inference requests through the registered model backends.
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from ..schemas.mcp_schemas import (
        CompletionRequest, ChatRequest, EmbeddingRequest,
        CompletionResponse, ChatResponse, EmbeddingResponse,
        InferenceType, ChatMessage
    )
    from ..models.registry import model_registry
    from ..core.protocol import MCPProtocolError, MCPErrorCodes
    from ..config.settings import mcp_settings
except ImportError:
    from schemas.mcp_schemas import (
        CompletionRequest, ChatRequest, EmbeddingRequest,
        CompletionResponse, ChatResponse, EmbeddingResponse,
        InferenceType, ChatMessage
    )
    from models.registry import model_registry
    from core.protocol import MCPProtocolError, MCPErrorCodes
    from config.settings import mcp_settings


logger = logging.getLogger(__name__)


class InferenceService:
    """
    Service for handling model inference requests.
    
    Provides a unified interface for different types of inference
    while managing rate limiting, context validation, and tenant isolation.
    """
    
    def __init__(self):
        self._active_requests: Dict[str, Dict[str, Any]] = {}
        self._request_counts: Dict[str, int] = {}
    
    async def completion(self, request: CompletionRequest) -> CompletionResponse:
        """
        Process a text completion request.
        
        Args:
            request: Completion request parameters
            
        Returns:
            Completion response
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Validate request
            await self._validate_request(request, InferenceType.COMPLETION)
            
            # Get model backend
            backend = model_registry.get_model_backend(request.model_id)
            if not backend:
                raise MCPProtocolError(
                    code=MCPErrorCodes.MODEL_NOT_AVAILABLE,
                    message=f"Model {request.model_id} not available"
                )
            
            # Check rate limits
            await self._check_rate_limits(request.tenant_id)
            
            # Track request
            self._track_request(request_id, request)
            
            # Process inference (placeholder - actual implementation depends on backend)
            generated_text = await self._process_completion(backend, request)
            
            # Create response
            response = CompletionResponse(
                request_id=request_id,
                model_id=request.model_id,
                text=generated_text,
                usage={
                    "prompt_tokens": len(request.prompt.split()),
                    "completion_tokens": len(generated_text.split()),
                    "total_tokens": len(request.prompt.split()) + len(generated_text.split())
                }
            )
            
            return response
            
        except MCPProtocolError:
            raise
        except Exception as e:
            logger.error(f"Completion inference failed: {e}")
            raise MCPProtocolError(
                code=MCPErrorCodes.INTERNAL_ERROR,
                message="Inference processing failed"
            )
        finally:
            self._untrack_request(request_id)
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat completion request.
        
        Args:
            request: Chat request parameters
            
        Returns:
            Chat response
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Validate request
            await self._validate_request(request, InferenceType.CHAT)
            
            # Get model backend
            backend = model_registry.get_model_backend(request.model_id)
            if not backend:
                raise MCPProtocolError(
                    code=MCPErrorCodes.MODEL_NOT_AVAILABLE,
                    message=f"Model {request.model_id} not available"
                )
            
            # Check rate limits
            await self._check_rate_limits(request.tenant_id)
            
            # Track request
            self._track_request(request_id, request)
            
            # Process inference
            response_message = await self._process_chat(backend, request)
            
            # Create response
            response = ChatResponse(
                request_id=request_id,
                model_id=request.model_id,
                message=response_message,
                usage={
                    "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                    "completion_tokens": len(response_message.content.split()),
                    "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_message.content.split())
                }
            )
            
            return response
            
        except MCPProtocolError:
            raise
        except Exception as e:
            logger.error(f"Chat inference failed: {e}")
            raise MCPProtocolError(
                code=MCPErrorCodes.INTERNAL_ERROR,
                message="Chat processing failed"
            )
        finally:
            self._untrack_request(request_id)
    
    async def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Process a text embedding request.
        
        Args:
            request: Embedding request parameters
            
        Returns:
            Embedding response
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Validate request
            await self._validate_request(request, InferenceType.EMBEDDING)
            
            # Get model backend
            backend = model_registry.get_model_backend(request.model_id)
            if not backend:
                raise MCPProtocolError(
                    code=MCPErrorCodes.MODEL_NOT_AVAILABLE,
                    message=f"Model {request.model_id} not available"
                )
            
            # Check rate limits
            await self._check_rate_limits(request.tenant_id)
            
            # Track request
            self._track_request(request_id, request)
            
            # Process inference
            embeddings = await self._process_embedding(backend, request)
            
            # Create response
            response = EmbeddingResponse(
                request_id=request_id,
                model_id=request.model_id,
                embeddings=embeddings,
                dimensions=len(embeddings[0]) if embeddings else 0,
                usage={
                    "prompt_tokens": len(str(request.text).split()),
                    "total_tokens": len(str(request.text).split())
                }
            )
            
            return response
            
        except MCPProtocolError:
            raise
        except Exception as e:
            logger.error(f"Embedding inference failed: {e}")
            raise MCPProtocolError(
                code=MCPErrorCodes.INTERNAL_ERROR,
                message="Embedding processing failed"
            )
        finally:
            self._untrack_request(request_id)
    
    async def _validate_request(self, request: Any, expected_type: InferenceType) -> None:
        """Validate inference request parameters."""
        # Check model exists and supports the inference type
        model = model_registry.get_model(request.model_id)
        if not model:
            raise MCPProtocolError(
                code=MCPErrorCodes.MODEL_NOT_AVAILABLE,
                message=f"Model {request.model_id} not found"
            )
        
        if expected_type not in model.capabilities:
            raise MCPProtocolError(
                code=MCPErrorCodes.INVALID_PARAMS,
                message=f"Model {request.model_id} does not support {expected_type.value}"
            )
        
        # Validate context length for text-based requests
        if hasattr(request, 'prompt'):
            prompt_length = len(request.prompt.split())
            if prompt_length > mcp_settings.MAX_CONTEXT_LENGTH:
                raise MCPProtocolError(
                    code=MCPErrorCodes.CONTEXT_TOO_LONG,
                    message=f"Prompt too long: {prompt_length} tokens > {mcp_settings.MAX_CONTEXT_LENGTH}"
                )
        
        if hasattr(request, 'messages'):
            total_length = sum(len(msg.content.split()) for msg in request.messages)
            if total_length > mcp_settings.MAX_CONTEXT_LENGTH:
                raise MCPProtocolError(
                    code=MCPErrorCodes.CONTEXT_TOO_LONG,
                    message=f"Conversation too long: {total_length} tokens > {mcp_settings.MAX_CONTEXT_LENGTH}"
                )
    
    async def _check_rate_limits(self, tenant_id: Optional[str]) -> None:
        """Check rate limits for the tenant."""
        if not tenant_id:
            return
        
        current_requests = sum(
            1 for req_info in self._active_requests.values()
            if req_info.get("tenant_id") == tenant_id
        )
        
        if current_requests >= mcp_settings.MAX_CONCURRENT_REQUESTS:
            raise MCPProtocolError(
                code=MCPErrorCodes.RATE_LIMIT_EXCEEDED,
                message=f"Rate limit exceeded: {current_requests} concurrent requests"
            )
    
    def _track_request(self, request_id: str, request: Any) -> None:
        """Track active request for monitoring and rate limiting."""
        self._active_requests[request_id] = {
            "tenant_id": getattr(request, 'tenant_id', None),
            "model_id": request.model_id,
            "inference_type": request.inference_type.value,
            "start_time": datetime.utcnow()
        }
    
    def _untrack_request(self, request_id: str) -> None:
        """Remove request from tracking."""
        self._active_requests.pop(request_id, None)
    
    async def _process_completion(self, backend, request: CompletionRequest) -> str:
        """
        Process completion request with the model backend.
        
        This is a placeholder implementation. The actual implementation
        would depend on the specific backend type and would call the
        appropriate model APIs or libraries.
        """
        # Placeholder implementation
        logger.info(f"Processing completion with {backend.model_id}")
        
        # This would be replaced with actual backend-specific inference
        if hasattr(backend, 'generate_completion'):
            return await backend.generate_completion(
                prompt=request.prompt,
                max_tokens=request.max_tokens or mcp_settings.MAX_RESPONSE_TOKENS,
                temperature=request.temperature or 0.7
            )
        else:
            # Fallback mock response for development/testing
            return f"Generated response for: {request.prompt[:50]}..."
    
    async def _process_chat(self, backend, request: ChatRequest) -> ChatMessage:
        """
        Process chat request with the model backend.
        
        This is a placeholder implementation. The actual implementation
        would depend on the specific backend type.
        """
        # Placeholder implementation
        logger.info(f"Processing chat with {backend.model_id}")
        
        # This would be replaced with actual backend-specific inference
        if hasattr(backend, 'generate_chat'):
            content = await backend.generate_chat(
                messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                max_tokens=request.max_tokens or mcp_settings.MAX_RESPONSE_TOKENS,
                temperature=request.temperature or 0.7
            )
        else:
            # Fallback mock response for development/testing
            last_message = request.messages[-1] if request.messages else None
            content = f"AI response to: {last_message.content[:50] if last_message else 'empty'}..."
        
        return ChatMessage(
            role="assistant",
            content=content
        )
    
    async def _process_embedding(self, backend, request: EmbeddingRequest) -> List[List[float]]:
        """
        Process embedding request with the model backend.
        
        This is a placeholder implementation. The actual implementation
        would depend on the specific backend type.
        """
        # Placeholder implementation
        logger.info(f"Processing embedding with {backend.model_id}")
        
        texts = [request.text] if isinstance(request.text, str) else request.text
        
        # This would be replaced with actual backend-specific inference
        if hasattr(backend, 'generate_embeddings'):
            return await backend.generate_embeddings(texts)
        else:
            # Fallback mock embeddings for development/testing
            import random
            return [[random.random() for _ in range(384)] for _ in texts]


# Global inference service instance
inference_service = InferenceService()
