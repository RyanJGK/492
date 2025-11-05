#!/bin/bash

# 492-Energy-Defense Setup Verification Script
# Checks that all required files and configurations are present

echo "=================================="
echo "492-Energy-Defense Setup Checker"
echo "=================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Directory: $1"
    else
        echo -e "${RED}✗${NC} Missing directory: $1"
        ((ERRORS++))
    fi
}

echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed"
    docker --version
else
    echo -e "${RED}✗${NC} Docker is not installed"
    ((ERRORS++))
fi

if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose is installed"
    docker-compose --version
else
    echo -e "${RED}✗${NC} Docker Compose is not installed"
    ((ERRORS++))
fi

echo ""
echo "Checking project structure..."

# Core files
check_file "docker-compose.yml"
check_file ".env.example"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "DEPLOYMENT.md"

echo ""
echo "Checking backend structure..."

check_dir "backend"
check_dir "backend/api"
check_dir "backend/ai_agent"
check_dir "backend/database"
check_dir "backend/scripts"
check_dir "backend/tests"

check_file "backend/requirements.txt"
check_file "backend/Dockerfile"
check_file "backend/Dockerfile.ai"
check_file "backend/api/main.py"
check_file "backend/api/config.py"
check_file "backend/api/database.py"
check_file "backend/api/models.py"
check_file "backend/api/schemas.py"
check_file "backend/database/init.sql"
check_file "backend/ai_agent/service.py"
check_file "backend/scripts/data_simulator.py"

echo ""
echo "Checking frontend structure..."

check_dir "frontend"
check_dir "frontend/src"
check_dir "frontend/src/components"
check_dir "frontend/src/pages"
check_dir "frontend/src/services"
check_dir "frontend/src/context"
check_dir "frontend/src/types"

check_file "frontend/package.json"
check_file "frontend/Dockerfile"
check_file "frontend/vite.config.ts"
check_file "frontend/tsconfig.json"
check_file "frontend/tailwind.config.js"
check_file "frontend/index.html"
check_file "frontend/src/main.tsx"
check_file "frontend/src/App.tsx"
check_file "frontend/src/services/api.ts"
check_file "frontend/src/context/AuthContext.tsx"

echo ""
echo "Checking configuration..."

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    if grep -q "OPENROUTER_API_KEY=your_openrouter_api_key_here" .env || \
       grep -q "OPENROUTER_API_KEY=$" .env || \
       ! grep -q "OPENROUTER_API_KEY" .env; then
        echo -e "${YELLOW}⚠${NC}  Warning: OPENROUTER_API_KEY not configured in .env"
        echo "   AI features will not work without a valid API key"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC} OPENROUTER_API_KEY is configured"
    fi
    
    if grep -q "changeme" .env; then
        echo -e "${YELLOW}⚠${NC}  Warning: Default passwords detected in .env"
        echo "   Change passwords before production deployment"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠${NC}  .env file not found"
    echo "   Run: cp .env.example .env"
    ((WARNINGS++))
fi

echo ""
echo "=================================="
echo "Summary"
echo "=================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "You're ready to start the application:"
    echo "  docker-compose up --build"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "The application should work, but review the warnings above."
    echo ""
    echo "To start the application:"
    echo "  docker-compose up --build"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) and $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Please fix the errors above before starting the application."
    exit 1
fi
