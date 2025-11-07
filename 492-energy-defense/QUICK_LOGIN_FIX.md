# 🚨 Quick Login Fix - 401 Unauthorized

**Problem:** Getting "Incorrect username or password" (401 error)

**Cause:** Database not initialized or password hash mismatch

---

## ⚡ **Fastest Fix** (2 minutes)

```bash
cd /workspace/492-energy-defense

# Complete database reset
docker compose down -v
docker compose up --build -d

# Wait for startup
sleep 60

# Test
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Should return: {"access_token": "eyJ...", ...}
```

**Then try logging in at http://localhost:3000 - it will work!**

---

## 🔧 **Automated Fix** (with diagnostics)

```bash
cd /workspace/492-energy-defense
./FIX_LOGIN_NOW.sh
```

This script will:
1. ✅ Check if users exist
2. ✅ Check password hash format  
3. ✅ Check enum types
4. ✅ Test login
5. 🔧 Fix if needed (resets database)
6. ✅ Verify fix worked

---

## 📋 **Manual Diagnosis** (if you want to understand the issue)

### Check 1: Do users exist?

```bash
docker compose exec postgres psql -U admin -d energy_defense -c "SELECT username, role FROM users;"
```

**Expected:**
```
 username | role
----------+----------
 admin    | admin
 analyst  | analyst
 observer | observer
```

**If you see 0 rows:** Database not initialized → Run fastest fix above

---

### Check 2: Is password hash correct?

```bash
docker compose exec postgres psql -U admin -d energy_defense -c \
  "SELECT username, substring(hashed_password, 1, 20) as hash FROM users WHERE username='admin';"
```

**Expected:**
```
 username |        hash
----------+--------------------
 admin    | $2b$12$EixZaYVK1fsb
```

**If hash doesn't start with `$2b$12$`:** Wrong password hash → Run fastest fix above

---

### Check 3: Are enum types correct?

```bash
docker compose exec postgres psql -U admin -d energy_defense -c \
  "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype;"
```

**Expected:**
```
 enumlabel
-----------
 admin
 analyst
 observer
```

**If you see ADMIN/ANALYST/OBSERVER (uppercase):** Wrong enum format → Run fastest fix above

---

## 🎯 **Why This Happened**

After applying the enum fixes (Fix #10, #12, #13), the database schema changed. The old database has:
- ❌ Wrong enum type names or values
- ❌ Possibly wrong password hashes

You need `docker compose down -v` to:
1. Delete the old database volume
2. Recreate database with new schema
3. Initialize with correct users and passwords

---

## ✅ **How to Verify Fix Worked**

### Test 1: Backend API

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Should return:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Test 2: Frontend Login

1. Open http://localhost:3000
2. Open DevTools (F12) → Console tab
3. Enter: admin / admin123
4. Click Sign In

**Should see in console:**
```
✅ [API] Login response received: {hasAccessToken: true, ...}
✅ [AuthContext] Login complete! User: admin Role: admin
✅ [LoginPage] Login successful! Navigating to dashboard...
🚀 [LoginPage] Navigation to dashboard triggered
```

**And page navigates to /dashboard**

---

## 🆘 **If Fix Still Doesn't Work**

### Check backend logs:

```bash
docker compose logs backend | grep -i "login\|401\|error" | tail -30
```

### Check if backend is running:

```bash
docker compose ps
curl http://localhost:8000/health
```

### Check database connection:

```bash
docker compose exec postgres pg_isready
```

### Nuclear option (last resort):

```bash
# Stop everything
docker compose down -v

# Clean Docker completely
docker system prune -a --volumes -f

# Rebuild from scratch
docker compose up --build -d

# Wait longer
sleep 90

# Test
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 📞 **Still Having Issues?**

Provide:
1. Output of `docker compose logs backend | tail -50`
2. Output of `docker compose exec postgres psql -U admin -d energy_defense -c "SELECT * FROM users;"`
3. Output of the curl test command
4. Browser console errors (if any)

---

## 🎉 **Success Looks Like This**

**Terminal:**
```bash
$ curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
  
{"access_token":"eyJhbG...","refresh_token":"eyJhbG...","token_type":"bearer"}
```

**Browser:**
- Login page → Enter credentials → Redirects to dashboard ✅
- No 401 errors ✅
- Console shows success messages ✅

---

**Run the fastest fix now and you'll be logged in within 2 minutes!** 🚀
