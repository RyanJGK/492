#!/bin/bash
# Complete Login Test Script
# Tests all authentication paths after debugging

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Energy Defense - Login Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Helper functions
pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASS_COUNT++))
}

fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAIL_COUNT++))
}

test_api() {
    local description=$1
    local method=$2
    local url=$3
    local data=$4
    local expected=$5
    local headers=$6
    
    echo -ne "${YELLOW}Testing:${NC} $description... "
    
    if [ "$method" == "POST" ]; then
        if [ -n "$headers" ]; then
            response=$(curl -s -X POST "$url" -H "Content-Type: application/json" -H "$headers" -d "$data" 2>&1)
        else
            response=$(curl -s -X POST "$url" -H "Content-Type: application/json" -d "$data" 2>&1)
        fi
    else
        if [ -n "$headers" ]; then
            response=$(curl -s -H "$headers" "$url" 2>&1)
        else
            response=$(curl -s "$url" 2>&1)
        fi
    fi
    
    if echo "$response" | grep -q "$expected"; then
        pass "$description"
        return 0
    else
        fail "$description"
        echo "  Expected to contain: $expected"
        echo "  Got: $response" | head -c 200
        echo ""
        return 1
    fi
}

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        pass "Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        fail "Backend did not start in time"
        exit 1
    fi
    sleep 1
done
echo ""

# Test 1: Backend Health
echo -e "${BLUE}Test Group 1: Service Health${NC}"
test_api "Backend health endpoint" "GET" "http://localhost:8000/health" "" "healthy"
test_api "Frontend accessible" "GET" "http://localhost:3000" "" "html"
echo ""

# Test 2: Database Verification
echo -e "${BLUE}Test Group 2: Database${NC}"
echo -ne "${YELLOW}Testing:${NC} Users exist in database... "
USERS=$(docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT COUNT(*) FROM users;" -t 2>&1)
if [ $(echo $USERS | tr -d ' ') -ge 3 ]; then
    pass "Users exist in database"
else
    fail "Users missing in database"
fi

echo -ne "${YELLOW}Testing:${NC} Enum values are lowercase... "
ENUM_VALUES=$(docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype;" -t 2>&1)
if echo "$ENUM_VALUES" | grep -q "admin" && ! echo "$ENUM_VALUES" | grep -q "ADMIN"; then
    pass "Enum values are lowercase"
else
    fail "Enum values incorrect"
fi
echo ""

# Test 3: Login API (various cases)
echo -e "${BLUE}Test Group 3: Login API${NC}"
test_api "Login with lowercase username" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"admin","password":"admin123"}' "access_token"
test_api "Login with uppercase username" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"ADMIN","password":"admin123"}' "access_token"
test_api "Login with mixed case username" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"AdMiN","password":"admin123"}' "access_token"
test_api "Login analyst user" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"analyst","password":"admin123"}' "access_token"
test_api "Login observer user" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"observer","password":"admin123"}' "access_token"
echo ""

# Test 4: Authentication Failures
echo -e "${BLUE}Test Group 4: Auth Failures${NC}"
test_api "Wrong password rejected" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"admin","password":"wrongpassword"}' "Incorrect username or password"
test_api "Non-existent user rejected" "POST" "http://localhost:8000/api/v1/auth/login" '{"username":"nonexistent","password":"admin123"}' "Incorrect username or password"
echo ""

# Test 5: Token Usage
echo -e "${BLUE}Test Group 5: Token Authentication${NC}"
echo -ne "${YELLOW}Testing:${NC} Get access token... "
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' 2>&1)

if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    pass "Got access token"
    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    
    if [ -n "$ACCESS_TOKEN" ]; then
        test_api "Access protected endpoint with token" "GET" "http://localhost:8000/api/v1/auth/me" "" "admin" "Authorization: Bearer $ACCESS_TOKEN"
    else
        fail "Could not extract access token"
    fi
else
    fail "Could not get access token"
fi
echo ""

# Test 6: Role Verification
echo -e "${BLUE}Test Group 6: Role Assignment${NC}"
for user in "admin" "analyst" "observer"; do
    echo -ne "${YELLOW}Testing:${NC} $user role... "
    TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$user\",\"password\":\"admin123\"}" 2>&1)
    
    TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    
    if [ -n "$TOKEN" ]; then
        USER_RESP=$(curl -s http://localhost:8000/api/v1/auth/me \
            -H "Authorization: Bearer $TOKEN" 2>&1)
        
        if echo "$USER_RESP" | grep -q "\"role\":\"$user\""; then
            pass "$user has correct role"
        else
            fail "$user role incorrect"
            echo "  Response: $USER_RESP"
        fi
    else
        fail "Could not get token for $user"
    fi
done
echo ""

# Test 7: Token Structure
echo -e "${BLUE}Test Group 7: Token Structure${NC}"
echo -ne "${YELLOW}Testing:${NC} Token contains required fields... "
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' 2>&1)

if echo "$TOKEN_RESP" | grep -q "access_token" && \
   echo "$TOKEN_RESP" | grep -q "refresh_token" && \
   echo "$TOKEN_RESP" | grep -q "token_type"; then
    pass "Token has all required fields"
else
    fail "Token missing required fields"
    echo "  Response: $TOKEN_RESP"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "You can now login at:"
    echo "  http://localhost:3000"
    echo ""
    echo "Credentials (case-insensitive):"
    echo "  Admin:    admin    / admin123"
    echo "  Analyst:  analyst  / admin123"
    echo "  Observer: observer / admin123"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    echo ""
    echo "Debugging steps:"
    echo "1. Check backend logs:"
    echo "   docker compose logs backend | tail -50"
    echo ""
    echo "2. Check database:"
    echo "   docker compose exec postgres psql -U admin -d energy_defense -c 'SELECT * FROM users;'"
    echo ""
    echo "3. Run complete cleanup:"
    echo "   ./DEBUG_AND_CLEANUP.sh"
    echo ""
    echo "4. See AUTH_DEBUG_GUIDE.md for detailed troubleshooting"
    echo ""
    exit 1
fi
