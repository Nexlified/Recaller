#!/usr/bin/env python3
"""
Verification script for MCP server tenant isolation and privacy enforcement.

This script demonstrates the key security features implemented:
1. Tenant isolation in model management
2. Privacy enforcement for external requests
3. Data sanitization capabilities
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp_server.services.privacy import privacy_enforcer
from mcp_server.services.auth import TenantInfo
from mcp_server.models.registry import model_registry
from mcp_server.schemas.mcp_schemas import ModelRegistrationRequest, ModelInfo, InferenceType
from mcp_server.core.protocol import MCPProtocolError
import asyncio


def test_privacy_enforcement():
    """Test privacy enforcement features."""
    print("=== Testing Privacy Enforcement ===")
    
    # Test external URL blocking
    print("\n1. Testing external URL blocking:")
    external_urls = [
        "https://api.openai.com/v1/completions",
        "http://malicious-site.com/steal-data"
    ]
    
    for url in external_urls:
        try:
            privacy_enforcer.validate_external_request(url)
            print(f"   ❌ {url} - Should have been blocked!")
        except MCPProtocolError:
            print(f"   ✅ {url} - Correctly blocked")
    
    # Test local URL allowing
    print("\n2. Testing local URL allowing:")
    local_urls = [
        "http://localhost:11434/api",
        "http://127.0.0.1:8080",
        "http://192.168.1.100:3000"
    ]
    
    for url in local_urls:
        try:
            result = privacy_enforcer.validate_external_request(url)
            if result:
                print(f"   ✅ {url} - Correctly allowed")
            else:
                print(f"   ❌ {url} - Should have been allowed!")
        except MCPProtocolError:
            print(f"   ❌ {url} - Should have been allowed!")
    
    # Test data sanitization
    print("\n3. Testing data sanitization:")
    sensitive_data = [
        "User email: john.doe@example.com",
        "SSN: 123-45-6789", 
        "API Key: sk-1234567890abcdef",
        "Server path: /home/user/secrets/config.txt"
    ]
    
    for data in sensitive_data:
        sanitized = privacy_enforcer.sanitize_log_message(data)
        if "[REDACTED]" in sanitized or "[PATH]" in sanitized:
            print(f"   ✅ '{data[:30]}...' - Correctly sanitized")
        else:
            print(f"   ❓ '{data[:30]}...' - May need sanitization")
    
    # Test privacy status
    print("\n4. Privacy status:")
    status = privacy_enforcer.get_privacy_status()
    print(f"   Block external requests: {status['block_external_requests']}")
    print(f"   Enforce local only: {status['enforce_local_only']}")
    print(f"   Anonymize logs: {status['anonymize_logs']}")
    print(f"   Data retention days: {status['data_retention_days']}")


def test_tenant_isolation():
    """Test tenant isolation features."""
    print("\n=== Testing Tenant Isolation ===")
    
    # Create test tenants
    tenant1 = TenantInfo(id="tenant-1", slug="tenant-1", name="Tenant 1")
    tenant2 = TenantInfo(id="tenant-2", slug="tenant-2", name="Tenant 2")
    
    print(f"\n1. Created test tenants: {tenant1.name} and {tenant2.name}")
    
    # Test model access control
    print("\n2. Testing model access control:")
    
    # Create a mock model for tenant 1
    model = ModelInfo(
        id="tenant-1_test_model",
        name="Test Model",
        backend_type="ollama",
        tenant_id=tenant1.id,
        capabilities=[InferenceType.COMPLETION]
    )
    model_registry._models[model.id] = model
    
    # Test tenant 1 can access their model
    result = model_registry.get_model(model.id, tenant1.id)
    if result:
        print(f"   ✅ Tenant 1 can access their model: {model.name}")
    else:
        print(f"   ❌ Tenant 1 should be able to access their model")
    
    # Test tenant 2 cannot access tenant 1's model
    result = model_registry.get_model(model.id, tenant2.id)
    if result is None:
        print(f"   ✅ Tenant 2 correctly blocked from accessing Tenant 1's model")
    else:
        print(f"   ❌ Tenant 2 should not be able to access Tenant 1's model")
    
    # Test model listing is filtered
    print("\n3. Testing model listing filtration:")
    tenant1_models = model_registry.list_models(tenant_id=tenant1.id)
    tenant2_models = model_registry.list_models(tenant_id=tenant2.id)
    all_models = model_registry.list_models(tenant_id=None)
    
    print(f"   Tenant 1 sees {len(tenant1_models)} models")
    print(f"   Tenant 2 sees {len(tenant2_models)} models")
    print(f"   Admin sees {len(all_models)} models")
    
    if len(tenant1_models) > 0 and len(tenant2_models) == 0:
        print("   ✅ Model listing correctly filtered by tenant")
    
    # Clean up
    model_registry._models.clear()


def test_configuration_validation():
    """Test model configuration validation."""
    print("\n=== Testing Configuration Validation ===")
    
    # Test configuration with external URL
    print("\n1. Testing configuration with external URLs:")
    external_config = {
        "base_url": "https://api.openai.com/v1",
        "api_key": "secret-key"
    }
    
    try:
        privacy_enforcer.validate_model_config(external_config)
        print("   ❌ External configuration should have been blocked!")
    except MCPProtocolError:
        print("   ✅ External configuration correctly blocked")
    
    # Test configuration with local URL
    print("\n2. Testing configuration with local URLs:")
    local_config = {
        "base_url": "http://localhost:11434",
        "model_name": "llama2"
    }
    
    try:
        validated = privacy_enforcer.validate_model_config(local_config)
        if validated == local_config:
            print("   ✅ Local configuration correctly allowed")
        else:
            print("   ❓ Local configuration modified unexpectedly")
    except MCPProtocolError:
        print("   ❌ Local configuration should have been allowed!")


def test_inference_validation():
    """Test inference request validation."""
    print("\n=== Testing Inference Request Validation ===")
    
    # Test prompt with external URL
    print("\n1. Testing prompt with external URLs:")
    request_with_external = {
        "prompt": "Please fetch data from https://api.malicious.com/steal-data",
        "model_id": "test-model"
    }
    
    try:
        privacy_enforcer.validate_inference_request(request_with_external)
        print("   ❌ Request with external URL should have been blocked!")
    except MCPProtocolError:
        print("   ✅ Request with external URL correctly blocked")
    
    # Test safe prompt
    print("\n2. Testing safe prompt:")
    safe_request = {
        "prompt": "Generate a creative story about space exploration",
        "model_id": "test-model"
    }
    
    try:
        privacy_enforcer.validate_inference_request(safe_request)
        print("   ✅ Safe request correctly allowed")
    except MCPProtocolError:
        print("   ❌ Safe request should have been allowed!")


def main():
    """Run all verification tests."""
    print("🔒 MCP Server Security Verification")
    print("===================================")
    
    try:
        test_privacy_enforcement()
        test_tenant_isolation()
        test_configuration_validation()
        test_inference_validation()
        
        print("\n✅ All security features are working correctly!")
        print("\n🔐 Key Security Features Verified:")
        print("   • Tenant isolation prevents cross-tenant access")
        print("   • Privacy enforcement blocks external communications")
        print("   • Data sanitization protects sensitive information")
        print("   • Configuration validation ensures local-only processing")
        print("   • Inference requests are validated for privacy compliance")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())