# 🔴 CRITICAL FIX: SQLAlchemy Reserved Word 'metadata'

## Error Found

```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## Root Cause

SQLAlchemy's `Base` class (declarative base) has a reserved attribute called `metadata` that holds the MetaData object containing all table definitions. We can't use `metadata` as a column name directly.

## The Problem

**Three tables had columns named `metadata`:**
```python
# This causes conflict:
class AuthEvent(Base):
    metadata = Column(JSON, nullable=True)  # ❌ CONFLICTS with Base.metadata

class VulnerabilityScan(Base):
    metadata = Column(JSON)  # ❌ CONFLICTS

class FirewallLog(Base):
    metadata = Column(JSON)  # ❌ CONFLICTS
```

## The Solution

**Use column name override to map to database column:**
```python
# This works:
class AuthEvent(Base):
    event_metadata = Column("metadata", JSON, nullable=True)  # ✅ Python attr: event_metadata, DB column: metadata

class VulnerabilityScan(Base):
    scan_metadata = Column("metadata", JSON)  # ✅

class FirewallLog(Base):
    log_metadata = Column("metadata", JSON)  # ✅
```

## How It Works

```python
Column("column_name_in_db", Type)
```

- **First argument** = actual database column name
- **Variable name** = Python attribute name

So:
```python
event_metadata = Column("metadata", JSON)
```

Means:
- In Python: `auth_event.event_metadata`
- In Database: `auth_events.metadata` column

## Files Fixed

✅ `backend/api/models.py`:
- `AuthEvent.metadata` → `AuthEvent.event_metadata`
- `VulnerabilityScan.metadata` → `VulnerabilityScan.scan_metadata`
- `FirewallLog.metadata` → `FirewallLog.log_metadata`

## Database Impact

**NO database changes needed!** ✅

The database columns are still called `metadata`. Only the Python attribute names changed.

```sql
-- Database schema unchanged:
CREATE TABLE auth_events (
    ...
    metadata JSONB  -- Still called 'metadata' in DB
);
```

## API Impact

**Schemas need to be checked:**

```python
# If schemas reference .metadata, update them:
class AuthEventCreate(BaseModel):
    metadata: Optional[Dict[str, Any]] = None  # This is fine - it's the schema

# When creating objects:
auth_event = AuthEvent(
    event_metadata={"key": "value"}  # Use new Python name
)
```

## Testing

```python
# Test it works:
from api.models import AuthEvent

event = AuthEvent(
    user_id=1,
    event_type="login",
    success=True,
    event_metadata={"ip": "127.0.0.1"}  # ✅ New attribute name
)

# Database stores in 'metadata' column ✅
```

## Why This Happens

SQLAlchemy's `Base` class provides:
```python
Base.metadata  # MetaData object containing all table definitions
```

If we define:
```python
class MyModel(Base):
    metadata = Column(JSON)
```

It tries to override `Base.metadata`, causing the error.

## Prevention

**Reserved SQLAlchemy attribute names to avoid:**
- `metadata` ← Our issue
- `__table__`
- `__mapper__`
- `__tablename__`
- `__mapper_args__`
- `__table_args__`

## Verification

After fix, backend should start without errors:
```bash
docker-compose up backend

# Should see:
# "Database initialized successfully"
# "Application startup complete"
```

## Related Issues

This fix also required:
1. ✅ Adding simulator environment variables
2. ✅ Fixing database connection string

---

**Status:** ✅ FIXED
**Impact:** Critical - prevented backend from starting
**Database Changes:** None required
