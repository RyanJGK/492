# System Architecture

## 492-Energy-Defense Architecture Overview

This document details the technical architecture, design decisions, and implementation patterns used in the 492-Energy-Defense system.

## Architecture Principles

### 12-Factor App Methodology

1. **Codebase**: Single repository with multiple services
2. **Dependencies**: Explicitly declared (requirements.txt, package.json)
3. **Config**: Environment-based configuration
4. **Backing Services**: Attached resources (PostgreSQL, OpenRouter)
5. **Build, Release, Run**: Strict separation via Docker
6. **Processes**: Stateless, share-nothing architecture
7. **Port Binding**: Self-contained services
8. **Concurrency**: Horizontal scaling via containers
9. **Disposability**: Fast startup and graceful shutdown
10. **Dev/Prod Parity**: Consistent environments
11. **Logs**: Treat logs as event streams
12. **Admin Processes**: Run as one-off processes

### Clean Architecture

```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer                      │
│  (React Components, API Routes, CLI)                │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│           Application Layer                          │
│  (Use Cases, Business Logic, Orchestration)         │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│              Domain Layer                            │
│  (Entities, Value Objects, Domain Services)         │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│          Infrastructure Layer                        │
│  (Database, External APIs, File System)             │
└─────────────────────────────────────────────────────┘
```

## Service Architecture

### Backend API (FastAPI)

**Purpose**: Central API gateway for all client interactions

**Responsibilities**:
- Authentication and authorization
- Request validation and sanitization
- Business logic orchestration
- Data persistence
- API documentation

**Technology Stack**:
- FastAPI: Async web framework
- SQLAlchemy: Async ORM
- Pydantic: Data validation
- Alembic: Database migrations
- Python-JOSE: JWT handling

**Key Components**:

```python
backend/
├── app/
│   ├── api/
│   │   └── endpoints/      # API route handlers
│   ├── core/
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Database connection
│   │   ├── security.py     # Auth utilities
│   │   └── dependencies.py # Dependency injection
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── middleware/         # Custom middleware
│   └── main.py            # Application entry point
└── tests/                 # Test suite
```

**Design Patterns**:
- Dependency Injection: FastAPI's Depends()
- Repository Pattern: Database abstraction
- Factory Pattern: Model creation
- Middleware Pattern: Cross-cutting concerns

### AI Agent Service

**Purpose**: Specialized service for AI-powered analysis

**Responsibilities**:
- OpenRouter API integration
- Analysis request processing
- Response caching
- Weight configuration application

**Technology Stack**:
- FastAPI: Async framework
- HTTPX: HTTP client for OpenRouter
- Custom caching: File-based storage

**Architecture**:

```python
ai-agent/
├── app/
│   ├── core/
│   │   └── config.py       # Service configuration
│   ├── services/
│   │   ├── openrouter.py   # OpenRouter client
│   │   ├── analyzer.py     # Analysis engine
│   │   └── cache.py        # Caching service
│   ├── main.py            # Service entry point
│   └── cache/             # Cache storage
```

**Analysis Flow**:

```
1. Request received → Validate schema
2. Check cache → Return if hit
3. Build prompt → Apply weights
4. Call OpenRouter → Process response
5. Structure result → Cache
6. Return to client
```

### Frontend Dashboard (React)

**Purpose**: Role-based user interface for security monitoring

**Responsibilities**:
- User authentication
- Real-time data display
- Role-based UI rendering
- API interaction

**Technology Stack**:
- React 18: UI library
- React Router: Client-side routing
- Tailwind CSS: Styling
- Axios: HTTP client
- Context API: State management

**Component Structure**:

```javascript
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   ├── contexts/         # React contexts
│   ├── services/         # API clients
│   ├── hooks/            # Custom hooks
│   └── utils/            # Utility functions
```

**State Management**:
- AuthContext: User authentication state
- Local state: Component-specific data
- API queries: Server state via axios

### Database Layer (PostgreSQL)

**Purpose**: Persistent storage for all system data

**Schema Design**:

```sql
-- Users and Authentication
users → auth_events
users → ai_weight_configs
users → audit_logs

-- Security Data
patch_levels
vulnerability_scans
firewall_logs

-- AI Analysis
ai_analysis → users (analyst feedback)
ai_weight_configs → users (creator)

-- Audit
audit_logs → users
```

**Indexing Strategy**:
- Primary keys: UUID for distributed systems
- Foreign keys: Relationship integrity
- Timestamp indexes: Temporal queries
- Status indexes: Filtering
- Composite indexes: Complex queries

### Data Simulator

**Purpose**: Continuous SOC data generation

**Responsibilities**:
- Realistic data generation
- Periodic ingestion
- Threat pattern simulation
- Asset state updates

**Simulation Patterns**:
- Auth events: 80% success, 20% failure
- Vulnerabilities: Critical/High focus
- Firewall logs: 30% threat detection
- Patch levels: Compliance drift

## Communication Patterns

### Synchronous Communication

