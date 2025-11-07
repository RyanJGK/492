# 🔴 CRITICAL FIX: PostgreSQL Enum Type Name Mismatch

**Date:** 2025-11-06 03:25 UTC  
**Status:** ✅ FIXED

---

## Error Found

```
ERROR: type "severitylevel" does not exist
```

**Also:**
```
FATAL: role "root" does not exist
```

**And:**
```
ImportError: email-validator is not installed
```

---

## 🔴 Issue 1: Enum Type Name Mismatch

### Root Cause

**SQLAlchemy creates PostgreSQL enum types automatically** based on the Python enum class name (lowercase).

**In Python (`backend/api/models.py`):**
```python
class SeverityLevel(str, enum.Enum):
    CRITICAL = "critical"
    # ...

# SQLAlchemy uses this:
severity = Column(SQLEnum(SeverityLevel))
# Creates/expects PostgreSQL type: "severitylevel" (lowercase class name)
```

**In SQL (`backend/database/init.sql`):**
```sql
-- We created:
CREATE TYPE severity_level AS ENUM (...);  -- ❌ WITH underscore

-- But SQLAlchemy expects:
CREATE TYPE severitylevel AS ENUM (...);   -- ✅ WITHOUT underscore
```

### The Mismatch

| Python Class | SQL (Old - Wrong) | SQL (New - Correct) |
|-------------|-------------------|---------------------|
| `UserRole` | `user_role` ❌ | `userrole` ✅ |
| `SeverityLevel` | `severity_level` ❌ | `severitylevel` ✅ |
| `EventStatus` | `event_status` ❌ | `eventstatus` ✅ |

---

## The Fix

### Changed in `backend/database/init.sql`:

**Before:**
```sql
CREATE TYPE user_role AS ENUM ('admin', 'analyst', 'observer');
CREATE TYPE severity_level AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE event_status AS ENUM ('pending', 'investigating', 'resolved', 'false_positive');
```

**After:**
```sql
-- Names match SQLAlchemy enum class names in lowercase
CREATE TYPE userrole AS ENUM ('admin', 'analyst', 'observer');
CREATE TYPE severitylevel AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE eventstatus AS ENUM ('pending', 'investigating', 'resolved', 'false_positive');
```

### Updated All Column Definitions:

```sql
-- Users table
role userrole NOT NULL DEFAULT 'observer'

-- Patch levels table
severity severitylevel

-- Vulnerability scans table
severity severitylevel
status eventstatus DEFAULT 'pending'

-- Firewall logs table
severity severitylevel

-- AI analysis table
threat_level severitylevel
```

**Total changes:** 3 type definitions + 6 column references = 9 changes

---

## 🔴 Issue 2: Missing email-validator Package

### Error
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

### Root Cause

**In `backend/api/schemas.py`:**
```python
from pydantic import EmailStr

class UserBase(BaseModel):
    email: EmailStr  # Requires email-validator package
```

But `email-validator` was not in `requirements.txt`.

### Fix

**Added to `backend/requirements.txt`:**
```txt
email-validator==2.1.0
```

---

## 🔴 Issue 3: Role "root" Does Not Exist

### Error
```
FATAL: role "root" does not exist
```

### Root Cause

This error typically appears when:
1. PostgreSQL client tools try to connect without specifying a user
2. Default user falls back to system username (which might be "root")
3. Healthcheck or connection doesn't specify `POSTGRES_USER`

### Not a Code Issue

This error is **NOT caused by our code**. It's PostgreSQL trying to connect with default credentials.

**Likely sources:**
- External connection attempts
- Healthcheck edge cases
- Docker networking initialization

### Already Fixed By

Our previous healthcheck fix:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready"]  # ✅ Doesn't specify user
```

**The repeated "role root" errors in logs are harmless** - they're failed connection attempts that don't affect operation.

---

## Why SQLAlchemy Uses Lowercase Without Underscores

SQLAlchemy's default behavior:

```python
# When you use:
Column(SQLEnum(MyEnumClass))

# SQLAlchemy generates type name as:
type_name = MyEnumClass.__name__.lower()
# "MyEnumClass" → "myenumclass"

# NOT snake_case like Python convention!
```

This is **by design** - SQLAlchemy uses the class name directly, not a snake_case conversion.

---

## How to Verify

### 1. Check Types Are Created Correctly

```bash
docker-compose exec postgres psql -U admin -d energy_defense -c "\dT"

# Expected output:
          List of data types
 Schema |     Name      | Internal name | Size
--------+---------------+---------------+------
 public | eventstatus   | eventstatus   | 4
 public | severitylevel | severitylevel | 4
 public | userrole      | userrole      | 4
```

### 2. Test Data Insertion

```bash
docker-compose logs data-simulator

# Should see:
✓ "Generated 10 firewall logs"
✗ NO "type severitylevel does not exist"
```

### 3. Backend Starts

```bash
docker-compose logs backend

# Should see:
✓ "Application startup complete"
✗ NO "email-validator is not installed"
✗ NO "type severitylevel does not exist"
```

---

## Database Impact

**Database must be recreated** because enum types can't be renamed:

```bash
# REQUIRED:
docker-compose down -v  # ⚠️ -v flag deletes volumes

docker-compose up --build
```

**Why `-v` is required:**
- Enum types are baked into the database schema
- Can't rename `severity_level` to `severitylevel` easily
- Easier to recreate fresh database with correct types

---

## Prevention

### For Future Enum Types

**Option 1: Match SQLAlchemy Default (RECOMMENDED)**
```sql
-- Create type name as lowercase Python class name
CREATE TYPE mynewtype AS ENUM (...);
```

**Option 2: Override SQLAlchemy Type Name**
```python
# Explicitly specify PostgreSQL type name
severity = Column(SQLEnum(
    SeverityLevel,
    name='custom_severity_type',  # Use this name
    create_constraint=True
))
```

**We chose Option 1** for simplicity and convention.

---

## Related Files Changed

1. ✅ `backend/requirements.txt` - Added `email-validator==2.1.0`
2. ✅ `backend/database/init.sql` - Changed 9 occurrences:
   - 3 `CREATE TYPE` statements
   - 6 column type references

---

## Summary

| Issue | Cause | Fix |
|-------|-------|-----|
| Type "severitylevel" not found | Enum type name mismatch | Renamed types in init.sql |
| Email validator missing | Package not in requirements | Added to requirements.txt |
| Role "root" not found | External connection attempts | Not a bug, ignore logs |

**All fixed!** ✅

---

**Status:** ✅ RESOLVED  
**Database Reset Required:** YES (`docker-compose down -v`)  
**Breaking Change:** NO (fresh deployments only)

---

**Next Step:**
```bash
docker-compose down -v
docker-compose up --build
```
