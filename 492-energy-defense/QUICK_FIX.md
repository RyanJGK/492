# ⚡ Quick Fix - Login Issues

**Having login problems? Follow these steps:**

---

## 🚀 Fast Track (3 minutes)

```bash
cd /workspace/492-energy-defense

# 1. Clean restart
docker compose down -v
docker compose up --build -d

# 2. Wait 60 seconds
sleep 60

# 3. Test login
./TEST_LOGIN_COMPLETE.sh

# 4. Open browser
open http://localhost:3000
```

**Login with:**
- Username: `admin` (case-insensitive)
- Password: `admin123`

---

## 🔧 If That Didn't Work

### Run Automated Debug

```bash
./DEBUG_AND_CLEANUP.sh
```

This will:
- Clean up files
- Rebuild containers
- Test all services
- Give you a report

---

## 📖 Detailed Guides

If you need more help:

1. **`AUTH_DEBUG_GUIDE.md`** - Comprehensive troubleshooting
2. **`COMPLETE_FIX_SUMMARY.md`** - Everything we fixed
3. **`AUTHENTICATION_VERIFIED.md`** - Code verification

---

## 🎯 Common Issues

### Issue 1: Services not running

```bash
docker compose ps
# Should show all "Up"
```

**Fix:**
```bash
docker compose up -d
```

### Issue 2: Database not initialized

```bash
docker compose exec postgres psql -U admin -d energy_defense -c "SELECT COUNT(*) FROM users;"
# Should return 3
```

**Fix:**
```bash
docker compose down -v
docker compose up --build
```

### Issue 3: Backend not responding

```bash
curl http://localhost:8000/health
# Should return {"status":"healthy"}
```

**Fix:**
```bash
docker compose restart backend
```

---

## ✅ Success = All These Work

- [ ] `docker compose ps` - all services "Up"
- [ ] `curl http://localhost:8000/health` - returns healthy
- [ ] `curl http://localhost:3000` - returns HTML
- [ ] Login page loads
- [ ] Login with admin/admin123 works
- [ ] Redirects to dashboard
- [ ] Dashboard shows data

---

## 🆘 Still Stuck?

```bash
# Check logs
docker compose logs backend | tail -50

# See what's failing
./TEST_LOGIN_COMPLETE.sh

# Read full debug guide
cat AUTH_DEBUG_GUIDE.md
```

---

**The code is correct. If login fails, it's a service/environment issue.**

Use the tools we created to diagnose! 🚀
