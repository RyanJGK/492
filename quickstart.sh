#!/bin/bash

# Energy Defense - Quick Start Script
# This script sets up and launches the entire system

set -e

echo "======================================"
echo "Energy Defense - Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with secure passwords before production use!"
    echo ""
fi

# Build containers
echo "🔨 Building Docker containers..."
echo "This may take 5-10 minutes on first run..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Wait for backend to be healthy
echo "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "======================================"
echo "✨ Energy Defense is ready!"
echo "======================================"
echo ""
echo "Access the application:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Default credentials:"
echo "  Admin:     admin / admin123"
echo "  Analyst:   analyst / analyst123"
echo "  Observer:  observer / observer123"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login with admin credentials"
echo "  3. Go to Configuration page"
echo "  4. Click 'Load All Scenarios' to import data"
echo "  5. Navigate to Dashboard to view threats"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "======================================"
