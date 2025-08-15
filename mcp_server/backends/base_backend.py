"""
Base model backend class for MCP server.

This module defines the abstract base class for all model backends,
establishing the interface that all backend implementations must follow.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod

# Import schemas with proper handling for both package and direct execution
try:
    from ..schemas.mcp_schemas import ModelStatus, InferenceType
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from schemas.mcp_schemas import ModelStatus, InferenceType

logger = logging.getLogger(__name__)


class ModelBackend(ABC):
    """
    Abstract base class for model backends.
    
    This class defines the interface that all model backends must implement
    to integrate with the MCP server's model management system.
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        """
        Initialize the model backend.
        
        Args:
            model_id: Unique identifier for the model
            config: Backend-specific configuration dictionary
        """
        self.model_id = model_id
        self.config = config
        self.status = ModelStatus.LOADING
        self._last_health_check = None
        self._initialized = False
        
        # Extract common configuration
        self.timeout = config.get("timeout", 120)
        self.max_retries = config.get("max_retries", 3)
        
        logger.info(f"Created {self.__class__.__name__} backend for model: {model_id}")
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the model backend.
        
        This method should:
        1. Establish connection to the model service
        2. Validate model availability
        3. Set up any required resources
        4. Update status to AVAILABLE or ERROR
        
        Raises:
            Exception: If initialization fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Perform a health check on the model.
        
        This method should:
        1. Test basic connectivity to the model service
        2. Verify the model is responsive
        3. Update _last_health_check timestamp
        
        Returns:
            True if the model is healthy and available
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Shutdown the model backend.
        
        This method should:
        1. Clean up any resources
        2. Close connections
        3. Update status appropriately
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[InferenceType]:
        """
        Get the inference types supported by this backend.
        
        Returns:
            List of supported InferenceType values
        """
        pass
    
    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Generate a text completion.
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional generation parameters
            
        Returns:
            Generated completion text
            
        Raises:
            NotImplementedError: If completion is not supported
        """
        pass
    
    @abstractmethod
    async def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat response.
        
        Args:
            messages: List of chat messages with 'role' and 'content' keys
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
            
        Raises:
            NotImplementedError: If chat is not supported
        """
        pass
    
    async def generate_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Generate text embeddings.
        
        Args:
            text: Input text to embed
            **kwargs: Additional embedding parameters
            
        Returns:
            List of embedding values
            
        Raises:
            NotImplementedError: If embeddings are not supported
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support embeddings")
    
    async def classify_text(self, text: str, labels: List[str], **kwargs) -> Dict[str, float]:
        """
        Classify text against provided labels.
        
        Args:
            text: Input text to classify
            labels: List of possible classification labels
            **kwargs: Additional classification parameters
            
        Returns:
            Dictionary mapping labels to confidence scores
            
        Raises:
            NotImplementedError: If classification is not supported
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support classification")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get detailed information about this model backend.
        
        Returns:
            Dictionary containing model metadata
        """
        return {
            "model_id": self.model_id,
            "backend_type": self.__class__.__name__.lower().replace("backend", ""),
            "status": self.status,
            "capabilities": self.get_capabilities(),
            "config": {k: v for k, v in self.config.items() if not k.startswith("_")},
            "last_health_check": self._last_health_check,
            "initialized": self._initialized
        }
    
    def _update_status(self, status: ModelStatus) -> None:
        """Update the backend status and log the change."""
        old_status = self.status
        self.status = status
        if old_status != status:
            logger.info(f"Model {self.model_id} status changed: {old_status} -> {status}")