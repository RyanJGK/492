# API Documentation

## Base URLs

- **Backend API**: `http://localhost:8000`
- **AI Agent API**: `http://localhost:8001`
- **Interactive Docs**: `http://localhost:8000/api/docs`

## Authentication Endpoints

### Switch Role
```http
POST /api/auth/switch-role
Content-Type: application/json

{
  "role": "admin"
}
```

**Response**:
```json
{
  "id": "uuid",
  "username": "admin_user",
  "role": "admin",
  "is_active": true,
  "last_login": "2024-01-01T00:00:00Z"
}
```

### Get Available Roles
```http
GET /api/auth/roles
```

## Dashboard Endpoints

### Get Summary
```http
GET /api/dashboard/summary
```

**Response**:
```json
{
  "total_events": 1234,
  "critical_threats": 5,
  "high_threats": 12,
  "open_vulnerabilities": 45,
  "pending_patches": 23,
  "ai_analyses_24h": 89,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

### Get Threat Trends
```http
GET /api/dashboard/threats/trends?hours=24
```

### Get Top Blocked IPs
```http
GET /api/dashboard/firewall/top-blocked-ips?limit=10
```

## AI Endpoints

### Get Active Configuration
```http
GET /api/ai/config/active
```

### Update AI Weights (Admin Only)
```http
POST /api/ai/config/weights?username=admin_user
Content-Type: application/json

{
  "auth_events": 0.30,
  "vulnerability_severity": 0.35,
  "firewall_anomalies": 0.25,
  "patch_criticality": 0.10
}
```

### Get Threat Analyses
```http
GET /api/ai/analyses?severity=critical&hours=24&limit=100
```

### Submit Feedback
```http
POST /api/ai/feedback?username=analyst_user
Content-Type: application/json

{
  "analysis_id": "uuid",
  "feedback_type": "true_positive",
  "accuracy_rating": 4,
  "comments": "Accurate threat detection"
}
```

## Vulnerability Endpoints

### Get Vulnerabilities
```http
GET /api/vulnerabilities?status=open&severity=critical&limit=100
```

### Get Scans
```http
GET /api/vulnerabilities/scans?limit=50
```

## Audit Endpoints

### Get Audit Logs
```http
GET /api/audit/logs?action=update_ai_weights&hours=24&limit=100
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error
