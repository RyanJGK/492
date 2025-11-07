#!/bin/bash
# Fix Login Authentication Issues
# Run this script to diagnose and fix login problems

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Login Authentication Fix${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Step 1: Check if users exist
echo -e "${YELLOW}Step 1: Checking if users exist in database...${NC}"
USERS=$(docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT COUNT(*) FROM users;" -t 2>&1 | tr -d ' ')

if [ "$USERS" -eq "0" ] || [ -z "$USERS" ]; then
    echo -e "${RED}❌ No users found in database!${NC}"
    echo -e "${YELLOW}Database was not initialized.${NC}"
    echo ""
    NEED_RESET=true
else
    echo -e "${GREEN}✅ Found $USERS users${NC}"
    NEED_RESET=false
fi
echo ""

# Step 2: Check password hash format
if [ "$NEED_RESET" = false ]; then
    echo -e "${YELLOW}Step 2: Checking password hash format...${NC}"
    HASH=$(docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT substring(hashed_password, 1, 7) FROM users WHERE username='admin';" -t 2>&1 | tr -d ' ')
    
    if [ "$HASH" = "\$2b\$12\$" ]; then
        echo -e "${GREEN}✅ Password hash format is correct (bcrypt)${NC}"
    else
        echo -e "${RED}❌ Password hash format is wrong: $HASH${NC}"
        echo -e "${YELLOW}Expected: \$2b\$12\$ (bcrypt format)${NC}"
        NEED_RESET=true
    fi
    echo ""
fi

# Step 3: Check enum types
if [ "$NEED_RESET" = false ]; then
    echo -e "${YELLOW}Step 3: Checking enum types...${NC}"
    ENUM_CHECK=$(docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype LIMIT 1;" -t 2>&1 | tr -d ' ')
    
    if [ "$ENUM_CHECK" = "admin" ]; then
        echo -e "${GREEN}✅ Enum types are correct (lowercase)${NC}"
    else
        echo -e "${RED}❌ Enum types are wrong${NC}"
        echo -e "${YELLOW}Expected: 'admin' (lowercase), Got: '$ENUM_CHECK'${NC}"
        NEED_RESET=true
    fi
    echo ""
fi

# Step 4: Test login if everything looks good
if [ "$NEED_RESET" = false ]; then
    echo -e "${YELLOW}Step 4: Testing login with current database...${NC}"
    LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "admin123"}' 2>&1)
    
    HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n 1)
    RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Login works! No fix needed.${NC}"
        echo -e "${GREEN}Response: $RESPONSE_BODY${NC}"
        echo ""
        echo -e "${GREEN}Try logging in again at http://localhost:3000${NC}"
        exit 0
    else
        echo -e "${RED}❌ Login failed with HTTP $HTTP_CODE${NC}"
        echo -e "${RED}Response: $RESPONSE_BODY${NC}"
        NEED_RESET=true
    fi
    echo ""
fi

# Step 5: Apply fix if needed
if [ "$NEED_RESET" = true ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}FIX REQUIRED: Database Reset Needed${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
    echo -e "${YELLOW}This will:${NC}"
    echo "  1. Stop all containers"
    echo "  2. Remove database volume (delete all data)"
    echo "  3. Rebuild containers with fresh database"
    echo "  4. Wait for services to start"
    echo "  5. Test login"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Starting fix...${NC}"
        echo ""
        
        echo -e "${YELLOW}Stopping containers...${NC}"
        docker compose down -v
        
        echo -e "${YELLOW}Rebuilding containers...${NC}"
        docker compose up --build -d
        
        echo -e "${YELLOW}Waiting for services to start (60 seconds)...${NC}"
        for i in {1..60}; do
            echo -ne "${BLUE}[$i/60]${NC}\r"
            sleep 1
        done
        echo ""
        
        echo -e "${YELLOW}Testing login...${NC}"
        LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
          -H "Content-Type: application/json" \
          -d '{"username": "admin", "password": "admin123"}' 2>&1)
        
        HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n 1)
        RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}✅ FIX SUCCESSFUL!${NC}"
            echo -e "${GREEN}========================================${NC}"
            echo ""
            echo -e "${GREEN}Login is now working!${NC}"
            echo ""
            echo -e "${BLUE}Next steps:${NC}"
            echo "1. Open browser: http://localhost:3000"
            echo "2. Login with:"
            echo "   Username: admin"
            echo "   Password: admin123"
            echo ""
            echo "You should now be redirected to the dashboard!"
        else
            echo -e "${RED}========================================${NC}"
            echo -e "${RED}❌ FIX FAILED${NC}"
            echo -e "${RED}========================================${NC}"
            echo ""
            echo -e "${RED}Login still failing with HTTP $HTTP_CODE${NC}"
            echo -e "${RED}Response: $RESPONSE_BODY${NC}"
            echo ""
            echo -e "${YELLOW}Check backend logs:${NC}"
            docker compose logs backend | tail -50
        fi
    else
        echo -e "${YELLOW}Fix cancelled.${NC}"
    fi
fi
