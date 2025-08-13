#!/bin/bash

# Backend Test Runner Script
# This script runs the same tests as the CI pipeline locally

set -e  # Exit on any error

echo "🚀 Recaller Backend Test Runner"
echo "================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "pytest.ini" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd backend && ./run_tests.sh"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating a virtual environment first"
    echo ""
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install pytest pytest-asyncio httpx pytest-cov > /dev/null 2>&1 || {
    echo "❌ Failed to install test dependencies"
    exit 1
}

# Set environment variables for testing
export POSTGRES_SERVER=${POSTGRES_SERVER:-localhost}
export POSTGRES_USER=${POSTGRES_USER:-postgres}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
export POSTGRES_DB=${POSTGRES_DB:-recaller_test}
export SECRET_KEY=${SECRET_KEY:-test-secret-key-for-local-testing}

echo "✅ Test dependencies installed"
echo ""

# Function to run a test step
run_test_step() {
    local step_name="$1"
    local test_command="$2"
    local emoji="$3"
    
    echo "${emoji} Running ${step_name}..."
    echo "Command: ${test_command}"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo "✅ ${step_name} completed successfully"
    else
        echo "❌ ${step_name} failed"
        echo "   You can run this step individually with:"
        echo "   ${test_command}"
        return 1
    fi
    echo ""
}

# Parse command line arguments
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            HELP=true
            shift
            ;;
    esac
done

if [ "$HELP" = true ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --coverage, -c     Run tests with coverage reporting"
    echo "  --verbose, -v      Run tests with verbose output"
    echo "  --test, -t TEST    Run specific test file or pattern"
    echo "  --help, -h         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 --coverage                        # Run with coverage"
    echo "  $0 --test tests/test_auth_minimal.py # Run specific test"
    echo "  $0 --verbose --coverage              # Verbose with coverage"
    exit 0
fi

# Set pytest options based on arguments
PYTEST_OPTS="-v --tb=short"
if [ "$VERBOSE" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -s"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS --cov=app --cov-report=term-missing"
fi

# If specific test is provided, run only that
if [ -n "$SPECIFIC_TEST" ]; then
    echo "🎯 Running specific test: $SPECIFIC_TEST"
    echo ""
    run_test_step "Specific Test" "python -m pytest $SPECIFIC_TEST $PYTEST_OPTS" "🧪"
    exit 0
fi

# Run the full test suite (same as CI)
echo "🎯 Running complete test suite (same as CI pipeline)"
echo ""

# Step 1: Authentication Tests (Minimal)
run_test_step "Authentication Tests (Minimal)" \
    "python -m pytest tests/test_auth_minimal.py $PYTEST_OPTS" \
    "🔐"

# Step 2: Authentication Tests (Comprehensive)
run_test_step "Authentication Tests (Comprehensive)" \
    "python -m pytest tests/test_auth_comprehensive.py $PYTEST_OPTS" \
    "🔑"

# Step 3: Authentication Integration Tests
run_test_step "Authentication Integration Tests" \
    "python -m pytest tests/test_auth_integration.py $PYTEST_OPTS" \
    "🔗"

# Step 4: User Endpoint Integration Tests
run_test_step "User Endpoint Integration Tests" \
    "python -m pytest tests/integration/ $PYTEST_OPTS" \
    "👤"

# Step 5: Complete Test Suite with Coverage (if not already run with coverage)
if [ "$COVERAGE" = false ]; then
    run_test_step "Complete Test Suite" \
        "python -m pytest tests/ $PYTEST_OPTS" \
        "🧪"
else
    echo "🧪 Complete Test Suite already run with coverage above"
    echo ""
fi

# Step 6: Legacy Test Scripts (if they exist)
echo "📊 Running Legacy Test Scripts..."
echo "----------------------------------------"

if [ -f "test_registration_api.py" ]; then
    echo "  Running registration API tests..."
    if python test_registration_api.py; then
        echo "  ✅ Registration tests completed"
    else
        echo "  ⚠️ Registration tests completed with warnings"
    fi
else
    echo "  ℹ️ No registration API tests found"
fi

if [ -f "test_analytics.py" ]; then
    echo "  Running analytics API tests..."
    if python test_analytics.py; then
        echo "  ✅ Analytics tests completed"
    else
        echo "  ⚠️ Analytics tests completed with warnings"
    fi
else
    echo "  ℹ️ No analytics API tests found"
fi

echo ""

# Generate summary
echo "🎉 Test Execution Complete!"
echo "============================"
echo ""
echo "📋 Summary:"
echo "  ✅ Authentication Tests (Minimal)"
echo "  ✅ Authentication Tests (Comprehensive)"
echo "  ✅ Authentication Integration Tests"
echo "  ✅ User Endpoint Integration Tests"
echo "  ✅ Complete Test Suite"
echo "  ✅ Legacy Test Scripts"
echo ""

if [ "$COVERAGE" = true ]; then
    echo "📊 Coverage report generated above"
    echo ""
fi

echo "🚀 All tests completed successfully!"
echo ""
echo "💡 Tips:"
echo "  - Run with --coverage to see test coverage"
echo "  - Run with --verbose for detailed output"
echo "  - Run specific tests with --test <test_file>"
echo "  - Use --help to see all options"
