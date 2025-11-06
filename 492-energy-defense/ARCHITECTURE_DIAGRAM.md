# 🏛️ Energy Defense System - Architecture Diagrams

**Visual representation of system architecture and data flows**

---

## 📐 High-Level Architecture

```
                             ┌─────────────────────────────────┐
                             │        END USERS                │
                             │  (Admins, Analysts, Observers)  │
                             └────────────┬────────────────────┘
                                          │
                                    HTTPS │ Browser
                                          ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                            │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              React Frontend (Port 3000)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │   │
│  │  │  Login Page  │  │  Dashboard   │  │  Admin Config    │   │   │
│  │  │  (Public)    │  │  (Auth Req)  │  │  (Admin Only)    │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │   │
│  │  │ Vulnerabil.  │  │  AI Feedback │  │  Reports         │   │   │
│  │  │ (Auth Req)   │  │ (Analyst+)   │  │  (Auth Req)      │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │   │
│  └───────────────────────┬──────────────────────────────────────┘   │
│                          │ Axios HTTP Client                        │
│                          │ JWT Token in Headers                     │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
                    REST API│ JSON
                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                               │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Port 8000)                      │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │              Middleware Stack                           │  │   │
│  │  │  • CORS     • GZip    • Auth    • Logging              │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │                 Route Handlers                         │  │   │
│  │  │  /auth  /dashboard  /vulns  /ai-config  /feedback     │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │              Business Logic Layer                      │  │   │
│  │  │  • Authentication  • Authorization  • Validation       │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └───────────────────┬───────────────────┬──────────────────────┘   │
│                      │                   │                          │
│                      ▼                   ▼                          │
│         ┌────────────────────┐  ┌────────────────────┐             │
│         │   AI Agent Service │  │  Data Simulator    │             │
│         │    (Port 8001)     │  │   (Background)     │             │
│         │                    │  │                    │             │
│         │ • OpenRouter API   │  │ • Generate Data    │             │
│         │ • Threat Analysis  │  │ • Every 5 min      │             │
│         │ • Weight Config    │  │ • Firewall Logs    │             │
│         │ • Confidence Score │  │ • Vulnerabilities  │             │
│         └──────┬─────────────┘  └─────────┬──────────┘             │
│                │                           │                        │
└────────────────┼───────────────────────────┼────────────────────────┘
                 │                           │
          Cache  │                           │ Database Write
          Access │                           │
                 ▼                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                  │
│                                                                        │
│  ┌──────────────────────┐              ┌───────────────────────────┐ │
│  │  Redis Cache         │              │  PostgreSQL Database      │ │
│  │  (Port 6379)         │              │  (Port 5432)              │ │
│  │                      │              │                           │ │
│  │ ┌──────────────────┐ │              │ ┌───────────────────────┐ │ │
│  │ │ AI Query Cache   │ │              │ │ users                 │ │ │
│  │ │ TTL: 1 hour      │ │              │ │ auth_events           │ │ │
│  │ └──────────────────┘ │              │ │ patch_levels          │ │ │
│  │ ┌──────────────────┐ │              │ │ vulnerability_scans   │ │ │
│  │ │ Session Store    │ │              │ │ firewall_logs         │ │ │
│  │ │ (Future)         │ │              │ │ ai_analysis           │ │ │
│  │ └──────────────────┘ │              │ │ ai_weight_config      │ │ │
│  │ ┌──────────────────┐ │              │ │ ai_feedback           │ │ │
│  │ │ Rate Limiting    │ │              │ └───────────────────────┘ │ │
│  │ │ (Future)         │ │              │                           │ │
│  │ └──────────────────┘ │              │ Volume: postgres_data     │ │
│  │                      │              │ Backup: Recommended       │ │
│  │ Volume: redis_data   │              └───────────────────────────┘ │
│  └──────────────────────┘                                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

                                    ▲
                                    │
                            External│API Call
                                    │
                        ┌───────────┴────────────┐
                        │   OpenRouter API       │
                        │   (External Service)   │
                        │                        │
                        │ Model: Hermes 3 405B   │
                        │ Provider: OpenRouter   │
                        └────────────────────────┘
```

---

## 🔄 Authentication Flow

