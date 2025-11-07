#!/bin/bash

# CORS Troubleshooting Script for 492-Energy-Defense

echo "🔍 CORS Troubleshooting for 492-Energy-Defense"
echo "=============================================="
echo ""

# Check if backend is running
echo "1️⃣ Checking if backend is running..."
if curl -f http://localhost:8000/health 2>/dev/null > /dev/null; then
    echo "✅ Backend is running and responding"
else
    echo "❌ Backend is not responding on http://localhost:8000"
    echo "   Try: docker-compose restart backend"
    echo ""
fi

# Check backend logs for CORS errors
echo ""
echo "2️⃣ Checking backend logs for CORS issues..."
docker-compose logs backend --tail=20 | grep -i "cors\|origin" || echo "No CORS-related messages found"

# Test CORS headers
echo ""
echo "3️⃣ Testing CORS headers..."
curl -I -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" 2>/dev/null | grep -i "access-control" || echo "❌ No CORS headers found"

# Check if frontend can reach backend
echo ""
echo "4️⃣ Testing backend connectivity from host..."
if curl -f http://localhost:8000/ 2>/dev/null > /dev/null; then
    echo "✅ Backend is accessible from host"
else
    echo "❌ Cannot reach backend from host"
fi

# Check Docker network
echo ""
echo "5️⃣ Checking Docker network..."
docker network inspect energy-defense-network > /dev/null 2>&1 && echo "✅ Docker network exists" || echo "❌ Docker network not found"

# Check if services are in the same network
echo ""
echo "6️⃣ Services in network:"
docker network inspect energy-defense-network -f '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null

# Provide solutions
echo ""
echo "🔧 Common Solutions:"
echo ""
echo "1. Restart all services:"
echo "   docker-compose down && docker-compose up --build"
echo ""
echo "2. Check backend environment variables:"
echo "   docker-compose exec backend env | grep CORS"
echo ""
echo "3. View backend logs:"
echo "   docker-compose logs backend -f"
echo ""
echo "4. Test API directly:"
echo '   curl -X POST http://localhost:8000/api/v1/auth/login \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"username":"admin","password":"demo123"}'"'"
echo ""
echo "5. Clear browser cache and try again"
echo ""
