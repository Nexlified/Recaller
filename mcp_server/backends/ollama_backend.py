"""
Ollama backend implementation for MCP server.

This module provides a complete implementation of the Ollama backend,
demonstrating how to create a functional model backend for the MCP server.
"""

import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .base_backend import ModelBackend, ModelStatus, InferenceType

logger = logging.getLogger(__name__)


class OllamaBackend(ModelBackend):
    """
    Ollama model backend implementation.
    
    This backend integrates with Ollama (https://ollama.ai/) to provide
    local LLM inference capabilities. It demonstrates a complete backend
    implementation with real API integration.
    
    Example configuration:
    {
        "base_url": "http://localhost:11434",
        "model_name": "llama3.2:3b",
        "timeout": 120,
        "max_retries": 3,
        "stream": false,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 1024
    }
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Ollama-specific configuration
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model_name = config.get("model_name", model_id)
        self.stream = config.get("stream", False)
        
        # Generation parameters
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9) 
        self.max_tokens = config.get("max_tokens", 1024)
        
        # Ensure URLs are properly formatted
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        self._session = None
        
    async def initialize(self) -> None:
        """Initialize Ollama model backend."""
        try:
            logger.info(f"Initializing Ollama model: {self.model_name} at {self.base_url}")
            
            # Create HTTP session
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Check if Ollama is running
            await self._check_ollama_service()
            
            # Check if model is available
            await self._check_model_availability()
            
            self._update_status(ModelStatus.AVAILABLE)
            self._initialized = True
            
            logger.info(f"Successfully initialized Ollama model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama model {self.model_name}: {e}")
            self._update_status(ModelStatus.ERROR)
            if self._session:
                await self._session.close()
                self._session = None
            raise
    
    async def _check_ollama_service(self) -> None:
        """Check if Ollama service is running."""
        try:
            async with self._session.get(f"{self.base_url}api/version") as response:
                if response.status == 200:
                    version_info = await response.json()
                    logger.info(f"Connected to Ollama service version: {version_info.get('version', 'unknown')}")
                else:
                    raise Exception(f"Ollama service returned status {response.status}")
        except Exception as e:
            raise Exception(f"Cannot connect to Ollama service at {self.base_url}: {e}")
    
    async def _check_model_availability(self) -> None:
        """Check if the specified model is available."""
        try:
            # List available models
            async with self._session.get(f"{self.base_url}api/tags") as response:
                if response.status == 200:
                    models_data = await response.json()
                    available_models = [model['name'] for model in models_data.get('models', [])]
                    
                    if self.model_name not in available_models:
                        # Try to pull the model
                        logger.info(f"Model {self.model_name} not found. Attempting to pull...")
                        await self._pull_model()
                    else:
                        logger.info(f"Model {self.model_name} is available")
                else:
                    raise Exception(f"Failed to list models: status {response.status}")
        except Exception as e:
            raise Exception(f"Error checking model availability: {e}")
    
    async def _pull_model(self) -> None:
        """Pull the model from Ollama registry."""
        try:
            pull_data = {"name": self.model_name}
            
            async with self._session.post(
                f"{self.base_url}api/pull",
                json=pull_data
            ) as response:
                if response.status == 200:
                    # Read the streaming response
                    async for line in response.content:
                        if line:
                            data = json.loads(line)
                            if data.get('status'):
                                logger.info(f"Pulling {self.model_name}: {data['status']}")
                            if data.get('error'):
                                raise Exception(f"Pull failed: {data['error']}")
                    
                    logger.info(f"Successfully pulled model: {self.model_name}")
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to pull model: {error_text}")
        except Exception as e:
            raise Exception(f"Error pulling model {self.model_name}: {e}")
    
    async def health_check(self) -> bool:
        """Check Ollama model health."""
        try:
            if not self._session:
                return False
            
            # Simple ping to check service availability
            async with self._session.get(f"{self.base_url}api/version") as response:
                is_healthy = response.status == 200
                
                if is_healthy:
                    # Optional: Test with a small generation request
                    test_prompt = "Hello"
                    try:
                        await self._generate_with_retries(test_prompt, max_tokens=5)
                    except Exception as e:
                        logger.warning(f"Health check generation test failed: {e}")
                        is_healthy = False
                
                self._last_health_check = datetime.utcnow()
                
                # Update status based on health
                if is_healthy:
                    self._update_status(ModelStatus.AVAILABLE)
                else:
                    self._update_status(ModelStatus.ERROR)
                
                return is_healthy
                
        except Exception as e:
            logger.error(f"Ollama health check failed for {self.model_name}: {e}")
            self._update_status(ModelStatus.ERROR)
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the Ollama backend."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self._update_status(ModelStatus.MAINTENANCE)
            self._initialized = False
            
            logger.info(f"Shutdown Ollama backend for model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Error during Ollama backend shutdown: {e}")
    
    def get_capabilities(self) -> List[InferenceType]:
        """Ollama supports completion and chat inference."""
        return [InferenceType.COMPLETION, InferenceType.CHAT]
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a text completion using Ollama."""
        if not self._session or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        # Merge generation parameters
        generation_params = {
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        return await self._generate_with_retries(prompt, **generation_params)
    
    async def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat response using Ollama."""
        if not self._session or self.status != ModelStatus.AVAILABLE:
            raise Exception(f"Model {self.model_id} is not available")
        
        # Convert messages to Ollama format and extract the conversation
        if messages:
            # For now, concatenate messages into a single prompt
            # A more sophisticated implementation would use Ollama's chat API
            conversation = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conversation += f"{role}: {content}\n"
            
            conversation += "assistant: "
            
            # Merge generation parameters
            generation_params = {
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens)
            }
            
            return await self._generate_with_retries(conversation, **generation_params)
        else:
            raise ValueError("No messages provided for chat")
    
    async def _generate_with_retries(self, prompt: str, **generation_params) -> str:
        """Generate text with automatic retries."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await self._generate_text(prompt, **generation_params)
            except Exception as e:
                last_exception = e
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)  # Brief delay before retry
        
        raise Exception(f"All {self.max_retries} generation attempts failed. Last error: {last_exception}")
    
    async def _generate_text(self, prompt: str, **generation_params) -> str:
        """Core text generation logic."""
        # Prepare request data for Ollama API
        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": self.stream,
            "options": {
                "temperature": generation_params.get("temperature", self.temperature),
                "top_p": generation_params.get("top_p", self.top_p),
                "num_predict": generation_params.get("max_tokens", self.max_tokens)
            }
        }
        
        try:
            async with self._session.post(
                f"{self.base_url}api/generate",
                json=request_data
            ) as response:
                
                if response.status == 200:
                    if self.stream:
                        # Handle streaming response
                        generated_text = ""
                        async for line in response.content:
                            if line:
                                data = json.loads(line)
                                if data.get('response'):
                                    generated_text += data['response']
                                if data.get('done'):
                                    break
                        return generated_text
                    else:
                        # Handle non-streaming response
                        result = await response.json()
                        return result.get('response', '')
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP client error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error: {e}")
        except Exception as e:
            raise Exception(f"Generation error: {e}")