```
┌─────────┐                                                      ┌──────────┐
│ Browser │                                                      │ Backend  │
└────┬────┘                                                      └────┬─────┘
     │                                                                │
     │ 1. POST /api/v1/auth/login                                    │
     │    { username: "admin", password: "admin123" }                │
     ├──────────────────────────────────────────────────────────────>│
     │                                                                │
     │                                2. Verify credentials           │
     │                                   (bcrypt compare)             │
     │                                   ┌──────────────────┐         │
     │                                   │   PostgreSQL     │         │
     │                                   │   users table    │         │
     │                                   └────────┬─────────┘         │
     │                                            │                   │
     │                                3. Load user record             │
     │<───────────────────────────────────────────┘                   │
     │                                                                │
     │                                4. Generate JWT token           │
     │                                   (include username, role)     │
     │                                                                │
     │                                5. Log auth event               │
     │                                   ┌──────────────────┐         │
     │                                   │   PostgreSQL     │         │
     │                                   │ auth_events      │         │
     │                                   └──────────────────┘         │
     │                                                                │
     │ 6. Response:                                                   │
     │    {                                                           │
     │      "access_token": "eyJhbGc...",                             │
     │      "token_type": "bearer",                                   │
     │      "user": { "id": 1, "username": "admin", "role": "admin" } │
     │    }                                                           │
     │<──────────────────────────────────────────────────────────────┤
     │                                                                │
     │ 7. Store token in localStorage                                │
     │    Set Authorization header for future requests               │
     │                                                                │
     │ 8. GET /api/v1/dashboard/stats                                │
     │    Headers: { Authorization: "Bearer eyJhbGc..." }            │
     ├──────────────────────────────────────────────────────────────>│
     │                                                                │
     │                                9. Verify JWT token             │
     │                                   Decode & validate            │
     │                                                                │
     │                               10. Load user from DB            │
     │                                   Check is_active              │
     │                                                                │
     │                               11. Execute request              │
     │                                   Apply RBAC                   │
     │                                                                │
     │ 12. Response: { stats data }                                  │
     │<──────────────────────────────────────────────────────────────┤
     │                                                                │
```

---

## 🤖 AI Analysis Flow

```
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌────────────┐
│   Backend   │    │   AI     │    │  Redis   │    │ OpenRouter│    │ PostgreSQL │
│   API       │    │  Agent   │    │  Cache   │    │    API    │    │  Database  │
└──────┬──────┘    └────┬─────┘    └────┬─────┘    └─────┬─────┘    └──────┬─────┘
       │                │               │                │                   │
       │                │                                                    │
       │ 1. Trigger AI analysis                                             │
       │    (manual or automatic)                                           │
       ├───────────────>│                                                    │
       │                │                                                    │
       │                │ 2. Fetch active weight configuration               │
       │                ├───────────────────────────────────────────────────>│
       │                │                                                    │
       │                │<───────────────────────────────────────────────────┤
       │                │ 3. Weights: { firewall: 0.35, vuln: 0.30, ... }   │
       │                │                                                    │
       │                │ 4. Gather recent security data                     │
       │                ├───────────────────────────────────────────────────>│
       │                │    (firewall_logs, vulnerability_scans, etc.)      │
       │                │<───────────────────────────────────────────────────┤
       │                │ 5. Data: { firewall: [...], vulns: [...] }        │
       │                │                                                    │
       │                │ 6. Build analysis prompt                           │
       │                │    with weights & data                             │
       │                │                                                    │
       │                │ 7. Check cache for this prompt                     │
       │                ├──────────────>│                                    │
       │                │                │                                    │
       │                │<───────────────┤                                    │
       │                │ 8. Cache MISS                                      │
       │                │                                                    │
       │                │ 9. POST /chat/completions                          │
       │                │    Model: hermes-3-405b                            │
       │                │    Prompt: "Analyze threats..."                    │
       │                ├────────────────────────────────>│                  │
       │                │                                 │                  │
       │                │                                 │ 10. LLM inference│
       │                │                                 │     (2-5 seconds)│
       │                │                                 │                  │
       │                │<────────────────────────────────┤                  │
       │                │ 11. AI Response:                                   │
       │                │     "Critical threat detected..."                  │
       │                │                                                    │
       │                │ 12. Store in cache (TTL: 1 hour)                  │
       │                ├──────────────>│                                    │
       │                │                │                                    │
       │                │ 13. Calculate confidence score                     │
       │                │     Based on data completeness                     │
       │                │                                                    │
       │                │ 14. Determine threat level                         │
       │                │     Apply severity multipliers                     │
       │                │                                                    │
       │                │ 15. Store analysis result                          │
       │                ├───────────────────────────────────────────────────>│
       │                │    INSERT INTO ai_analysis (...)                   │
       │                │                                                    │
       │<───────────────┤                                                    │
       │ 16. Return analysis to API                                         │
       │     {                                                              │
       │       "analysis_id": "uuid...",                                    │
       │       "threat_level": "critical",                                  │
       │       "confidence_score": 0.85,                                    │
       │       "ai_response": "...",                                        │
       │       "model_version": "hermes-3-405b"                             │
       │     }                                                              │
       │                                                                    │
```

