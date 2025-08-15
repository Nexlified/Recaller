"""
Model backends for the MCP server.

This module contains various model backend implementations that integrate
with different AI/ML services and local model providers.
"""

from .ollama_backend import OllamaBackend
from .huggingface_backend import HuggingFaceBackend
from .base_backend import ModelBackend

__all__ = [
    "ModelBackend",
    "OllamaBackend", 
    "HuggingFaceBackend"
]