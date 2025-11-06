# 🚀 Energy Defense - Component Quick Reference

**Fast lookup guide for all system components**

---

## 📦 Component Overview

| Component | Port | Technology | Purpose | Container Name |
|-----------|------|------------|---------|----------------|
| PostgreSQL | 5432 | PostgreSQL 15 | Data persistence | energy-defense-db |
| Backend API | 8000 | FastAPI + Python | REST API & business logic | energy-defense-api |
| AI Agent | 8001 | Python + OpenRouter | Threat analysis | energy-defense-ai-agent |
| Redis | 6379 | Redis 7 | Caching | energy-defense-redis |
| Data Simulator | - | Python | Generate test data | energy-defense-simulator |
| Frontend | 3000 | React + Vite | Web dashboard | energy-defense-frontend |

---

## 🗄️ Database Tables (8 Total)

| Table | Rows (typical) | Primary Use | Key Relationships |
|-------|----------------|-------------|-------------------|
| users | ~10 | Authentication & RBAC | → auth_events, ai_analysis |
| auth_events | 1000s | Audit trail | users ← |
| patch_levels | 100s | System patch status | users (assigned_to) |
| vulnerability_scans | 1000s | Vuln findings | users (assigned_to) |
| firewall_logs | 10,000s+ | Network events | None (high volume) |
| ai_analysis | 100s | AI threat reports | users, ai_feedback |
| ai_weight_config | ~5 | AI tuning | users (created_by) |
| ai_feedback | 100s | Analyst feedback | ai_analysis, users |

---

## 🔐 User Roles & Permissions

| Role | Login | View Data | Modify Data | AI Config | Assign Tasks |
|------|-------|-----------|-------------|-----------|--------------|
| **Admin** | ✅ | ✅ All | ✅ All | ✅ Yes | ✅ Yes |
| **Analyst** | ✅ | ✅ All | ✅ Limited | ❌ No | ❌ No |
| **Observer** | ✅ | ✅ All | ❌ No | ❌ No | ❌ No |

**Test Credentials:**
- Admin: `admin` / `admin123`
- Analyst: `analyst` / `analyst123`
- Observer: `observer` / `observer123`

---

## 🌐 API Endpoints

### Authentication
```
POST   /api/v1/auth/login          Login & get JWT token
POST   /api/v1/auth/logout         Logout
POST   /api/v1/auth/refresh        Refresh JWT token
```

### Dashboard
```
GET    /api/v1/dashboard/stats              Aggregated statistics
GET    /api/v1/dashboard/trends/threats     Threat trends (7 days)
```

### Vulnerabilities
```
GET    /api/v1/vulnerabilities              List all vulnerabilities
GET    /api/v1/vulnerabilities/{id}         Get specific vulnerability
PATCH  /api/v1/vulnerabilities/{id}         Update vulnerability
POST   /api/v1/vulnerabilities              Create vulnerability
```

### AI Configuration (Admin Only)
```
GET    /api/v1/ai-config/weights            Get active weight config
POST   /api/v1/ai-config/weights            Update weight config
GET    /api/v1/ai-config/weights/history    Get config history
```

### AI Feedback (Analyst+)
```
POST   /api/v1/ai-feedback                  Submit feedback
GET    /api/v1/ai-feedback/{analysis_id}    Get feedback
```

### Health
```
GET    /health                              Health check
GET    /                                    API info
GET    /api/docs                            Swagger UI (dev only)
```

---

## 🤖 AI Agent

### Model Information
- **Provider:** OpenRouter
- **Model:** Nous: Hermes 3 405B Instruct
- **Context Window:** 200k tokens
- **API Endpoint:** `https://openrouter.ai/api/v1/chat/completions`

### Default Weights
```json
{
  "firewall_threat_weight": 0.35,          // 35% - Network threats
  "vulnerability_severity_weight": 0.30,   // 30% - Vulnerabilities
  "patch_criticality_weight": 0.20,        // 20% - Patch status
  "auth_anomaly_weight": 0.15,             // 15% - Auth issues
  "confidence_threshold": 0.70,            // 70% - Min confidence
  "severity_multipliers": {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
    "info": 0.10
  }
}
```

### Cache Strategy
- **Storage:** Redis
- **TTL:** 1 hour (3600 seconds)
- **Key Format:** `ai_query:{hash_of_prompt}`
- **Hit Rate:** ~70% after warm-up

---

## 📊 Data Simulator

### Generation Schedule
**Every 5 minutes, generates:**
- 10 firewall logs
- 5 vulnerability scans
- 8 patch level records

### Realistic Data Features
- **IPs:** Mix of internal (10.0.x.x) and threat IPs
- **Threats:** 15% of firewall logs marked as threats
- **Systems:** SCADA, HMI, PLC (energy sector specific)
- **CVEs:** Realistic CVE identifiers
- **Severity:** Weighted distribution (more low/medium than critical)

---

## 🎨 Frontend Pages

| Route | Component | Access | Purpose |
|-------|-----------|--------|---------|
| `/login` | LoginPage | Public | User authentication |
| `/dashboard` | Dashboard | All authenticated | Main overview |
| `/vulnerabilities` | VulnerabilitiesPage | All authenticated | Vuln management |
| `/ai-config` | AIConfigPage | Admin only | AI weight tuning |
| `/ai-feedback` | FeedbackPage | Analyst+ | Submit feedback |
| `/reports` | ReportsPage | All authenticated | Generate reports |
| `/users` | UsersPage | Admin only | User management |

