# Deployment Guide

## Production Deployment for 492-Energy-Defense

This guide covers deploying the system in a production environment with security hardening and scalability considerations.

## Prerequisites

- Linux server (Ubuntu 22.04 LTS recommended)
- Docker Engine 24.0+
- Docker Compose v2.20+
- Valid SSL/TLS certificates
- OpenRouter API key
- Minimum 8GB RAM, 4 CPU cores
- 50GB available storage

## Pre-Deployment Checklist

- [ ] Server hardened (firewall, SSH keys, fail2ban)
- [ ] SSL/TLS certificates obtained
- [ ] Backup strategy defined
- [ ] Monitoring solution ready
- [ ] Secrets management configured
- [ ] DNS records configured
- [ ] Load balancer configured (if applicable)

## Security Configuration

### 1. Generate Secure Secrets

```bash
# Generate SECRET_KEY (minimum 32 characters)
openssl rand -hex 32

# Generate database password
openssl rand -base64 32
```

### 2. Configure Environment Variables

Create production `.env` file:

```bash
# Database
POSTGRES_USER=energydefense_prod
POSTGRES_PASSWORD=<generated-secure-password>
POSTGRES_DB=energy_defense_prod
POSTGRES_PORT=5432

# Backend
BACKEND_PORT=8000
SECRET_KEY=<generated-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# AI Agent
AI_AGENT_PORT=8001
OPENROUTER_API_KEY=<your-api-key>

# Frontend
FRONTEND_PORT=3000
VITE_API_URL=https://api.yourdomain.com

# Environment
ENVIRONMENT=production
```

### 3. File Permissions

```bash
chmod 600 .env
chown root:root .env
```

## Docker Compose Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - /var/lib/energy-defense/postgres:/var/lib/postgresql/data
    networks:
      - backend-network
    # No exposed ports - internal only

  backend:
    restart: always
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
    networks:
      - backend-network
      - frontend-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ai-agent:
    restart: always
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    networks:
      - backend-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    restart: always
    environment:
      - VITE_API_URL=${VITE_API_URL}
    networks:
      - frontend-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - frontend-network

networks:
  backend-network:
    driver: bridge
    internal: true
  frontend-network:
    driver: bridge

volumes:
  postgres_data:
  ai_cache:
```

## Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login endpoint - stricter rate limiting
        location /api/v1/auth/login {
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Deployment Steps

### 1. Initial Deployment

```bash
# Pull latest code
git pull origin main

# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. Database Initialization

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Verify database
docker-compose -f docker-compose.prod.yml exec postgres psql -U energydefense_prod -d energy_defense_prod -c "\dt"
```

### 3. Create Initial Users

```bash
# Access backend container
docker-compose -f docker-compose.prod.yml exec backend python

# In Python shell
from app.core.security import get_password_hash
from app.models.user import User
# Create admin user with secure password
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check service health
curl https://yourdomain.com/api/health
curl https://yourdomain.com/api/ai/health

# Monitor container status
docker-compose -f docker-compose.prod.yml ps
```

### Log Management

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f ai-agent

# Configure log rotation
# Add to /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/var/backups/energy-defense"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T postgres pg_dump \
  -U energydefense_prod \
  energy_defense_prod \
  | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Backup configuration
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
  .env docker-compose.prod.yml nginx/

# Keep last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### Updates & Rollback

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Rollback if needed
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Security Hardening

### Firewall Configuration

```bash
# UFW firewall rules
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw enable
```

### Fail2Ban Configuration

```bash
# Install fail2ban
apt-get install fail2ban

# Configure for nginx
cat > /etc/fail2ban/jail.local <<EOF
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
```

### Docker Security

```bash
# Run as non-root
# Configure in Dockerfile
USER appuser

# Use security options
docker-compose run --security-opt="no-new-privileges:true" backend

# Enable AppArmor/SELinux
```

## Performance Tuning

### PostgreSQL

```sql
-- Optimize for production
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_connections = 100;
```

### Application

- Enable connection pooling
- Configure caching strategies
- Optimize database queries
- Use CDN for static assets

## Monitoring & Alerting

### Prometheus + Grafana Setup

```yaml
# Add to docker-compose.prod.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
```

### Key Metrics to Monitor

- CPU and memory usage
- Database connections
- API response times
- Error rates
- Authentication failures
- Disk space usage

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check database credentials
   - Verify network connectivity
   - Review PostgreSQL logs

2. **AI Agent timeouts**
   - Check OpenRouter API key
   - Verify network connectivity
   - Review timeout settings

3. **Frontend not loading**
   - Check VITE_API_URL configuration
   - Verify nginx configuration
   - Review browser console

### Debug Mode

```bash
# Enable debug logging
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "from app.core.config import settings; settings.LOG_LEVEL='DEBUG'"
```

## Compliance & Audit

- Regular security audits
- Dependency vulnerability scanning
- Access log review
- Compliance reporting
- Incident response procedures

---

**Note**: This is a reference implementation. Adjust based on your specific infrastructure and security requirements.
