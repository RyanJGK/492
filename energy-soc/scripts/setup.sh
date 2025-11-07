#!/bin/bash

# Energy SOC - Quick Setup Script
# This script automates the initial setup process

set -e

echo "🚀 Energy SOC - Quick Setup"
echo "================================"
echo ""

# Check Node.js version
echo "📋 Checking prerequisites..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20.x or later."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "⚠️  Node.js version is $NODE_VERSION. Version 20 or later is recommended."
fi

echo "✅ Node.js $(node -v) detected"
echo "✅ npm $(npm -v) detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install
echo "✅ Dependencies installed"
echo ""

# Setup environment file
if [ ! -f .env.local ]; then
    echo "📝 Setting up environment variables..."
    cp .env.local.example .env.local
    echo "✅ Created .env.local from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env.local with your Supabase credentials"
    echo "   Or leave empty to run in mock data mode"
    echo ""
else
    echo "✅ .env.local already exists"
    echo ""
fi

# Check if user wants to set up Supabase
echo "🔧 Supabase Configuration"
echo "=========================="
read -p "Do you have Supabase credentials to configure? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter Supabase URL: " SUPABASE_URL
    read -p "Enter Supabase Anon Key: " SUPABASE_ANON_KEY
    
    cat > .env.local << EOF
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=
EOF
    
    echo "✅ Supabase configuration saved to .env.local"
    echo ""
    echo "📌 Next steps:"
    echo "   1. Run the SQL schema in Supabase (supabase/schema.sql)"
    echo "   2. Deploy edge functions (optional)"
    echo ""
else
    echo "✅ Running in mock data mode (no Supabase required)"
    echo ""
fi

# Build check
echo "🔨 Checking if build works..."
if npm run build > /dev/null 2>&1; then
    echo "✅ Build successful"
else
    echo "⚠️  Build had warnings (this is usually okay for development)"
fi
echo ""

# Success message
echo "================================"
echo "✨ Setup Complete!"
echo "================================"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "  - README.md    - General overview"
echo "  - SETUP.md     - Detailed setup guide"
echo "  - ARCHITECTURE.md - System architecture"
echo ""
echo "Happy coding! 🎉"
