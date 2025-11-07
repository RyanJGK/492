# 492-Energy-Defense: AI-Powered Energy Sector Cybersecurity Demo

A comprehensive, containerized cybersecurity demonstration system that simulates realistic threat scenarios against energy sector infrastructure. The system uses TensorFlow-based anomaly detection to analyze pre-recorded attack scenarios and provides role-based dashboards for security operations center (SOC) analysts.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104-green.svg)

## 🎯 Features

### Core Capabilities
- **AI-Powered Threat Detection**: TensorFlow models (Isolation Forest, LSTM Autoencoder, Gradient Boosting) detect anomalies in real-time
- **Pre-recorded Attack Scenarios**: 5 realistic cybersecurity scenarios based on real-world threats
- **Role-Based Access Control**: Three user roles (Admin, Analyst, Observer) with granular permissions
- **Interactive Dashboard**: Real-time threat visualization with Recharts
- **Data Replay System**: Load and replay attack scenarios at configurable speeds
- **Feedback Loop**: Analysts can mark false positives to improve model accuracy
- **Fully Containerized**: Docker Compose orchestration for easy deployment

### Attack Scenarios
1. **SCADA Brute Force Attack**: 847 failed logins targeting supervisory control systems
2. **EternalBlue Vulnerability**: Unpatched Windows servers leading to lateral movement
3. **DNS Tunneling**: 1.2 GB data exfiltration over 6 days
4. **Port Scan Reconnaissance**: Systematic scanning of OT network infrastructure
5. **Phishing Campaign**: Credential harvesting with subsequent SCADA access

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL
- **AI/ML**: TensorFlow 2.15, scikit-learn
- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts
- **Authentication**: JWT tokens with bcrypt password hashing
- **Containerization**: Docker, Docker Compose

### System Components

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  React Frontend │◄────►│  FastAPI Backend│◄────►│   PostgreSQL    │
│  (Port 3000)    │      │   (Port 8000)   │      │   (Port 5432)   │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │                 │
                         │  TensorFlow     │
                         │  AI Models      │
                         │                 │
                         └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 16GB RAM (recommended)
- 10GB free disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/492-energy-defense.git
   cd 492-energy-defense
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and update passwords/secrets
   ```

3. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

4. **Wait for services to initialize** (30-60 seconds)
   - PostgreSQL: Initializing database schema
   - Backend: Loading AI models
   - Frontend: Building React application

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Credentials

| Role     | Username   | Password     | Permissions                              |
|----------|------------|--------------|------------------------------------------|
| Admin    | admin      | admin123     | Full access + configuration management   |
| Analyst  | analyst    | analyst123   | Read access + feedback submission        |
| Observer | observer   | observer123  | Read-only access to dashboards           |

## 📊 Usage Guide

### 1. Initial Setup

After logging in as **admin**, go to **Configuration** page:

1. Click **"Load All Scenarios"** to populate the database with attack data
2. Wait for data import to complete (~30 seconds)
3. Navigate to **Dashboard** to view threat overview

### 2. Running AI Analysis

**Method 1: Automatic (Recommended)**
- Dashboard auto-refreshes every 30 seconds
- AI analysis runs automatically on new data

**Method 2: Manual**
1. Go to **AI Insights** page
2. Click **"Run Analysis"** button
3. Review results and threat levels

### 3. Investigating Threats

**Authentication Events**
- View failed login attempts
- Filter by suspicious activity
- Track geographic anomalies

**Network Traffic**
- Monitor data transfer volumes
- Identify threat indicators
- Analyze protocol patterns

**Vulnerabilities**
- Review CVE scan results
- Prioritize by CVSS score
- Track remediation status

### 4. Submitting Feedback (Analyst/Admin)

1. Navigate to **AI Insights**
2. Click **"Submit Feedback"** on any analysis
3. Mark as false positive or confirmed
4. Add optional notes
5. System learns from feedback

### 5. Adjusting Model Weights (Admin Only)

1. Go to **Configuration** page
2. Select model category (Authentication/Network/Vulnerability)
3. Adjust feature importance sliders
4. Changes apply immediately to future analyses

## 🔧 Configuration

### Environment Variables

```bash
# Database
DB_PASSWORD=SecureDefense2024!

# Security
JWT_SECRET=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Data Replay
REPLAY_SPEED=100  # 100x faster than real-time
```

### Model Configuration

Feature weights can be adjusted via API or admin panel:

**Authentication Weights**
- `failed_login_rate`: 0.35 (default)
- `geo_velocity`: 0.25
- `time_anomaly`: 0.20
- `enumeration_score`: 0.20

**Network Weights**
- `data_volume`: 0.30
- `connection_pattern`: 0.25
- `port_entropy`: 0.25
- `protocol_anomaly`: 0.20

**Vulnerability Weights**
- `cvss_score`: 0.40
- `days_unpatched`: 0.30
- `exploit_available`: 0.20
- `asset_criticality`: 0.10

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

### Manual Testing

1. **Authentication Flow**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

2. **Get Dashboard Data**
   ```bash
   curl http://localhost:8000/api/analyze/dashboard \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Run Anomaly Detection**
   ```bash
   curl -X POST http://localhost:8000/api/analyze/anomaly \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "start_date": "2024-11-01T00:00:00",
       "end_date": "2024-11-02T00:00:00",
       "event_type": "auth"
     }'
   ```

