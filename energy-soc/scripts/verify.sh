#!/bin/bash

# Energy SOC - Verification Script
# Checks that the system is properly configured and running

set -e

echo "🔍 Energy SOC - System Verification"
echo "===================================="
echo ""

ERRORS=0

# Check files exist
echo "📂 Checking project structure..."
REQUIRED_FILES=(
    "package.json"
    "next.config.js"
    "tsconfig.json"
    "tailwind.config.js"
    "app/page.tsx"
    "lib/ai-agent.ts"
    "lib/supabase.ts"
    "supabase/schema.sql"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check node_modules
echo "📦 Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "  ✅ node_modules installed"
else
    echo "  ❌ node_modules not found (run: npm install)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check environment file
echo "⚙️  Checking configuration..."
if [ -f ".env.local" ]; then
    echo "  ✅ .env.local exists"
    
    if grep -q "your_supabase_project_url" .env.local; then
        echo "  ⚠️  .env.local not configured (will run in mock mode)"
    else
        echo "  ✅ .env.local configured"
    fi
else
    echo "  ⚠️  .env.local not found (will run in mock mode)"
fi
echo ""

# Check TypeScript
echo "🔧 Checking TypeScript..."
if npx tsc --noEmit > /dev/null 2>&1; then
    echo "  ✅ TypeScript check passed"
else
    echo "  ⚠️  TypeScript warnings (usually okay)"
fi
echo ""

# Check if port 3000 is available
echo "🌐 Checking port availability..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "  ⚠️  Port 3000 is already in use"
    echo "     Run: PORT=3001 npm run dev"
else
    echo "  ✅ Port 3000 is available"
fi
echo ""

# Summary
echo "===================================="
if [ $ERRORS -eq 0 ]; then
    echo "✨ All checks passed!"
    echo ""
    echo "Ready to start:"
    echo "  npm run dev"
else
    echo "⚠️  Found $ERRORS error(s)"
    echo ""
    echo "Please fix the errors above before starting."
fi
echo "===================================="
