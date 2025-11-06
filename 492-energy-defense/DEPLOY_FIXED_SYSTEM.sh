#!/bin/bash
# Complete Deployment Script - All Fixes Applied
# Energy Defense System - 2025-11-06

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Energy Defense System - Complete Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will DELETE all existing data!${NC}"
echo -e "${YELLOW}⚠️  Press Ctrl+C now to cancel...${NC}"
echo ""
echo "Starting in 5 seconds..."
sleep 5

echo ""
echo -e "${GREEN}Step 1/5: Stopping all containers...${NC}"
docker-compose down

echo ""
echo -e "${GREEN}Step 2/5: Removing volumes (required for enum type fixes)...${NC}"
docker-compose down -v

echo ""
echo -e "${GREEN}Step 3/5: Rebuilding images with all fixes...${NC}"
docker-compose build --no-cache

echo ""
echo -e "${GREEN}Step 4/5: Starting all services...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN}Step 5/5: Waiting for initialization (60 seconds)...${NC}"
for i in {1..60}; do
    echo -ne "${BLUE}[$i/60]${NC}\r"
    sleep 1
done
echo ""

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

echo "🔍 Checking service status..."
docker-compose ps
echo ""

echo "📊 Quick Health Checks:"
echo ""

# Check backend
echo -n "Backend API: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ UP${NC}"
else
    echo -e "${RED}❌ DOWN${NC}"
fi

# Check frontend
echo -n "Frontend:    "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ UP${NC}"
else
    echo -e "${RED}❌ DOWN${NC}"
fi

# Check database
echo -n "Database:    "
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ UP${NC}"
else
    echo -e "${RED}❌ DOWN${NC}"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}🎉 System is ready!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🔐 Test Credentials:"
echo "   Admin:    admin / admin123"
echo "   Analyst:  analyst / analyst123"
echo "   Observer: observer / observer123"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop system:"
echo "   docker-compose down"
echo ""
echo -e "${GREEN}Happy Securing! 🛡️⚡${NC}"