**REST API** (Backend ↔ Frontend):
```
HTTP/HTTPS → JSON payloads
Authentication: JWT Bearer tokens
Rate limiting: Per endpoint
```

**Internal Service** (Backend ↔ AI Agent):
```
HTTP → JSON payloads
No authentication (internal network)
Timeout: 60 seconds
```

### Asynchronous Patterns

**Background Tasks**:
- Data ingestion from simulator
- Periodic cache cleanup
- Database maintenance
- Log rotation

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. Backend validates against database
   ↓
3. Generate JWT access + refresh tokens
   ↓
4. Return tokens to client
   ↓
5. Client stores in localStorage
   ↓
6. Include in Authorization header
   ↓
7. Backend validates on each request
```

### Authorization Layers

**API Level**:
```python
@router.get("/admin-only")
async def admin_endpoint(
    user: User = Depends(require_admin)
):
    # Only admin role can access
```

**Database Level**:
- Row-level security policies
- User-specific views
- Audit triggers

**Frontend Level**:
- Route protection
- Component visibility
- Action restrictions

### Data Protection

**At Rest**:
- PostgreSQL encryption support
- Volume encryption (production)
- Secure secrets storage

**In Transit**:
- TLS/HTTPS (production)
- JWT signed tokens
- Secure headers

**In Use**:
- Input validation
- SQL injection prevention
- XSS protection

## Scalability Considerations

### Horizontal Scaling

**Backend**:
- Stateless design
- Load balancer ready
- Session management via JWT

**AI Agent**:
- Independent scaling
- Cache per instance
- Queue-based processing (future)

**Database**:
- Connection pooling
- Read replicas (future)
- Partitioning strategy

### Vertical Scaling

**Resource Allocation**:
```yaml
backend:
  cpu: 2 cores
  memory: 2GB

ai-agent:
  cpu: 2 cores
  memory: 2GB

postgres:
  cpu: 2 cores
  memory: 4GB
```

## Data Flow Diagrams

### Authentication Flow

```
User → Frontend → Backend → Database
  1. POST /login
  2. Validate credentials
  3. Query users table
  4. Generate JWT
  5. Log auth_event
  6. Return tokens
```

### AI Analysis Flow

```
Analyst → Frontend → Backend → AI Agent → OpenRouter
  1. Request analysis
  2. Validate permissions
  3. Forward request
  4. Check cache
  5. Build prompt
  6. Call LLM API
  7. Process response
  8. Cache result
  9. Store in database
  10. Return to frontend
```

### Data Ingestion Flow

```
Simulator → Backend → Database
  1. Generate data batch
  2. Authenticate
  3. POST bulk data
  4. Validate schemas
  5. Insert into tables
  6. Log audit entry
  7. Return confirmation
```

## Error Handling

### Backend

```python
try:
    result = await operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(
        status_code=400,
        detail="User-friendly message"
    )
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### Frontend

```javascript
try {
  const response = await api.getData();
  setData(response.data);
} catch (error) {
  if (error.response?.status === 401) {
    // Redirect to login
  } else {
    // Show error message
    setError(error.message);
  }
}
```

## Logging Strategy

### Structured Logging

```python
logger.info(
    "User action",
    extra={
        "user_id": user.id,
        "action": "login",
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow()
    }
)
```

### Log Levels

- **DEBUG**: Development debugging
- **INFO**: Normal operations
- **WARNING**: Unexpected but handled
- **ERROR**: Operation failures
- **CRITICAL**: System failures

### Log Aggregation

- Container stdout/stderr
- File-based rotation
- External logging service (production)

## Performance Optimization

### Database

- Connection pooling: 10 min, 20 max
- Query optimization via indexes
- Pagination on large datasets
- Async queries throughout

### API

- Response caching
- Request validation early
- Async processing
- Rate limiting

### Frontend

- Code splitting
- Lazy loading
- Memoization
- Debouncing

## Testing Strategy

### Backend

```python
# Unit tests
def test_password_hashing():
    hashed = get_password_hash("password")
    assert verify_password("password", hashed)

# Integration tests
async def test_login_endpoint(client):
    response = await client.post("/api/v1/auth/login", ...)
    assert response.status_code == 200
```

### Frontend

```javascript
// Component tests
test('Login form submits', () => {
  render(<LoginForm />);
  fireEvent.submit(screen.getByRole('form'));
  expect(mockLogin).toHaveBeenCalled();
});
```

## Future Enhancements

### Planned Architecture Changes

1. **Message Queue**: RabbitMQ/Redis for async tasks
2. **Caching Layer**: Redis for distributed caching
3. **Service Mesh**: Istio for microservices
4. **Event Sourcing**: Audit trail improvements
5. **CQRS**: Read/write separation
6. **GraphQL**: Alternative API layer

### Scalability Roadmap

1. **Phase 1**: Optimize current architecture
2. **Phase 2**: Implement caching layer
3. **Phase 3**: Add read replicas
4. **Phase 4**: Microservices split
5. **Phase 5**: Cloud-native deployment

---

**Architecture Review**: Quarterly reviews recommended to adapt to changing requirements and technology advancements.
