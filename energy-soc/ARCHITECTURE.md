# Energy SOC - System Architecture

This document provides an in-depth view of the system architecture, design decisions, and implementation details.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Data Flow](#data-flow)
4. [AI/ML Pipeline](#aiml-pipeline)
5. [Real-Time System](#real-time-system)
6. [Security Considerations](#security-considerations)
7. [Scalability](#scalability)

## System Overview

The Energy SOC is a three-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Interface Layer                       │
│              (Next.js / React Frontend)                  │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐        │
│  │   Admin   │  │ Analyst  │  │   Observer   │        │
│  │   View    │  │   View   │  │     View     │        │
│  └───────────┘  └──────────┘  └──────────────┘        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                     AI Logic Layer                       │
│              (TensorFlow.js Agent)                       │
│  ┌─────────────────────────────────────────────┐       │
│  │  Threat Analysis │ Feature Extraction │     │       │
│  │  Pattern Match   │ Anomaly Detection  │     │       │
│  └─────────────────────────────────────────────┘       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                     Data Layer                           │
│                   (Supabase)                             │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │PostgreSQL│  │   Realtime  │  │Edge Functions│      │
│  │ Database │  │Subscriptions│  │   (Deno)     │      │
│  └──────────┘  └─────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. Interface Layer (Frontend)

**Technology Stack**:
- Next.js 15 (App Router)
- React 18 with hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Recharts for data visualization

**Components**:

```
app/
├── layout.tsx          # Root layout with global styles
├── page.tsx            # Main dashboard controller
└── globals.css         # Global styles and theme

components/
├── DashboardLayout.tsx # Dashboard wrapper
├── RoleSelector.tsx    # Role switching component
├── AlertCard.tsx       # Individual alert display
├── StatsCard.tsx       # Statistics card
└── views/
    ├── AdminView.tsx   # Admin interface
    ├── AnalystView.tsx # Analyst interface
    └── ObserverView.tsx# Observer interface
```

**Design Patterns**:

1. **Composition**: Components built from smaller, reusable pieces
2. **Container/Presenter**: Views handle logic, components handle display
3. **Custom Hooks**: Reusable logic for data fetching and subscriptions
4. **Controlled Components**: Form inputs managed by React state

### 2. AI Logic Layer

**Technology Stack**:
- TensorFlow.js 4.15
- WebGL backend for GPU acceleration
- Custom neural network architecture

**Architecture**:

```typescript
class ThreatAnalysisAgent {
  // Neural network model
  private model: tf.LayersModel
  
  // Configuration
  private weights: AIModelWeights
  
  // Feature extraction
  extractFeatures(alert: Alert): number[]
  
  // Threat scoring
  analyzeAlert(alert: Alert): Promise<AIAnalysis>
  
  // Model updates
  updateWeights(weights: AIModelWeights): void
}
```

**Neural Network Architecture**:

```
Input Layer (5 features)
    ↓
Dense Layer (64 units, ReLU)
    ↓
Dropout Layer (20%)
    ↓
Dense Layer (32 units, ReLU)
    ↓
Dense Layer (16 units, ReLU)
    ↓
Output Layer (1 unit, Sigmoid)
    ↓
Threat Score (0-1)
```

**Features Used**:

1. **Severity Score**: Weighted alert severity (critical/high/medium/low)
2. **Source Risk**: Reputation of the alert source
3. **Pattern Match**: Similarity to known attack patterns
4. **Anomaly Score**: Statistical deviation from baseline
5. **Frequency Score**: Rarity of the alert type

### 3. Data Layer

**Technology Stack**:
- Supabase (PostgreSQL 15)
- Realtime subscriptions (WebSocket)
- Edge Functions (Deno runtime)

**Database Schema**:

```sql
-- Core Tables
alerts              (Security alerts with AI scores)
security_logs       (Raw security events)
vulnerabilities     (CVE and vulnerability tracking)
patches             (Patch management)
ai_analysis         (AI analysis results)
ai_model_weights    (Model configuration)
threat_intelligence (Threat indicators)
system_metrics      (Performance monitoring)
```

**Key Design Decisions**:

1. **UUID Primary Keys**: Better for distributed systems
2. **JSONB Metadata**: Flexible storage for varying alert properties
3. **Indexed Columns**: Fast queries on timestamp, severity, status
4. **Triggers**: Auto-update timestamps and maintain consistency
5. **Array Types**: Efficient storage for tags, affected systems

## Data Flow

### Alert Processing Pipeline

```
1. Alert Generation
   ├── Supabase Edge Function (generate-alerts)
   ├── Triggers every 15-30 seconds
   └── Inserts into alerts table

2. Database Insert
   ├── PostgreSQL triggers fire
   ├── Indexes updated
   └── Realtime notification sent

3. Frontend Subscription
   ├── WebSocket receives update
   ├── React state updated
   └── UI re-renders

4. AI Analysis (On-Demand)
   ├── User clicks alert
   ├── TensorFlow.js agent processes
   ├── Features extracted
   ├── Neural network predicts
   └── Results stored in ai_analysis

5. User Action
   ├── Analyst updates status
   ├── Database updated
   ├── Realtime notifies all clients
   └── Dashboard reflects changes
```

### Real-Time Data Flow

```
Supabase Database
    ↓ (INSERT/UPDATE)
Realtime Server
    ↓ (WebSocket)
Frontend Subscription
    ↓ (React State)
UI Update
```

## AI/ML Pipeline

### Training vs Inference

**Current Implementation** (Inference Only):
- Pre-configured neural network
- No training data required
- Deterministic feature extraction
- Configurable weights

**Future Enhancement** (Training Capability):
```
Historical Alerts
    ↓
Feature Engineering
    ↓
Training Dataset
    ↓
Model Training (TensorFlow.js)
    ↓
Model Evaluation
    ↓
Model Deployment
    ↓
Real-time Inference
```

### Feature Engineering

**Severity Weighting**:
```typescript
const severityMap = {
  critical: 1.0,  // Maximum weight
  high: 0.75,     // High priority
  medium: 0.5,    // Moderate
  low: 0.25       // Low priority
}
```

**Source Risk Calculation**:
```typescript
calculateSourceRisk(source: string): number {
  // Check against threat intelligence
  // External sources = higher risk
  // Internal trusted sources = lower risk
  // Returns 0-1 score
}
```

**Pattern Matching**:
```typescript
const attackPatterns = [
  'intrusion', 'malware', 'ransomware',
  'dos', 'ddos', 'unauthorized', 'breach'
]
// Count matches and normalize
```

### Model Configuration

Admin users can adjust these parameters in real-time:

```typescript
interface AIModelWeights {
  weights: {
    severity_weight: number         // 0.30 default
    frequency_weight: number        // 0.15 default
    source_reputation_weight: number // 0.25 default
    pattern_match_weight: number    // 0.20 default
    anomaly_score_weight: number    // 0.10 default
  }
  threshold_settings: {
    critical_threshold: number      // 0.80 default
    high_threshold: number          // 0.60 default
    medium_threshold: number        // 0.40 default
    auto_escalate_threshold: number // 0.85 default
  }
}
```

## Real-Time System

### Supabase Realtime

**Protocol**: WebSocket over HTTP
**Channels**: Separate channels per table
**Events**: INSERT, UPDATE, DELETE

**Implementation**:

```typescript
const channel = supabase
  .channel('alerts-channel')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'alerts'
  }, (payload) => {
    // Handle new alert
  })
  .subscribe()
```

**Reconnection Strategy**:
- Automatic reconnection on disconnect
- Exponential backoff
- State synchronization on reconnect

### Mock Data Mode

When Supabase is unavailable:

```typescript
// Fallback to local generation
const interval = setInterval(() => {
  const newAlert = generateMockAlert()
  setAlerts(prev => [newAlert, ...prev])
}, 15000)
```

**Benefits**:
- Development without Supabase
- Demo mode for presentations
- Testing and validation

## Security Considerations

### Authentication & Authorization

**Current**: Role-based UI switching (no authentication)
**Production**: Enable Supabase Auth

```typescript
// Future implementation
const { data: { user } } = await supabase.auth.getUser()
const role = user?.user_metadata?.role
```

### Row Level Security (RLS)

**Recommended Policies**:

```sql
-- Admins: Full access
CREATE POLICY "admin_all" ON alerts
  FOR ALL USING (auth.jwt()->>'role' = 'admin');

-- Analysts: Read + Update
CREATE POLICY "analyst_read_update" ON alerts
  FOR SELECT, UPDATE 
  USING (auth.jwt()->>'role' IN ('admin', 'analyst'));

-- Observers: Read only
CREATE POLICY "observer_read" ON alerts
  FOR SELECT 
  USING (auth.jwt()->>'role' IN ('admin', 'analyst', 'observer'));
```

### API Security

**Environment Variables**:
- `NEXT_PUBLIC_*`: Safe to expose to client
- `SUPABASE_SERVICE_ROLE_KEY`: Server-side only, never expose

**Rate Limiting**: Supabase provides built-in rate limiting

**CORS**: Configured in edge functions

### Data Sanitization

```typescript
// All user inputs validated
const sanitizedInput = input.replace(/[<>]/g, '')

// SQL injection prevention through parameterized queries
const { data } = await supabase
  .from('alerts')
  .select('*')
  .eq('id', userId) // Parameterized
```

## Scalability

### Horizontal Scaling

**Frontend**:
- Static generation with Next.js
- CDN deployment (Vercel, Netlify)
- Edge caching

**Database**:
- Supabase auto-scales
- Connection pooling
- Read replicas for high traffic

**Edge Functions**:
- Serverless auto-scaling
- Regional deployment
- Cold start optimization

### Performance Optimization

**Frontend**:
```typescript
// Component memoization
const MemoizedAlert = React.memo(AlertCard)

// Lazy loading
const Charts = lazy(() => import('./Charts'))

// Virtual scrolling for large lists
<VirtualList items={alerts} />
```

**Database**:
```sql
-- Strategic indexes
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);

-- Partitioning (future)
CREATE TABLE alerts_2024_01 PARTITION OF alerts
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**AI/ML**:
```typescript
// Batch processing
async analyzeAlerts(alerts: Alert[]) {
  const tensor = tf.tensor2d(
    alerts.map(a => this.extractFeatures(a))
  )
  const predictions = this.model.predict(tensor)
  // Process batch at once
}
```

### Monitoring

**Metrics to Track**:
- Alert processing latency
- AI inference time
- Database query performance
- Real-time connection count
- Memory usage
- CPU utilization

**Implementation**:
```typescript
// Performance monitoring
const startTime = performance.now()
await analyzeAlert(alert)
const duration = performance.now() - startTime

// Store in system_metrics table
await supabase.from('system_metrics').insert({
  ai_processing_time_ms: duration
})
```

## Technology Choices

### Why Next.js?

✅ Server-side rendering for performance
✅ API routes for backend logic
✅ Excellent TypeScript support
✅ Built-in optimization
✅ Large ecosystem

### Why Supabase?

✅ PostgreSQL (battle-tested database)
✅ Real-time subscriptions built-in
✅ RESTful API auto-generated
✅ Edge functions for serverless
✅ Easy local development

### Why TensorFlow.js?

✅ Run ML in browser (no server needed)
✅ GPU acceleration via WebGL
✅ Large model zoo
✅ Active community
✅ Production-ready

### Why TypeScript?

✅ Type safety prevents bugs
✅ Better IDE support
✅ Self-documenting code
✅ Refactoring confidence
✅ Industry standard

## Future Enhancements

### Short-term
- [ ] Add user authentication
- [ ] Implement report exports
- [ ] Add more chart types
- [ ] Mobile responsive design
- [ ] Notification system

### Mid-term
- [ ] Advanced ML models (LSTM, Transformers)
- [ ] Integration with real threat feeds
- [ ] Incident response workflows
- [ ] Compliance reporting
- [ ] Multi-tenancy support

### Long-term
- [ ] Predictive threat modeling
- [ ] Automated incident response
- [ ] Integration with SIEM systems
- [ ] Advanced analytics and forensics
- [ ] Federated learning across utilities

---

**Architecture Version**: 1.0
**Last Updated**: 2024
**Maintained By**: Energy SOC Development Team
