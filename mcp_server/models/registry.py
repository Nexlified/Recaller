"""
Model registry and management service.

This module provides model registration, discovery, and lifecycle management
for the MCP server, supporting multiple backend types and configurations.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from enum import Enum

try:
    from ..schemas.mcp_schemas import (
        ModelInfo, ModelStatus, ModelRegistrationRequest, InferenceType
    )
    from ..config.settings import mcp_settings
    from ..services.privacy import privacy_enforcer
    from ..services.config_loader import config_loader
except ImportError:
    from schemas.mcp_schemas import (
        ModelInfo, ModelStatus, ModelRegistrationRequest, InferenceType
    )
    from config.settings import mcp_settings
    from services.privacy import privacy_enforcer
    from services.config_loader import config_loader


logger = logging.getLogger(__name__)


class ModelBackend:
    """Base class for model backends."""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        self.model_id = model_id
        self.config = config
        self.status = ModelStatus.LOADING
        self._last_health_check = None
    
    async def initialize(self) -> None:
        """Initialize the model backend."""
        raise NotImplementedError
    
    async def health_check(self) -> bool:
        """Perform a health check on the model."""
        raise NotImplementedError
    
    async def shutdown(self) -> None:
        """Shutdown the model backend."""
        raise NotImplementedError
    
    def get_capabilities(self) -> List[InferenceType]:
        """Get supported inference types."""
        raise NotImplementedError


class OllamaBackend(ModelBackend):
    """Ollama model backend implementation."""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model_name = config.get("model_name", model_id)
    
    async def initialize(self) -> None:
        """Initialize Ollama model."""
        try:
            # Check if Ollama is running and model is available
            # Implementation would use aiohttp to call Ollama API
            logger.info(f"Initializing Ollama model: {self.model_name}")
            self.status = ModelStatus.AVAILABLE
        except Exception as e:
            logger.error(f"Failed to initialize Ollama model {self.model_name}: {e}")
            self.status = ModelStatus.ERROR
            raise
    
    async def health_check(self) -> bool:
        """Check Ollama model health."""
        try:
            # Implementation would ping Ollama API
            self._last_health_check = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Ollama health check failed for {self.model_name}: {e}")
            return False
    
    def get_capabilities(self) -> List[InferenceType]:
        """Ollama typically supports completion and chat."""
        return [InferenceType.COMPLETION, InferenceType.CHAT]


class HuggingFaceBackend(ModelBackend):
    """HuggingFace model backend implementation."""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        self.model_name = config.get("model_name", model_id)
        self.device = config.get("device", "cpu")
        self.dtype = config.get("dtype", "float32")
    
    async def initialize(self) -> None:
        """Initialize HuggingFace model."""
        try:
            # Implementation would load HuggingFace model
            logger.info(f"Initializing HuggingFace model: {self.model_name}")
            self.status = ModelStatus.AVAILABLE
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace model {self.model_name}: {e}")
            self.status = ModelStatus.ERROR
            raise
    
    async def health_check(self) -> bool:
        """Check HuggingFace model health."""
        try:
            # Implementation would test model inference
            self._last_health_check = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"HuggingFace health check failed for {self.model_name}: {e}")
            return False
    
    def get_capabilities(self) -> List[InferenceType]:
        """HuggingFace can support multiple inference types."""
        return [
            InferenceType.COMPLETION, 
            InferenceType.CHAT, 
            InferenceType.EMBEDDING,
            InferenceType.CLASSIFICATION
        ]


class ModelRegistry:
    """
    Model registry and management service.
    
    Manages model lifecycle, registration, discovery, and health monitoring.
    """
    
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._backends: Dict[str, ModelBackend] = {}
        self._registry_path = mcp_settings.MODEL_REGISTRY_PATH
        self._backend_classes = {
            "ollama": OllamaBackend,
            "huggingface": HuggingFaceBackend,
            # Add more backend types as needed
        }
    
    async def initialize(self) -> None:
        """Initialize the model registry."""
        logger.info("Initializing model registry")
        
        # Create registry directory if it doesn't exist
        os.makedirs(self._registry_path, exist_ok=True)
        
        # Initialize configuration loader
        await config_loader.initialize()
        
        # Load models from configuration files first
        await self._load_models_from_config()
        
        # Load existing model configurations from registry
        await self._load_registry()
        
        # Initialize all registered models
        for model_id in list(self._models.keys()):
            try:
                await self._initialize_model(model_id)
            except Exception as e:
                logger.error(f"Failed to initialize model {model_id}: {e}")
    
    async def _load_models_from_config(self) -> None:
        """Load models from configuration files."""
        try:
            model_requests = await config_loader.get_model_requests()
            
            for request in model_requests:
                try:
                    # Use default tenant for configuration-loaded models
                    await self.register_model(request, "default")
                    logger.info(f"Loaded model from configuration: {request.name}")
                except Exception as e:
                    logger.error(f"Failed to load model from configuration {request.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load models from configuration: {e}")
    
    async def reload_configuration(self) -> bool:
        """
        Reload models from configuration files.
        
        Returns:
            True if configuration was reloaded successfully
        """
        try:
            # Check if configuration has changed
            if await config_loader.reload_configuration():
                logger.info("Reloading models from updated configuration")
                
                # Load new models from configuration
                await self._load_models_from_config()
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            raise
    
    async def register_model(self, request: ModelRegistrationRequest, tenant_id: str) -> str:
        """
        Register a new model.
        
        Args:
            request: Model registration request
            tenant_id: Tenant ID for isolation (from auth context)
            
        Returns:
            Model ID
        """
        # Create tenant-scoped model ID to prevent conflicts
        model_id = f"{tenant_id}_{request.backend_type}_{request.name}".lower().replace(" ", "_").replace("-", "_")
        
        # Check if model already exists for this tenant
        if model_id in self._models:
            raise ValueError(f"Model {request.name} already registered for tenant {tenant_id}")
        
        # Validate backend type
        if request.backend_type not in self._backend_classes:
            raise ValueError(f"Unsupported backend type: {request.backend_type}")
        
        # Validate configuration for privacy compliance
        validated_config = privacy_enforcer.validate_model_config(request.config)
        
        # Create model info with tenant isolation
        model_info = ModelInfo(
            id=model_id,
            name=request.name,
            description=request.description,
            backend_type=request.backend_type,
            capabilities=request.capabilities or [],
            status=ModelStatus.LOADING,
            tenant_id=tenant_id
        )
        
        # Register the model
        self._models[model_id] = model_info
        
        # Save to registry
        await self._save_model_config(model_id, validated_config)
        
        # Initialize the model backend
        try:
            await self._initialize_model(model_id, validated_config)
            logger.info(f"Successfully registered model: {model_id} for tenant: {tenant_id}")
        except Exception as e:
            # Remove from registry if initialization fails
            self._models.pop(model_id, None)
            logger.error(f"Failed to register model {model_id}: {e}")
            raise
        
        return model_id
    
    async def unregister_model(self, model_id: str, tenant_id: str) -> None:
        """
        Unregister a model.
        
        Args:
            model_id: Model ID to unregister
            tenant_id: Tenant ID for access control
        """
        if model_id not in self._models:
            raise ValueError(f"Model {model_id} not found")
        
        # Verify tenant ownership
        model = self._models[model_id]
        if model.tenant_id != tenant_id:
            raise ValueError(f"Access denied: Model {model_id} belongs to different tenant")
        
        # Shutdown backend if exists
        if model_id in self._backends:
            await self._backends[model_id].shutdown()
            del self._backends[model_id]
        
        # Remove from registry
        del self._models[model_id]
        
        # Remove config file
        config_path = os.path.join(self._registry_path, f"{model_id}.json")
        if os.path.exists(config_path):
            os.remove(config_path)
        
        logger.info(f"Unregistered model: {model_id} for tenant: {tenant_id}")
    
    def get_model(self, model_id: str, tenant_id: Optional[str] = None) -> Optional[ModelInfo]:
        """
        Get model information with tenant access control.
        
        Args:
            model_id: Model ID
            tenant_id: Tenant ID for access control (optional for admin access)
            
        Returns:
            Model information if accessible by tenant
        """
        model = self._models.get(model_id)
        if not model:
            return None
        
        # If tenant_id is provided, enforce tenant isolation
        if tenant_id is not None and model.tenant_id != tenant_id:
            return None
        
        return model
    
    def list_models(self, tenant_id: Optional[str] = None, status_filter: Optional[ModelStatus] = None) -> List[ModelInfo]:
        """
        List models with tenant isolation.
        
        Args:
            tenant_id: Tenant ID for filtering (None for admin access to all models)
            status_filter: Optional status filter
            
        Returns:
            List of models accessible by tenant
        """
        models = list(self._models.values())
        
        # Filter by tenant if specified
        if tenant_id is not None:
            models = [m for m in models if m.tenant_id == tenant_id]
        
        # Filter by status if specified
        if status_filter:
            models = [m for m in models if m.status == status_filter]
        
        return models
    
    def get_model_backend(self, model_id: str, tenant_id: Optional[str] = None) -> Optional[ModelBackend]:
        """
        Get model backend instance with tenant access control.
        
        Args:
            model_id: Model ID
            tenant_id: Tenant ID for access control
            
        Returns:
            Model backend if accessible by tenant
        """
        # Verify tenant access to model first
        model = self.get_model(model_id, tenant_id)
        if not model:
            return None
        
        return self._backends.get(model_id)
    
    async def health_check_model(self, model_id: str) -> bool:
        """Perform health check on a specific model."""
        backend = self._backends.get(model_id)
        if not backend:
            return False
        
        try:
            is_healthy = await backend.health_check()
            
            # Update model status
            model = self._models.get(model_id)
            if model:
                model.status = ModelStatus.AVAILABLE if is_healthy else ModelStatus.ERROR
                model.updated_at = datetime.utcnow()
            
            return is_healthy
        except Exception as e:
            logger.error(f"Health check error for model {model_id}: {e}")
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all models."""
        results = {}
        
        for model_id in self._models.keys():
            results[model_id] = await self.health_check_model(model_id)
        
        return results
    
    async def _load_registry(self) -> None:
        """Load model registry from disk."""
        if not os.path.exists(self._registry_path):
            return
        
        for filename in os.listdir(self._registry_path):
            if filename.endswith(".json"):
                model_id = filename[:-5]  # Remove .json extension
                config_path = os.path.join(self._registry_path, filename)
                
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    
                    # Create model info from config
                    model_info = ModelInfo(
                        id=model_id,
                        name=config.get("name", model_id),
                        description=config.get("description"),
                        backend_type=config.get("backend_type"),
                        capabilities=config.get("capabilities", []),
                        status=ModelStatus.LOADING,
                        tenant_id=config.get("tenant_id", "default")  # Use default for legacy models
                    )
                    
                    self._models[model_id] = model_info
                    
                except Exception as e:
                    logger.error(f"Failed to load model config {filename}: {e}")
    
    async def _save_model_config(self, model_id: str, config: Dict[str, Any]) -> None:
        """Save model configuration to disk."""
        config_path = os.path.join(self._registry_path, f"{model_id}.json")
        
        model_info = self._models[model_id]
        full_config = {
            "name": model_info.name,
            "description": model_info.description,
            "backend_type": model_info.backend_type,
            "capabilities": model_info.capabilities,
            "tenant_id": model_info.tenant_id,
            "config": config
        }
        
        with open(config_path, "w") as f:
            json.dump(full_config, f, indent=2)
    
    async def _initialize_model(self, model_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a model backend."""
        model_info = self._models[model_id]
        
        # Load config if not provided
        if config is None:
            config_path = os.path.join(self._registry_path, f"{model_id}.json")
            with open(config_path, "r") as f:
                full_config = json.load(f)
                config = full_config.get("config", {})
        
        # Get backend class
        backend_class = self._backend_classes.get(model_info.backend_type)
        if not backend_class:
            raise ValueError(f"Unknown backend type: {model_info.backend_type}")
        
        # Create and initialize backend
        backend = backend_class(model_id, config)
        await backend.initialize()
        
        # Update model info with backend capabilities
        model_info.capabilities = backend.get_capabilities()
        model_info.status = backend.status
        model_info.updated_at = datetime.utcnow()
        
        # Store backend
        self._backends[model_id] = backend
        
        logger.info(f"Initialized model backend: {model_id}")


# Global model registry instance
model_registry = ModelRegistry()
