"""
Tests for privacy enforcement in MCP server.

These tests verify that privacy protection mechanisms work correctly
and prevent data leakage outside the self-hosted environment.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.privacy import privacy_enforcer
from core.protocol import MCPProtocolError, MCPErrorCodes
from config.settings import mcp_settings


class TestPrivacyEnforcer:
    """Test privacy enforcement mechanisms."""
    
    def test_external_request_validation_blocks_external_urls(self):
        """Test that external URLs are blocked when privacy protection is enabled."""
        # Test various external URLs
        external_urls = [
            "https://api.openai.com/v1/completions",
            "http://external-service.com/api",
            "https://huggingface.co/models",
            "http://suspicious-site.evil"
        ]
        
        for url in external_urls:
            with pytest.raises(MCPProtocolError, match="External requests are blocked"):
                privacy_enforcer.validate_external_request(url)
    
    def test_external_request_validation_allows_local_urls(self):
        """Test that local URLs are allowed."""
        local_urls = [
            "http://localhost:8080/api",
            "http://127.0.0.1:11434/api",
            "http://192.168.1.100:3000",
            "http://10.0.0.5:5000",
            "http://172.16.0.1:8000"
        ]
        
        for url in local_urls:
            # Should not raise an exception
            result = privacy_enforcer.validate_external_request(url)
            assert result is True
    
    def test_external_request_validation_respects_whitelist(self):
        """Test that whitelisted external hosts are allowed."""
        with patch.object(mcp_settings, 'ALLOWED_EXTERNAL_HOSTS', ['api.trusted-partner.com']):
            # Should be allowed due to whitelist
            result = privacy_enforcer.validate_external_request("https://api.trusted-partner.com/data")
            assert result is True
            
            # Should still be blocked
            with pytest.raises(MCPProtocolError):
                privacy_enforcer.validate_external_request("https://malicious-site.com/steal-data")
    
    def test_external_request_validation_disabled(self):
        """Test that external request blocking can be disabled."""
        with patch.object(mcp_settings, 'BLOCK_EXTERNAL_REQUESTS', False):
            # Should be allowed when blocking is disabled
            result = privacy_enforcer.validate_external_request("https://any-external-site.com")
            assert result is True
    
    def test_log_message_sanitization(self):
        """Test that sensitive information is removed from log messages."""
        sensitive_message = "User email is user@example.com and SSN is 123-45-6789"
        sanitized = privacy_enforcer.sanitize_log_message(sensitive_message)
        
        assert "user@example.com" not in sanitized
        assert "123-45-6789" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_log_message_sanitization_respects_setting(self):
        """Test that log sanitization can be disabled."""
        sensitive_message = "User email is user@example.com"
        
        with patch.object(mcp_settings, 'ANONYMIZE_LOGS', False):
            sanitized = privacy_enforcer.sanitize_log_message(sensitive_message)
            # Should not be sanitized when setting is disabled
            assert "user@example.com" in sanitized
    
    def test_error_message_sanitization(self):
        """Test that error messages are sanitized to prevent data leakage."""
        error_with_paths = "File not found: /home/user/secret/data.txt at https://internal-api.com/users"
        sanitized = privacy_enforcer.sanitize_error_message(error_with_paths)
        
        assert "/home/user/secret/data.txt" not in sanitized
        assert "https://internal-api.com/users" not in sanitized
        assert "[PATH]" in sanitized
        assert "[URL]" in sanitized
    
    def test_error_message_sanitization_disabled(self):
        """Test that error message sanitization can be disabled."""
        error_message = "Internal error at /path/to/file"
        
        with patch.object(mcp_settings, 'ANONYMIZE_ERROR_MESSAGES', False):
            sanitized = privacy_enforcer.sanitize_error_message(error_message)
            assert "/path/to/file" in sanitized
    
    def test_model_config_validation_blocks_external_urls(self):
        """Test that model configurations with external URLs are blocked."""
        config_with_external_url = {
            "base_url": "https://api.openai.com",
            "model_name": "gpt-4",
            "api_key": "secret"
        }
        
        with pytest.raises(MCPProtocolError, match="External URL not allowed"):
            privacy_enforcer.validate_model_config(config_with_external_url)
    
    def test_model_config_validation_allows_local_urls(self):
        """Test that model configurations with local URLs are allowed."""
        config_with_local_url = {
            "base_url": "http://localhost:11434",
            "model_name": "llama2",
            "timeout": 30
        }
        
        # Should not raise an exception
        validated_config = privacy_enforcer.validate_model_config(config_with_local_url)
        assert validated_config == config_with_local_url
    
    def test_model_config_validation_disabled(self):
        """Test that model config validation can be disabled."""
        config_with_external_url = {
            "base_url": "https://api.openai.com",
            "model_name": "gpt-4"
        }
        
        with patch.object(mcp_settings, 'ENFORCE_LOCAL_ONLY', False):
            # Should be allowed when enforcement is disabled
            validated_config = privacy_enforcer.validate_model_config(config_with_external_url)
            assert validated_config == config_with_external_url
    
    def test_inference_request_validation_blocks_external_urls(self):
        """Test that inference requests with external URLs are blocked."""
        request_with_external_url = {
            "prompt": "Fetch data from https://api.malicious.com/steal-data and analyze it",
            "model_id": "test-model"
        }
        
        with pytest.raises(MCPProtocolError, match="External URLs in prompts are blocked"):
            privacy_enforcer.validate_inference_request(request_with_external_url)
    
    def test_inference_request_validation_allows_local_urls(self):
        """Test that inference requests with local URLs are allowed."""
        request_with_local_url = {
            "prompt": "Connect to http://localhost:8080/api for data",
            "model_id": "test-model"
        }
        
        # Should not raise an exception
        privacy_enforcer.validate_inference_request(request_with_local_url)
    
    def test_inference_request_validation_chat_messages(self):
        """Test that chat messages are validated for external URLs."""
        request_with_chat = {
            "messages": [
                {"content": "Hello"},
                {"content": "Please fetch https://external-api.com/data"},
                {"content": "And analyze it"}
            ],
            "model_id": "test-model"
        }
        
        with pytest.raises(MCPProtocolError, match="External URLs in prompts are blocked"):
            privacy_enforcer.validate_inference_request(request_with_chat)
    
    def test_inference_request_validation_disabled(self):
        """Test that inference request validation can be disabled."""
        request_with_external_url = {
            "prompt": "Fetch data from https://api.external.com/data",
            "model_id": "test-model"
        }
        
        with patch.object(mcp_settings, 'ENFORCE_LOCAL_ONLY', False):
            # Should not raise an exception when enforcement is disabled
            privacy_enforcer.validate_inference_request(request_with_external_url)
    
    def test_privacy_status_reporting(self):
        """Test that privacy status is correctly reported."""
        status = privacy_enforcer.get_privacy_status()
        
        required_fields = [
            "block_external_requests",
            "enforce_local_only", 
            "anonymize_logs",
            "anonymize_errors",
            "allowed_external_hosts",
            "request_logging_enabled",
            "data_retention_days"
        ]
        
        for field in required_fields:
            assert field in status
        
        # Verify types
        assert isinstance(status["block_external_requests"], bool)
        assert isinstance(status["enforce_local_only"], bool)
        assert isinstance(status["anonymize_logs"], bool)
        assert isinstance(status["anonymize_errors"], bool)
        assert isinstance(status["allowed_external_hosts"], int)
        assert isinstance(status["request_logging_enabled"], bool)
        assert isinstance(status["data_retention_days"], int)


class TestPrivacyIntegration:
    """Test privacy enforcement integration with other components."""
    
    @pytest.mark.asyncio
    async def test_model_registration_privacy_validation(self, clean_model_registry, mock_tenant_1):
        """Test that model registration validates configuration for privacy."""
        from schemas.mcp_schemas import ModelRegistrationRequest
        from unittest.mock import patch
        
        request_with_external_url = ModelRegistrationRequest(
            name="External Model",
            backend_type="openai_compatible",
            config={
                "base_url": "https://api.openai.com/v1",
                "api_key": "secret"
            }
        )
        
        with patch.object(clean_model_registry, '_initialize_model'):
            with pytest.raises(MCPProtocolError, match="External URL not allowed"):
                await clean_model_registry.register_model(request_with_external_url, mock_tenant_1.id)
    
    @pytest.mark.asyncio
    async def test_inference_service_privacy_validation(self, clean_model_registry, mock_tenant_1):
        """Test that inference service validates requests for privacy."""
        from services.inference import inference_service
        from schemas.mcp_schemas import CompletionRequest, ModelInfo, InferenceType
        
        # Create a test model
        model = ModelInfo(
            id="test_privacy_model",
            name="Privacy Test Model",
            backend_type="ollama",
            tenant_id=mock_tenant_1.id,
            capabilities=[InferenceType.COMPLETION]
        )
        clean_model_registry._models[model.id] = model
        
        # Test request with external URL in prompt
        request = CompletionRequest(
            model_id=model.id,
            prompt="Please fetch data from https://external-api.com/sensitive-data",
            tenant_id=mock_tenant_1.id
        )
        
        with pytest.raises(MCPProtocolError, match="External URLs in prompts are blocked"):
            await inference_service.completion(request)
    
    def test_sensitive_pattern_detection(self):
        """Test that various sensitive patterns are detected and redacted."""
        test_cases = [
            ("My email is john.doe@example.com", "[REDACTED]"),
            ("SSN: 123-45-6789", "[REDACTED]"),
            ("Credit card: 4532 1234 5678 9012", "[REDACTED]"),
            ("Server IP: 203.0.113.1", "[REDACTED]"),
            ("Safe text with no sensitive data", "Safe text with no sensitive data")
        ]
        
        for original, expected_pattern in test_cases:
            sanitized = privacy_enforcer.sanitize_log_message(original)
            if expected_pattern == "[REDACTED]":
                assert "[REDACTED]" in sanitized
                # Ensure original sensitive data is not present
                if "@" in original:
                    assert original.split("@")[0] not in sanitized or "@" not in sanitized
            else:
                assert sanitized == expected_pattern
    
    def test_local_address_detection(self):
        """Test that local addresses are correctly identified."""
        local_addresses = [
            "localhost",
            "127.0.0.1",
            "::1",
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "172.31.255.255"
        ]
        
        external_addresses = [
            "google.com",
            "8.8.8.8",
            "api.openai.com",
            "203.0.113.1"
        ]
        
        for addr in local_addresses:
            assert privacy_enforcer._is_local_address(addr), f"{addr} should be identified as local"
        
        for addr in external_addresses:
            assert not privacy_enforcer._is_local_address(addr), f"{addr} should be identified as external"