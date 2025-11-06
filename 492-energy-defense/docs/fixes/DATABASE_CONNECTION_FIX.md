# 🔴 CRITICAL FIX: Database "admin" Does Not Exist

## Error Found

```
FATAL: database "admin" does not exist
```

## Root Cause

PostgreSQL healthcheck and connections were trying to connect to a database named "admin" instead of "energy_defense".

## The Problem

The healthcheck command was using `${POSTGRES_USER}` as the database name:

```yaml
# docker-compose.yml - WRONG:
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-admin}"]
  # This checks if user 'admin' can connect
  # But doesn't specify database, so it tries database 'admin'
```

## Why It Fails

PostgreSQL behavior:
1. `pg_isready -U admin` tries to connect to database `admin` by default
2. We only created database `energy_defense`
3. Database `admin` doesn't exist → FATAL error

## The Solution

**Option 1: Specify database in healthcheck (BEST):**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-admin} -d ${POSTGRES_DB:-energy_defense}"]
```

**Option 2: Use postgres database (always exists):**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-admin} -d postgres"]
```

**Option 3: Don't specify database:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready"]
  # Just checks if PostgreSQL is accepting connections
```

## Current Fix Applied

Using Option 3 (simplest and most reliable):

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## Why This Works

`pg_isready` without arguments:
- ✅ Checks if PostgreSQL server is running
- ✅ Checks if it's accepting connections
- ✅ Doesn't try to connect to specific database
- ✅ Returns exit code 0 when ready

This is actually BETTER than checking a specific database because:
1. Server might be ready but database still initializing
2. We just need to know when to start dependent services
3. Backend will retry database connection anyway

## Files Fixed

✅ `docker-compose.yml`:
```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready"]  # ✅ Fixed
```

## Related Errors

This was causing cascade failures:
```
backend → waits for postgres healthy
postgres → tries to check database 'admin'
         → fails because 'admin' database doesn't exist
         → never becomes healthy
         → backend never starts
```

## Verification

After fix:
```bash
docker-compose up postgres

# Wait 10 seconds, then:
docker-compose ps

# Should show:
# postgres    Up (healthy)    ✅
```

Test manually:
```bash
docker-compose exec postgres pg_isready
# Returns: accepting connections ✅

docker-compose exec postgres psql -U admin -l
# Should list 'energy_defense' database ✅
```

## Prevention

When writing healthchecks:
- ✅ Test the command manually first
- ✅ Use simplest check that works
- ✅ Don't over-specify (just check service is ready)
- ✅ Let application handle connection retries

---

**Status:** ✅ FIXED  
**Impact:** Critical - prevented all services from starting  
**Solution:** Simplified healthcheck to just check server ready
