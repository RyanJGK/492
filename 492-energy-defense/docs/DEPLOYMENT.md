# Deployment Guide

## Production Deployment Checklist

### 1. Pre-Deployment

#### Security Configuration
- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Set secure PostgreSQL password
- [ ] Review and restrict CORS origins
- [ ] Configure HTTPS/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable database SSL connections

#### Environment Variables
```bash
# Required Production Variables
POSTGRES_PASSWORD=<secure-password>
SECRET_KEY=<generated-secret>
LOG_LEVEL=INFO
SIMULATION_INTERVAL=60
```

#### Infrastructure
- [ ] Provision servers with adequate resources
  - Backend: 2 CPU, 4GB RAM
  - AI Agent: 4 CPU, 8GB RAM
  - PostgreSQL: 4 CPU, 8GB RAM, 100GB SSD
  - Frontend: 1 CPU, 2GB RAM
- [ ] Configure persistent volumes
- [ ] Set up backup storage
- [ ] Configure monitoring

### 2. Database Setup

#### Initial Setup
```bash
# Create database backup directory
mkdir -p /var/backups/postgres

# Configure automated backups
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

#### Backup Script
```bash
#!/bin/bash
# backup-script.sh
BACKUP_DIR="/var/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U postgres energy_defense > "$BACKUP_DIR/backup_$DATE.sql"
# Keep last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### 3. Docker Deployment

#### Production docker-compose
```yaml
# docker-compose.prod.yml
version: '3.9'
services:
  postgres:
    restart: always
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - /var/lib/postgres/data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
  
  backend:
    restart: always
    environment:
      LOG_LEVEL: INFO
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

#### Deploy
```bash
# Build and deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Verify deployment
docker-compose ps
curl http://localhost:8000/health
```

### 4. Monitoring Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'ai-agent'
    static_configs:
      - targets: ['ai-agent:8001']
```

#### Grafana Dashboards
- System metrics (CPU, memory, disk)
- Application metrics (request rate, latency)
- Database metrics (connections, query performance)
- AI model metrics (inference time, accuracy feedback)

### 5. Log Aggregation

#### ELK Stack Setup
```bash
# elasticsearch
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  elasticsearch:8.11.0

# logstash
docker run -d \
  --name logstash \
  -p 5000:5000 \
  -v ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf \
  logstash:8.11.0

# kibana
docker run -d \
  --name kibana \
  -p 5601:5601 \
  kibana:8.11.0
```

### 6. SSL/TLS Configuration

#### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/energy-defense
server {
    listen 443 ssl http2;
    server_name energy-defense.example.com;

    ssl_certificate /etc/letsencrypt/live/energy-defense.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/energy-defense.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. Scaling

#### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
  
  ai-agent:
    deploy:
      replicas: 2
```

#### Load Balancing
```bash
# Start scaled services
docker-compose up -d --scale backend=3 --scale ai-agent=2
```

### 8. Disaster Recovery

#### Backup Strategy
- **Database**: Daily full backup, hourly incremental
- **Configurations**: Version controlled in Git
- **Logs**: Retained for 90 days
- **AI Models**: Versioned and stored in object storage

#### Recovery Procedure
```bash
# Stop services
docker-compose down

# Restore database
docker-compose up -d postgres
sleep 10
docker-compose exec -T postgres psql -U postgres < backup.sql

# Restart all services
docker-compose up -d
```

### 9. Security Hardening

#### Container Security
```bash
# Run as non-root user (already configured in Dockerfiles)
# Scan for vulnerabilities
docker scan energy-defense-backend:latest

# Use security scanning in CI/CD
# Already configured in GitHub Actions
```

#### Network Security
- Use Docker networks for service isolation
- Restrict external access to necessary ports only
- Implement rate limiting
- Enable fail2ban for brute force protection

### 10. Performance Tuning

#### PostgreSQL Optimization
```sql
-- In postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
```

#### Application Optimization
- Enable connection pooling (already configured)
- Use caching for frequent queries
- Optimize database indexes
- Monitor slow queries

### 11. Maintenance

#### Regular Tasks
- [ ] Weekly: Review logs for errors
- [ ] Weekly: Check disk usage
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review security advisories
- [ ] Quarterly: Load testing
- [ ] Quarterly: Disaster recovery drill

#### Update Procedure
```bash
# 1. Backup
./backup-script.sh

# 2. Pull updates
git pull origin main

# 3. Update containers
docker-compose pull
docker-compose up -d --build

# 4. Verify
curl http://localhost:8000/health

# 5. Rollback if needed
docker-compose down
docker-compose up -d --no-build
```

## Cloud Deployment

### AWS
- Use ECS/EKS for container orchestration
- RDS for PostgreSQL
- S3 for backups and model storage
- CloudWatch for monitoring
- ALB for load balancing

### Azure
- Use AKS for Kubernetes
- Azure Database for PostgreSQL
- Blob Storage for backups
- Application Insights for monitoring
- Application Gateway for load balancing

### Google Cloud
- Use GKE for Kubernetes
- Cloud SQL for PostgreSQL
- Cloud Storage for backups
- Cloud Monitoring
- Cloud Load Balancing

## Support

For production issues:
1. Check logs: `docker-compose logs -f [service]`
2. Verify health: `curl http://localhost:8000/health`
3. Check database: `docker-compose exec postgres psql -U postgres energy_defense`
4. Review audit logs via API: `/api/audit/logs`
