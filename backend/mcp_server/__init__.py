"""
MCP Server for Recaller - Model Context Protocol Implementation

This module provides the MCP (Model Context Protocol) server implementation for Recaller,
enabling secure, privacy-first connections with local or self-hosted Large Language Models.

The MCP server acts as a bridge between the FastAPI backend and LLMs, supporting:
- On-device AI features
- Extensible model management
- Tenant isolation and privacy
- Standardized LLM communication via MCP v1 protocol
"""

__version__ = "1.0.0"
__author__ = "Recaller Team"
__description__ = "MCP Server for Recaller LLM Integration"