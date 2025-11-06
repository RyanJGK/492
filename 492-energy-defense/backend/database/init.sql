-- Initialize Energy Defense Database
-- Security-hardened schema with RBAC and audit trails

-- Create custom types (names match SQLAlchemy enum class names in lowercase)
CREATE TYPE userrole AS ENUM ('admin', 'analyst', 'observer');
CREATE TYPE severitylevel AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE eventstatus AS ENUM ('pending', 'investigating', 'resolved', 'false_positive');

-- Users table with role-based access
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role userrole NOT NULL DEFAULT 'observer',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Authentication events table
CREATE TABLE IF NOT EXISTS auth_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- login, logout, failed_login, token_refresh
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Patch levels table
CREATE TABLE IF NOT EXISTS patch_levels (
    id SERIAL PRIMARY KEY,
    system_name VARCHAR(255) NOT NULL,
    component_name VARCHAR(255) NOT NULL,
    current_version VARCHAR(100),
    latest_version VARCHAR(100),
    patch_status VARCHAR(50), -- up_to_date, outdated, critical
    severity severitylevel,
    cve_ids TEXT[], -- Array of CVE identifiers
    last_patched TIMESTAMP WITH TIME ZONE,
    next_scheduled_patch TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vulnerability scans table
CREATE TABLE IF NOT EXISTS vulnerability_scans (
    id SERIAL PRIMARY KEY,
    scan_id UUID UNIQUE NOT NULL,
    target_system VARCHAR(255) NOT NULL,
    scan_type VARCHAR(100), -- network, application, infrastructure
    severity severitylevel,
    vulnerability_name VARCHAR(255),
    vulnerability_description TEXT,
    cve_id VARCHAR(50),
    cvss_score DECIMAL(3, 1),
    affected_component VARCHAR(255),
    remediation_steps TEXT,
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status eventstatus DEFAULT 'pending',
    assigned_to INTEGER REFERENCES users(id),
    metadata JSONB
);

-- Firewall logs table
CREATE TABLE IF NOT EXISTS firewall_logs (
    id SERIAL PRIMARY KEY,
    log_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_ip INET NOT NULL,
    destination_ip INET NOT NULL,
    source_port INTEGER,
    destination_port INTEGER,
    protocol VARCHAR(20), -- TCP, UDP, ICMP
    action VARCHAR(20), -- allow, deny, drop
    rule_id VARCHAR(100),
    packet_size INTEGER,
    flags TEXT,
    severity severitylevel,
    threat_indicator BOOLEAN DEFAULT false,
    country_code VARCHAR(5),
    metadata JSONB
);

-- AI Agent analysis results
CREATE TABLE IF NOT EXISTS ai_analysis (
    id SERIAL PRIMARY KEY,
    analysis_id UUID UNIQUE NOT NULL,
    analysis_type VARCHAR(100), -- threat_correlation, risk_assessment, anomaly_detection
    input_data JSONB NOT NULL,
    ai_response TEXT,
    confidence_score DECIMAL(5, 4), -- 0.0000 to 1.0000
    threat_level severitylevel,
    recommendations TEXT,
    data_sources TEXT[], -- Which tables/sources were analyzed
    weight_configuration JSONB, -- Snapshot of weights used for this analysis
    model_version VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    reviewed BOOLEAN DEFAULT false,
    reviewed_by INTEGER REFERENCES users(id),
    review_timestamp TIMESTAMP WITH TIME ZONE
);

-- AI Agent weighting configuration (Admin only)
CREATE TABLE IF NOT EXISTS ai_weight_config (
    id SERIAL PRIMARY KEY,
    config_name VARCHAR(255) UNIQUE NOT NULL,
    config_version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT false,
    weights JSONB NOT NULL, -- JSON object with weight parameters
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- Analyst feedback on AI accuracy
CREATE TABLE IF NOT EXISTS ai_feedback (
    id SERIAL PRIMARY KEY,
    analysis_id UUID REFERENCES ai_analysis(analysis_id),
    analyst_id INTEGER REFERENCES users(id),
    accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 5),
    is_accurate BOOLEAN,
    false_positive BOOLEAN,
    false_negative BOOLEAN,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for compliance and traceability
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    changes JSONB,
    ip_address INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_auth_events_user_id ON auth_events(user_id);
CREATE INDEX idx_auth_events_timestamp ON auth_events(timestamp);
CREATE INDEX idx_patch_levels_severity ON patch_levels(severity);
CREATE INDEX idx_vuln_scans_severity ON vulnerability_scans(severity);
CREATE INDEX idx_vuln_scans_status ON vulnerability_scans(status);
CREATE INDEX idx_firewall_logs_timestamp ON firewall_logs(log_timestamp);
CREATE INDEX idx_firewall_logs_source_ip ON firewall_logs(source_ip);
CREATE INDEX idx_firewall_logs_threat ON firewall_logs(threat_indicator);
CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);
CREATE INDEX idx_ai_analysis_created_at ON ai_analysis(created_at);

-- Create trigger for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patch_levels_updated_at BEFORE UPDATE ON patch_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_weight_config_updated_at BEFORE UPDATE ON ai_weight_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION)
-- Password hash generated with bcrypt
-- IMPORTANT: Generate fresh hash with: docker-compose exec backend python3 generate-password-hash.py
-- Or manually: python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('admin123'))"
INSERT INTO users (username, email, hashed_password, role) VALUES
    ('admin', 'admin@energy-defense.local', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin'),
    ('analyst', 'analyst@energy-defense.local', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'analyst'),
    ('observer', 'observer@energy-defense.local', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'observer')
ON CONFLICT (username) DO NOTHING;

-- Insert default AI weight configuration
INSERT INTO ai_weight_config (config_name, is_active, weights, description, created_by) VALUES
    ('default', true, '{
        "firewall_threat_weight": 0.35,
        "vulnerability_severity_weight": 0.30,
        "patch_criticality_weight": 0.20,
        "auth_anomaly_weight": 0.15,
        "confidence_threshold": 0.70,
        "severity_multipliers": {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.50,
            "low": 0.25,
            "info": 0.10
        }
    }', 'Default AI weighting configuration for threat analysis', 1)
ON CONFLICT (config_name) DO NOTHING;

-- Create database roles for RBAC
-- These roles can be used in production for fine-grained access control
CREATE ROLE observer_role;
CREATE ROLE analyst_role;
CREATE ROLE admin_role;

-- Grant appropriate permissions (principle of least privilege)
GRANT CONNECT ON DATABASE energy_defense TO observer_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_role;
GRANT SELECT, INSERT ON ai_feedback TO analyst_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;

-- Grant usage on sequences for insert operations
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO analyst_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_role;
