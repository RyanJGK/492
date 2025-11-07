# Energy SOC - AI-Powered Security Operations Center

A realistic AI-powered SOC (Security Operations Center) simulation for the energy sector, modeling Puget Sound Energy-style infrastructure for cyber defense and threat analytics.

![Next.js](https://img.shields.io/badge/Next.js-15.0-black)
![React](https://img.shields.io/badge/React-18.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![TensorFlow.js](https://img.shields.io/badge/TensorFlow.js-4.15-orange)
![Supabase](https://img.shields.io/badge/Supabase-2.39-green)

## 🎯 Overview

This system provides a fully functional simulation of an energy-sector AI defense platform that appears "live" while running locally and safely. It demonstrates advanced concepts in cybersecurity, AI/ML threat detection, and real-time data visualization.

### Core Features

- **Role-Based Dashboard**: Admin, Analyst, and Observer views with different capabilities
- **AI Threat Analysis**: TensorFlow.js-powered threat triage and scoring
- **Real-Time Updates**: Live alert feeds using Supabase real-time subscriptions
- **Synthetic Data Generation**: Simulates continuous SOC activity
- **Clean Architecture**: Separation between Data, AI Logic, and Interface layers

## 🏗️ Architecture

### Frontend Layer
- **Framework**: Next.js 15 with React 18
- **Styling**: Tailwind CSS with custom dark theme
- **Charts**: Recharts for data visualization
- **State Management**: React hooks and context

### Backend Layer
- **Database**: Supabase (PostgreSQL)
- **Real-time**: Supabase Realtime subscriptions
- **Edge Functions**: Serverless functions for alert generation and analysis
- **Authentication**: Supabase Auth (optional)

### AI Layer
- **Framework**: TensorFlow.js
- **Model**: Custom neural network for threat scoring
- **Features**: Severity analysis, pattern matching, anomaly detection
- **Configurability**: Admin-adjustable weights and thresholds

## 🚀 Quick Start

### Prerequisites

- Node.js 20.x or later
- npm or yarn
- Supabase account (or run locally with Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd energy-soc
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` with your Supabase credentials:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```

4. **Set up the database**
   
   Run the SQL schema in your Supabase project:
   ```bash
   # Using Supabase CLI
   supabase db push
   
   # Or manually execute supabase/schema.sql in Supabase Studio
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```

6. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker only

```bash
# Build the image
docker build -t energy-soc .

# Run the container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_SUPABASE_URL=your_url \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key \
  energy-soc
```

## 📚 User Roles

### Admin View
- **Full Control**: Configure AI model weights and thresholds
- **System Management**: Adjust detection sensitivity
- **Real-time Monitoring**: View all alerts and system metrics
- **Access**: Complete view of all SOC operations

### Analyst View
- **Investigation**: Analyze and triage security alerts
- **AI Evaluation**: Review AI threat scores and recommendations
- **Status Management**: Update alert status (investigating, resolved, false positive)
- **Access**: Full read/write on alerts, read-only on configuration

### Observer View
- **Monitoring**: Read-only dashboard for management and reporting
- **Trends**: View charts and statistics
- **Activity Feed**: Live view of security events
- **Access**: Complete read-only access

## 🔧 Configuration

### AI Model Weights

Admins can adjust these weights to tune threat detection:

- **Severity Weight** (default: 0.30): Impact of alert severity
- **Frequency Weight** (default: 0.15): How often similar alerts occur
- **Source Reputation Weight** (default: 0.25): Trustworthiness of source
- **Pattern Match Weight** (default: 0.20): Match against known attack patterns
- **Anomaly Score Weight** (default: 0.10): Statistical anomaly detection

### Threat Thresholds

- **Critical Threshold** (0.80): Auto-escalation point
- **High Threshold** (0.60): Requires immediate attention
- **Medium Threshold** (0.40): Standard investigation
- **Auto Escalate Threshold** (0.85): Automatic senior analyst notification

## 📊 Database Schema

### Core Tables

1. **alerts**: Security alerts with AI scoring
2. **security_logs**: Raw security event logs
3. **vulnerabilities**: Known vulnerabilities and CVEs
4. **patches**: Available and deployed patches
5. **ai_analysis**: AI threat analysis results
6. **ai_model_weights**: Configuration for AI models
7. **threat_intelligence**: Threat indicators and IOCs
8. **system_metrics**: Performance and health metrics

## 🔄 Real-Time Features

### Supabase Realtime Subscriptions

The dashboard uses Supabase realtime subscriptions for:

- **New Alerts**: Instant notification of new security events
- **Alert Updates**: Live status changes
- **System Metrics**: Continuous performance monitoring

### Mock Data Mode

If Supabase is not configured, the system automatically falls back to mock data generation:

- Synthetic alerts every 15 seconds
- System metrics updates every 10 seconds
- Full simulation of live SOC environment

## 🧪 Supabase Edge Functions

### generate-alerts

Periodically generates synthetic security alerts:

```bash
# Deploy function
supabase functions deploy generate-alerts

# Invoke function
curl -X POST 'https://your-project.supabase.co/functions/v1/generate-alerts' \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

### analyze-threats

Performs AI analysis on alerts:

```bash
# Deploy function
supabase functions deploy analyze-threats

# Invoke function
curl -X POST 'https://your-project.supabase.co/functions/v1/analyze-threats' \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"alert_id": "uuid-here"}'
```

## 🛠️ Development

### Project Structure

```
energy-soc/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main dashboard page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── views/            # Role-specific views
│   │   ├── AdminView.tsx
│   │   ├── AnalystView.tsx
│   │   └── ObserverView.tsx
│   ├── AlertCard.tsx
│   ├── StatsCard.tsx
│   ├── DashboardLayout.tsx
│   └── RoleSelector.tsx
├── lib/                   # Core libraries
│   ├── ai-agent.ts       # TensorFlow AI agent
│   ├── supabase.ts       # Supabase client
│   ├── types.ts          # TypeScript types
│   ├── mock-data.ts      # Mock data generators
│   └── utils.ts          # Utility functions
├── hooks/                 # Custom React hooks
│   ├── useRealtimeAlerts.ts
│   └── useRealtimeMetrics.ts
├── supabase/             # Supabase configuration
│   ├── schema.sql        # Database schema
│   └── functions/        # Edge functions
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose config
└── README.md            # This file
```

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🔒 Security Best Practices

### Environment Variables

Never commit `.env.local` or expose sensitive keys:

```env
# ❌ DO NOT commit these
SUPABASE_SERVICE_ROLE_KEY=xxx
SUPABASE_ACCESS_TOKEN=xxx

# ✅ Safe to expose (client-side)
NEXT_PUBLIC_SUPABASE_URL=xxx
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### Row Level Security (RLS)

Enable RLS in production:

```sql
-- Enable RLS on sensitive tables
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_model_weights ENABLE ROW LEVEL SECURITY;

-- Create policies based on user roles
CREATE POLICY "Admins have full access" ON alerts
  FOR ALL USING (auth.jwt()->>'role' = 'admin');
```

## 📈 Performance Optimization

### TensorFlow.js

- Uses WebGL backend for GPU acceleration
- Model is loaded once and cached
- Batch processing for multiple alerts

### Real-time Subscriptions

- Connection pooling with Supabase
- Automatic reconnection on disconnect
- Throttled updates (max 10 events/second)

### React Optimization

- Memoized components
- Lazy loading for charts
- Virtual scrolling for large lists

## 🧩 Extending the System

### Adding New Alert Types

1. Update `ALERT_TYPES` in `lib/mock-data.ts`
2. Add corresponding descriptions
3. Update AI pattern matching in `lib/ai-agent.ts`

### Custom AI Models

Replace the default TensorFlow model:

```typescript
// In lib/ai-agent.ts
async initialize() {
  // Load your custom model
  this.model = await tf.loadLayersModel('path/to/model.json')
}
```

### Additional Views

Create new views in `components/views/`:

```typescript
export default function CustomView() {
  // Your custom view implementation
}
```

## 🤝 Contributing

This is a simulation project for educational and demonstration purposes. Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Puget Sound Energy infrastructure
- Built with Next.js, TensorFlow.js, and Supabase
- Security concepts from NIST Cybersecurity Framework
- ICS/SCADA protocols: DNP3, MODBUS, IEC 61850

## 📧 Support

For questions or issues:

1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🗺️ Roadmap

- [ ] Multi-tenancy support
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Integration with real threat intelligence feeds
- [ ] Mobile responsive dashboard
- [ ] Export reports (PDF, CSV)
- [ ] Incident response playbooks
- [ ] Integration with SIEM systems
- [ ] Compliance reporting (NERC CIP, IEC 62443)

---

**Built with ❤️ for the energy sector cybersecurity community**
