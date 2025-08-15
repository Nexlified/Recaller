"""
Comprehensive tests for privacy enforcement in MCP server.

These tests verify that privacy protection mechanisms work correctly
and prevent data leakage outside the self-hosted environment.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.privacy import privacy_enforcer, PrivacyEnforcer
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
            "http://suspicious-site.evil",
            "https://malicious-ai-service.com/steal-data"
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
            assert result is None  # No exception means validation passed
    
    def test_external_request_validation_allows_allowed_hosts(self):
        """Test that explicitly allowed external hosts are permitted."""
        # Temporarily add an allowed host
        original_hosts = mcp_settings.ALLOWED_EXTERNAL_HOSTS[:]
        mcp_settings.ALLOWED_EXTERNAL_HOSTS.append("trusted-service.com")
        
        try:
            # Should not raise exception for allowed host
            privacy_enforcer.validate_external_request("https://trusted-service.com/api")
        finally:
            # Restore original hosts
            mcp_settings.ALLOWED_EXTERNAL_HOSTS[:] = original_hosts
    
    def test_model_config_validation_blocks_external_endpoints(self):
        """Test that model configurations with external endpoints are blocked."""
        external_configs = [
            {
                "base_url": "https://api.openai.com",
                "model_name": "gpt-4"
            },
            {
                "endpoint": "http://external-ai.com/inference",
                "api_key": "secret"
            },
            {
                "server_url": "https://huggingface.co/api/models"
            }
        ]
        
        for config in external_configs:
            with pytest.raises(MCPProtocolError, match="External.*blocked"):
                privacy_enforcer.validate_model_config(config)
    
    def test_model_config_validation_allows_local_endpoints(self):
        """Test that model configurations with local endpoints are allowed."""
        local_configs = [
            {
                "base_url": "http://localhost:11434",
                "model_name": "llama2"
            },
            {
                "endpoint": "http://127.0.0.1:8080/inference",
                "timeout": 30
            },
            {
                "server_url": "http://192.168.1.10:5000"
            }
        ]
        
        for config in local_configs:
            # Should not raise exception
            result = privacy_enforcer.validate_model_config(config)
            assert result == config  # Should return the same config if valid
    
    def test_sensitive_data_detection_in_text(self):
        """Test detection of sensitive data patterns in text."""
        sensitive_texts = [
            "My email is user@example.com and phone is 555-1234",
            "SSN: 123-45-6789",
            "Credit card: 4532 1234 5678 9012",
            "IP address: 192.168.1.100 should be private",
            "API key: sk-1234567890abcdef"
        ]
        
        for text in sensitive_texts:
            result = privacy_enforcer.scan_for_sensitive_data(text)
            assert len(result) > 0, f"Should detect sensitive data in: {text}"
    
    def test_sensitive_data_anonymization(self):
        """Test anonymization of sensitive data."""
        original_text = "Contact me at john.doe@company.com or call 555-123-4567"
        anonymized = privacy_enforcer.anonymize_text(original_text)
        
        assert "john.doe@company.com" not in anonymized
        assert "555-123-4567" not in anonymized
        assert "[EMAIL]" in anonymized or "***" in anonymized
        assert "[PHONE]" in anonymized or "***" in anonymized
    
    def test_request_content_validation_blocks_external_references(self):
        """Test that request content with external references is blocked."""
        prompts_with_external_refs = [
            "Please fetch data from https://api.example.com/users",
            "Access the file at http://external-server.com/data.json",
            "Send a request to api.openai.com to get completions",
            "Connect to ftp://files.company.com/documents/"
        ]
        
        for prompt in prompts_with_external_refs:
            with pytest.raises(MCPProtocolError, match="External.*blocked"):
                privacy_enforcer.validate_request_content(prompt)
    
    def test_request_content_validation_allows_safe_content(self):
        """Test that safe request content is allowed."""
        safe_prompts = [
            "Write a story about a brave knight",
            "Explain the concept of machine learning",
            "Generate code for a sorting algorithm",
            "Summarize this text: Lorem ipsum dolor sit amet"
        ]
        
        for prompt in safe_prompts:
            # Should not raise exception
            privacy_enforcer.validate_request_content(prompt)
    
    def test_log_anonymization_when_enabled(self):
        """Test that logs are anonymized when privacy protection is enabled."""
        original_setting = mcp_settings.ANONYMIZE_LOGS
        mcp_settings.ANONYMIZE_LOGS = True
        
        try:
            log_message = "User john.doe@company.com requested model inference with IP 192.168.1.50"
            anonymized = privacy_enforcer.anonymize_log_message(log_message)
            
            assert "john.doe@company.com" not in anonymized
            assert "192.168.1.50" not in anonymized
            assert "[EMAIL]" in anonymized or "***" in anonymized
            assert "[IP]" in anonymized or "***" in anonymized
        finally:
            mcp_settings.ANONYMIZE_LOGS = original_setting
    
    def test_error_message_anonymization_when_enabled(self):
        """Test that error messages are anonymized when privacy protection is enabled."""
        original_setting = mcp_settings.ANONYMIZE_ERROR_MESSAGES
        mcp_settings.ANONYMIZE_ERROR_MESSAGES = True
        
        try:
            error_message = "Failed to connect to database at 192.168.1.100:5432 for user admin@company.com"
            anonymized = privacy_enforcer.anonymize_error_message(error_message)
            
            assert "192.168.1.100" not in anonymized
            assert "admin@company.com" not in anonymized
            assert "[IP]" in anonymized or "***" in anonymized
            assert "[EMAIL]" in anonymized or "***" in anonymized
        finally:
            mcp_settings.ANONYMIZE_ERROR_MESSAGES = original_setting
    
    def test_data_retention_enforcement(self):
        """Test that data retention policies are enforced."""
        # Mock stored data with timestamps
        old_data = {
            "timestamp": "2023-01-01T00:00:00Z",
            "content": "old request data"
        }
        recent_data = {
            "timestamp": "2024-01-01T00:00:00Z", 
            "content": "recent request data"
        }
        
        with patch('services.privacy.datetime') as mock_datetime:
            # Mock current time to be 2024-06-01
            mock_datetime.utcnow.return_value.isoformat.return_value = "2024-06-01T00:00:00Z"
            
            # Test with retention period of 90 days
            should_retain_old = privacy_enforcer.should_retain_data(old_data, retention_days=90)
            should_retain_recent = privacy_enforcer.should_retain_data(recent_data, retention_days=90)
            
            assert should_retain_old is False  # Old data should be purged
            assert should_retain_recent is True  # Recent data should be retained
    
    def test_privacy_status_reporting(self):
        """Test privacy status reporting functionality."""
        status = privacy_enforcer.get_privacy_status()
        
        # Should include all privacy protection settings
        assert "block_external_requests" in status
        assert "enforce_local_only" in status
        assert "anonymize_logs" in status
        assert "anonymize_errors" in status
        assert "allowed_external_hosts" in status
        assert "request_logging_enabled" in status
        assert "data_retention_days" in status
        
        # Values should match current settings
        assert status["block_external_requests"] == mcp_settings.BLOCK_EXTERNAL_REQUESTS
        assert status["enforce_local_only"] == mcp_settings.ENFORCE_LOCAL_ONLY
        assert status["anonymize_logs"] == mcp_settings.ANONYMIZE_LOGS
        assert status["anonymize_errors"] == mcp_settings.ANONYMIZE_ERROR_MESSAGES
    
    def test_privacy_enforcer_initialization(self):
        """Test privacy enforcer initialization."""
        enforcer = PrivacyEnforcer()
        
        # Should have sensitive patterns compiled
        assert hasattr(enforcer, '_compiled_patterns')
        assert len(enforcer._compiled_patterns) > 0
        
        # Should have basic patterns for email, phone, SSN, credit cards, etc.
        patterns_count = len(enforcer._compiled_patterns)
        assert patterns_count >= 4  # At least email, SSN, credit card, IP patterns


class TestPrivacyComplianceIntegration:
    """Test privacy compliance integration across the system."""
    
    def test_model_registration_privacy_validation(self):
        """Test that model registration validates privacy compliance."""
        from models.registry import ModelRegistry
        from schemas.mcp_schemas import ModelRegistrationRequest
        
        registry = ModelRegistry()
        
        # Test external model configuration rejection
        external_request = ModelRegistrationRequest(
            name="External Model",
            backend_type="ollama",
            config={"base_url": "https://api.openai.com"},
            capabilities=["completion"]
        )
        
        with pytest.raises((MCPProtocolError, ValueError), match="External.*blocked"):
            # This should fail privacy validation
            privacy_enforcer.validate_model_config(external_request.config)
    
    def test_inference_request_privacy_validation(self):
        """Test that inference requests validate privacy compliance."""
        # Test prompt with external reference
        external_prompt = "Please access https://external-api.com/data and summarize the content"
        
        with pytest.raises(MCPProtocolError, match="External.*blocked"):
            privacy_enforcer.validate_request_content(external_prompt)
    
    def test_configuration_privacy_defaults(self):
        """Test that privacy protection is enabled by default."""
        from config.settings import mcp_settings
        
        # These should be enabled by default for privacy protection
        assert mcp_settings.BLOCK_EXTERNAL_REQUESTS is True
        assert mcp_settings.ENFORCE_LOCAL_ONLY is True
        assert mcp_settings.ANONYMIZE_LOGS is True
        assert mcp_settings.ANONYMIZE_ERROR_MESSAGES is True
    
    @patch('services.privacy.mcp_settings')
    def test_privacy_enforcement_can_be_disabled_for_testing(self, mock_settings):
        """Test that privacy enforcement can be disabled for testing purposes."""
        # Mock settings to disable privacy protection
        mock_settings.BLOCK_EXTERNAL_REQUESTS = False
        mock_settings.ENFORCE_LOCAL_ONLY = False
        
        # Create new enforcer instance with mocked settings
        test_enforcer = PrivacyEnforcer()
        
        # External requests should be allowed when disabled
        try:
            test_enforcer.validate_external_request("https://external-api.com")
            # Should not raise exception when disabled
        except MCPProtocolError:
            pytest.fail("Privacy enforcement should be disabled for testing")
    
    def test_privacy_audit_logging(self):
        """Test that privacy-related events are properly logged."""
        import logging
        from unittest.mock import Mock
        
        # Mock the logger
        mock_logger = Mock()
        
        with patch('services.privacy.logger', mock_logger):
            # Test logging of blocked external request
            try:
                privacy_enforcer.validate_external_request("https://blocked-site.com")
            except MCPProtocolError:
                pass
            
            # Should have logged the privacy violation
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "blocked" in call_args.lower() or "privacy" in call_args.lower()
    
    def test_sensitive_data_handling_in_errors(self):
        """Test that sensitive data is not leaked in error messages."""
        # Create an error that might contain sensitive data
        original_error = Exception("Database connection failed for user admin@company.com at 192.168.1.100")
        
        # Privacy enforcer should sanitize error messages
        sanitized_message = privacy_enforcer.anonymize_error_message(str(original_error))
        
        assert "admin@company.com" not in sanitized_message
        assert "192.168.1.100" not in sanitized_message
    
    def test_privacy_compliance_documentation(self):
        """Test that privacy compliance features are properly documented."""
        # Test that privacy enforcer has proper docstrings
        assert privacy_enforcer.__class__.__doc__ is not None
        assert "privacy" in privacy_enforcer.__class__.__doc__.lower()
        
        # Test that key methods have documentation
        assert privacy_enforcer.validate_external_request.__doc__ is not None
        assert privacy_enforcer.validate_model_config.__doc__ is not None
        assert privacy_enforcer.anonymize_text.__doc__ is not None
    
    def test_privacy_settings_validation(self):
        """Test that privacy settings are validated on startup."""
        from config.settings import mcp_settings
        
        # Test that data retention days is reasonable
        assert mcp_settings.DATA_RETENTION_DAYS > 0
        assert mcp_settings.DATA_RETENTION_DAYS <= 365  # Not more than a year
        
        # Test that allowed external hosts is a list
        assert isinstance(mcp_settings.ALLOWED_EXTERNAL_HOSTS, list)


class TestPrivacyEnforcementEdgeCases:
    """Test edge cases and corner cases for privacy enforcement."""
    
    def test_empty_and_none_inputs(self):
        """Test privacy enforcement with empty and None inputs."""
        # Should handle empty strings gracefully
        privacy_enforcer.validate_request_content("")
        privacy_enforcer.anonymize_text("")
        
        # Should handle None gracefully
        result = privacy_enforcer.scan_for_sensitive_data(None)
        assert result == []
        
        anonymized = privacy_enforcer.anonymize_text(None)
        assert anonymized == ""
    
    def test_unicode_and_special_characters(self):
        """Test privacy enforcement with unicode and special characters."""
        unicode_text = "Contact émile@société.fr or call +33-1-23-45-67-89"
        
        # Should detect email even with unicode domain
        sensitive_data = privacy_enforcer.scan_for_sensitive_data(unicode_text)
        assert len(sensitive_data) > 0
        
        # Should anonymize properly
        anonymized = privacy_enforcer.anonymize_text(unicode_text)
        assert "émile@société.fr" not in anonymized
    
    def test_very_long_inputs(self):
        """Test privacy enforcement with very long inputs."""
        # Create a very long text with embedded sensitive data
        long_text = "Lorem ipsum " * 1000 + " contact user@example.com " + "dolor sit amet " * 1000
        
        # Should still detect sensitive data in long text
        sensitive_data = privacy_enforcer.scan_for_sensitive_data(long_text)
        assert len(sensitive_data) > 0
        
        # Should anonymize without performance issues
        anonymized = privacy_enforcer.anonymize_text(long_text)
        assert "user@example.com" not in anonymized
    
    def test_nested_configuration_validation(self):
        """Test privacy validation with nested configuration objects."""
        nested_config = {
            "model": {
                "backend": {
                    "url": "https://external-api.com",
                    "fallback": {
                        "url": "http://localhost:8080"
                    }
                }
            },
            "auth": {
                "endpoint": "https://auth.external.com"
            }
        }
        
        # Should detect external URLs in nested structures
        with pytest.raises(MCPProtocolError, match="External.*blocked"):
            privacy_enforcer.validate_model_config(nested_config)
    
    def test_false_positive_handling(self):
        """Test handling of false positives in sensitive data detection."""
        # Text that might trigger false positives
        false_positive_texts = [
            "Version 1.2.3.4 was released",  # Looks like IP but is version
            "The regex pattern is \\d{3}-\\d{2}-\\d{4}",  # Looks like SSN but is documentation
            "localhost:3000",  # Local address, should be allowed
            "127.0.0.1:8080"   # Local IP, should be allowed
        ]
        
        for text in false_positive_texts:
            # Should not block legitimate content
            try:
                privacy_enforcer.validate_request_content(text)
            except MCPProtocolError:
                pytest.fail(f"False positive detected in: {text}")
    
    def test_performance_with_large_configurations(self):
        """Test privacy enforcement performance with large configurations."""
        import time
        
        # Create large configuration
        large_config = {}
        for i in range(1000):
            large_config[f"param_{i}"] = f"value_{i}"
        
        # Add one external URL
        large_config["api_endpoint"] = "https://external-api.com"
        
        # Should still detect external URL efficiently
        start_time = time.time()
        
        with pytest.raises(MCPProtocolError):
            privacy_enforcer.validate_model_config(large_config)
        
        end_time = time.time()
        
        # Should complete within reasonable time (less than 1 second)
        assert end_time - start_time < 1.0
    
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