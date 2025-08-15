# Extending the MCP Server with Custom Model Backends

This guide explains how to create custom model backends for the MCP server, allowing you to integrate with any AI/ML service or local model provider.

## Overview

The MCP server uses a pluggable backend architecture that allows easy integration of new model providers. Each backend implements a standard interface defined by the `ModelBackend` abstract base class.

## Backend Architecture

### Core Components

1. **ModelBackend**: Abstract base class defining the interface
2. **Backend Registry**: System for registering and managing backends
3. **Configuration System**: JSON-based configuration for model instances
4. **Health Monitoring**: Automatic health checks and status management

### Key Interfaces

All backends must implement these core methods:

- `initialize()`: Set up the backend and establish connections
- `health_check()`: Verify the backend is operational
- `shutdown()`: Clean up resources
- `get_capabilities()`: Return supported inference types
- `generate_completion()`: Text completion functionality
- `generate_chat_response()`: Chat-based interactions

## Creating a Custom Backend

### Step 1: Create the Backend Class

Create a new file in `mcp_server/backends/your_backend.py`:

```python
"""
Custom backend implementation for MCP server.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_backend import ModelBackend, ModelStatus, InferenceType

logger = logging.getLogger(__name__)


class CustomBackend(ModelBackend):
    """
    Custom model backend implementation.
    
    Example configuration:
    {
        "api_url": "https://your-api.com/v1",
        "api_key": "your-api-key",
        "model_name": "your-model",
        "timeout": 120,
        "max_retries": 3
    }
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Extract your backend-specific configuration
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.model_name = config.get("model_name", model_id)
        
        # Initialize any required clients or connections
        self._client = None
    
    async def initialize(self) -> None:
        """Initialize your backend."""
        try:
            logger.info(f"Initializing custom backend for model: {self.model_name}")
            
            # Set up your API client, authenticate, etc.
            await self._setup_client()
            
            # Verify the model is available
            await self._verify_model()
            
            self._update_status(ModelStatus.AVAILABLE)
            self._initialized = True
            
            logger.info(f"Successfully initialized custom backend: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize custom backend {self.model_name}: {e}")
            self._update_status(ModelStatus.ERROR)
            raise
    
    async def _setup_client(self) -> None:
        """Set up your API client."""
        # Implement your client setup logic
        pass
    
    async def _verify_model(self) -> None:
        """Verify the model is available."""
        # Implement model verification logic
        pass
    
    async def health_check(self) -> bool:
        """Check backend health."""
        try:
            # Implement your health check logic
            # This might involve pinging your API, testing a simple request, etc.
            
            is_healthy = True  # Replace with actual health check
            
            self._last_health_check = datetime.utcnow()
            
            if is_healthy:
                self._update_status(ModelStatus.AVAILABLE)
            else:
                self._update_status(ModelStatus.ERROR)
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed for {self.model_name}: {e}")
            self._update_status(ModelStatus.ERROR)
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the backend."""
        try:
            # Clean up resources, close connections, etc.
            if self._client:
                # await self._client.close()
                self._client = None
            
            self._update_status(ModelStatus.MAINTENANCE)
            self._initialized = False
            
            logger.info(f"Shutdown custom backend for model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Error during custom backend shutdown: {e}")
    
    def get_capabilities(self) -> List[InferenceType]:
        """Return supported inference types."""
        # Return the types your backend supports
        return [InferenceType.COMPLETION, InferenceType.CHAT]
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a text completion."""
        if not self._client or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        try:
            # Implement your completion logic
            # This might involve calling your API, running local inference, etc.
            
            result = f"Custom completion for: {prompt[:50]}..."
            return result
            
        except Exception as e:
            raise Exception(f"Completion generation failed: {e}")
    
    async def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat response."""
        if not self._client or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        try:
            # Implement your chat logic
            # Convert messages to your API format and generate response
            
            result = f"Custom chat response for {len(messages)} messages"
            return result
            
        except Exception as e:
            raise Exception(f"Chat generation failed: {e}")
```

### Step 2: Register the Backend

Update `mcp_server/backends/__init__.py` to include your backend:

```python
from .your_backend import CustomBackend

__all__ = [
    "ModelBackend",
    "OllamaBackend", 
    "HuggingFaceBackend",
    "CustomBackend"  # Add your backend
]
```

### Step 3: Register in the Model Registry

Update the `_backend_classes` mapping in `mcp_server/models/registry.py`:

```python
from ..backends import ModelBackend, OllamaBackend, HuggingFaceBackend, CustomBackend

# In ModelRegistry.__init__()
self._backend_classes = {
    "ollama": OllamaBackend,
    "huggingface": HuggingFaceBackend,
    "custom": CustomBackend,  # Add your backend
}
```

### Step 4: Create Configuration

Create a configuration file or register via API:

```json
{
  "name": "My Custom Model",
  "backend_type": "custom",
  "config": {
    "api_url": "https://your-api.com/v1",
    "api_key": "your-api-key",
    "model_name": "your-model",
    "timeout": 120,
    "max_retries": 3
  },
  "capabilities": ["completion", "chat"]
}
```

## Backend Implementation Guidelines

### Error Handling

Always implement proper error handling:

```python
try:
    # Your implementation
    pass
except Exception as e:
    logger.error(f"Operation failed: {e}")
    self._update_status(ModelStatus.ERROR)
    raise
```

### Status Management

Use the provided status update method:

```python
# Update status when things change
self._update_status(ModelStatus.AVAILABLE)
self._update_status(ModelStatus.ERROR)
self._update_status(ModelStatus.MAINTENANCE)
```

### Logging

Use structured logging:

