# 🚀 Quick Start Guide

Get 492-Energy-Defense running in under 5 minutes.

## Prerequisites

- Docker installed and running
- Docker Compose v2+
- 4GB available RAM
- OpenRouter API key (get free at https://openrouter.ai)

## Setup Steps

### 1. Environment Configuration

```bash
cd /workspace/492-energy-defense

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Required: Add your OpenRouter API key:**
```bash
OPENROUTER_API_KEY=your_key_here
```

Optional: Change default passwords (recommended for production)

### 2. Start Services

```bash
# Build and start all services
docker-compose up --build -d

# Watch logs (optional)
docker-compose logs -f
```

Wait 30-60 seconds for services to initialize.

### 3. Access Application

**Frontend Dashboard:**
http://localhost:3000

**API Documentation:**
http://localhost:8000/api/docs

**Database:**
- Host: localhost
- Port: 5432
- Database: energy_defense
- User: admin
- Password: changeme

### 4. Login

Use these demo credentials:

| Username | Password | Role     |
|----------|----------|----------|
| admin    | admin123 | Admin    |
| analyst  | admin123 | Analyst  |
| observer | admin123 | Observer |

## What You'll See

### Dashboard (All Users)
- Real-time threat statistics
- Vulnerability counts
- Firewall activity
- AI analysis metrics
- Trend visualizations

### Vulnerabilities Page (All Users)
- Security scan results
- CVE tracking
- Severity filtering
- System targets

### AI Configuration (Admin Only)
- Weight parameter management
- Configuration versioning
- Active config selection

### Feedback (Analyst + Admin)
- AI accuracy rating
- False positive reporting
- Analysis comments

## Service Status

Check if everything is running:

```bash
docker-compose ps
```

You should see:
- ✓ energy-defense-db (postgres)
- ✓ energy-defense-redis (redis)
- ✓ energy-defense-api (backend)
- ✓ energy-defense-ai-agent
- ✓ energy-defense-simulator
- ✓ energy-defense-frontend

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Verify environment
cat .env | grep OPENROUTER_API_KEY
```

### Frontend shows connection error
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in .env
echo $CORS_ORIGINS
```

### Database connection issues
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U admin -d energy_defense -c "\dt"

# Restart database
docker-compose restart postgres
```

### AI Agent not responding
```bash
# Verify API key is set
docker-compose exec backend env | grep OPENROUTER

# Check AI agent logs
docker-compose logs ai-agent
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
```

## Next Steps

1. **Explore the Dashboard**
   - Navigate through different pages
   - Try different user roles (logout/login as different users)

2. **Monitor Data Simulation**
   - Watch as the simulator generates realistic security events
   - Check the vulnerabilities page for new scans

3. **Test AI Configuration (Admin)**
   - View current AI weight settings
   - Understand how weights affect threat analysis

4. **Submit Feedback (Analyst)**
   - Rate AI analysis accuracy
   - Provide feedback on threat detection

5. **Review API Documentation**
   - Visit http://localhost:8000/api/docs
   - Explore available endpoints
   - Test API calls with built-in interface

## Key Features to Try

### Role-Based Access Control
1. Login as **admin** - full access to all features
2. Login as **analyst** - can view and provide feedback
3. Login as **observer** - read-only access

### AI Configuration (Admin)
- View active weight configuration
- See how different weights affect threat scoring
- Understand confidence threshold settings

### Data Simulation
- Real-time firewall log generation
- Automated vulnerability scan simulation
- Dynamic patch status updates

### Security Features
- JWT token authentication
- Secure password hashing
- Role-based route protection
- Audit logging

## Performance Tips

- **First startup**: Takes 1-2 minutes for database initialization
- **Subsequent startups**: ~30 seconds
- **Dashboard load**: ~2 seconds with live data
- **API response**: <100ms typical

## Default Data

The system starts with:
- 3 pre-configured users (admin, analyst, observer)
- Default AI weight configuration
- Simulated security events (generated continuously)

Data simulator runs every 5 minutes and creates:
- 5-15 firewall logs
- 2-5 vulnerability scans
- 2-5 patch level records

## Support

If you encounter issues:

1. **Check service health:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

2. **Review logs:**
   ```bash
   docker-compose logs [service-name]
   ```

3. **Verify configuration:**
   ```bash
   docker-compose config
   ```

4. **Fresh restart:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

## Production Deployment

⚠️ Before deploying to production:

1. Change all default passwords
2. Generate secure SECRET_KEY
3. Configure HTTPS/TLS
4. Set up database backups
5. Review DEPLOYMENT.md for full guide

---

**You're all set! Explore the system and see AI-driven cybersecurity defense in action.**

For detailed documentation, see [README.md](README.md)
