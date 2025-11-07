# 492-Energy-Defense

## AI-Driven Cybersecurity Defense System for the Energy Sector

A comprehensive, containerized demonstration system showcasing how AI-driven analytics can assist in cybersecurity defense for critical energy infrastructure. This system implements a full-stack, role-based security operations center (SOC) environment with real-time threat monitoring, vulnerability analysis, and AI-powered threat correlation.

![System Architecture](docs/architecture-diagram.png)

## 🌟 Features

### Multi-Service Architecture
- **PostgreSQL Database**: Live data backend with structured security tables
- **FastAPI Backend**: Modular API service with JWT authentication
- **AI Agent Service**: OpenRouter-powered analysis with configurable weighting
- **React Frontend**: Role-based dashboard with real-time monitoring
- **Data Simulator**: Continuous SOC environment data generation

### Role-Based Access Control (RBAC)
- **Admin**: Full system access, AI weight configuration, user management
- **Analyst**: Data analysis, AI query submission, feedback provision
- **Observer**: Read-only dashboard access, monitoring capabilities

### Security Features
- JWT-based authentication and authorization
- Input validation and sanitization
- Database-level access policies
- Audit logging for all system changes
- Least privilege access enforcement

### AI-Powered Analysis
- Threat correlation and pattern detection
- Risk assessment and scoring
- Anomaly detection in security events
- Trend analysis and incident prediction
- Configurable weighting mechanisms (Admin only)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (v2.0+)
- OpenRouter API key (for AI features)
- 4GB+ available RAM
- Linux/macOS/Windows with WSL2

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 492-Energy-Defense
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key and secure secrets
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Credentials

```
Admin:    username: admin     | password: demo123
Analyst:  username: analyst1  | password: demo123
Observer: username: observer1 | password: demo123
```

## 📋 System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Dashboard                       │
│          (React + Tailwind CSS + React Router)              │
│           Role-based UI (Admin/Analyst/Observer)             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST
┌────────────────────────┴────────────────────────────────────┐
│                    FastAPI Backend API                       │
│  • JWT Authentication   • Input Validation                   │
│  • RBAC Middleware     • Data Ingestion                     │
│  • Query Aggregation   • Audit Logging                      │
└──────┬─────────────────┴─────────────────┬─────────────────┘
       │                                    │
       │ PostgreSQL                         │ HTTP/REST
       │                                    │
┌──────┴────────────────────┐      ┌──────┴─────────────────┐
│   PostgreSQL Database      │      │   AI Agent Service      │
│  • Security Event Tables   │      │  • OpenRouter Client    │
│  • User & Role Tables      │      │  • Analysis Engine      │
│  • AI Analysis Storage     │      │  • Caching Layer        │
│  • Audit Logs              │      │  • Weight Management    │
└───────────────────────────┘      └────────────────────────┘
                                             │
                         ┌───────────────────┴──────────────┐
                         │   Data Ingestion Simulator        │
                         │  • Auth Events   • Patches        │
                         │  • Vulnerabilities • Firewall     │
                         └──────────────────────────────────┘
