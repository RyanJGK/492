# Troubleshooting Guide

## Common Issues and Solutions

### CORS Error: "Cross-Origin Request Blocked"

**Error Message:**
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading 
the remote resource at http://localhost:8000/api/v1/auth/login. 
(Reason: CORS request did not succeed).
```

**Root Cause:**
The frontend (running in your browser) cannot connect to the backend service.

**Solutions:**

#### 1. Quick Fix - Restart Services
```bash
# Stop all services
docker-compose down

# Rebuild and start
docker-compose up --build

# Wait for all services to be healthy (30-60 seconds)
```

#### 2. Run the CORS Troubleshooting Script
```bash
bash scripts/troubleshoot-cors.sh
```

#### 3. Check Backend is Running
```bash
# Check container status
docker-compose ps

# Backend should show "Up" and port 8000 exposed
# If not, check logs:
docker-compose logs backend
```

#### 4. Test Backend Directly
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy","version":"1.0.0"}

# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"demo123"}'

# Should return JWT tokens
```

#### 5. Verify Environment Variables
```bash
# Check backend CORS configuration
docker-compose exec backend python -c "
from app.core.config import settings
print('CORS Origins:', settings.BACKEND_CORS_ORIGINS)
"
```

#### 6. Check Docker Network
```bash
# Verify all services are in the same network
docker network inspect energy-defense-network

# All services should be listed
```

#### 7. Clear Browser Cache
- Open Developer Tools (F12)
- Right-click refresh button → "Empty Cache and Hard Reload"
- Or use incognito/private browsing mode

---

### Backend Container Won't Start

**Symptoms:**
- Backend container exits immediately
- Error in logs about missing SECRET_KEY

**Solution:**
```bash
# Ensure .env file exists and has SECRET_KEY
cat .env | grep SECRET_KEY

# If missing, generate one:
openssl rand -hex 32

# Add to .env:
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Restart
docker-compose up -d backend
```

---

### Database Connection Failed

**Error Message:**
```
could not connect to server: Connection refused
```

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Wait for database to be ready (can take 30 seconds)
docker-compose exec postgres pg_isready -U energydefense

# If not ready, restart:
docker-compose restart postgres
sleep 10
docker-compose restart backend
```

---

### AI Agent Not Responding

**Error Message:**
```
AI Agent service unavailable
```

**Solutions:**

1. **Check OpenRouter API Key:**
```bash
# Verify key is set
cat .env | grep OPENROUTER_API_KEY

# Should not be empty or the example value
```

2. **Check AI Agent Logs:**
```bash
docker-compose logs ai-agent

# Look for authentication errors or API failures
```

3. **Test AI Agent Directly:**
```bash
curl http://localhost:8001/health

# Should return health status
```

---

### Frontend Not Loading

**Symptoms:**
- Blank page at http://localhost:3000
- Vite errors in logs

**Solutions:**

1. **Check Node Modules:**
```bash
# Rebuild frontend with fresh node_modules
docker-compose down
docker-compose up --build frontend
```

2. **Check Frontend Logs:**
```bash
docker-compose logs frontend

# Look for compilation errors
```

3. **Verify Port Availability:**
```bash
# Check if port 3000 is available
lsof -i :3000

# If in use, kill the process or change port in .env
```

---

### Data Simulator Not Ingesting Data

**Symptoms:**
- No data appearing in dashboard
- Simulator logs show authentication errors

**Solutions:**

1. **Check Simulator Logs:**
```bash
docker-compose logs data-simulator

# Look for authentication failures
```

2. **Verify Backend is Accessible:**
```bash
# From simulator container
docker-compose exec data-simulator curl http://backend:8000/health
```

3. **Check Default User Exists:**
```bash
# Connect to database
docker-compose exec postgres psql -U energydefense energy_defense

# Check users
SELECT username, role FROM users;

# Should show analyst1 user
```

---

### Docker Compose Issues

**Error: "network not found"**
```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up
```

**Error: "port already in use"**
```bash
# Find and kill process using the port
lsof -i :8000  # or :3000, :5432
kill -9 <PID>

# Or change port in .env
echo "BACKEND_PORT=8001" >> .env
```

**Error: "no space left on device"**
```bash
# Clean up Docker
docker system prune -a --volumes

# WARNING: This removes all unused containers, networks, and images
```

---

## Debugging Tools

### View All Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail=50 backend
```

### Access Container Shell
```bash
# Backend
docker-compose exec backend /bin/bash

# Database
docker-compose exec postgres psql -U energydefense energy_defense

# Frontend
docker-compose exec frontend /bin/sh
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Network Debugging
```bash
# Test connectivity between services
docker-compose exec frontend ping backend
docker-compose exec backend ping postgres
docker-compose exec backend ping ai-agent
```

---

## Advanced Debugging

### Enable Debug Logging

**Backend:**
```yaml
# In docker-compose.yml, add to backend environment:
LOG_LEVEL: DEBUG
```

**AI Agent:**
```yaml
# In docker-compose.yml, add to ai-agent environment:
LOG_LEVEL: DEBUG
```

### Check API Endpoints
```bash
# View all available endpoints
curl http://localhost:8000/docs

# Or use the interactive docs in browser
```

### Database Queries
```bash
# Connect to database
docker-compose exec postgres psql -U energydefense energy_defense

# Check data
SELECT COUNT(*) FROM auth_events;
SELECT COUNT(*) FROM vulnerabilities;
SELECT COUNT(*) FROM firewall_logs;
```

---

## Getting Help

If you're still experiencing issues:

1. **Run the health check:**
   ```bash
   bash scripts/check-health.sh
   ```

2. **Collect debug information:**
   ```bash
   # Save logs
   docker-compose logs > debug-logs.txt
   
   # Save configuration
   docker-compose config > debug-config.yml
   
   # Save container status
   docker-compose ps > debug-status.txt
   ```

3. **Check documentation:**
   - README.md
   - ARCHITECTURE.md
   - API_GUIDE.md

4. **Reset everything (last resort):**
   ```bash
   # WARNING: This deletes all data
   docker-compose down -v
   docker system prune -a
   rm -rf backend/__pycache__ ai-agent/__pycache__
   docker-compose up --build
   ```

---

## Quick Reference

### Restart Single Service
```bash
docker-compose restart <service-name>
```

### Rebuild Single Service
```bash
docker-compose up --build <service-name>
```

### View Service Configuration
```bash
docker-compose config
```

### Clean Restart
```bash
docker-compose down
docker-compose up --build
```

### Check All Health Endpoints
```bash
curl http://localhost:8000/health    # Backend
curl http://localhost:8001/health    # AI Agent
curl http://localhost:3000           # Frontend
```

---

**Still stuck? Check the logs first - they usually tell you exactly what's wrong!**
