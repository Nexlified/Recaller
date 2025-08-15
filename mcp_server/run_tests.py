#!/usr/bin/env python3
"""
Test runner script for MCP server tests.

This script provides a convenient way to run different categories of tests
with proper configuration and reporting.
"""

import sys
import subprocess
import argparse
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🧪 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run MCP server tests")
    parser.add_argument(
        "--category", 
        choices=["all", "unit", "integration", "tenant", "privacy", "error"], 
        default="all",
        help="Test category to run"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--fail-fast", "-x", action="store_true", help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    # Add common flags
    if args.verbose:
        base_cmd.append("-v")
    if args.fail_fast:
        base_cmd.append("-x")
    if args.parallel:
        base_cmd.extend(["-n", "auto"])
    if args.coverage:
        base_cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Test configurations
    test_configs = {
        "unit": {
            "description": "Unit Tests (MCP Protocol)",
            "files": ["tests/test_mcp_protocol.py"]
        },
        "integration": {
            "description": "Integration Tests (API Endpoints)",
            "files": ["tests/test_api_endpoints.py", "tests/test_api_integration.py"]
        },
        "tenant": {
            "description": "Tenant Isolation Tests",
            "files": ["tests/test_tenant_isolation_comprehensive.py"]
        },
        "privacy": {
            "description": "Privacy Enforcement Tests",
            "files": ["tests/test_privacy_enforcement.py"]
        },
        "error": {
            "description": "Error Handling Tests",
            "files": ["tests/test_error_handling.py"]
        },
        "all": {
            "description": "All Tests",
            "files": ["tests/"]
        }
    }
    
    # Install dependencies if needed
    install_cmd = [
        "pip", "install", "pytest", "pytest-asyncio", "fastapi", 
        "uvicorn", "pydantic", "pydantic-settings", "websockets", "httpx"
    ]
    if args.coverage:
        install_cmd.append("pytest-cov")
    if args.parallel:
        install_cmd.append("pytest-xdist")
    
    print("🔧 Installing test dependencies...")
    if not run_command(install_cmd, "Installing dependencies"):
        return 1
    
    # Run selected tests
    config = test_configs[args.category]
    cmd = base_cmd + config["files"]
    
    success = run_command(cmd, config["description"])
    
    if success:
        print("\n🎉 All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
        
        print("\n📋 Test Summary:")
        print(f"Category: {args.category}")
        print(f"Files: {', '.join(config['files'])}")
        
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())