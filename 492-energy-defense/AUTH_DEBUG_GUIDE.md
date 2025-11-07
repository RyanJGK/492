# 🔍 Authentication Debug Guide - Complete Checklist

**Use this guide to systematically debug login issues**

---

## 🎯 Quick Diagnosis

### Test 1: Is the backend running?
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy",...}`  
**If fails:** Backend isn't running or port is wrong

### Test 2: Can you reach the database?
```bash
docker compose exec postgres pg_isready
```
**Expected:** `accepting connections`  
**If fails:** Database isn't running

### Test 3: Do users exist?
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
**If fails:** Database wasn't initialized

### Test 4: Are enum values correct?
```bash
docker compose exec postgres psql -U admin -d energy_defense -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'userrole'::regtype;"
```
**Expected:**
```
 enumlabel
-----------
 admin
 analyst
 observer
```
**If shows ADMIN/ANALYST/OBSERVER:** Database enum mismatch!

### Test 5: Test login API directly
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```
**Expected:** JSON with `access_token` field  
**If fails:** See error message for details

---

## 🔧 Common Issues & Fixes

### Issue 1: "Incorrect username or password"

**Possible Causes:**
1. Password hash mismatch
2. Username case sensitivity
3. User doesn't exist

**Debug:**
```bash
# Check if user exists
docker compose exec postgres psql -U admin -d energy_defense -c \
  "SELECT username, role FROM users WHERE username = 'admin';"

# If empty, database wasn't initialized
# Solution: docker compose down -v && docker compose up --build
```

**Verify password hash:**
```bash
docker compose exec postgres psql -U admin -d energy_defense -c \
  "SELECT username, substring(hashed_password, 1, 20) || '...' as hash_preview FROM users;"
```
**Expected:** Should start with `$2b$12$` (bcrypt format)

---

### Issue 2: "LookupError: enum values"

**Error:**
```
'admin' is not among the defined enum values
Possible values: ADMIN, ANALYST, OBSERVER
```

**Cause:** SQLAlchemy using enum NAMES instead of VALUES

**Fix:** Check `backend/api/models.py` line 48:
```python
# Should have values_callable:
role = Column(
    SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
    nullable=False,
    default=UserRole.OBSERVER
)
```

**Verify fix is applied:**
```bash
grep "values_callable" backend/api/models.py | wc -l
```
**Expected:** Should show 6 (one for each enum column)

---

### Issue 3: Frontend can't connect to backend

**Symptoms:**
- Login button doesn't respond
- Network errors in browser console
- CORS errors

**Debug:**
```bash
# Check if backend is accessible from host
curl http://localhost:8000/health

# Check frontend environment
docker compose exec frontend env | grep VITE_API_URL
```

**Expected:**
- Backend: `{"status":"healthy"}`
- Frontend: `VITE_API_URL=http://localhost:8000`

**Check browser console:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try logging in
4. Look for errors

**Common frontend errors:**
- `CORS`: Backend CORS not configured
- `Network Error`: Backend not running
- `401`: Authentication failed
- `500`: Backend error

---

### Issue 4: Services won't start

**Check logs:**
```bash
docker compose logs backend | tail -50
docker compose logs postgres | tail -50
docker compose logs frontend | tail -50
```

**Common errors:**
- `port already in use`: Stop conflicting service
- `connection refused`: Database not ready
- `module not found`: Missing dependencies

---

## 📋 Complete Restart Checklist

Use this when making major changes:

```bash
# 1. Stop everything
docker compose down -v

# 2. Clean Docker cache (optional, for major issues)
docker system prune -a --volumes

# 3. Rebuild
docker compose up --build

# 4. Wait 60 seconds
sleep 60

# 5. Check status
docker compose ps

# 6. Test backend
curl http://localhost:8000/health

# 7. Test database
docker compose exec postgres psql -U admin -d energy_defense -c "\dt"

# 8. Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 9. Open frontend
open http://localhost:3000
```

---

## 🎓 Understanding the Auth Flow

### Step-by-Step Login Process:

1. **User enters credentials in frontend**
   - Frontend: `LoginPage.tsx` line 24
   - Calls: `login({ username, password })`

2. **Frontend AuthContext handles login**
   - Frontend: `AuthContext.tsx` line 46-64
   - Makes POST to `/api/v1/auth/login`

3. **API client sends request**
   - Frontend: `api.ts` line 58-66
   - Headers: `Content-Type: application/json`
   - Body: `{"username": "...", "password": "..."}`

4. **Backend receives request**
   - Backend: `routes/auth.py` line 23-77
   - Validates schema with Pydantic
   - Calls `authenticate_user()`

