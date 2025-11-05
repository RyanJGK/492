# Deployment Guide

## Local Development Deployment

### Quick Start
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 2. Start all services
docker-compose up --build

# 3. Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Individual Service Management

```bash
# Start specific services
docker-compose up backend frontend postgres

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

## Production Deployment

### Prerequisites

1. **Server Requirements**
   - Ubuntu 20.04+ or similar
   - 4GB+ RAM
   - 20GB+ disk space
   - Docker 20.10+
   - Docker Compose 2.0+

2. **Security Credentials**
   - OpenRouter API key
   - Strong database password
   - JWT secret key (256-bit recommended)
   - SSL/TLS certificates

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create application user
sudo useradd -m -s /bin/bash energydefense
sudo usermod -aG docker energydefense
```

### Step 2: Application Setup

```bash
# Switch to application user
sudo su - energydefense

# Clone or copy project
# git clone <repository> 492-energy-defense
cd 492-energy-defense

# Configure environment
cp .env.example .env
nano .env
```

### Step 3: Production Configuration

Edit `.env` with production values:

```bash
# Database - Use strong passwords
POSTGRES_DB=energy_defense_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=<STRONG_RANDOM_PASSWORD>

# Security - Generate with: openssl rand -hex 32
SECRET_KEY=<64_CHARACTER_HEX_STRING>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter
OPENROUTER_API_KEY=<YOUR_API_KEY>

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS - Your domain
CORS_ORIGINS=https://yourdomain.com

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

### Step 4: SSL/TLS Setup

For production, add nginx reverse proxy:

```yaml
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - backend
      - frontend
```

Create `nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 5: Database Initialization

```bash
# Start database first
docker-compose up -d postgres

# Wait for initialization
sleep 10

# Verify database
docker-compose exec postgres psql -U prod_user -d energy_defense_prod -c "\dt"
```

### Step 6: Start Production Services

```bash
# Build and start all services
docker-compose up -d --build

# Verify all services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### Step 7: Change Default Credentials

```bash
# Connect to backend container
docker-compose exec backend bash

# Use Python to hash new password
python -c "from api.middleware.auth import get_password_hash; print(get_password_hash('NEW_SECURE_PASSWORD'))"

# Update in database
docker-compose exec postgres psql -U prod_user -d energy_defense_prod

UPDATE users SET hashed_password = '<NEW_HASH>' WHERE username = 'admin';
UPDATE users SET hashed_password = '<NEW_HASH>' WHERE username = 'analyst';
UPDATE users SET hashed_password = '<NEW_HASH>' WHERE username = 'observer';
```

## Monitoring & Maintenance

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
docker-compose exec postgres pg_isready

# Service status
docker-compose ps
```

### Log Management

```bash
# View logs
docker-compose logs -f [service]

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow specific service
docker-compose logs -f ai-agent
```

### Backup Strategy

```bash
# Database backup
docker-compose exec postgres pg_dump -U prod_user energy_defense_prod > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20231201.sql | docker-compose exec -T postgres psql -U prod_user energy_defense_prod

# Automated backups (crontab)
0 2 * * * cd /home/energydefense/492-energy-defense && docker-compose exec postgres pg_dump -U prod_user energy_defense_prod > /backups/db_$(date +\%Y\%m\%d).sql
```

### Updates & Scaling

```bash
# Pull latest changes
git pull

# Rebuild specific service
docker-compose up -d --build backend

# Scale data simulator (if needed)
docker-compose up -d --scale data-simulator=0

# View resource usage
docker stats
```

## Security Hardening

### 1. Firewall Configuration

```bash
# UFW firewall rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Rate Limiting

Add to nginx.conf:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20;
    proxy_pass http://backend;
}
```

### 3. Database Security

```sql
-- Limit user permissions
REVOKE ALL ON DATABASE energy_defense_prod FROM PUBLIC;
GRANT CONNECT ON DATABASE energy_defense_prod TO prod_user;

-- Create read-only user for observers
CREATE USER observer_db WITH PASSWORD '<password>';
GRANT CONNECT ON DATABASE energy_defense_prod TO observer_db;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_db;
```

### 4. Secret Management

For production, use external secret management:

```bash
# Example with Docker secrets
echo "your_secret_key" | docker secret create jwt_secret -
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs [service-name]

# Verify environment variables
docker-compose config

# Test database connection
docker-compose exec backend python -c "from api.database import engine; print(engine)"
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Database performance
docker-compose exec postgres psql -U prod_user -d energy_defense_prod -c "SELECT * FROM pg_stat_activity;"

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

### Network Issues

```bash
# Verify network
docker network ls
docker network inspect 492-energy-defense_energy-defense-network

# Check service connectivity
docker-compose exec backend ping postgres
```

## Rollback Procedure

```bash
# Stop current version
docker-compose down

# Restore previous version
git checkout <previous-commit>

# Restore database backup
cat backup_YYYYMMDD.sql | docker-compose exec -T postgres psql -U prod_user energy_defense_prod

# Restart services
docker-compose up -d --build
```

## Performance Optimization

### Database Tuning

```sql
-- Add indexes for common queries
CREATE INDEX idx_firewall_timestamp ON firewall_logs(log_timestamp DESC);
CREATE INDEX idx_vuln_severity_status ON vulnerability_scans(severity, status);

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Redis Optimization

```bash
# Set maxmemory policy
docker-compose exec redis redis-cli CONFIG SET maxmemory 256mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Monitoring Setup (Optional)

For production monitoring, consider adding:

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation
- **Sentry** - Error tracking

---

**Remember**: Always test deployments in a staging environment before production!
