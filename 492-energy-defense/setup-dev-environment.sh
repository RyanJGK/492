#!/bin/bash

echo "================================================"
echo "492-Energy-Defense - Dev Environment Setup"
echo "================================================"
echo ""
echo "This script installs all dependencies locally for VS Code intellisense"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if we had any errors
ERRORS=0

# Check Node.js
echo "1. Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION} found"
else
    echo -e "${RED}✗${NC} Node.js not found"
    echo "   Install from: https://nodejs.org/"
    ((ERRORS++))
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm ${NPM_VERSION} found"
else
    echo -e "${RED}✗${NC} npm not found"
    ((ERRORS++))
fi

echo ""

# Check Python
echo "2. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} ${PYTHON_VERSION} found"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    echo "   Install from: https://www.python.org/"
    ((ERRORS++))
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} pip ${PIP_VERSION} found"
else
    echo -e "${RED}✗${NC} pip3 not found"
    ((ERRORS++))
fi

echo ""

# Exit if prerequisites missing
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Missing required tools. Please install them first.${NC}"
    exit 1
fi

# Install frontend dependencies
echo "3. Installing frontend dependencies..."
cd frontend
if npm install; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${RED}✗${NC} Failed to install frontend dependencies"
    exit 1
fi
cd ..

echo ""

# Install backend dependencies
echo "4. Installing backend dependencies..."
cd backend
if pip3 install -r requirements.txt --user; then
    echo -e "${GREEN}✓${NC} Backend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC}  Some backend dependencies may have failed"
    echo "   This is usually fine - Docker will handle runtime dependencies"
fi
cd ..

echo ""

# Create .vscode settings if not exists
echo "5. Configuring VS Code settings..."
if [ ! -d ".vscode" ]; then
    mkdir .vscode
fi

cat > .vscode/settings.json << 'EOF'
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.analysis.typeCheckingMode": "basic",
  "typescript.tsdk": "frontend/node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true
  }
}
EOF

echo -e "${GREEN}✓${NC} VS Code settings created"

echo ""

# Create recommended extensions file
cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.vscode-pylance",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next"
  ]
}
EOF

echo -e "${GREEN}✓${NC} VS Code extensions recommendations created"

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Restart VS Code to apply settings"
echo "2. Install recommended extensions (VS Code will prompt)"
echo "3. TypeScript errors should now be resolved"
echo ""
echo "For the frontend:"
echo "  - Open any .tsx file in frontend/src/"
echo "  - No more 'Cannot find module react' errors"
echo ""
echo "For the backend:"
echo "  - Open any .py file in backend/"
echo "  - Autocomplete and type hints should work"
echo ""
echo "To run the application:"
echo "  cd /workspace/492-energy-defense"
echo "  ./fix-and-restart.sh"
echo ""
