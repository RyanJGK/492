# API Reference Guide

## 492-Energy-Defense API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## Authentication

All endpoints except `/auth/login` and `/auth/register` require authentication.

### Request Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Error Responses

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

---

## Authentication Endpoints

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "demo123"}'
```

### POST /auth/register

Register a new user (Admin only in production).

**Request Body**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "role": "admin|analyst|observer"
}
```

**Response**: User object

### GET /auth/me

Get current authenticated user information.

**Response**:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  "role": "analyst",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Dashboard Endpoints

### GET /dashboard/summary

Get system overview with key metrics.

**Permissions**: All authenticated users

**Response**:
```json
{
  "auth_events": {
    "total": 1234,
    "failed_24h": 45
  },
  "patch_compliance": {
    "critical_assets": 3
  },
  "vulnerabilities": {
    "critical_open": 5,
    "high_open": 12
  },
  "firewall": {
    "threats_24h": 28
  },
  "ai_analysis": {
    "critical_findings": 2
  },
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### GET /dashboard/auth-events

Get authentication events with pagination.

**Permissions**: All authenticated users

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Max records to return (default: 100, max: 1000)
- `user_id`: Filter by user UUID
- `success`: Filter by success status (true/false)

**Response**: Array of AuthEvent objects

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "event_type": "login_success",
    "ip_address": "10.0.1.100",
    "user_agent": "Mozilla/5.0...",
    "success": true,
    "risk_score": 5,
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

### GET /dashboard/patch-levels

Get patch compliance status.

**Permissions**: All authenticated users

**Query Parameters**:
- `skip`, `limit`: Pagination
- `compliance_status`: Filter by status (critical|at_risk|non_compliant|compliant)
- `asset_type`: Filter by type (server|workstation|network_device|ics_component|scada_system)

**Response**: Array of PatchLevel objects

### GET /dashboard/vulnerabilities

Get vulnerability scan results.

**Permissions**: All authenticated users

**Query Parameters**:
- `skip`, `limit`: Pagination
- `severity`: Filter by severity (critical|high|medium|low|informational)
- `status`: Filter by status (open|mitigated|remediated|accepted_risk|false_positive)
- `asset_id`: Filter by asset

**Response**: Array of VulnerabilityScan objects

```json
[
  {
    "id": "uuid",
    "scan_id": "SCAN-001",
    "asset_id": "SRV-001",
    "asset_name": "Primary SCADA Server",
    "vulnerability_id": "VULN-12345",
    "cve_id": "CVE-2024-1234",
    "severity": "critical",
    "cvss_score": 9.8,
    "title": "Remote Code Execution",
    "description": "...",
    "exploit_available": true,
    "status": "open",
    "risk_score": 98,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET /dashboard/firewall-logs

Get firewall log entries.

**Permissions**: All authenticated users

**Query Parameters**:
- `skip`, `limit`: Pagination
- `action`: Filter by action (allow|deny|drop|reject)
- `threat_detected`: Filter by threat detection (true/false)
- `source_ip`: Filter by source IP

**Response**: Array of FirewallLog objects

### GET /dashboard/ai-analyses

Get AI analysis results.

**Permissions**: All authenticated users

**Query Parameters**:
- `skip`, `limit`: Pagination
- `analysis_type`: Filter by type (threat_correlation|risk_assessment|anomaly_detection|trend_analysis|incident_prediction)
- `severity`: Filter by severity

**Response**: Array of AIAnalysis objects

---

## Data Ingestion Endpoints

**Permissions**: Analyst and Admin roles only

### POST /ingest/auth-events

Ingest single authentication event.

**Request Body**: AuthEvent object (without id, timestamp)

### POST /ingest/auth-events/bulk

Bulk ingest authentication events.

**Request Body**: Array of AuthEvent objects

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/ingest/auth-events/bulk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "event_type": "login_success",
      "ip_address": "10.0.1.100",
      "user_agent": "Mozilla/5.0...",
      "success": true,
      "risk_score": 5
    }
  ]'