**Next Request with Same Prompt:**
```
       │ 7. Check cache                                                     │
       │    ├──────────────>│                                               │
       │    │<───────────────┤                                               │
       │    │ 8. Cache HIT (instant response, skip steps 9-11)              │
```

---

## 📊 Data Simulation Flow

```
┌──────────────────┐                              ┌────────────────┐
│  Data Simulator  │                              │   PostgreSQL   │
│   (Background)   │                              │    Database    │
└────────┬─────────┘                              └────────┬───────┘
         │                                                 │
         │ Every 5 minutes:                               │
         │                                                 │
         │ 1. Generate 10 firewall logs                   │
         │    - Random IPs (internal + threat IPs)        │
         │    - Random ports (22, 80, 443, 3389)          │
         │    - Random protocols (TCP, UDP)               │
         │    - 15% marked as threats                     │
         │    - Realistic timestamps                      │
         │                                                 │
         │ 2. INSERT INTO firewall_logs                   │
         ├────────────────────────────────────────────────>│
         │                                                 │
         │ 3. Generate 5 vulnerability scans              │
         │    - Target systems: SCADA, HMI, PLC           │
         │    - Random CVE IDs                            │
         │    - CVSS scores (0.0-10.0)                    │
         │    - Status: pending/investigating             │
         │                                                 │
         │ 4. INSERT INTO vulnerability_scans             │
         ├────────────────────────────────────────────────>│
         │                                                 │
         │ 5. Generate 8 patch level records              │
         │    - Energy sector systems                     │
         │    - Version comparisons                       │
         │    - Patch status: up_to_date/outdated         │
         │                                                 │
         │ 6. INSERT INTO patch_levels                    │
         ├────────────────────────────────────────────────>│
         │                                                 │
         │ 7. Log generation stats                        │
         │    "Generated 10 firewall logs, 5 vulns, 8 patches"│
         │                                                 │
         │ 8. Sleep for 5 minutes (300 seconds)          │
         │    ⏰ zzz...                                    │
         │                                                 │
         │ 9. Repeat from step 1                          │
         │                                                 │
```

---

## 🎯 Dashboard Data Aggregation

```
┌──────────┐                              ┌────────────────┐
│ Frontend │                              │   Backend API  │
│Dashboard │                              └────────┬───────┘
└────┬─────┘                                       │
     │                                             │
     │ 1. GET /api/v1/dashboard/stats             │
     ├────────────────────────────────────────────>│
     │                                             │
     │                           2. Execute 5 DB queries in parallel:
     │                                             │
     │                           ┌─────────────────┼──────────────┐
     │                           │                 │              │
     │                           ▼                 ▼              ▼
     │                    Query 1:          Query 2:       Query 3:
     │                    Critical          Pending        Firewall
     │                    Vulns             Patches        Blocks
     │                    ▲                 ▲              ▲
     │                    │                 │              │
     │                    └─────────────────┴──────────────┘
     │                                             │
     │                           Query 4: Total threats
     │                           Query 5: AI avg confidence
     │                                             │
     │ 3. Response:                               │
     │    {                                       │
     │      "total_threats": 142,                 │
     │      "critical_vulnerabilities": 23,       │
     │      "pending_patches": 47,                │
     │      "firewall_blocks_today": 1842,        │
     │      "ai_analyses_count": 89,              │
     │      "average_confidence": 0.78            │
     │    }                                       │
     │<────────────────────────────────────────────┤
     │                                             │
     │ 4. Render dashboard cards                  │
     │    ┌─────────────┬─────────────┐           │
     │    │ 142 Threats │ 23 Critical │           │
     │    ├─────────────┼─────────────┤           │
     │    │ 47 Patches  │ 78% AI Conf │           │
     │    └─────────────┴─────────────┘           │
     │                                             │
```

