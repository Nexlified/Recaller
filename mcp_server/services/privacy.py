"""
Privacy enforcement service for MCP server.

This module provides privacy protection mechanisms to ensure
that user data remains within the self-hosted environment.
"""

import logging
import re
from typing import Any, Dict, Optional, List
from urllib.parse import urlparse

try:
    from ..config.settings import mcp_settings
    from ..core.protocol import MCPProtocolError, MCPErrorCodes
except ImportError:
    from config.settings import mcp_settings
    from core.protocol import MCPProtocolError, MCPErrorCodes


logger = logging.getLogger(__name__)


class PrivacyEnforcer:
    """
    Privacy enforcement service.
    
    Provides mechanisms to ensure user data privacy and prevent
    data leakage outside the self-hosted environment.
    """
    
    def __init__(self):
        self._sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card pattern
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP addresses
        ]
        self._compiled_patterns = [re.compile(pattern) for pattern in self._sensitive_patterns]
    
    def validate_external_request(self, url: str) -> bool:
        """
        Validate if an external request is allowed.
        
        Args:
            url: URL to validate
            
        Returns:
            True if request is allowed
            
        Raises:
            MCPProtocolError: If request is blocked
        """
        if not mcp_settings.BLOCK_EXTERNAL_REQUESTS:
            return True
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        # Check if it's a local address
        if self._is_local_address(hostname):
            return True
        
        # Check whitelist
        if hostname in mcp_settings.ALLOWED_EXTERNAL_HOSTS:
            return True
        
        # Block external request
        logger.warning(f"Blocked external request to {hostname} for privacy protection")
        raise MCPProtocolError(
            code=MCPErrorCodes.TENANT_ACCESS_DENIED,
            message="External requests are blocked for privacy protection"
        )
    
    def _is_local_address(self, hostname: Optional[str]) -> bool:
        """Check if hostname is a local address."""
        if not hostname:
            return False
        
        local_addresses = [
            'localhost', '127.0.0.1', '::1',
            '0.0.0.0', '192.168.', '10.', '172.16.',
            '172.17.', '172.18.', '172.19.', '172.20.',
            '172.21.', '172.22.', '172.23.', '172.24.',
            '172.25.', '172.26.', '172.27.', '172.28.',
            '172.29.', '172.30.', '172.31.'
        ]
        
        hostname_lower = hostname.lower()
        return any(hostname_lower.startswith(addr) for addr in local_addresses)
    
    def sanitize_log_message(self, message: str) -> str:
        """
        Sanitize log messages to remove sensitive information.
        
        Args:
            message: Original log message
            
        Returns:
            Sanitized log message
        """
        if not mcp_settings.ANONYMIZE_LOGS:
            return message
        
        sanitized = message
        
        for pattern in self._compiled_patterns:
            sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized
    
    def sanitize_error_message(self, error_message: str) -> str:
        """
        Sanitize error messages to prevent data leakage.
        
        Args:
            error_message: Original error message
            
        Returns:
            Sanitized error message
        """
        if not mcp_settings.ANONYMIZE_ERROR_MESSAGES:
            return error_message
        
        # Remove potential file paths
        sanitized = re.sub(r'/[^\s]+', '[PATH]', error_message)
        
        # Remove potential URLs
        sanitized = re.sub(r'https?://[^\s]+', '[URL]', sanitized)
        
        # Apply general sanitization
        sanitized = self.sanitize_log_message(sanitized)
        
        return sanitized
    
    def validate_model_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize model configuration for privacy.
        
        Args:
            config: Model configuration
            
        Returns:
            Validated configuration
            
        Raises:
            MCPProtocolError: If configuration violates privacy rules
        """
        if not mcp_settings.ENFORCE_LOCAL_ONLY:
            return config
        
        # Check for external URLs in configuration
        for key, value in config.items():
            if isinstance(value, str) and (value.startswith('http://') or value.startswith('https://')):
                try:
                    self.validate_external_request(value)
                except MCPProtocolError:
                    raise MCPProtocolError(
                        code=MCPErrorCodes.INVALID_PARAMS,
                        message=f"External URL not allowed in configuration: {key}"
                    )
        
        return config
    
    def validate_inference_request(self, request_data: Dict[str, Any]) -> None:
        """
        Validate inference request for privacy compliance.
        
        Args:
            request_data: Request data to validate
            
        Raises:
            MCPProtocolError: If request violates privacy rules
        """
        # Check for potential external references in prompts
        if 'prompt' in request_data:
            self._check_for_external_references(request_data['prompt'])
        
        if 'messages' in request_data:
            for message in request_data.get('messages', []):
                if isinstance(message, dict) and 'content' in message:
                    self._check_for_external_references(message['content'])
    
    def _check_for_external_references(self, text: str) -> None:
        """Check text for external references that might leak data."""
        # Check for URLs
        url_pattern = r'https?://[^\s]+'
        if re.search(url_pattern, text):
            urls = re.findall(url_pattern, text)
            for url in urls:
                try:
                    self.validate_external_request(url)
                except MCPProtocolError:
                    if mcp_settings.ENFORCE_LOCAL_ONLY:
                        raise MCPProtocolError(
                            code=MCPErrorCodes.INVALID_PARAMS,
                            message="External URLs in prompts are blocked for privacy protection"
                        )
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """
        Get current privacy enforcement status.
        
        Returns:
            Privacy status information
        """
        return {
            "block_external_requests": mcp_settings.BLOCK_EXTERNAL_REQUESTS,
            "enforce_local_only": mcp_settings.ENFORCE_LOCAL_ONLY,
            "anonymize_logs": mcp_settings.ANONYMIZE_LOGS,
            "anonymize_errors": mcp_settings.ANONYMIZE_ERROR_MESSAGES,
            "allowed_external_hosts": len(mcp_settings.ALLOWED_EXTERNAL_HOSTS),
            "request_logging_enabled": mcp_settings.ENABLE_REQUEST_LOGGING,
            "data_retention_days": mcp_settings.DATA_RETENTION_DAYS
        }


# Global privacy enforcer instance
privacy_enforcer = PrivacyEnforcer()