"""
Example OpenAI-compatible backend implementation for MCP server.

This example demonstrates how to create a backend that works with
OpenAI-compatible APIs like LocalAI, Oobabooga, vLLM, etc.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp

# Import with proper handling for both package and direct execution
try:
    from ..backends.base_backend import ModelBackend, ModelStatus, InferenceType
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from backends.base_backend import ModelBackend, ModelStatus, InferenceType

logger = logging.getLogger(__name__)


class OpenAICompatibleBackend(ModelBackend):
    """
    OpenAI-compatible API backend implementation.
    
    This backend works with any API that follows the OpenAI API format,
    including LocalAI, Oobabooga, vLLM, and other local inference servers.
    
    Example configuration:
    {
        "base_url": "http://localhost:8080/v1",
        "api_key": "your-api-key-or-none",
        "model_name": "your-model",
        "timeout": 120,
        "max_retries": 3,
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": false
    }
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # OpenAI-compatible API configuration
        self.base_url = config.get("base_url", "http://localhost:8080/v1")
        self.api_key = config.get("api_key")  # Optional for local APIs
        self.model_name = config.get("model_name", model_id)
        
        # Generation parameters
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1024)
        self.stream = config.get("stream", False)
        
        # Ensure URLs are properly formatted
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        self._session = None
        self._headers = {"Content-Type": "application/json"}
        
        # Add authorization header if API key is provided
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def initialize(self) -> None:
        """Initialize OpenAI-compatible backend."""
        try:
            logger.info(f"Initializing OpenAI-compatible backend: {self.model_name} at {self.base_url}")
            
            # Create HTTP session
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=self._headers
            )
            
            # Check if API is running
            await self._check_api_health()
            
            # Check if model is available
            await self._check_model_availability()
            
            self._update_status(ModelStatus.AVAILABLE)
            self._initialized = True
            
            logger.info(f"Successfully initialized OpenAI-compatible backend: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI-compatible backend {self.model_name}: {e}")
            self._update_status(ModelStatus.ERROR)
            if self._session:
                await self._session.close()
                self._session = None
            raise
    
    async def _check_api_health(self) -> None:
        """Check if the OpenAI-compatible API is running."""
        try:
            # Try to get models list to verify API is working
            async with self._session.get(f"{self.base_url}models") as response:
                if response.status == 200:
                    models_data = await response.json()
                    logger.info(f"Connected to OpenAI-compatible API with {len(models_data.get('data', []))} models")
                else:
                    raise Exception(f"API health check returned status {response.status}")
        except Exception as e:
            raise Exception(f"Cannot connect to OpenAI-compatible API at {self.base_url}: {e}")
    
    async def _check_model_availability(self) -> None:
        """Check if the specified model is available."""
        try:
            # Get list of available models
            async with self._session.get(f"{self.base_url}models") as response:
                if response.status == 200:
                    models_data = await response.json()
                    available_models = [model.get('id', '') for model in models_data.get('data', [])]
                    
                    if self.model_name in available_models:
                        logger.info(f"Model {self.model_name} is available")
                    else:
                        logger.warning(f"Model {self.model_name} not found in available models: {available_models}")
                        # Some APIs don't list models properly, so we'll continue anyway
                else:
                    logger.warning(f"Could not verify model availability: status {response.status}")
        except Exception as e:
            logger.warning(f"Error checking model availability: {e}")
            # Continue anyway, as some APIs may not support model listing
    
    async def health_check(self) -> bool:
        """Check OpenAI-compatible backend health."""
        try:
            if not self._session:
                return False
            
            # Simple ping to check API availability
            async with self._session.get(f"{self.base_url}models") as response:
                is_healthy = response.status == 200
                
                if is_healthy:
                    # Optional: Test with a small completion request
                    try:
                        await self._test_completion()
                    except Exception as e:
                        logger.warning(f"Health check completion test failed: {e}")
                        is_healthy = False
                
                self._last_health_check = datetime.utcnow()
                
                # Update status based on health
                if is_healthy:
                    self._update_status(ModelStatus.AVAILABLE)
                else:
                    self._update_status(ModelStatus.ERROR)
                
                return is_healthy
                
        except Exception as e:
            logger.error(f"OpenAI-compatible health check failed for {self.model_name}: {e}")
            self._update_status(ModelStatus.ERROR)
            return False
    
    async def _test_completion(self) -> None:
        """Test completion functionality for health check."""
        test_data = {
            "model": self.model_name,
            "prompt": "Hello",
            "max_tokens": 5,
            "temperature": 0.1
        }
        
        async with self._session.post(f"{self.base_url}completions", json=test_data) as response:
            if response.status != 200:
                raise Exception(f"Test completion failed with status {response.status}")
    
    async def shutdown(self) -> None:
        """Shutdown the OpenAI-compatible backend."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self._update_status(ModelStatus.MAINTENANCE)
            self._initialized = False
            
            logger.info(f"Shutdown OpenAI-compatible backend for model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Error during OpenAI-compatible backend shutdown: {e}")
    
    def get_capabilities(self) -> List[InferenceType]:
        """OpenAI-compatible APIs typically support completion and chat."""
        return [InferenceType.COMPLETION, InferenceType.CHAT]
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a text completion using OpenAI-compatible API."""
        if not self._session or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        try:
            # Prepare request data
            request_data = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": kwargs.get("stream", self.stream)
            }
            
            # Add optional parameters
            if "top_p" in kwargs:
                request_data["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                request_data["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                request_data["presence_penalty"] = kwargs["presence_penalty"]
            
            async with self._session.post(f"{self.base_url}completions", json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract completion text
                    choices = result.get("choices", [])
                    if choices:
                        return choices[0].get("text", "")
                    else:
                        raise Exception("No completion choices returned")
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                    
        except Exception as e:
            raise Exception(f"Completion generation failed: {e}")
    
    async def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat response using OpenAI-compatible API."""
        if not self._session or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        try:
            # Prepare request data for chat completion
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": kwargs.get("stream", self.stream)
            }
            
            # Add optional parameters
            if "top_p" in kwargs:
                request_data["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                request_data["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                request_data["presence_penalty"] = kwargs["presence_penalty"]
            
            async with self._session.post(f"{self.base_url}chat/completions", json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract chat response
                    choices = result.get("choices", [])
                    if choices:
                        message = choices[0].get("message", {})
                        return message.get("content", "")
                    else:
                        raise Exception("No chat choices returned")
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                    
        except Exception as e:
            raise Exception(f"Chat generation failed: {e}")
    
    async def generate_embedding(self, text: str, **kwargs) -> List[float]:
        """Generate embeddings if the API supports it."""
        if not self._session or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        try:
            request_data = {
                "model": self.model_name,
                "input": text
            }
            
            async with self._session.post(f"{self.base_url}embeddings", json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract embedding
                    data = result.get("data", [])
                    if data:
                        return data[0].get("embedding", [])
                    else:
                        raise Exception("No embedding data returned")
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                    
        except Exception as e:
            raise Exception(f"Embedding generation failed: {e}")


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_openai_compatible_backend():
        """Test the OpenAI-compatible backend."""
        config = {
            "base_url": "http://localhost:8080/v1",
            "model_name": "test-model",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        backend = OpenAICompatibleBackend("test-model", config)
        
        try:
            # Initialize backend
            print("Initializing backend...")
            await backend.initialize()
            print(f"Backend status: {backend.status}")
            
            # Test health check
            print("Testing health check...")
            healthy = await backend.health_check()
            print(f"Health check: {'PASS' if healthy else 'FAIL'}")
            
            # Test completion
            if healthy:
                print("Testing completion...")
                result = await backend.generate_completion("Hello, world!")
                print(f"Completion result: {result}")
                
                # Test chat
                print("Testing chat...")
                messages = [
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there!"},
                    {"role": "user", "content": "How are you?"}
                ]
                chat_result = await backend.generate_chat_response(messages)
                print(f"Chat result: {chat_result}")
            
        except Exception as e:
            print(f"Test failed: {e}")
        
        finally:
            # Clean up
            print("Shutting down backend...")
            await backend.shutdown()
            print("Test complete")
    
    # Uncomment to run test
    # asyncio.run(test_openai_compatible_backend())