---

## 🔐 Role-Based Access Control

```
                         ┌─────────────────────────┐
                         │     User Login          │
                         │   (authenticated)       │
                         └────────────┬────────────┘
                                      │
                         Check user.role from JWT token
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   ADMIN ROLE    │    │  ANALYST ROLE   │    │ OBSERVER ROLE   │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
             │                      │                      │
             │ Full Access          │ Limited Access       │ Read-Only
             │                      │                      │
    ┌────────┴────────┐    ┌────────┴────────┐    ┌────────┴────────┐
    │                 │    │                 │    │                 │
    │ ✅ View all     │    │ ✅ View all     │    │ ✅ View all     │
    │ ✅ Create/Edit  │    │ ✅ View details │    │ ✅ View details │
    │ ✅ Delete       │    │ ❌ No delete    │    │ ❌ No edit      │
    │ ✅ AI Config    │    │ ❌ No AI config │    │ ❌ No AI config │
    │ ✅ Users Mgmt   │    │ ❌ No users     │    │ ❌ No users     │
    │ ✅ Feedback     │    │ ✅ Feedback     │    │ ❌ No feedback  │
    │ ✅ Assign       │    │ ❌ No assign    │    │ ❌ No assign    │
    │                 │    │                 │    │                 │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
             │                      │                      │
             │                      │                      │
             ▼                      ▼                      ▼
    ┌─────────────────────────────────────────────────────────────┐
    │               Backend Enforces Permissions                  │
    │                                                             │
    │  @router.post("/ai-config/weights")                         │
    │  async def update_weights(                                  │
    │      admin: User = Depends(require_admin)  # ← Check role  │
    │  ):                                                         │
    │      ...                                                    │
    └─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Network & Port Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                     HOST MACHINE                                │
│                                                                 │
│  localhost:3000  ──────┐                                        │
│  localhost:8000  ──────┼────────┐                               │
│  localhost:5432  ──────┼────────┼────────┐                      │
│  localhost:6379  ──────┼────────┼────────┼────────┐             │
│                        │        │        │        │             │
└────────────────────────┼────────┼────────┼────────┼─────────────┘
                         │        │        │        │
              Docker     │        │        │        │
              Network:   │        │        │        │
         energy-defense- │        │        │        │
              network    │        │        │        │
                         ▼        ▼        ▼        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DOCKER NETWORK                                │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │   Frontend     │  │   Backend      │  │   AI Agent       │ │
│  │   :3000        │  │   :8000        │  │   :8001          │ │
│  │                │  │                │  │                  │ │
│  │  Talks to:     │  │  Talks to:     │  │  Talks to:       │ │
│  │  • backend     │  │  • postgres    │  │  • postgres      │ │
│  │                │  │  • ai-agent    │  │  • redis         │ │
│  │                │  │                │  │  • openrouter    │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │  PostgreSQL    │  │     Redis      │  │  Data Simulator  │ │
│  │   :5432        │  │     :6379      │  │   (no port)      │ │
│  │                │  │                │  │                  │ │
│  │  Accessed by:  │  │  Accessed by:  │  │  Talks to:       │ │
│  │  • backend     │  │  • ai-agent    │  │  • postgres      │ │
│  │  • ai-agent    │  │                │  │                  │ │
│  │  • simulator   │  │                │  │                  │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Service-to-Service Communication:
• frontend → backend:    HTTP (backend:8000)
• backend → postgres:    PostgreSQL protocol (postgres:5432)
• backend → ai-agent:    HTTP (ai-agent:8001)
• ai-agent → redis:      Redis protocol (redis:6379)
• ai-agent → postgres:   PostgreSQL protocol (postgres:5432)
• simulator → postgres:  PostgreSQL protocol (postgres:5432)
```

---

