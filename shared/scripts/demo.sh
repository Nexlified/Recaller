#!/bin/bash
# Demo script to showcase the configuration management system

echo "🔧 Configuration Management System Demo"
echo "======================================="

# Get the correct paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo ""
echo "📋 1. Validating all YAML configuration files..."
echo "-----------------------------------------------"
cd "$BACKEND_DIR"
for file in ../shared/config/reference-data/*/*.yml; do
    if [ -f "$file" ]; then
        echo "Validating: $(basename "$file")"
        python -m app.cli config validate "$file"
    fi
done

echo ""
echo "📊 2. Dry run sync to see what would be processed..."
echo "---------------------------------------------------"
python -m app.cli config sync --dry-run

echo ""
echo "🎯 3. Generated TypeScript types preview..."
echo "--------------------------------------------"
if [ -f "../shared/types/generated/enums.ts" ]; then
    echo "Enums generated:"
    head -n 20 ../shared/types/generated/enums.ts
else
    echo "Enums file not found - may need to run type generation"
fi

echo ""
if [ -f "../shared/types/generated/interfaces.ts" ]; then
    echo "Interfaces generated:"
    head -n 30 ../shared/types/generated/interfaces.ts
else
    echo "Interfaces file not found - may need to run type generation"
fi

echo ""
echo "✅ Configuration management system is ready!"
echo ""
echo "Next steps to complete setup:"
echo "1. Set up PostgreSQL database"
echo "2. Run: python -m app.cli config sync (to populate database)"
echo "3. Start FastAPI server: uvicorn app.main:app --reload"
echo "4. Access configuration API at: http://localhost:8000/api/v1/config"
echo "5. Use generated TypeScript types in frontend development"
echo ""
echo "📚 Available CLI commands:"
echo "  python -m app.cli config sync      # Sync YAML to database"
echo "  python -m app.cli config validate  # Validate YAML files"
echo "  python -m app.cli config list-values   # List database configs"
echo ""
echo "🌐 Available API endpoints:"
echo "  GET /api/v1/config/categories       # List categories"
echo "  GET /api/v1/config/types           # List configuration types"
echo "  GET /api/v1/config/values          # List configuration values"
echo "  GET /api/v1/config/values/{cat}/{type} # Get specific config"
echo "  POST /api/v1/config/sync           # Trigger sync via API"