```

### POST /ingest/patch-levels

Ingest patch level data.

**Request Body**: PatchLevel object

### POST /ingest/patch-levels/bulk

Bulk ingest patch levels.

### POST /ingest/vulnerabilities

Ingest vulnerability scan data.

**Request Body**: VulnerabilityScan object

### POST /ingest/vulnerabilities/bulk

Bulk ingest vulnerability scans.

### POST /ingest/firewall-logs

Ingest firewall log entry.

**Request Body**: FirewallLog object

### POST /ingest/firewall-logs/bulk

Bulk ingest firewall logs.

---

## AI Agent Endpoints

### POST /ai/analyze

Request AI-powered security analysis.

**Permissions**: Analyst and Admin roles

**Request Body**:
```json
{
  "analysis_type": "threat_correlation",
  "source_data": {
    "vulnerabilities": [...],
    "firewall_logs": [...],
    "auth_events": [...]
  },
  "weight_config": {
    "data_sources": {
      "auth_events": 0.25,
      "patch_levels": 0.20,
      "vulnerability_scans": 0.35,
      "firewall_logs": 0.20
    },
    "threat_indicators": {
      "critical_severity": 1.0,
      "high_severity": 0.8
    }
  },
  "query": "Optional specific question"
}
```

**Response**:
```json
{
  "id": "uuid",
  "analysis_type": "threat_correlation",
  "response": "Detailed analysis text...",
  "confidence_score": 85.5,
  "severity": "high",
  "recommendations": "Specific recommendations...",
  "model_used": "anthropic/claude-3.5-sonnet",
  "tokens_used": 1234,
  "cached": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /ai/analyze/feedback/{analysis_id}

Submit feedback on AI analysis.

**Permissions**: Analyst and Admin roles

**Query Parameters**:
- `feedback`: accurate|mostly_accurate|needs_improvement|inaccurate|false_positive
- `notes`: Optional feedback notes

**Response**:
```json
{
  "message": "Feedback submitted successfully"
}
```

### GET /ai/weights

Get all AI weight configurations.

**Permissions**: All authenticated users

**Response**: Array of AIWeightConfig objects

### GET /ai/weights/active

Get currently active weight configuration.

**Response**: AIWeightConfig object

### POST /ai/weights

Create new weight configuration.

**Permissions**: Admin only

**Request Body**:
```json
{
  "config_name": "custom_config",
  "description": "Custom weighting for high-risk scenarios",
  "weights": {
    "data_sources": { ... },
    "threat_indicators": { ... },
    "temporal_factors": { ... },
    "asset_criticality": { ... }
  },
  "is_active": false
}
```

### PUT /ai/weights/{config_id}/activate

Activate a weight configuration.

**Permissions**: Admin only

**Response**:
```json
{
  "message": "Configuration activated successfully"
}
```

---

## Rate Limiting

- Default: 60 requests per minute per IP
- Login endpoint: 5 requests per minute per IP
- Exceeded: HTTP 429 Too Many Requests

---

## Webhooks (Future)

Planned webhook support for:
- Critical security events
- AI analysis completion
- System alerts

---

## SDK Examples

### Python

```python
import httpx

class EnergyDefenseClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = None
        self.client = httpx.Client()
        self.login(username, password)
    
    def login(self, username, password):
        response = self.client.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        self.token = response.json()["access_token"]
    
    def get_summary(self):
        response = self.client.get(
            f"{self.base_url}/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()
```

### JavaScript

```javascript
class EnergyDefenseClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    });
    const data = await response.json();
    this.token = data.access_token;
  }

  async getSummary() {
    const response = await fetch(`${this.baseUrl}/api/v1/dashboard/summary`, {
      headers: {'Authorization': `Bearer ${this.token}`}
    });
    return await response.json();
  }
}
```

---

## Pagination

All list endpoints support pagination:

```
GET /endpoint?skip=0&limit=100
```

Response includes:
- Array of objects
- Total count in headers (if supported)

---

## Filtering

Many endpoints support query parameter filtering:

```
GET /dashboard/vulnerabilities?severity=critical&status=open
```

Multiple filters combine with AND logic.

---

## Sorting

Use `order_by` parameter (where supported):

```
GET /endpoint?order_by=created_at&order=desc
```

---

## Error Handling Best Practices

```javascript
try {
  const response = await api.getData();
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error status
    switch (error.response.status) {
      case 401:
        // Redirect to login
        break;
      case 403:
        // Show access denied
        break;
      case 422:
        // Show validation errors
        break;
      default:
        // Generic error
    }
  } else {
    // Network error
  }
}
```

---

**For complete API documentation with interactive testing, visit**: `http://localhost:8000/docs`
