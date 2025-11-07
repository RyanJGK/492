-- Energy SOC Database Schema
-- This schema supports the AI-powered Security Operations Center simulation

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ALERTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'investigating', 'resolved', 'false_positive')),
    ai_score DECIMAL(5,4),
    ai_confidence DECIMAL(5,4),
    assigned_to TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_source ON alerts(source);

-- =====================================================
-- SECURITY LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS security_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type TEXT NOT NULL,
    source_ip INET NOT NULL,
    destination_ip INET,
    protocol TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT NOT NULL,
    severity TEXT NOT NULL,
    raw_log TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_security_logs_timestamp ON security_logs(timestamp DESC);
CREATE INDEX idx_security_logs_source_ip ON security_logs(source_ip);
CREATE INDEX idx_security_logs_event_type ON security_logs(event_type);

-- =====================================================
-- VULNERABILITIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cve_id TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    cvss_score DECIMAL(3,1),
    affected_systems TEXT[] NOT NULL,
    discovered_date TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'patched', 'mitigated', 'accepted')),
    remediation TEXT,
    patch_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulnerabilities_status ON vulnerabilities(status);
CREATE INDEX idx_vulnerabilities_cve_id ON vulnerabilities(cve_id);

-- =====================================================
-- PATCHES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS patches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patch_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    release_date TIMESTAMPTZ NOT NULL,
    applies_to TEXT[] NOT NULL,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'scheduled', 'deployed', 'failed')),
    priority TEXT NOT NULL CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    deployment_date TIMESTAMPTZ,
    vulnerabilities_fixed TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patches_status ON patches(status);
CREATE INDEX idx_patches_priority ON patches(priority);

-- =====================================================
-- AI ANALYSIS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL,
    threat_score DECIMAL(5,4) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    findings TEXT NOT NULL,
    recommendations TEXT[],
    false_positive_probability DECIMAL(5,4),
    related_incidents UUID[],
    model_version TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_analysis_alert_id ON ai_analysis(alert_id);
CREATE INDEX idx_ai_analysis_timestamp ON ai_analysis(timestamp DESC);
CREATE INDEX idx_ai_analysis_threat_score ON ai_analysis(threat_score DESC);

-- =====================================================
-- AI MODEL WEIGHTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS ai_model_weights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT NOT NULL,
    weights JSONB NOT NULL,
    threshold_settings JSONB NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_model_weights_active ON ai_model_weights(is_active);

-- =====================================================
-- THREAT INTELLIGENCE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS threat_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator TEXT NOT NULL,
    indicator_type TEXT NOT NULL CHECK (indicator_type IN ('ip', 'domain', 'hash', 'url', 'email')),
    threat_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    first_seen TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    source TEXT NOT NULL,
    tags TEXT[],
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_threat_intelligence_indicator ON threat_intelligence(indicator);
CREATE INDEX idx_threat_intelligence_type ON threat_intelligence(indicator_type);
CREATE INDEX idx_threat_intelligence_severity ON threat_intelligence(severity);

-- =====================================================
-- SYSTEM METRICS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cpu_usage DECIMAL(5,2) NOT NULL,
    memory_usage DECIMAL(5,2) NOT NULL,
    network_in DECIMAL(10,2) NOT NULL,
    network_out DECIMAL(10,2) NOT NULL,
    active_connections INTEGER NOT NULL,
    threat_events_per_minute INTEGER NOT NULL,
    ai_processing_time_ms DECIMAL(10,2) NOT NULL
);

CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vulnerabilities_updated_at BEFORE UPDATE ON vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patches_updated_at BEFORE UPDATE ON patches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threat_intelligence_updated_at BEFORE UPDATE ON threat_intelligence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate synthetic alerts (simulates live environment)
CREATE OR REPLACE FUNCTION generate_synthetic_alert()
RETURNS void AS $$
DECLARE
    alert_types TEXT[] := ARRAY['Intrusion Detection', 'Malware Detection', 'Unauthorized Access', 'DDoS Attack', 'Port Scan', 'Brute Force Attempt'];
    sources TEXT[] := ARRAY['Firewall-01', 'IDS-Gateway', 'SCADA-Monitor', 'Substation-Alpha', 'Substation-Beta'];
    severities TEXT[] := ARRAY['critical', 'high', 'medium', 'low'];
BEGIN
    INSERT INTO alerts (severity, type, source, description, status, ai_score, ai_confidence, metadata)
    VALUES (
        severities[1 + floor(random() * 4)],
        alert_types[1 + floor(random() * array_length(alert_types, 1))],
        sources[1 + floor(random() * array_length(sources, 1))],
        'Automatically generated security alert',
        'new',
        random(),
        0.6 + (random() * 0.35),
        jsonb_build_object(
            'source_ip', concat('10.', floor(random() * 255)::text, '.', floor(random() * 255)::text, '.', floor(random() * 255)::text),
            'auto_generated', true
        )
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ROW LEVEL SECURITY (Optional - for production)
-- =====================================================

-- Enable RLS on tables
-- ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE security_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ai_analysis ENABLE ROW LEVEL SECURITY;

-- Create policies based on roles
-- CREATE POLICY "Admins have full access to alerts" ON alerts
--     FOR ALL USING (auth.jwt()->>'role' = 'admin');

-- CREATE POLICY "Analysts can view and update alerts" ON alerts
--     FOR SELECT USING (auth.jwt()->>'role' IN ('admin', 'analyst'));

-- CREATE POLICY "Observers can only view alerts" ON alerts
--     FOR SELECT USING (auth.jwt()->>'role' IN ('admin', 'analyst', 'observer'));

-- =====================================================
-- INITIAL DATA SEED (Optional)
-- =====================================================

-- Insert default AI model weights
INSERT INTO ai_model_weights (model_name, weights, threshold_settings, updated_by, is_active)
VALUES (
    'threat_triage_v1',
    '{"severity_weight": 0.30, "frequency_weight": 0.15, "source_reputation_weight": 0.25, "pattern_match_weight": 0.20, "anomaly_score_weight": 0.10}',
    '{"critical_threshold": 0.80, "high_threshold": 0.60, "medium_threshold": 0.40, "auto_escalate_threshold": 0.85}',
    'system',
    true
);

-- Generate some initial sample data
SELECT generate_synthetic_alert() FROM generate_series(1, 10);
