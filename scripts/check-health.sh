#!/bin/bash

# Health check script for all services

echo "🔍 Checking 492-Energy-Defense System Health"
echo "=========================================="
echo ""

# Check if services are running
echo "📦 Container Status:"
docker-compose ps
echo ""

# Check backend health
echo "🔧 Backend API Health:"
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi
echo ""

# Check AI agent health
echo "🤖 AI Agent Health:"
if curl -f http://localhost:8001/health 2>/dev/null; then
    echo "✅ AI Agent is healthy"
else
    echo "❌ AI Agent is not responding"
fi
echo ""

# Check frontend
echo "🌐 Frontend Health:"
if curl -f http://localhost:3000 2>/dev/null > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding"
fi
echo ""

# Check database
echo "🗄️  Database Health:"
if docker-compose exec -T postgres pg_isready -U energydefense > /dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready"
fi
echo ""

# Check logs for errors
echo "📋 Recent Errors (last 5 minutes):"
docker-compose logs --since 5m 2>&1 | grep -i "error" | tail -5
echo ""

echo "✅ Health check complete"
