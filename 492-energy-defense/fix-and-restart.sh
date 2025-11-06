#!/bin/bash

echo "================================================"
echo "492-Energy-Defense - Fix and Restart Script"
echo "================================================"
echo ""

# Stop all containers
echo "1. Stopping all containers..."
docker-compose down -v 2>/dev/null || docker compose down -v

# Wait a moment
sleep 2

echo ""
echo "2. Rebuilding containers with fixes..."
echo ""

# Rebuild and start
docker-compose up --build -d 2>/dev/null || docker compose up --build -d

echo ""
echo "3. Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "4. Checking service status..."
echo ""

docker-compose ps 2>/dev/null || docker compose ps

echo ""
echo "5. Checking for errors..."
echo ""

# Check for database errors
echo "Database errors:"
docker-compose logs postgres 2>/dev/null | grep -i "error\|fatal" | tail -5 || docker compose logs postgres | grep -i "error\|fatal" | tail -5

echo ""
echo "Backend errors:"
docker-compose logs backend 2>/dev/null | grep -i "error" | tail -5 || docker compose logs backend | grep -i "error" | tail -5

echo ""
echo "================================================"
echo "Startup complete!"
echo "================================================"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo "Login credentials:"
echo "  admin / admin123"
echo "  analyst / admin123"
echo "  observer / admin123"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "Services: backend, frontend, postgres, redis, ai-agent, data-simulator"
echo ""
