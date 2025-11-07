#!/bin/bash
# Complete Debug and Cleanup Script
# Systematically checks all authentication issues and removes unused files

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Energy Defense - Debug & Cleanup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Remove empty/unused directories
echo -e "${YELLOW}Step 1: Cleaning up empty directories...${NC}"

if [ -d "backend/api/models" ] && [ -z "$(ls -A backend/api/models 2>/dev/null | grep -v __)" ]; then
    echo "  Removing empty backend/api/models/"
    rm -rf backend/api/models
fi

if [ -d "backend/api/schemas" ] && [ -z "$(ls -A backend/api/schemas 2>/dev/null | grep -v __)" ]; then
    echo "  Removing empty backend/api/schemas/"
    rm -rf backend/api/schemas
fi

if [ -d "backend/api/services" ] && [ -z "$(ls -A backend/api/services 2>/dev/null | grep -v __)" ]; then
    echo "  Removing empty backend/api/services/"
    rm -rf backend/api/services
fi

if [ -d "backend/database/migrations" ] && [ -z "$(ls -A backend/database/migrations 2>/dev/null | grep -v __)" ]; then
    echo "  Removing empty backend/database/migrations/"
    rm -rf backend/database/migrations
fi

if [ -d "backend/database/schemas" ] && [ -z "$(ls -A backend/database/schemas 2>/dev/null | grep -v __)" ]; then
    echo "  Removing empty backend/database/schemas/"
    rm -rf backend/database/schemas
fi

echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 2: Remove Python cache files
echo -e "${YELLOW}Step 2: Removing Python cache files...${NC}"
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find backend -type f -name "*.pyc" -delete 2>/dev/null || true
find backend -type f -name "*.pyo" -delete 2>/dev/null || true
find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Cache cleaned${NC}"
echo ""

# Step 3: Stop and clean containers
echo -e "${YELLOW}Step 3: Stopping and cleaning Docker containers...${NC}"
docker compose down -v 2>&1 | head -10
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Step 4: Rebuild containers
echo -e "${YELLOW}Step 4: Rebuilding containers...${NC}"
docker compose build --no-cache backend 2>&1 | tail -20
echo -e "${GREEN}✓ Backend rebuilt${NC}"
echo ""

# Step 5: Start services
echo -e "${YELLOW}Step 5: Starting services...${NC}"
docker compose up -d
echo -e "${GREEN}✓ Services starting${NC}"
echo ""

# Step 6: Wait for services
echo -e "${YELLOW}Step 6: Waiting for services to initialize (60 seconds)...${NC}"
for i in {1..60}; do
    echo -ne "${BLUE}[$i/60]${NC}\r"
    sleep 1
done
echo ""

# Step 7: Check services
echo -e "${YELLOW}Step 7: Checking service status...${NC}"
docker compose ps
echo ""

# Step 8: Verify database
echo -e "${YELLOW}Step 8: Verifying database...${NC}"
echo "  Checking users table..."
docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT username, role, is_active FROM users;" 2>&1 | head -10
echo ""
echo "  Checking enum values..."
docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype;" 2>&1 | head -10
echo ""

# Step 9: Test backend health
echo -e "${YELLOW}Step 9: Testing backend health...${NC}"
sleep 5
HEALTH=$(curl -s http://localhost:8000/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
    echo "$HEALTH"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "$HEALTH"
fi
echo ""

# Step 10: Test login endpoint
echo -e "${YELLOW}Step 10: Testing login endpoint...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>&1)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Login successful!${NC}"
    echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESPONSE"
    echo ""
    echo "Checking backend logs for errors..."
    docker compose logs backend | grep -i "error\|exception" | tail -20
fi
echo ""

# Step 11: Check frontend
echo -e "${YELLOW}Step 11: Testing frontend...${NC}"
FRONTEND=$(curl -s http://localhost:3000 2>&1)
if echo "$FRONTEND" | grep -q "html\|HTML"; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend not responding${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Open browser: http://localhost:3000"
echo "2. Try logging in with:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo ""
echo "If issues persist, check logs:"
echo "  docker compose logs backend"
echo "  docker compose logs frontend"
echo ""
echo -e "${GREEN}Debug and cleanup complete!${NC}"
