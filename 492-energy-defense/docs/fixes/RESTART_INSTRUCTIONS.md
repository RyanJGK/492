# 🔄 Restart Instructions After Database Fix

## Issue Fixed ✅

The database role error has been resolved. The `init.sql` script now creates database roles before granting permissions.

## How to Apply the Fix

### Quick Restart (Recommended)

```bash
cd /workspace/492-energy-defense

# Clean restart with fresh database
docker-compose down -v
docker-compose up --build
```

**OR** if using Docker Compose v2:

```bash
cd /workspace/492-energy-defense

# Clean restart with fresh database
docker compose down -v
docker compose up --build
```

### What the Commands Do

**`docker-compose down -v`**
- Stops all running containers
- Removes containers
- **Removes volumes** (including postgres_data)
- This ensures a fresh database initialization

**`docker-compose up --build`**
- Rebuilds container images
- Starts all services
- Runs init.sql with the fix
- Creates database roles correctly

## Startup Sequence

After running the commands, you'll see:

1. **Building images** (~1-2 minutes first time)
   ```
   Building backend...
   Building frontend...
   Building ai-agent...
   ```

2. **Starting services** (~30 seconds)
   ```
   Creating energy-defense-db...
   Creating energy-defense-redis...
   Creating energy-defense-api...
   Creating energy-defense-ai-agent...
   Creating energy-defense-simulator...
   Creating energy-defense-frontend...
   ```

3. **Database initialization** (~10 seconds)
   ```
   energy-defense-db | PostgreSQL init process complete
   energy-defense-db | database system is ready to accept connections
   ```

4. **Services ready** 
   ```
   energy-defense-api | INFO:     Application startup complete
   energy-defense-frontend | VITE ready in X ms
   ```

## Verify Success

### Check All Services Are Running

```bash
docker-compose ps
# or
docker compose ps
```

Expected output:
```
NAME                        STATUS
energy-defense-db           Up (healthy)
energy-defense-redis        Up
energy-defense-api          Up
energy-defense-ai-agent     Up
energy-defense-simulator    Up
energy-defense-frontend     Up
```

### Verify No Database Errors

```bash
docker-compose logs postgres | grep ERROR
# or
docker compose logs postgres | grep ERROR
```

Expected: **NO errors** (or only INFO messages)

### Verify Roles Were Created

```bash
docker-compose exec postgres psql -U admin -d energy_defense -c "\du"
# or
docker compose exec postgres psql -U admin -d energy_defense -c "\du"
```

Expected output should include:
```
observer_role
analyst_role
admin_role
```

### Test the Application

1. Open browser: http://localhost:3000
2. Login: admin / admin123
3. Dashboard should load with statistics

## What Changed in init.sql

**Before (causing error):**
```sql
-- This failed because roles didn't exist
GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_role;
```

**After (fixed):**
```sql
-- Create roles first
CREATE ROLE observer_role;
CREATE ROLE analyst_role;
CREATE ROLE admin_role;

-- Then grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_role;
GRANT SELECT, INSERT ON ai_feedback TO analyst_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;
```

## Troubleshooting

### If "docker-compose" command not found

Try without the hyphen:
```bash
docker compose down -v
docker compose up --build
```

### If services fail to start

Check individual service logs:
```bash
docker-compose logs backend
docker-compose logs postgres
docker-compose logs frontend
```

### If port conflicts

Another service might be using the ports. Check:
```bash
# Check port 3000 (frontend)
lsof -i :3000

# Check port 8000 (backend)
lsof -i :8000

# Check port 5432 (postgres)
lsof -i :5432
```

Kill conflicting processes or change ports in `docker-compose.yml`

### If database still has errors

Completely remove the volume manually:
```bash
docker-compose down
docker volume ls | grep postgres
docker volume rm 492-energy-defense_postgres_data
docker-compose up --build
```

### If frontend shows "Cannot connect to API"

1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check CORS settings in `.env`:
   ```bash
   cat .env | grep CORS_ORIGINS
   ```

3. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

## After Successful Startup

1. ✅ Login at http://localhost:3000
2. ✅ Try different user roles (admin, analyst, observer)
3. ✅ Check dashboard statistics
4. ✅ View vulnerabilities page
5. ✅ Monitor data simulator: `docker-compose logs -f data-simulator`

## Keep Running in Background

Once verified, run in detached mode:
```bash
docker-compose up -d
```

View logs when needed:
```bash
docker-compose logs -f [service-name]
```

Stop when done:
```bash
docker-compose down
```

## Performance Notes

- First startup: ~2-3 minutes (building images)
- Subsequent startups: ~30-45 seconds
- Database init: ~10 seconds
- Frontend ready: ~15-20 seconds

---

**You're ready to go! The database role issue is fixed.**

Next: Add your OpenRouter API key to `.env` if you haven't already, then start the system.