```

### Data Flow

1. **Authentication**: User logs in → JWT token issued → Token validated on each request
2. **Data Ingestion**: Simulator generates → Backend validates → PostgreSQL stores
3. **AI Analysis**: User requests analysis → Backend forwards → AI Agent processes → Results cached and stored
4. **Dashboard Updates**: Frontend polls → Backend aggregates → Real-time display

## 🔐 Security Implementation

### Authentication & Authorization
- JWT tokens with configurable expiration
- Role-based middleware enforcement
- Password hashing with bcrypt
- Session management with refresh tokens

### Input Validation
- Pydantic schema validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in frontend
- CSRF token implementation

### Database Security
- Parameterized queries only
- Connection pooling with limits
- Row-level security policies
- Encrypted connections in production

### Audit & Compliance
- All actions logged with timestamps
- User activity tracking
- Configuration change history
- Failed authentication monitoring

## 📊 AI Agent Configuration

### Weight Configuration (Admin Only)

The AI agent uses configurable weights to influence analysis outputs:

```json
{
  "data_sources": {
    "auth_events": 0.25,
    "patch_levels": 0.20,
    "vulnerability_scans": 0.35,
    "firewall_logs": 0.20
  },
  "threat_indicators": {
    "critical_severity": 1.0,
    "high_severity": 0.8,
    "exploit_available": 1.2,
    "exploited_in_wild": 1.5
  },
  "temporal_factors": {
    "last_hour": 1.5,
    "last_day": 1.2,
    "last_week": 1.0
  }
}
```

### Analysis Types

1. **Threat Correlation**: Identifies patterns across multiple data sources
2. **Risk Assessment**: Evaluates overall security posture
3. **Anomaly Detection**: Flags unusual patterns
4. **Trend Analysis**: Identifies emerging threats
5. **Incident Prediction**: Forecasts potential security events

## 🛠️ Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Dashboard Endpoints

- `GET /api/v1/dashboard/summary` - System overview
- `GET /api/v1/dashboard/auth-events` - Authentication events
- `GET /api/v1/dashboard/vulnerabilities` - Vulnerability scans
- `GET /api/v1/dashboard/firewall-logs` - Firewall logs
- `GET /api/v1/dashboard/patch-levels` - Patch compliance

### Data Ingestion Endpoints

- `POST /api/v1/ingest/auth-events` - Ingest auth events
- `POST /api/v1/ingest/vulnerabilities` - Ingest vulnerability data
- `POST /api/v1/ingest/firewall-logs` - Ingest firewall logs
- `POST /api/v1/ingest/patch-levels` - Ingest patch data

### AI Agent Endpoints

- `POST /api/v1/ai/analyze` - Request AI analysis
- `POST /api/v1/ai/analyze/feedback/{id}` - Submit feedback
- `GET /api/v1/ai/weights` - Get weight configurations
- `POST /api/v1/ai/weights` - Create weight config (Admin)
- `PUT /api/v1/ai/weights/{id}/activate` - Activate config (Admin)

Full API documentation available at: http://localhost:8000/docs

## 🐳 Docker Deployment

### Services

- **postgres**: PostgreSQL 16 with persistent storage
- **backend**: FastAPI application server
- **ai-agent**: AI analysis service
- **frontend**: React development server
- **data-simulator**: Continuous data generation

### Production Deployment

For production deployment, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

Key considerations:
- Use production-grade secrets
- Enable HTTPS/TLS
- Configure rate limiting
- Set up monitoring and alerting
- Implement backup strategies

## 📦 Technology Stack

### Backend
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM with async support
- **PostgreSQL**: Robust relational database
- **Pydantic**: Data validation
- **Python-JOSE**: JWT implementation

### Frontend
- **React 18**: UI library
- **Tailwind CSS**: Utility-first styling
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Recharts**: Data visualization

### AI/ML
- **OpenRouter**: LLM API access
- **Custom Weighting Engine**: Configurable analysis
- **File-based Caching**: Performance optimization

### Infrastructure
- **Docker Compose**: Multi-container orchestration
- **Uvicorn**: ASGI server
- **Vite**: Frontend build tool

## 🤝 Contributing

This is a demonstration project. For production use:

1. Implement comprehensive test coverage
2. Add monitoring and observability
3. Configure production-grade secrets management
4. Set up CI/CD pipelines
5. Implement disaster recovery

## 📝 License

This project is for demonstration and educational purposes.

## 🆘 Support

For issues and questions:
1. Check the documentation in `/docs`
2. Review API docs at `/docs` endpoint
3. Check container logs: `docker-compose logs [service]`

## 🔒 Security Notice

This is a **demonstration system**. Before production deployment:
- Change all default credentials
- Use strong, unique secrets
- Enable all security features
- Conduct security audit
- Implement monitoring
- Set up intrusion detection

## 📈 Performance Considerations

- Database connection pooling configured
- AI response caching enabled
- Frontend pagination on large datasets
- Asynchronous processing throughout
- Optimized database indexes

## 🎯 Roadmap

Future enhancements:
- [ ] Machine learning model training
- [ ] Advanced threat intelligence integration
- [ ] Multi-tenant support
- [ ] Mobile application
- [ ] Enhanced reporting capabilities
- [ ] Integration with SIEM systems

---

**Built with ❤️ for energy sector cybersecurity**
