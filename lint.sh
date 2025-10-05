#!/bin/bash

# SlayFlashcards - Linting Script
# Runs all linters on the codebase

set -e

echo "🔍 Running linters on SlayFlashcards..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Function to run a linter and report results
run_linter() {
    local name=$1
    local command=$2

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Running $name..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if eval "$command"; then
        echo -e "${GREEN}✅ $name passed!${NC}"
    else
        echo -e "${RED}❌ $name found issues${NC}"
        return 1
    fi
    echo ""
}

# Track overall success
overall_success=true

# Run flake8
if ! run_linter "Flake8 (PEP 8 Style Checker)" \
    "flake8 core/ api/ --count --statistics --max-line-length=120 --exclude=__pycache__,.git,__init__.py"; then
    overall_success=false
fi

# Run black in check mode
if ! run_linter "Black (Code Formatter Check)" \
    "black --check --line-length=120 core/ api/"; then
    overall_success=false
fi

# Run isort in check mode
if ! run_linter "isort (Import Sorter Check)" \
    "isort --check-only --profile=black core/ api/"; then
    overall_success=false
fi

# Run mypy for type checking
if ! run_linter "MyPy (Type Checker)" \
    "mypy core/ api/ --ignore-missing-imports --no-strict-optional"; then
    overall_success=false
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$overall_success" = true ]; then
    echo -e "${GREEN}🎉 All linters passed successfully!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo -e "${RED}⚠️  Some linters found issues. Please fix them.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  - Run 'black core/ api/' to auto-format code"
    echo "  - Run 'isort core/ api/' to auto-sort imports"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi
