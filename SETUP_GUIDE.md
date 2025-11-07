# Energy Defense - Detailed Setup Guide

This guide provides step-by-step instructions for setting up and running the Energy Defense cybersecurity demo system.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [First-Time Setup](#first-time-setup)
4. [Generating and Loading Data](#generating-and-loading-data)
5. [Training AI Models](#training-ai-models)
6. [Verification](#verification)
7. [Common Issues](#common-issues)

## System Requirements

### Hardware
- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for initial setup

### Software
- **Docker**: 20.10 or later
- **Docker Compose**: 2.0 or later
- **Git**: For cloning the repository

### Operating Systems
- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- macOS (11+)
- Windows 10/11 with WSL2

## Installation Steps

### Step 1: Install Docker

#### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### macOS
```bash
# Install Docker Desktop from
# https://www.docker.com/products/docker-desktop/

# Or use Homebrew
brew install --cask docker
```

#### Windows
1. Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
2. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
3. Enable WSL2 integration in Docker Desktop settings

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/492-energy-defense.git

# Navigate to project directory
cd 492-energy-defense

# Verify directory structure
ls -la
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables (use your preferred editor)
nano .env
# OR
vim .env
```

**Important Environment Variables:**
```bash
# Database password (CHANGE THIS!)
DB_PASSWORD=YourSecurePasswordHere123!

# JWT secret key (GENERATE A NEW ONE!)
JWT_SECRET=your-secret-key-min-32-chars-use-openssl-rand-hex-32

# Data replay speed (100 = 100x faster than real-time)
REPLAY_SPEED=100
```

**Generate secure JWT secret:**
```bash
openssl rand -hex 32
```

## First-Time Setup

### Step 1: Build Docker Images

```bash
# Build all containers (this may take 5-10 minutes)
docker-compose build

# Expected output:
# Building postgres...
# Building backend...
# Building frontend...
```

### Step 2: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Monitor logs
docker-compose logs -f

# Wait for services to be healthy
# You should see:
# - postgres    | database system is ready to accept connections
# - backend     | INFO:     Uvicorn running on http://0.0.0.0:8000
# - frontend    | VITE ready in X ms
```

### Step 3: Verify Services

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                 STATUS
# postgres             Up (healthy)
# backend              Up
# frontend             Up

# Test backend API
curl http://localhost:8000/health

# Test frontend (should return HTML)
curl http://localhost:3000
```

## Generating and Loading Data

### Option 1: Generate Datasets Locally

```bash
# Enter backend container
docker-compose exec backend bash

# Generate datasets
python generate_datasets.py

# Verify datasets were created
ls -lh /workspace/datasets/

# Exit container
exit
```

### Option 2: Use Admin Panel (Recommended)

1. Open browser: http://localhost:3000
2. Login with admin credentials:
   - Username: `admin`
   - Password: `admin123`
3. Navigate to **Configuration** page
4. Click **"Load All Scenarios"**
5. Wait for completion (30-60 seconds)
6. Navigate to **Dashboard** to see data

### Verify Data Loading

```bash
# Check database has records
docker-compose exec postgres psql -U defense_user -d energy_defense -c "SELECT COUNT(*) FROM authentication_events;"
docker-compose exec postgres psql -U defense_user -d energy_defense -c "SELECT COUNT(*) FROM network_logs;"
docker-compose exec postgres psql -U defense_user -d energy_defense -c "SELECT COUNT(*) FROM vulnerability_scans;"
```

## Training AI Models

### Automatic Training (on container start)

Models are trained automatically when backend starts. Check logs:

```bash
docker-compose logs backend | grep "Model training"
```

### Manual Training

```bash
# Enter backend container
docker-compose exec backend bash

# Train all models
python train_models.py

# Verify models were created
ls -lh /app/models/

# Expected files:
# - isolation_forest_auth.pkl
# - lstm_autoencoder_network.h5
# - gradient_boosting_vuln.pkl
# - scalers.pkl

# Exit container
exit
```

## Verification

### 1. Access Frontend
- URL: http://localhost:3000
- Login with any demo credentials
- Should see dashboard with threat overview

### 2. Test API Endpoints
```bash
# Get authentication token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Get dashboard data
curl -s http://localhost:8000/api/analyze/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq

# Get authentication events
curl -s http://localhost:8000/api/events/auth?limit=10 \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 3. Run AI Analysis
1. Login to frontend as `analyst`
2. Go to **AI Insights** page
3. Click **"Run Analysis"**
4. Should see analysis results with threat levels

### 4. Check System Health
```bash
# Check all container health
docker-compose ps

# Check database connections
docker-compose exec postgres psql -U defense_user -d energy_defense -c "\dt"

# Check API health
curl http://localhost:8000/health
```

## Common Issues

### Issue 1: Port Already in Use
```bash
# Error: "port 8000 is already allocated"

# Solution: Stop service using the port
sudo lsof -i :8000
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Issue 2: Database Connection Failed
```bash
# Error: "could not connect to server"

# Solution: Wait for database to be ready
docker-compose logs postgres

# Or restart PostgreSQL
docker-compose restart postgres
docker-compose logs -f postgres
```

### Issue 3: Models Not Loading
```bash
# Error: "Could not load AI models"

# Solution: Train models manually
docker-compose exec backend python train_models.py

# Check models exist
docker-compose exec backend ls -la /app/models/
```

### Issue 4: Frontend Not Loading
```bash
# Error: White screen or connection error

# Solution: Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose down
docker-compose up --build frontend
```

### Issue 5: Out of Memory
```bash
# Error: Container killed (OOM)

# Solution: Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
# Set to at least 8GB, recommended 16GB
```

## Performance Tuning

### Database Optimization
```bash
# Increase PostgreSQL shared_buffers
# Edit docker-compose.yml under postgres:
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_WORK_MEM=64MB
```

### API Performance
```bash
# Increase worker processes
# Edit docker-compose.yml under backend:
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Performance
```bash
# Build production version
cd frontend
npm run build

# Serve with nginx
docker run -p 80:80 -v $(pwd)/dist:/usr/share/nginx/html nginx
```

## Backup and Restore

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U defense_user energy_defense > backup.sql

# With compression
docker-compose exec postgres pg_dump -U defense_user energy_defense | gzip > backup.sql.gz
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T postgres psql -U defense_user energy_defense < backup.sql

# With compression
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U defense_user energy_defense
```

## Next Steps

1. **Explore Dashboard**: Navigate through all pages to understand features
2. **Run Scenarios**: Load different attack scenarios individually
3. **Adjust Weights**: Experiment with model weight configurations
4. **Submit Feedback**: Practice marking false positives
5. **Monitor Performance**: Check system resource usage

For additional help, see:
- Main README.md
- API Documentation: http://localhost:8000/docs
- GitHub Issues: https://github.com/yourusername/492-energy-defense/issues
