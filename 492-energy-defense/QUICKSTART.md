# Quick Start Guide

Get 492-Energy-Defense running in under 5 minutes.

## Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- 8GB RAM minimum
- 20GB free disk space

## One-Command Start

```bash
cd 492-energy-defense
./scripts/start.sh
```

The script will:
1. Verify Docker installation
2. Create secure `.env` file with generated secrets
3. Build all services
4. Start the platform
5. Wait for services to be healthy
6. Display access URLs

## Manual Start

If you prefer manual control:

```bash
# 1. Create environment file
cp .env.example .env

# 2. Generate secure credentials
# Edit .env and set:
# - POSTGRES_PASSWORD
# - SECRET_KEY

# 3. Start services
docker-compose up --build -d

# 4. Verify
docker-compose ps
curl http://localhost:8000/health
```

## Access the Platform

Once started, open:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs

## First Steps

### 1. Explore Role Views

Click the role selector at the top to switch between:
- **Admin**: Configure AI weights, view audit logs
- **Analyst**: Submit feedback, view detailed analyses
- **Observer**: Read-only dashboard access

### 2. Review Real-Time Data

The dashboard automatically refreshes every 30 seconds showing:
- Critical and high-priority threats
- Open vulnerabilities by severity
- AI threat analyses with explanations
- Pending security patches

### 3. Configure AI Model (Admin Only)

1. Switch to Admin role
2. Scroll to "AI Model Configuration" panel
3. Adjust feature importance weights:
   - Authentication Events
   - Vulnerability Severity
   - Firewall Anomalies
   - Patch Criticality
4. Ensure weights sum to 1.0
5. Click "Save Configuration"

### 4. Submit Feedback (Analyst/Admin)

1. Click the message icon on any threat analysis
2. Select feedback type:
   - True Positive
   - False Positive
   - Accuracy Comment
3. Rate accuracy (1-5)
4. Add optional comments
5. Submit

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai-agent
docker-compose logs -f frontend
```

## Stop the Platform

```bash
# Stop services (preserve data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Troubleshooting

### Services Not Starting

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs backend

# Restart problematic service
docker-compose restart backend
```

### Database Connection Error

```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### Port Already in Use

If ports 3000, 8000, or 8001 are in use, modify `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change external port
```

## Next Steps

- **Explore API**: Visit http://localhost:8000/api/docs
- **View Architecture**: Read `ARCHITECTURE.md`
- **Production Setup**: See `docs/DEPLOYMENT.md`
- **API Reference**: Check `docs/API.md`

## Sample Use Cases

### Use Case 1: Detect Authentication Anomaly

1. Watch the dashboard for new authentication events
2. Data simulator generates login failures
3. AI agent analyzes patterns
4. Threat analysis appears with recommendations
5. Analyst can submit feedback on accuracy

### Use Case 2: Configure Threat Priorities

1. Admin reviews current threat distribution
2. Notices firewall anomalies are underweighted
3. Adjusts AI weights to prioritize network threats
4. Saves new configuration
5. Future analyses reflect new priorities
6. Change logged in audit trail

### Use Case 3: Vulnerability Management

1. Monitor "Open Vulnerabilities" panel
2. Click severity badge for details
3. Review affected systems and CVE IDs
4. Track remediation status
5. Cross-reference with pending patches

## Performance Notes

Initial startup takes 2-5 minutes as services:
- Build container images
- Initialize database schema
- Load TensorFlow model
- Start data simulation

Subsequent starts are faster using cached images.

## Support

For issues:
1. Check logs: `docker-compose logs [service]`
2. Verify health: `curl http://localhost:8000/health`
3. Review documentation in `docs/`
4. Check GitHub Issues

---

**Ready to explore? Start with the Dashboard at http://localhost:3000**
