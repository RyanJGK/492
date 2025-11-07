# 🔍 Login Issue Diagnosis Guide

**Problem:** Login page refreshes but doesn't navigate to dashboard

---

## 🎯 Step-by-Step Diagnosis

### Step 1: Open Browser DevTools

1. Open http://localhost:3000
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Clear console (trash icon)
5. Try to login with `admin` / `admin123`
6. Watch console output

### Step 2: Check Console Logs

**Look for these messages in order:**

```
✅ Expected Flow:
[Login attempt started: {username: "admin", passwordLength: 8}]
[AuthContext] Login attempt: admin
[AuthContext] Calling apiClient.login...
[API] POST /api/v1/auth/login {username: "admin"}
[API] Login response received: {hasAccessToken: true, ...}
[API] Tokens stored in localStorage
[AuthContext] Login API successful, tokens received
[AuthContext] Fetching current user...
[API] GET /api/v1/auth/me
[API] User data received: {id: 1, username: "admin", role: "admin"}
[AuthContext] Current user fetched: {username: "admin", ...}
[AuthContext] ✅ Login complete! User: admin Role: admin
Login successful, navigating to dashboard...
Navigation to dashboard triggered
```

**If you see this, login is working and should navigate!**

---

### Step 3: Check Network Tab

1. Go to **Network** tab in DevTools
2. Clear network log
3. Try login again
4. Look for these requests:

#### Request 1: Login

```
POST http://localhost:8000/api/v1/auth/login
Status: 200 OK
Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Request 2: Get User

```
GET http://localhost:8000/api/v1/auth/me
Status: 200 OK
Response: {
  "id": 1,
  "username": "admin",
  "email": "admin@...",
  "role": "admin",
  ...
}
```

---

## 🚨 Common Issues & Solutions

### Issue 1: No Console Logs Appear

**Symptom:** Console is blank after clicking login

**Cause:** JavaScript not loading or frontend not built

**Solution:**
```bash
cd /workspace/492-energy-defense
docker compose restart frontend
sleep 10
# Try again
```

---

### Issue 2: API Request Fails (Network Error)

**Symptom:** Console shows:
```
[API] Login request failed: Error: Network Error
```

**Cause:** Backend not running or wrong URL

**Check:**
```bash
# Is backend running?
docker compose ps

# Can you reach it?
curl http://localhost:8000/health
```

**Solution:**
```bash
docker compose restart backend
sleep 10
```

---

### Issue 3: 401 Unauthorized

**Symptom:** Console shows:
```
[API] Login request failed
[API] Error response: {detail: "Incorrect username or password"}
```

**Cause:** Wrong credentials or database issue

**Check database:**
```bash
docker compose exec postgres psql -U admin -d energy_defense -c "SELECT username, role FROM users;"
```

**Should see:**
```
 username | role
----------+----------
 admin    | admin
 analyst  | analyst
 observer | observer
```

**If empty, reset database:**
```bash
docker compose down -v
docker compose up --build -d
sleep 60
```

---

### Issue 4: Login Succeeds But No Navigation

**Symptom:** Console shows:
```
[AuthContext] ✅ Login complete!
Login successful, navigating to dashboard...
Navigation to dashboard triggered
```

**But page doesn't change**

**Cause:** React Router issue

**Check:**
1. Look for errors after "Navigation to dashboard triggered"
2. Check if URL changed in browser (should be http://localhost:3000/dashboard)
3. Check browser console for React Router errors

**Solution:**
```bash
# Rebuild frontend
cd /workspace/492-energy-defense
docker compose down frontend
docker compose up --build frontend -d
```

---

### Issue 5: Page Just Refreshes

**Symptom:** No console logs, page refreshes, back to login

**Cause:** Form submission not prevented

**This should be fixed in the code, but verify:**
1. Check if you see `[Login attempt started: ...]` in console
2. If not, form is submitting instead of using JavaScript

---

### Issue 6: CORS Error

**Symptom:** Console shows:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/auth/login' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Cause:** Backend CORS not configured for frontend

**Check backend logs:**
```bash
docker compose logs backend | grep -i cors
```

**Solution:**
Check `backend/api/main.py` has CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Manual API Test

Test backend directly:

```bash
# Test login API
curl -v -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Should return:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer"
# }

# Save token
TOKEN="<paste access_token here>"

# Test get user
curl -v http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Should return user data
```

If this works, backend is fine and issue is in frontend.

---

## 🔧 Quick Fixes

### Fix 1: Restart Everything

```bash
cd /workspace/492-energy-defense
docker compose restart
sleep 30
```

### Fix 2: Rebuild Frontend

```bash
docker compose down frontend
docker compose up --build frontend -d
sleep 20
```

### Fix 3: Complete Reset

```bash
docker compose down -v
docker compose up --build -d
sleep 60
```

### Fix 4: Check Frontend Logs

```bash
docker compose logs frontend | tail -50
```

Look for build errors or warnings.

---

## 📋 Checklist

After trying login, verify:

- [ ] Console shows login attempt started
- [ ] Console shows API call being made
- [ ] Network tab shows POST to /api/v1/auth/login
- [ ] POST returns 200 with access_token
- [ ] Console shows tokens stored
- [ ] Network tab shows GET to /api/v1/auth/me
- [ ] GET returns 200 with user data
- [ ] Console shows "Login complete!"
- [ ] Console shows "Navigation to dashboard triggered"
- [ ] URL changes to /dashboard
- [ ] Dashboard page loads

**If all checkboxes pass but still on login page:**
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Try different browser
- Check for React errors in console

---

## 🆘 Still Not Working?

**Provide these details:**

1. **Console output** (copy all logs from console)
2. **Network tab** (screenshot of login POST request and response)
3. **Backend logs:**
   ```bash
   docker compose logs backend | tail -100
   ```
4. **Frontend logs:**
   ```bash
   docker compose logs frontend | tail -100
   ```
5. **Service status:**
   ```bash
   docker compose ps
   ```

---

## 🎯 Expected Behavior

**When working correctly:**

1. Enter credentials
2. Click "Sign In"
3. See loading spinner briefly
4. URL changes to /dashboard
5. Dashboard loads with data
6. Console shows success messages
7. No errors anywhere

**That's it!** If you see anything different, consult the issue above that matches your symptom.
