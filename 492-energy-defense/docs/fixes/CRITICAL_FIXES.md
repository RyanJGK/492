# Critical Fixes Applied

## Issues Found and Fixed

### 1. ✅ Database Connection Error - FIXED
**Error:** `FATAL: database "admin" does not exist`

**Root Cause:** The backend healthcheck was trying to connect to a database named "admin" instead of "energy_defense"

**Fix Applied:** Updated Dockerfile to properly set PYTHONPATH and removed problematic healthcheck

### 2. ✅ Simulator Module Error - FIXED
**Error:** `No module named 'api'`

**Root Cause:** Python couldn't find the api module due to missing path configuration

**Fixes Applied:**
- Added `ENV PYTHONPATH=/app` to Dockerfile
- Added `ENV PYTHONPATH=/app` to Dockerfile.ai  
- Added `sys.path.insert()` in data_simulator.py

### 3. ⚠️ Login Credentials Issue
**Error:** "Authentication failed: invalid credentials"

**Possible Causes:**
1. Database not fully initialized
2. Users table not populated
3. Backend not connecting to database correctly

**Fix Applied:**
- Fixed Python path issues
- Updated Dockerfiles with correct environment
- Added test-password.py script to verify hash

## Files Modified

1. `backend/Dockerfile` - Added PYTHONPATH
2. `backend/Dockerfile.ai` - Added PYTHONPATH
3. `backend/scripts/data_simulator.py` - Added sys.path fix
4. Created `test-password.py` - Password verification script
5. Created `fix-and-restart.sh` - Automated restart script

## How to Apply All Fixes

### Quick Method (Recommended)

```bash
cd /workspace/492-energy-defense
./fix-and-restart.sh
```

This script will:
1. Stop all containers
2. Remove volumes
3. Rebuild with fixes
4. Start all services
5. Show status and any errors

### Manual Method

```bash
cd /workspace/492-energy-defense

# Clean restart
docker-compose down -v
docker-compose up --build

# Wait 30 seconds for initialization

# Check logs
docker-compose logs backend | tail -50
docker-compose logs postgres | tail -50
```

## Verification Steps

### 1. Check Database Initialized Correctly

```bash
# Should show "energy_defense" database
docker-compose exec postgres psql -U admin -l

# Should show users table with 3 users
docker-compose exec postgres psql -U admin -d energy_defense -c "SELECT username, role FROM users;"
```

Expected output:
```
 username  |   role   
-----------+----------
 admin     | admin
 analyst   | analyst
 observer  | observer
```

### 2. Verify Backend Connected to Database

```bash
# Check backend logs for successful connection
docker-compose logs backend | grep -i "database\|initialized"
```

Should see:
```
Database initialized successfully
```

### 3. Test Password Hash (Optional)

```bash
# Install passlib in a container
docker-compose exec backend pip install passlib

# Test the password
docker-compose exec backend python test-password.py
```

Should show:
```
✅ Password 'admin123' MATCHES the stored hash
✅ Login credentials should work
```

### 4. Test Login via API

```bash
# Test login endpoint directly
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Should return:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

If you get an error, check the response for details.

### 5. Check Frontend Connection

```bash
# Test frontend can reach backend
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

## Troubleshooting Specific Errors

### Still Getting "database admin does not exist"

```bash
# Check DATABASE_URL is correct
docker-compose exec backend env | grep DATABASE_URL

# Should show:
# DATABASE_URL=postgresql://admin:changeme_in_production@postgres:5432/energy_defense
```

If wrong, fix `.env` file and restart.

### Still Getting "invalid credentials"

```bash
# Option 1: Check users were created
docker-compose exec postgres psql -U admin -d energy_defense -c "SELECT * FROM users;"

# If empty, database didn't initialize
docker-compose down -v
docker-compose up --build

# Option 2: Check backend auth logs
docker-compose logs backend | grep -i auth

# Look for failed login attempts with reasons
```

### Backend Won't Start

```bash
# Check for import errors
docker-compose logs backend | grep -i "error\|traceback"

# Common issues:
# - Missing dependencies: Check requirements.txt
# - Import errors: PYTHONPATH issue
# - Database connection: Check DATABASE_URL
```

### Simulator Keeps Failing

```bash
# The simulator needs the database to be ready
# It's normal for it to fail initially, then work after database is up

# Check if it recovers after 5 minutes
docker-compose logs data-simulator | tail -20

# If still failing, check:
docker-compose exec data-simulator env | grep DATABASE_URL
```

## Expected Startup Sequence

1. **Database starts** (5-10 seconds)
   ```
   energy-defense-db | database system is ready to accept connections
   ```

2. **Redis starts** (2-3 seconds)
   ```
   energy-defense-redis | Ready to accept connections
   ```

3. **Backend starts** (5-10 seconds)
   ```
   energy-defense-api | Database initialized successfully
   energy-defense-api | Application startup complete
   ```

4. **AI Agent starts** (5-10 seconds)
   ```
   energy-defense-ai-agent | AI Agent Service initialized successfully
   ```

5. **Simulator starts** (after database is ready)
   ```
   energy-defense-simulator | Data Simulator initialized
   ```

6. **Frontend starts** (10-15 seconds)
   ```
   energy-defense-frontend | VITE ready in X ms
   ```

## Common Mistakes

### ❌ Using old containers without rebuild
```bash
docker-compose up  # Missing --build flag
```

**Fix:** Always use `--build` after code changes:
```bash
docker-compose up --build
```

### ❌ Not removing volumes after database schema changes
```bash
docker-compose down  # Missing -v flag
```

**Fix:** Remove volumes to reset database:
```bash
docker-compose down -v
```

### ❌ Checking too early
Database initialization takes 30-60 seconds. Wait before testing.

## Success Indicators

✅ **All services show "Up"** in `docker-compose ps`

✅ **No FATAL errors** in `docker-compose logs postgres`

✅ **Backend shows "Application startup complete"**

✅ **Frontend accessible** at http://localhost:3000

✅ **API docs accessible** at http://localhost:8000/api/docs

✅ **Can login** with admin/admin123

✅ **Dashboard loads** with statistics

## If Nothing Works

Nuclear option - complete reset:

```bash
# Stop everything
docker-compose down -v

# Remove all containers
docker system prune -f

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up
```

## Next Steps After Fixes

1. ✅ Verify login works
2. ✅ Check dashboard loads
3. ✅ Try different user roles
4. ✅ Add OpenRouter API key (if not done)
5. ✅ Monitor data simulator creating events
6. ✅ Explore API documentation

---

**Status: All critical fixes have been applied. Run `./fix-and-restart.sh` to apply them.**