## 📁 Project Structure

```
492-energy-defense/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection
│   ├── models/
│   │   ├── database.py        # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── events.py          # Event query endpoints
│   │   ├── analysis.py        # AI analysis endpoints
│   │   └── admin.py           # Admin configuration
│   ├── services/
│   │   ├── ai_model.py        # TensorFlow model service
│   │   └── data_replay.py     # Dataset replay service
│   ├── middleware/
│   │   └── rbac.py            # Role-based access control
│   ├── tests/
│   │   └── test_api.py        # API tests
│   ├── generate_datasets.py   # Dataset generator
│   ├── train_models.py        # Model training script
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/          # Login components
│   │   │   ├── layout/        # Navigation components
│   │   │   ├── charts/        # Recharts visualizations
│   │   │   └── tables/        # Data table components
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AuthEvents.tsx
│   │   │   ├── NetworkAnalysis.tsx
│   │   │   ├── Vulnerabilities.tsx
│   │   │   ├── AIInsights.tsx
│   │   │   └── AdminConfig.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.tsx    # Authentication hook
│   │   ├── services/
│   │   │   └── api.ts         # API client
│   │   ├── types/
│   │   │   └── index.ts       # TypeScript types
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── package.json
│   └── tailwind.config.js
├── datasets/                   # Generated CSV files
├── models/                     # Pre-trained TensorFlow models
├── docker-compose.yml
├── .env
└── README.md
```

## 🔐 Security Considerations

### For Production Deployment

1. **Change Default Credentials**
   ```bash
   # Update in backend/init.sql
   # Use strong, unique passwords for each user
   ```

2. **Update JWT Secret**
   ```bash
   # Generate secure random key
   openssl rand -hex 32
   ```

3. **Enable HTTPS**
   - Add reverse proxy (nginx/traefik)
   - Configure SSL certificates
   - Update CORS settings

4. **Database Security**
   - Use strong PostgreSQL password
   - Restrict network access
   - Enable connection encryption

5. **Rate Limiting**
   - Add rate limiting middleware
   - Configure per-endpoint limits
   - Implement IP-based throttling

## 📈 Performance Optimization

### Database Indexing
All critical columns are indexed for fast queries:
- Timestamp fields (for time-range queries)
- Source/destination IPs
- Threat indicators
- CVE IDs

### Query Optimization
- Pagination on all list endpoints (default: 100 records)
- Efficient date range filtering
- Bulk insert for data replay

### Frontend Performance
- React Query caching (30s TTL)
- Virtualized tables for large datasets
- Lazy loading of chart components

## 🐛 Troubleshooting

### Issue: "Connection refused" errors
**Solution**: Wait for all services to fully start (~60 seconds)
```bash
docker-compose logs -f
```

### Issue: Database connection errors
**Solution**: Check PostgreSQL is healthy
```bash
docker-compose ps
docker-compose restart postgres
```

### Issue: AI models not loading
**Solution**: Train models manually
```bash
docker-compose exec backend python train_models.py
```

### Issue: Frontend build errors
**Solution**: Clear npm cache and rebuild
```bash
docker-compose down -v
docker-compose up --build
```

## 📚 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**Authentication**
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh access token

**Events**
- `GET /api/events/auth` - Authentication events
- `GET /api/events/network` - Network traffic logs
- `GET /api/events/patches` - Patch status records
- `GET /api/events/vulnerabilities` - CVE scan results
- `GET /api/events/stats` - Aggregated statistics

**Analysis**
- `POST /api/analyze/anomaly` - Run anomaly detection
- `GET /api/analyze/threats` - Get threat analysis
- `POST /api/analyze/feedback` - Submit feedback
- `GET /api/analyze/dashboard` - Dashboard summary
- `POST /api/analyze/run-all-analysis` - Run all analyses

**Admin** (Admin only)
- `GET /api/config/model-weights` - Get model weights
- `PUT /api/config/model-weights` - Update weights
- `GET /api/config/replay-status` - Data replay status
- `POST /api/config/replay-control` - Control replay
- `GET /api/config/system-info` - System information

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MITRE ATT&CK framework for threat modeling
- NIST Cybersecurity Framework
- ICS-CERT advisories for energy sector threats
- Open-source community for excellent tools

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@energydefense.local
- Documentation: https://docs.energydefense.local

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Real-time data streaming (Apache Kafka)
- [ ] Advanced LSTM models for time-series prediction
- [ ] Integration with SIEM systems (Splunk, ELK)
- [ ] Mobile app for SOC alerts
- [ ] Multi-tenant support
- [ ] Custom scenario builder
- [ ] Automated incident response playbooks

---

**Built with ❤️ for energy sector cybersecurity**
