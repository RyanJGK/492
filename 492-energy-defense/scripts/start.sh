#!/bin/bash

# 492-Energy-Defense Platform Startup Script
# Automates initial setup and deployment

set -e

echo "=================================================="
echo "492-Energy-Defense Platform - Quick Start"
echo "=================================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose detected"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/generate-a-strong-secret-key-here/$SECRET_KEY/" .env
    
    # Generate secure database password
    DB_PASSWORD=$(openssl rand -base64 24)
    sed -i "s/change-this-secure-password/$DB_PASSWORD/" .env
    
    echo "✅ .env file created with secure credentials"
else
    echo "✅ .env file already exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p database/migrations
mkdir -p backend/logs
mkdir -p ai-agent/logs
mkdir -p ai-agent/models
echo "✅ Directories created"
echo ""

# Pull latest images (optional, for faster startup)
echo "🐳 Pulling base images (this may take a few minutes)..."
docker-compose pull postgres || true
echo ""

# Build and start services
echo "🚀 Building and starting services..."
echo "This will take several minutes on first run..."
echo ""
docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check backend health
for i in {1..30}; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend API did not become healthy in time"
        echo "Check logs: docker-compose logs backend"
    fi
    sleep 2
done

# Check AI agent health
for i in {1..30}; do
    if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ AI Agent is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  AI Agent did not become healthy in time"
        echo "Check logs: docker-compose logs ai-agent"
    fi
    sleep 2
done

# Check frontend
for i in {1..30}; do
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is accessible"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Frontend did not become accessible in time"
        echo "Check logs: docker-compose logs frontend"
    fi
    sleep 2
done

echo ""
echo "=================================================="
echo "🎉 Platform is ready!"
echo "=================================================="
echo ""
echo "Access the platform:"
echo "  🌐 Dashboard:     http://localhost:3000"
echo "  📡 Backend API:   http://localhost:8000"
echo "  📚 API Docs:      http://localhost:8000/api/docs"
echo "  🤖 AI Agent:      http://localhost:8001"
echo ""
echo "Default credentials (demo mode):"
echo "  - Switch between roles using the UI"
echo "  - Default role: Admin"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f [service]"
echo "  Stop platform:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Full cleanup:     docker-compose down -v"
echo ""
echo "For production deployment, see: docs/DEPLOYMENT.md"
echo "=================================================="