5. **Backend authenticates**
   - Backend: `middleware/auth.py` line 150-167
   - Normalizes username to lowercase
   - Looks up user in database
   - Verifies password with bcrypt

6. **Backend creates tokens**
   - Backend: `middleware/auth.py` line 36-55
   - Generates JWT access token (30 min)
   - Generates JWT refresh token (7 days)
   - Returns `Token` schema

7. **Frontend stores tokens**
   - Frontend: `api.ts` line 63-64
   - Stores in localStorage
   - Sets Authorization header

8. **Frontend fetches user data**
   - Frontend: `AuthContext.tsx` line 52
   - Calls `/api/v1/auth/me`
   - Updates user state

9. **Frontend navigates to dashboard**
   - Frontend: `LoginPage.tsx` line 27
   - Uses `navigate('/dashboard', { replace: true })`

---

## 🔍 Debug Each Step

### Debug Step 1-3 (Frontend → API):

**Open browser console (F12), Network tab:**
- Look for POST request to `/api/v1/auth/login`
- Check request payload
- Check response status

**If request doesn't appear:**
- Frontend not sending request
- Check `LoginPage.tsx` submit handler
- Check for JavaScript errors in console

**If request fails (CORS error):**
- Backend CORS not configured
- Check `backend/api/main.py` CORS settings

### Debug Step 4-6 (Backend Auth):

**Check backend logs:**
```bash
docker compose logs backend | grep -A5 -B5 "login"
```

**Common backend errors:**
- `Incorrect username or password`: Auth failed
- `LookupError`: Enum mismatch
- `KeyError`: Missing field in request
- `ValidationError`: Pydantic schema mismatch

### Debug Step 7-8 (Token Creation):

**Check if tokens are created:**
```bash
docker compose logs backend | grep "token\|Token"
```

**Verify token structure:**
```bash
# Login and capture response
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

# Decode token (first part)
echo "$TOKEN" | cut -d. -f1 | base64 -d 2>/dev/null
echo "$TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null
```

### Debug Step 9 (Navigation):

**Check browser console for:**
- `Login successful, user: admin, role: admin`
- `User authenticated: admin, navigating to protected route`

**If navigation doesn't happen:**
- React Router issue
- Check `App.tsx` routes
- Check `ProtectedRoute` logic

---

## 🚨 Emergency Fixes

### Nuclear Option: Complete Reset
```bash
cd /workspace/492-energy-defense

# Stop and remove everything
docker compose down -v
docker system prune -a --volumes -f

# Remove node_modules and Python cache
rm -rf frontend/node_modules
find backend -type d -name "__pycache__" -exec rm -rf {} +

# Rebuild from scratch
docker compose up --build

# Wait and test
sleep 90
curl http://localhost:8000/health
open http://localhost:3000
```

### Quick Backend Fix
```bash
# Just restart backend (preserves database)
docker compose restart backend
sleep 10
curl http://localhost:8000/health
```

### Database Only Reset
```bash
# Reset database only (preserves code)
docker compose stop postgres
docker compose rm -f postgres
docker volume rm 492-energy-defense_postgres_data
docker compose up -d postgres
sleep 15
docker compose restart backend
```

---

## ✅ Success Checklist

After fixes, all these should work:

- [ ] `docker compose ps` shows all services "Up"
- [ ] `curl http://localhost:8000/health` returns healthy
- [ ] `curl http://localhost:3000` returns HTML
- [ ] Login with `admin`/`admin123` works
- [ ] Redirects to dashboard after login
- [ ] Dashboard shows data
- [ ] No console errors in browser
- [ ] Backend logs show no errors
- [ ] Can logout and login again

---

## 📞 Still Having Issues?

If you've gone through all the above and still have problems:

1. **Capture complete logs:**
   ```bash
   docker compose logs > all_logs.txt
   ```

2. **Check specific service:**
   ```bash
   docker compose logs backend > backend_logs.txt
   docker compose logs postgres > db_logs.txt
   docker compose logs frontend > frontend_logs.txt
   ```

3. **Test each component individually:**
   ```bash
   # Database
   docker compose exec postgres psql -U admin -d energy_defense -c "SELECT 1;"
   
   # Backend health
   curl -v http://localhost:8000/health
   
   # Backend login
   curl -v -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   
   # Frontend
   curl -v http://localhost:3000
   ```

4. **Check environment variables:**
   ```bash
   cat .env
   docker compose config
   ```

---

**Most Common Issue:** Enum values mismatch (fixed in issue #12)  
**Second Most Common:** Database not initialized (run `docker compose down -v && docker compose up --build`)  
**Third Most Common:** Backend not running (check `docker compose ps`)

**Good luck!** 🍀