```python
logger.info(f"Starting operation for model: {self.model_id}")
logger.warning(f"Retry attempt {attempt} for model: {self.model_id}")
logger.error(f"Operation failed for model: {self.model_id}: {error}")
```

### Configuration Validation

Validate configuration in `__init__`:

```python
def __init__(self, model_id: str, config: Dict[str, Any]):
    super().__init__(model_id, config)
    
    # Validate required configuration
    if not config.get("api_url"):
        raise ValueError("api_url is required for custom backend")
    
    if not config.get("api_key"):
        raise ValueError("api_key is required for custom backend")
```

### Async Best Practices

Use proper async/await patterns:

```python
async def _make_api_call(self, data: Dict[str, Any]) -> Dict[str, Any]:
    async with self._session.post(self.api_url, json=data) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"API error: {response.status}")
```

## Advanced Features

### Streaming Support

For streaming responses:

```python
async def generate_completion_stream(self, prompt: str, **kwargs):
    """Generate streaming completion."""
    async for chunk in self._stream_generate(prompt, **kwargs):
        yield chunk

async def _stream_generate(self, prompt: str, **kwargs):
    # Implement streaming logic
    async with self._session.post(url, json=data) as response:
        async for line in response.content:
            yield process_line(line)
```

### Custom Inference Types

Add support for specialized inference:

```python
async def generate_embedding(self, text: str, **kwargs) -> List[float]:
    """Generate embeddings if your backend supports it."""
    if InferenceType.EMBEDDING not in self.get_capabilities():
        raise NotImplementedError("Embeddings not supported")
    
    # Implement embedding generation
    return embedding_vector

async def classify_text(self, text: str, labels: List[str], **kwargs) -> Dict[str, float]:
    """Classify text if your backend supports it."""
    if InferenceType.CLASSIFICATION not in self.get_capabilities():
        raise NotImplementedError("Classification not supported")
    
    # Implement classification
    return label_scores
```

### Resource Management

Implement proper resource management:

```python
async def __aenter__(self):
    await self.initialize()
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.shutdown()
```

## Testing Your Backend

### Unit Tests

Create tests for your backend:

```python
import pytest
from your_backend import CustomBackend

@pytest.mark.asyncio
async def test_custom_backend_initialization():
    config = {
        "api_url": "https://test-api.com",
        "api_key": "test-key",
        "model_name": "test-model"
    }
    
    backend = CustomBackend("test-model", config)
    
    # Test initialization
    await backend.initialize()
    assert backend.status == ModelStatus.AVAILABLE
    
    # Test health check
    is_healthy = await backend.health_check()
    assert is_healthy
    
    # Test generation
    result = await backend.generate_completion("Hello world")
    assert isinstance(result, str)
    
    # Clean up
    await backend.shutdown()
```

### Integration Tests

Test with the full MCP server:

```python
@pytest.mark.asyncio
async def test_backend_registration():
    from models.registry import model_registry
    
    request = ModelRegistrationRequest(
        name="Test Custom Model",
        backend_type="custom",
        config={
            "api_url": "https://test-api.com",
            "api_key": "test-key"
        }
    )
    
    model_id = await model_registry.register_model(request, "test-tenant")
    
    # Test model is registered and available
    model = model_registry.get_model(model_id, "test-tenant")
    assert model is not None
    assert model.status == ModelStatus.AVAILABLE
```

## Configuration Examples

### Local Model Backend

```json
{
  "name": "Local PyTorch Model",
  "backend_type": "pytorch_local",
  "config": {
    "model_path": "/path/to/model",
    "device": "cuda:0",
    "batch_size": 1,
    "max_length": 2048
  }
}
```

### API-based Backend

```json
{
  "name": "External API Model",
  "backend_type": "external_api",
  "config": {
    "base_url": "https://api.example.com/v1",
    "api_key": "${API_KEY}",
    "model_id": "gpt-3.5-turbo",
    "timeout": 60,
    "rate_limit": 100
  }
}
```

### Embedding-specific Backend

```json
{
  "name": "Sentence Transformer",
  "backend_type": "sentence_transformers",
  "config": {
    "model_name": "all-MiniLM-L6-v2",
    "device": "cpu",
    "normalize_embeddings": true
  },
  "capabilities": ["embedding"]
}
```

## Best Practices

1. **Error Handling**: Always handle errors gracefully and update status appropriately
2. **Logging**: Use structured logging for debugging and monitoring
3. **Configuration**: Validate configuration and provide clear error messages
4. **Resource Management**: Properly initialize and clean up resources
5. **Status Updates**: Keep model status current for health monitoring
6. **Documentation**: Document your backend's configuration options and capabilities
7. **Testing**: Write comprehensive tests for your backend
8. **Performance**: Consider timeout, retry, and rate limiting strategies
9. **Security**: Protect API keys and sensitive configuration
10. **Compatibility**: Follow the established patterns and interfaces

## Deployment

### Docker Integration

If your backend has dependencies, create a custom Docker image:

```dockerfile
FROM python:3.12-slim

# Install your backend's dependencies
RUN pip install your-backend-dependencies

# Copy MCP server code
COPY mcp_server/ /app/mcp_server/
WORKDIR /app

# Install MCP server requirements
RUN pip install -r mcp_server/requirements.txt

CMD ["python", "-m", "mcp_server.main"]
```

### Environment Configuration

Use environment variables for sensitive configuration:

```bash
# .env file
CUSTOM_BACKEND_API_KEY=your-secret-key
CUSTOM_BACKEND_URL=https://your-api.com

# Configuration can reference environment variables
"api_key": "${CUSTOM_BACKEND_API_KEY}"
```

This guide provides a comprehensive foundation for creating custom model backends. The modular architecture makes it easy to add support for any AI/ML service or local model provider while maintaining consistency and reliability.