---

## 🔧 Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment variables | `/workspace/492-energy-defense/` |
| `docker-compose.yml` | Service orchestration | `/workspace/492-energy-defense/` |
| `init.sql` | Database schema | `/workspace/492-energy-defense/backend/database/` |
| `requirements.txt` | Python dependencies | `/workspace/492-energy-defense/backend/` |
| `package.json` | Node dependencies | `/workspace/492-energy-defense/frontend/` |

---

## 🔍 Common Operations

### Start System
```bash
docker-compose up --build
```

### Stop System
```bash
docker-compose down
```

### Reset Database (DELETES DATA)
```bash
docker-compose down -v
docker-compose up --build
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai-agent
docker-compose logs -f data-simulator
```

### Database Access
```bash
docker-compose exec postgres psql -U admin -d energy_defense
```

### Backend Shell
```bash
docker-compose exec backend bash
```

### Redis CLI
```bash
docker-compose exec redis redis-cli
```

---

## 🐛 Debugging

### Check Service Health
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

### Common Issues

**Issue:** Can't log in  
**Fix:** Check backend logs for authentication errors
```bash
docker-compose logs backend | grep -i auth
```

**Issue:** No data in dashboard  
**Fix:** Check if data simulator is running
```bash
docker-compose logs data-simulator
```

**Issue:** AI analysis not working  
**Fix:** Verify OpenRouter API key in `.env`
```bash
grep OPENROUTER_API_KEY .env
```

**Issue:** Database connection errors  
**Fix:** Recreate database volume
```bash
docker-compose down -v
docker-compose up --build
```

---

## 📈 Performance Metrics

### Expected Response Times
| Operation | Time | Notes |
|-----------|------|-------|
| API Health Check | <10ms | In-memory |
| Login | 200-500ms | Bcrypt hashing |
| Dashboard Stats | 50-200ms | 5 DB queries |
| AI Analysis (cached) | <50ms | Redis cache hit |
| AI Analysis (uncached) | 2-5s | OpenRouter API call |
| Vulnerability List | 100-300ms | Depends on volume |

### Resource Usage (Typical)
| Service | CPU | Memory | Disk |
|---------|-----|--------|------|
| PostgreSQL | 5-15% | 100-500MB | 500MB-2GB |
| Backend | 2-10% | 50-200MB | Minimal |
| AI Agent | 1-5% | 50-150MB | Minimal |
| Redis | 1-3% | 10-50MB | 10-100MB |
| Frontend | 1-5% | 50-150MB | Minimal |
| Simulator | 1-2% | 50-100MB | Minimal |

---

## 🔒 Security Checklist

### Production Deployment
- [ ] Change all default passwords
- [ ] Generate new `SECRET_KEY`
- [ ] Set `ENVIRONMENT=production`
- [ ] Disable API docs (`/api/docs`)
- [ ] Configure HTTPS/TLS
- [ ] Restrict CORS origins
- [ ] Enable rate limiting
- [ ] Configure database backups
- [ ] Set up monitoring alerts
- [ ] Review firewall rules
- [ ] Audit user access
- [ ] Rotate JWT secrets regularly

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| [README.md](./README.md) | Project overview |
| [SYSTEM_COMPONENTS_DETAILED.md](./SYSTEM_COMPONENTS_DETAILED.md) | Deep dive (600+ lines) |
| [QUICKSTART.md](./QUICKSTART.md) | 5-minute setup |
| [START_HERE.md](./START_HERE.md) | Entry point |
| [MODEL_INFO.md](./MODEL_INFO.md) | AI model details |
| [ALL_10_FIXES_COMPLETE.md](./ALL_10_FIXES_COMPLETE.md) | Bug fix history |
| [DEPLOY_NOW.md](./DEPLOY_NOW.md) | Deployment guide |

---

## 🎯 Quick Access URLs

**After deployment, access:**

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/api/docs |
| Database | localhost:5432 |
| Redis | localhost:6379 |

---

## 💡 Pro Tips

1. **Use Redis CLI to check cache:**
   ```bash
   docker-compose exec redis redis-cli
   > KEYS ai_query:*
   ```

2. **Monitor database size:**
   ```bash
   docker-compose exec postgres psql -U admin -d energy_defense -c \
     "SELECT pg_size_pretty(pg_database_size('energy_defense'));"
   ```

3. **Clear old firewall logs:**
   ```sql
   DELETE FROM firewall_logs WHERE log_timestamp < NOW() - INTERVAL '30 days';
   ```

4. **Export AI analysis results:**
   ```bash
   docker-compose exec postgres psql -U admin -d energy_defense -c \
     "COPY ai_analysis TO '/tmp/analysis.csv' CSV HEADER;"
   ```

5. **Benchmark API performance:**
   ```bash
   ab -n 1000 -c 10 http://localhost:8000/health
   ```

---

**For detailed technical information, see [SYSTEM_COMPONENTS_DETAILED.md](./SYSTEM_COMPONENTS_DETAILED.md)**