## 📦 Docker Volume Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Volumes                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  postgres_data                                       │  │
│  │  └── /var/lib/postgresql/data                        │  │
│  │      ├── base/             (database files)          │  │
│  │      ├── global/           (cluster-wide data)       │  │
│  │      ├── pg_wal/           (write-ahead log)         │  │
│  │      └── ...                                         │  │
│  │                                                       │  │
│  │  Mounted in: energy-defense-db                       │  │
│  │  Persistence: Data survives container restarts       │  │
│  │  Size: 500MB - 2GB (grows over time)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  redis_data                                          │  │
│  │  └── /data                                           │  │
│  │      └── dump.rdb          (Redis snapshot)          │  │
│  │                                                       │  │
│  │  Mounted in: energy-defense-redis                    │  │
│  │  Persistence: Cache data can be persisted            │  │
│  │  Size: 10-100MB                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  backend_cache                                       │  │
│  │  └── /app/.cache                                     │  │
│  │      └── (temporary backend cache files)             │  │
│  │                                                       │  │
│  │  Mounted in: energy-defense-api                      │  │
│  │  Persistence: Optional, can be cleared               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ai_cache                                            │  │
│  │  └── /app/.ai_cache                                  │  │
│  │      └── (AI agent local cache)                      │  │
│  │                                                       │  │
│  │  Mounted in: energy-defense-ai-agent                 │  │
│  │  Persistence: Optional, can be cleared               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

⚠️  To completely reset the system:
    docker-compose down -v    # Deletes ALL volumes
```

---

## 🔄 Request Lifecycle

```
1. User clicks "View Dashboard" in browser
   │
   ▼
2. React Router navigates to /dashboard
   │
   ▼
3. Dashboard component calls useEffect()
   │
   ▼
4. Axios GET /api/v1/dashboard/stats
   │  Headers: { Authorization: "Bearer eyJ..." }
   │
   ▼
5. NGINX/Docker routes to backend:8000
   │
   ▼
6. FastAPI receives request
   │
   ▼
7. CORS middleware checks origin ✅
   │
   ▼
8. Auth middleware:
   │  - Extracts JWT token
   │  - Validates signature
   │  - Decodes payload
   │  - Loads user from DB
   │  - Checks is_active ✅
   │
   ▼
9. Request logging middleware logs:
   │  "GET /api/v1/dashboard/stats - User: admin"
   │
   ▼
10. Route handler executes:
    │  - Queries PostgreSQL (5 queries in parallel)
    │  - Aggregates results
    │
    ▼
11. Pydantic schema validates response
    │
    ▼
12. GZip middleware compresses response
    │
    ▼
13. Response sent back to frontend
    │  Status: 200 OK
    │  Content-Type: application/json
    │  Content-Encoding: gzip
    │
    ▼
14. Axios receives response
    │  - Decompresses
    │  - Parses JSON
    │
    ▼
15. React component updates state
    │
    ▼
16. React re-renders with new data
    │
    ▼
17. User sees updated dashboard 🎉
```

---

## 🎯 Component Dependency Graph

```
                            ┌─────────────┐
                            │  OpenRouter │
                            │  (External) │
                            └──────┬──────┘
                                   │
                                   │ API Calls
                                   ▼
          ┌────────────────────────────────────────┐
          │                                        │
    ┌─────▼──────┐                     ┌──────────▼─────┐
    │  AI Agent  │◄────────────────────│    Backend     │
    │  Service   │  Trigger Analysis   │      API       │
    └─────┬──────┘                     └──────┬─────────┘
          │                                   │
          │                                   │
          │                                   │
    ┌─────▼──────┐                     ┌──────▼─────────┐
    │   Redis    │                     │   Frontend     │
    │   Cache    │                     │   Dashboard    │
    └─────┬──────┘                     └────────────────┘
          │                                   ▲
          │                                   │
          │                                   │ User Access
          │                                   │
    ┌─────▼──────────────────────────────────┴──────┐
    │                PostgreSQL                     │
    │                 Database                      │
    │                                              │
    │  All services read/write here                │
    └───────────────────────────────────────────────┘
          ▲
          │
          │ Generate Data
          │
    ┌─────┴──────┐
    │    Data    │
    │ Simulator  │
    └────────────┘

Legend:
  ──►  Required dependency
  ◄──  Optional/Triggered interaction
```

---

**For detailed implementation details, see [SYSTEM_COMPONENTS_DETAILED.md](./SYSTEM_COMPONENTS_DETAILED.md)**
