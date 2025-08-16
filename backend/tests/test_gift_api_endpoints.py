#!/usr/bin/env python3
"""
Test script to validate Gift System API endpoints
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_gift_system_endpoints():
    """Test that all gift system endpoints are properly registered"""
    
    print("🧪 Testing Gift System API Endpoints...")
    
    # Test configuration endpoints
    config_endpoints = [
        "/api/v1/config/gift-system/config",
        "/api/v1/config/gift-system/status",
        "/api/v1/config/gift-system/permissions",
        "/api/v1/config/gift-system/reference-data/categories",
        "/api/v1/config/gift-system/reference-data/occasions",
        "/api/v1/config/gift-system/reference-data/budget-ranges"
    ]
    
    # Test gift CRUD endpoints 
    gift_endpoints = [
        "/api/v1/gifts/gifts/",
        "/api/v1/gifts/gift-ideas/",
        "/api/v1/gifts/analytics/",
        "/api/v1/gifts/recommendations/upcoming-occasions/"
    ]
    
    print("📋 Configuration Endpoints:")
    for endpoint in config_endpoints:
        try:
            # These should return 401/403 without auth, not 404
            response = client.get(endpoint)
            if response.status_code in [401, 403, 422]:  # Auth required or validation error
                print(f"  ✅ {endpoint} - Endpoint exists (auth required)")
            elif response.status_code == 404:
                print(f"  ❌ {endpoint} - Endpoint not found!")
            else:
                print(f"  ⚠️ {endpoint} - Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    print("\n🎁 Gift Management Endpoints:")
    for endpoint in gift_endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code in [401, 403, 422]:  # Auth required or validation error
                print(f"  ✅ {endpoint} - Endpoint exists (auth required)")
            elif response.status_code == 404:
                print(f"  ❌ {endpoint} - Endpoint not found!")
            else:
                print(f"  ⚠️ {endpoint} - Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    print("\n📊 Testing OpenAPI docs...")
    try:
        response = client.get("/docs")
        if response.status_code == 200:
            print("  ✅ FastAPI docs accessible at /docs")
        else:
            print(f"  ❌ Docs endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Docs endpoint error: {e}")
    
    print("\n🔍 Testing OpenAPI schema...")
    try:
        response = client.get("/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            
            # Check if our endpoints are in the schema
            paths = openapi_data.get("paths", {})
            gift_paths = [path for path in paths.keys() if "/gifts/" in path]
            config_paths = [path for path in paths.keys() if "/config/gift-system" in path]
            
            print(f"  ✅ Found {len(gift_paths)} gift management endpoints in OpenAPI schema")
            print(f"  ✅ Found {len(config_paths)} configuration endpoints in OpenAPI schema")
            
            # Show some example endpoints
            if gift_paths:
                print(f"    Example gift endpoints: {gift_paths[:3]}")
            if config_paths:
                print(f"    Example config endpoints: {config_paths[:3]}")
                
        else:
            print(f"  ❌ OpenAPI schema failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ OpenAPI schema error: {e}")
    
    print("\n✨ Gift System API validation complete!")

if __name__ == "__main__":
    test_gift_system_endpoints()