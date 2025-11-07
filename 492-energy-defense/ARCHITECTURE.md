# System Architecture

## Overview

492-Energy-Defense is a microservices-based platform implementing defense-in-depth principles for cybersecurity operations in critical infrastructure.

## Component Architecture

### 1. Frontend Dashboard (React + Vite)

**Technology Stack**:
- React 18 with functional components and hooks
- Vite for fast development and optimized builds
- TailwindCSS for modern, responsive UI
- Recharts for data visualization
- Axios for API communication

**Key Features**:
- Role-based UI rendering (Admin/Analyst/Observer)
- Real-time data refresh (30s intervals)
- Interactive threat analysis cards
- Configurable AI model weights (Admin only)
- Feedback submission interface (Admin/Analyst)
- Audit log viewer (Admin only)

**State Management**:
- React Context for user/role management
- Local component state for UI interactions
- Polling-based data fetching (WebSocket-ready)

### 2. Backend API (FastAPI)

**Technology Stack**:
- FastAPI 0.104+ with async/await
- SQLAlchemy 2.0 with async support
- Pydantic for data validation
- Structlog for JSON logging
- AsyncPG for PostgreSQL connections

**Architecture Patterns**:
- Clean Architecture with separation of concerns
- Dependency Injection via FastAPI
- Repository pattern for data access
- Service layer for business logic
- Middleware for logging and CORS

**Key Endpoints**:
- `/api/auth/*` - Role switching and user management
- `/api/dashboard/*` - Aggregated metrics and trends
- `/api/ai/*` - AI configuration and threat analyses
- `/api/vulnerabilities/*` - Vulnerability management
- `/api/audit/*` - Audit log access

### 3. AI Agent (TensorFlow)

**Technology Stack**:
- TensorFlow 2.15 for model inference
- NumPy/Pandas for data processing
- Custom model manager with explainability

**Model Architecture**:
```
Input Layer (4 features)
    ↓
Dense Layer (16 units, ReLU)
    ↓
Dropout (0.2)
    ↓
Dense Layer (8 units, ReLU)
    ↓
Output Layer (1 unit, Sigmoid)
```

**Feature Engineering**:
1. **Authentication Score** - Derived from login failures, suspicious patterns
2. **Vulnerability Score** - Based on CVSS scores and count
3. **Firewall Score** - Anomaly detection on network traffic
4. **Patch Score** - Critical patch status and age

**Explainability Mechanism**:
- Weighted feature contributions
- Confidence scoring based on model certainty and feature variance
- Human-readable explanations
- Recommended actions based on threat category

### 4. Database (PostgreSQL)

**Schema Design**:
- **Normalized** to 3NF for data integrity
- **Indexed** for query performance
- **Partitionable** for scale (system_metrics)
- **Auditable** with triggers and logs

**Key Tables**:
- `users` - Role-based access control
- `auth_events` - Authentication activity
- `vulnerabilities` - CVE tracking
- `firewall_logs` - Network events
- `patches` - Update management
- `ai_threat_analyses` - ML model outputs
- `ai_feedback` - User evaluations
- `audit_logs` - Complete traceability

**Performance Optimizations**:
- Connection pooling (20 base, 10 overflow)
- Materialized views for dashboard aggregations
- Strategic indexing on time-series data
- JSONB for flexible metadata

### 5. Data Simulator

**Purpose**: Generate realistic security events for demonstration

**Event Types**:
- Authentication events (login success/failure)
- Firewall logs (allow/deny/drop)
- Vulnerability scans (periodic)
- Patch records (scheduled)

**Characteristics**:
- Realistic IP generation (private/public ranges)
- Weighted probability distributions
- Time-based patterns
- Correlated event sequences

## Data Flow

### Threat Analysis Pipeline

```
1. Raw Events → Database
   ├─ Auth Events
   ├─ Vulnerabilities
   ├─ Firewall Logs
   └─ Patches

2. Backend API Aggregation
   ├─ Calculate feature scores
   └─ Normalize to [0, 1] range

3. AI Agent Inference
   ├─ Apply current weights
   ├─ TensorFlow model prediction
   ├─ Confidence calculation
   └─ Generate explanation

4. Store Results
   ├─ ai_threat_analyses table
   └─ Update dashboard cache

5. Frontend Display
   ├─ Real-time updates
   ├─ Interactive visualizations
   └─ Actionable recommendations
```

