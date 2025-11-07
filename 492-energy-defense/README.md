# 492-Energy-Defense Platform

A production-ready, real-time cybersecurity defense platform demonstrating AI-driven threat analysis for the energy sector. Built with FastAPI, TensorFlow, React, and PostgreSQL.

## 🎯 Overview

492-Energy-Defense is a comprehensive, Dockerized security operations platform that showcases how AI and data-driven analytics enhance cyber defense operations in critical infrastructure environments. The platform features:

- **Live Backend Database**: PostgreSQL with persistent storage and normalized schemas
- **FastAPI Backend**: RESTful API with authentication, data aggregation, and AI integration
- **TensorFlow AI Agent**: Local threat classification with configurable weighting and explainability
- **React Dashboard**: Role-based interactive interface with real-time metrics
- **Data Simulation**: Continuous generation of realistic SOC activity

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│              Role-based Dashboard (Port 3000)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                      │
│          Data Aggregation & Orchestration (8000)            │
└──────┬──────────────────────────────────────┬──────────────┘
       │                                       │
       ▼                                       ▼
┌──────────────────┐              ┌──────────────────────────┐
│  AI Agent (TF)   │              │   PostgreSQL Database    │
│  Port 8001       │              │   Persistent Volumes     │
└──────────────────┘              └──────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 8GB RAM minimum
- 20GB disk space

### 1. Clone and Setup

```bash
cd 492-energy-defense
cp .env.example .env
# Edit .env with your configurations
```

### 2. Launch Platform

```bash
docker-compose up --build
```

Services will be available at:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Agent API**: http://localhost:8001
- **API Documentation**: http://localhost:8000/api/docs

### 3. Access Dashboard

Open http://localhost:3000 in your browser. The platform will automatically start with admin role.

## 🎭 Role-Based Access

The dashboard supports three role views, switchable via the interface:

### 👑 Admin
- Full system access
- Configure AI model weights and sensitivity thresholds
- Submit evaluation feedback on AI flagging
- Access audit logs and system configuration

### 🔬 Analyst
- View all dashboards and alerts
- Submit evaluation feedback on AI flagging accuracy
- Access detailed analysis reports
- View historical trends

### 👁️ Observer
- Read-only access to dashboards
- Monitor real-time metrics
- View summaries and trends
- Presentation-friendly views

## 📊 Key Features

### 1. Real-Time Threat Dashboard
- Live metrics from authentication, vulnerabilities, firewall, and patches
- AI-powered threat scores with confidence levels
- Interactive trend visualizations
- Severity-based alerting

### 2. AI Threat Analysis
- **Configurable Weighting**: Admin users adjust feature importance
- **Explainability**: Detailed reasoning for each threat classification
- **Confidence Scoring**: Model uncertainty quantification
- **Feedback Loop**: Analyst/Admin feedback collection for model refinement

### 3. Data Sources
- **Authentication Events**: Login attempts, failures, suspicious activity
- **Vulnerability Scans**: CVE tracking, CVSS scoring, remediation status
- **Firewall Logs**: Network traffic, blocked IPs, protocol analysis
- **Patch Management**: Critical updates, scheduling, deployment tracking

### 4. Audit Trail
- Complete traceability of all actions
- User activity logging
- Configuration change tracking
- AI decision logging with rationale

## 🧠 AI Model Configuration

The TensorFlow-based threat classifier uses four primary features:

1. **Authentication Events** (default: 30%)
2. **Vulnerability Severity** (default: 35%)
3. **Firewall Anomalies** (default: 25%)
4. **Patch Criticality** (default: 10%)

Admins can adjust these weights through the dashboard. The AI agent:
- Maintains explainability logs
- Provides confidence scores
- Categorizes threats (intrusion, exploitation, anomaly, etc.)
- Suggests remediation actions

## 📁 Project Structure

```
492-energy-defense/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── core/           # Configuration & logging
│   │   ├── db/             # Database models & session
│   │   └── services/       # Data simulation
│   ├── tests/              # pytest suite
│   └── requirements.txt
├── ai-agent/               # TensorFlow AI service
│   ├── app/
│   │   ├── api/            # Analysis endpoints
│   │   ├── ml/             # Model manager
│   │   └── core/           # Configuration
│   ├── tests/              # Model tests
│   └── requirements.txt
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Dashboard page
│   │   └── context/        # State management
│   └── package.json
├── database/               # PostgreSQL schemas
│   └── init.sql            # Schema definitions
├── docker-compose.yml      # Service orchestration
└── README.md
```

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run Backend Tests

```bash
cd backend
pytest -v
```

### AI Agent Development

```bash
cd ai-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

### Backend Tests
```bash
docker-compose exec backend pytest -v --cov=app
```

### AI Agent Tests
```bash
docker-compose exec ai-agent pytest -v --cov=app
```

### Integration Tests
```bash
# Run full integration test suite
./run-integration-tests.sh
```

## 📈 Data Simulation

The platform includes a data simulator that generates realistic security events:

- Configurable interval (default: 30 seconds)
- Realistic IP addresses and user agents
- Multiple severity levels
- Event correlation patterns

Control via environment variable:
```bash
SIMULATION_INTERVAL=60  # seconds
```

## 🔒 Security Considerations

### Production Deployment

1. **Change Default Credentials**
   ```bash
   # In .env file
   POSTGRES_PASSWORD=<strong-password>
   SECRET_KEY=<generated-secret-key>
   ```

2. **Enable TLS/SSL**
   - Configure HTTPS for frontend
   - Use SSL for database connections
   - Implement certificate management

3. **Network Isolation**
   - Use Docker networks for service isolation
   - Expose only necessary ports
   - Implement firewall rules

4. **Input Validation**
   - Already implemented with Pydantic
   - SQL injection protection via SQLAlchemy
   - CORS configuration in place

## 📊 Database Management

### Backup Database
```bash
docker-compose exec postgres pg_dump -U postgres energy_defense > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U postgres energy_defense < backup.sql
```

### Access Database
```bash
docker-compose exec postgres psql -U postgres energy_defense
```

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs backend
docker-compose logs ai-agent
docker-compose logs frontend

# Restart services
docker-compose restart
```

### Database Connection Issues
```bash
# Verify database is healthy
docker-compose ps postgres

# Check database logs
docker-compose logs postgres
```

### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose up --build frontend

# Check if backend is accessible
curl http://localhost:8000/health
```

## 📚 API Documentation

Once running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **AI Agent Docs**: http://localhost:8001/ai/docs

## 🤝 Contributing

This is a demonstration platform. For production deployment:

1. Implement proper authentication/authorization
2. Add comprehensive monitoring (Prometheus, Grafana)
3. Set up log aggregation (ELK stack)
4. Configure backup automation
5. Implement disaster recovery procedures

## 📄 License

This project is for demonstration and educational purposes.

## 🏆 Engineering Standards

Built following:
- **12-Factor App** principles
- **Clean Architecture** patterns
- **Type Safety** with Python type hints and Pydantic
- **Structured Logging** with JSON format
- **Containerization** best practices
- **API-First** design
- **Comprehensive Testing** with pytest and integration tests

## 📧 Support

For issues or questions, consult the API documentation or check the logs for detailed error messages.

---

**Built by senior engineers for production-grade cybersecurity operations.**
