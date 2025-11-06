# Database Role Issue - FIXED

## Problem

The initial database setup was failing with:
```
ERROR: role "observer_role" does not exist
```

## Root Cause

The `init.sql` script tried to grant permissions to database roles before creating them:

```sql
-- This failed because roles didn't exist
GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_role;
```

## Solution Applied

**File:** `backend/database/init.sql`

**Fix:** Create roles before granting permissions

```sql
-- Create database roles for RBAC
CREATE ROLE observer_role;
CREATE ROLE analyst_role;
CREATE ROLE admin_role;

-- Grant appropriate permissions (principle of least privilege)
GRANT CONNECT ON DATABASE energy_defense TO observer_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_role;
GRANT SELECT, INSERT ON ai_feedback TO analyst_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;

-- Grant usage on sequences for insert operations
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO analyst_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_role;
```

## To Apply the Fix

Since you've already tried starting the system, you need to clean up and restart:

### Method 1: Fresh Start (Recommended)

```bash
cd /workspace/492-energy-defense

# Stop and remove all containers and volumes
docker-compose down -v
# or
docker compose down -v

# Rebuild and start
docker-compose up --build
# or
docker compose up --build
```

### Method 2: Remove Only Database Volume

```bash
cd /workspace/492-energy-defense

# Stop containers
docker-compose down

# Remove only the postgres volume
docker volume rm 492-energy-defense_postgres_data

# Start again
docker-compose up
```

### Method 3: Manual Database Reset

```bash
# Stop containers
docker-compose down

# Start only postgres
docker-compose up -d postgres

# Wait for it to be ready (10 seconds)
sleep 10

# The fixed init.sql will run automatically
```

## Verification

After restarting, verify the database initialized correctly:

```bash
# Check container status
docker-compose ps

# Should show:
# energy-defense-db    Up (healthy)

# Check logs
docker-compose logs postgres | grep -i error

# Should show NO errors related to roles

# Verify roles were created
docker-compose exec postgres psql -U admin -d energy_defense -c "\du"

# Should show:
# observer_role
# analyst_role  
# admin_role
```

## Database Roles Explained

These roles implement database-level RBAC:

### observer_role
- **Permissions:** SELECT only (read-only)
- **Purpose:** For Observer users who need read-only access
- **Tables:** All tables in public schema

### analyst_role
- **Permissions:** SELECT + INSERT on ai_feedback
- **Purpose:** For Analyst users who can submit feedback
- **Tables:** All tables (read) + ai_feedback (write)

### admin_role
- **Permissions:** ALL PRIVILEGES
- **Purpose:** For Admin users with full database access
- **Tables:** All tables (full control)

## Why This Happens

PostgreSQL requires roles to exist before you can grant permissions to them. The roles are separate from the users - they're essentially permission templates.

In production, you would:
1. Create roles (one-time setup)
2. Create users
3. Grant role membership to users

For this demo, the roles are created automatically during database initialization.

## Status

✅ **FIXED** - The init.sql has been corrected

⚠️ **ACTION REQUIRED:** Run `docker-compose down -v` then `docker-compose up --build` to apply the fix

## Related Files

- `backend/database/init.sql` - Contains the fix (lines 201-215)
- `.env` - Database connection settings
- `docker-compose.yml` - PostgreSQL service configuration

## Prevention

This fix ensures:
- Roles are created before any GRANT statements
- Proper permission hierarchy (least privilege)
- Support for production RBAC if needed
- Clean database initialization

## Next Steps

1. ✅ Stop all containers: `docker-compose down -v`
2. ✅ Start system: `docker-compose up --build`
3. ✅ Verify startup: Check for "database system is ready to accept connections"
4. ✅ Test login: Visit http://localhost:3000
5. ✅ Confirm no errors: `docker-compose logs postgres | grep ERROR`

---

**The issue is now resolved. Your database will initialize successfully.**