### Configuration Update Flow

```
1. Admin adjusts AI weights in UI
   ↓
2. Frontend validates sum = 1.0
   ↓
3. POST to backend /api/ai/config/weights
   ↓
4. Backend validates and creates new config
   ↓
5. Backend logs to audit_logs table
   ↓
6. Backend calls AI agent /api/model/weights
   ↓
7. AI agent updates model_manager weights
   ↓
8. Future analyses use new weights
```

### Feedback Loop

```
1. Analyst reviews threat analysis
   ↓
2. Submits feedback via dashboard
   ↓
3. Backend stores in ai_feedback table
   ↓
4. Linked to specific analysis_id
   ↓
5. Available for model refinement
   ↓
6. Admin can review feedback trends
```

## Security Architecture

### Defense Layers

1. **Network**: Docker network isolation, port restrictions
2. **Application**: Input validation, parameterized queries
3. **Authentication**: Role-based access control
4. **Authorization**: Endpoint-level permission checks
5. **Data**: Encrypted connections, sanitized inputs
6. **Audit**: Complete action logging

### Threat Model

**Mitigations**:
- SQL Injection: SQLAlchemy ORM, parameterized queries
- XSS: React auto-escaping, Content-Security-Policy headers
- CSRF: SameSite cookies, Origin validation
- DDoS: Rate limiting (ready for implementation)
- Data Breach: Connection pooling limits, read-only roles

## Scalability

### Horizontal Scaling

**Stateless Services**:
- Backend API: Scale to N instances behind load balancer
- AI Agent: Independent instances for parallel inference
- Frontend: Static assets via CDN

**Stateful Services**:
- PostgreSQL: Read replicas, connection pooling
- Shared state via database, not memory

### Vertical Scaling

**Resource Allocation**:
- Backend: 2 CPU, 4GB RAM per instance
- AI Agent: 4 CPU, 8GB RAM per instance
- Database: 4+ CPU, 8+ GB RAM, SSD storage

### Caching Strategy

**Levels**:
1. **Application**: In-memory caching for config
2. **Database**: Materialized views for aggregations
3. **CDN**: Static frontend assets

## Observability

### Logging

**Structured JSON Logs**:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "backend",
  "action": "threat_analysis",
  "user": "admin_user",
  "threat_score": 0.85,
  "severity": "critical"
}
```

**Log Levels**:
- DEBUG: Development only
- INFO: Normal operations
- WARNING: Degraded performance
- ERROR: Application errors
- CRITICAL: Service failures

### Metrics

**Application Metrics**:
- Request rate and latency
- Error rates by endpoint
- AI inference time
- Database query performance

**System Metrics**:
- CPU/Memory/Disk usage
- Network throughput
- Container health

### Tracing

**Distributed Tracing Ready**:
- Request ID propagation
- Service-to-service correlation
- OpenTelemetry compatible

## Disaster Recovery

### Backup Strategy

**Database**:
- Daily full backups
- Hourly incremental backups
- 30-day retention
- Off-site storage

**Configuration**:
- Version controlled in Git
- Immutable infrastructure

**State**:
- AI model versions in object storage
- Audit logs replicated

### Recovery Objectives

- **RTO** (Recovery Time Objective): 1 hour
- **RPO** (Recovery Point Objective): 1 hour
- **Data Loss Tolerance**: Minimal (< 1 hour)

## Future Enhancements

### Technical Roadmap

1. **WebSocket Support**: Real-time push notifications
2. **Advanced ML**: LSTM for time-series anomaly detection
3. **Federated Learning**: Multi-site threat intelligence
4. **GraphQL API**: Flexible query interface
5. **Kubernetes**: Cloud-native orchestration
6. **Service Mesh**: Advanced traffic management

### Feature Roadmap

1. **Incident Response**: Automated playbooks
2. **Threat Intelligence**: External feed integration
3. **Compliance Reporting**: NERC-CIP, IEC 62443
4. **User Management**: Full authentication system
5. **Alert Routing**: Integration with SIEM platforms

## Conclusion

This architecture provides a production-ready foundation for AI-driven cybersecurity operations, with emphasis on:
- **Reliability**: Service health checks, graceful degradation
- **Security**: Defense-in-depth, audit logging
- **Scalability**: Horizontal scaling, performance optimization
- **Maintainability**: Clean code, comprehensive testing
- **Observability**: Structured logging, metrics, tracing
