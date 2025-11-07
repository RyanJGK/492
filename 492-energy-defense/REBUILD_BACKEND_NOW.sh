#!/bin/bash
# Rebuild backend with bcrypt fix

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Rebuilding Backend with Bcrypt Fix${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

echo -e "${YELLOW}Step 1: Stopping backend...${NC}"
docker compose stop backend
echo -e "${GREEN}✅ Backend stopped${NC}"
echo ""

echo -e "${YELLOW}Step 2: Removing backend container...${NC}"
docker compose rm -f backend
echo -e "${GREEN}✅ Container removed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Rebuilding backend with new dependencies...${NC}"
docker compose build --no-cache backend
echo -e "${GREEN}✅ Backend rebuilt${NC}"
echo ""

echo -e "${YELLOW}Step 4: Starting backend...${NC}"
docker compose up -d backend
echo -e "${GREEN}✅ Backend starting${NC}"
echo ""

echo -e "${YELLOW}Step 5: Waiting for backend to be ready (20 seconds)...${NC}"
for i in {1..20}; do
    echo -ne "${BLUE}[$i/20]${NC}\r"
    sleep 1
done
echo ""

echo -e "${YELLOW}Step 6: Checking for bcrypt errors...${NC}"
BCRYPT_ERROR=$(docker compose logs backend | grep -i "__about__" | wc -l)
if [ "$BCRYPT_ERROR" -eq 0 ]; then
    echo -e "${GREEN}✅ No bcrypt errors found${NC}"
else
    echo -e "${RED}⚠️  Still seeing bcrypt errors${NC}"
    docker compose logs backend | grep -i "bcrypt\|error" | tail -10
fi
echo ""

echo -e "${YELLOW}Step 7: Testing login...${NC}"
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' 2>&1)

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ SUCCESS! Login is working!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "${GREEN}You can now login at:${NC}"
    echo "  http://localhost:3000"
    echo ""
    echo -e "${BLUE}Credentials:${NC}"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    echo -e "${GREEN}The page will now redirect to dashboard after login!${NC}"
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}❌ Login still failing${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo -e "${RED}HTTP Status: $HTTP_CODE${NC}"
    echo -e "${RED}Response: $RESPONSE_BODY${NC}"
    echo ""
    echo -e "${YELLOW}Checking backend logs for errors...${NC}"
    docker compose logs backend | tail -30
fi
