#!/bin/bash
# Test backend authentication directly

echo "================================"
echo "Backend Authentication Test"
echo "================================"
echo ""

# Test 1: Check if backend is running
echo "Test 1: Backend health check..."
HEALTH=$(curl -s http://localhost:8000/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not responding"
    echo "Run: docker compose up -d backend"
    exit 1
fi
echo ""

# Test 2: Check database users
echo "Test 2: Check database users..."
docker compose exec -T postgres psql -U admin -d energy_defense -c "SELECT username, role FROM users;" 2>&1 | head -10
echo ""

# Test 3: Test login API
echo "Test 3: Testing login API with admin/admin123..."
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' 2>&1)

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_STATUS"
echo "Response: $RESPONSE_BODY"
echo ""

if [ "$HTTP_STATUS" == "200" ]; then
    echo "✅ Login successful!"
    exit 0
else
    echo "❌ Login failed with status $HTTP_STATUS"
    echo ""
    echo "Checking backend logs..."
    docker compose logs backend | tail -30
    echo ""
    echo "Possible fixes:"
    echo "1. Reset database:"
    echo "   docker compose down -v"
    echo "   docker compose up --build -d"
    echo ""
    echo "2. Check password hash:"
    echo "   docker compose exec postgres psql -U admin -d energy_defense -c \"SELECT username, substring(hashed_password, 1, 10) FROM users;\""
    exit 1
fi
