#!/bin/bash

echo "================================================"
echo "VS Code Environment Diagnostic Check"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1. Frontend Dependencies Check"
echo "================================"

if [ -d "frontend/node_modules" ]; then
    COUNT=$(ls -1 frontend/node_modules | wc -l)
    echo -e "${GREEN}✓${NC} node_modules exists with $COUNT packages"
else
    echo -e "${RED}✗${NC} node_modules NOT FOUND"
    echo "   Run: cd frontend && npm install"
fi

if [ -d "frontend/node_modules/react" ]; then
    echo -e "${GREEN}✓${NC} React is installed"
else
    echo -e "${RED}✗${NC} React NOT installed"
fi

if [ -d "frontend/node_modules/typescript" ]; then
    echo -e "${GREEN}✓${NC} TypeScript is installed"
else
    echo -e "${RED}✗${NC} TypeScript NOT installed"
fi

echo ""
echo "2. VS Code Configuration Check"
echo "================================"

if [ -f ".vscode/settings.json" ]; then
    echo -e "${GREEN}✓${NC} VS Code settings.json exists"
else
    echo -e "${RED}✗${NC} VS Code settings.json NOT FOUND"
fi

if [ -f ".vscode/extensions.json" ]; then
    echo -e "${GREEN}✓${NC} VS Code extensions.json exists"
else
    echo -e "${RED}✗${NC} VS Code extensions.json NOT FOUND"
fi

echo ""
echo "3. Backend Dependencies Check"
echo "================================"

if pip3 list 2>/dev/null | grep -q fastapi; then
    echo -e "${GREEN}✓${NC} FastAPI is installed"
else
    echo -e "${RED}✗${NC} FastAPI NOT installed"
fi

if pip3 list 2>/dev/null | grep -q sqlalchemy; then
    echo -e "${GREEN}✓${NC} SQLAlchemy is installed"
else
    echo -e "${RED}✗${NC} SQLAlchemy NOT installed"
fi

echo ""
echo "4. System Tools Check"
echo "================================"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION}"
else
    echo -e "${RED}✗${NC} Node.js NOT installed"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm ${NPM_VERSION}"
else
    echo -e "${RED}✗${NC} npm NOT installed"
fi

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} ${PYTHON_VERSION}"
else
    echo -e "${RED}✗${NC} Python 3 NOT installed"
fi

echo ""
echo "5. Key Files Check"
echo "================================"

if [ -f "frontend/src/pages/LoginPage.tsx" ]; then
    echo -e "${GREEN}✓${NC} LoginPage.tsx exists"
else
    echo -e "${RED}✗${NC} LoginPage.tsx NOT FOUND"
fi

if [ -f "backend/api/main.py" ]; then
    echo -e "${GREEN}✓${NC} main.py exists"
else
    echo -e "${RED}✗${NC} main.py NOT FOUND"
fi

echo ""
echo "================================================"
echo "Diagnostic Summary"
echo "================================================"
echo ""
echo "If you see any ✗ marks above, fix those issues first."
echo ""
echo "To open VS Code with correct TypeScript:"
echo "1. Open: code frontend/src/pages/LoginPage.tsx"
echo "2. Bottom right corner → Click TypeScript version"
echo "3. Select 'Use Workspace Version'"
echo "4. Press Cmd/Ctrl+Shift+P → 'TypeScript: Restart TS Server'"
echo ""
echo "To manually install extensions in VS Code:"
echo "1. Press Cmd/Ctrl+Shift+X (Extensions panel)"
echo "2. Search and install: ESLint, Prettier, Python, Pylance"
echo ""
