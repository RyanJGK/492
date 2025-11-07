#!/bin/bash

# 492-Energy-Defense System Initialization Script
# This script sets up and starts the complete system

set -e

echo "🛡️  492-Energy-Defense System Initialization"
echo "==========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenRouter API key!"
    echo "   Open .env and set OPENROUTER_API_KEY=your-key-here"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
fi

# Check if OpenRouter API key is set
if grep -q "your-openrouter-api-key-here" .env; then
    echo ""
    echo "⚠️  WARNING: OpenRouter API key not configured!"
    echo "   The AI agent will not function without a valid API key."
    echo "   You can continue, but AI features will fail."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🔧 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "✅ System is starting up!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🌐 Access Points:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API:        http://localhost:8000"
echo "   API Documentation:  http://localhost:8000/docs"
echo ""
echo "👤 Default Credentials:"
echo "   Admin:    username: admin     | password: demo123"
echo "   Analyst:  username: analyst1  | password: demo123"
echo "   Observer: username: observer1 | password: demo123"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:    docker-compose logs -f [service]"
echo "   Stop system:  docker-compose down"
echo "   Restart:      docker-compose restart [service]"
echo "   Status:       docker-compose ps"
echo ""
echo "📚 Documentation:"
echo "   README:       ./README.md"
echo "   Architecture: ./docs/ARCHITECTURE.md"
echo "   API Guide:    ./docs/API_GUIDE.md"
echo "   Deployment:   ./docs/DEPLOYMENT.md"
echo ""
echo "🎉 Initialization complete! The system is ready to use."
