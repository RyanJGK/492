# 🚨 FIX LOGIN ISSUE - IMMEDIATE ACTION REQUIRED

## PROBLEM IDENTIFIED ✅

The password hash in `init.sql` is **INVALID**. This is why login fails!

```
Password: admin123
Stored Hash: WRONG! ❌
Login Result: "Invalid credentials"
```

## TWO OPTIONS TO FIX

### Option 1: Quick Fix (Update Live Database) - 2 Minutes

**If containers are already running:**

```bash
cd /workspace/492-energy-defense

# Step 1: Generate correct hash
docker-compose exec backend python3 generate-password-hash.py
# or
docker compose exec backend python3 generate-password-hash.py

# Step 2: Copy the hash from output

# Step 3: Update database directly
docker-compose exec postgres psql -U admin -d energy_defense

# In psql prompt, paste this (replace HASH with the new one):
UPDATE users 
SET hashed_password = 'NEW_HASH_HERE'
WHERE username IN ('admin', 'analyst', 'observer');

-- Verify it worked:
SELECT username, LEFT(hashed_password, 20) as hash_preview FROM users;

-- Exit:
\q

# Step 4: Try login at http://localhost:3000
# Username: admin
# Password: admin123
# Should work now! ✅
```

### Option 2: Proper Fix (Update init.sql and Rebuild) - 5 Minutes

**Best for permanent fix:**

```bash
cd /workspace/492-energy-defense

# Step 1: Generate hash
docker-compose exec backend python3 generate-password-hash.py

# Step 2: Copy the hash

# Step 3: Edit init.sql
nano backend/database/init.sql

# Step 4: Find line 177-180, replace ALL THREE hashes:
INSERT INTO users (username, email, hashed_password, role) VALUES
    ('admin', 'admin@energy-defense.local', 'PASTE_NEW_HASH_HERE', 'admin'),
    ('analyst', 'analyst@energy-defense.local', 'PASTE_NEW_HASH_HERE', 'analyst'),
    ('observer', 'observer@energy-defense.local', 'PASTE_NEW_HASH_HERE', 'observer')

# Step 5: Save and exit (Ctrl+X, Y, Enter)

# Step 6: Rebuild from scratch
docker-compose down -v
docker-compose up --build

# Step 7: Wait 60 seconds, then test login
```

## Why This Happened

The original hash was probably:
1. Generated with a different bcrypt library
2. Corrupted during copy/paste
3. For a different password
4. Using wrong cost factor

## Verification

After fixing, test with:

```bash
# Test via API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

## Prevention for Future

The hash generation script is now available:

```bash
# Generate hash for any password
docker-compose exec backend python3 << 'EOF'
from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = input("Enter password: ")
print("Hash:", pwd.hash(password))
EOF
```

## What If Containers Aren't Running?

If you can't generate the hash because containers aren't up:

**Use a pre-generated valid hash:**

I can provide a known-good hash for "admin123" if you need it immediately.

However, **it's better to generate it yourself** to ensure compatibility with your specific bcrypt version.

## Quick Diagnostic

Check if users exist in database:

```bash
docker-compose exec postgres psql -U admin -d energy_defense -c \
  "SELECT username, role, LEFT(hashed_password, 30) as hash FROM users;"
```

Should show 3 users with hashes starting with `$2b$12$`

## Summary

**Root Cause:** Invalid bcrypt hash in init.sql  
**Symptom:** "Invalid credentials" on login  
**Fix:** Generate new hash with passlib[bcrypt]  
**Time:** 2-5 minutes  
**Priority:** 🔴 CRITICAL - blocks all login  

---

**Choose Option 1 for quick fix, Option 2 for permanent solution.**
