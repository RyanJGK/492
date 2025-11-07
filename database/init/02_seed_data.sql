-- Seed data for 492-Energy-Defense
-- Default users with hashed passwords (password: "demo123" for all)
-- In production, use proper password hashing via the application

INSERT INTO users (username, email, hashed_password, role) VALUES
    ('admin', 'admin@energydefense.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEtBem', 'admin'),
    ('analyst1', 'analyst1@energydefense.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEtBem', 'analyst'),
    ('observer1', 'observer1@energydefense.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEtBem', 'observer');

-- Default AI weight configuration
INSERT INTO ai_weight_configs (config_name, description, weights, is_active, created_by) VALUES
    (
        'default',
        'Default weight configuration for AI agent analysis',
        '{
            "data_sources": {
                "auth_events": 0.25,
                "patch_levels": 0.20,
                "vulnerability_scans": 0.35,
                "firewall_logs": 0.20
            },
            "threat_indicators": {
                "critical_severity": 1.0,
                "high_severity": 0.8,
                "medium_severity": 0.5,
                "low_severity": 0.3,
                "exploit_available": 1.2,
                "exploited_in_wild": 1.5
            },
            "temporal_factors": {
                "last_hour": 1.5,
                "last_day": 1.2,
                "last_week": 1.0,
                "older": 0.7
            },
            "asset_criticality": {
                "critical": 1.5,
                "high": 1.2,
                "medium": 1.0,
                "low": 0.8
            }
        }'::jsonb,
        true,
        (SELECT id FROM users WHERE username = 'admin')
    );

-- Sample authentication events
INSERT INTO auth_events (user_id, event_type, ip_address, user_agent, success, risk_score, timestamp) VALUES
    ((SELECT id FROM users WHERE username = 'admin'), 'login_success', '10.0.1.100', 'Mozilla/5.0', true, 5, NOW() - INTERVAL '2 hours'),
    ((SELECT id FROM users WHERE username = 'analyst1'), 'login_success', '10.0.1.101', 'Mozilla/5.0', true, 5, NOW() - INTERVAL '1 hour'),
    ((SELECT id FROM users WHERE username = 'observer1'), 'login_failure', '192.168.1.50', 'curl/7.68.0', false, 65, NOW() - INTERVAL '30 minutes'),
    ((SELECT id FROM users WHERE username = 'analyst1'), 'login_success', '10.0.1.101', 'Mozilla/5.0', true, 5, NOW() - INTERVAL '15 minutes');

-- Sample patch levels data
INSERT INTO patch_levels (asset_id, asset_name, asset_type, operating_system, current_patch_level, latest_patch_level, missing_critical_patches, missing_high_patches, compliance_status, criticality_score) VALUES
    ('SRV-001', 'Primary SCADA Server', 'scada_system', 'Windows Server 2019', '2024.08', '2024.11', 2, 5, 'critical', 95),
    ('SRV-002', 'Secondary SCADA Server', 'scada_system', 'Windows Server 2019', '2024.10', '2024.11', 0, 2, 'at_risk', 80),
    ('NET-001', 'Core Switch', 'network_device', 'Cisco IOS 15.7', '15.7.3', '15.7.4', 0, 1, 'non_compliant', 70),
    ('ICS-001', 'PLC Controller 1', 'ics_component', 'Proprietary', '3.2.1', '3.2.5', 1, 3, 'critical', 90);

-- Sample vulnerability scans
INSERT INTO vulnerability_scans (scan_id, asset_id, asset_name, vulnerability_id, cve_id, severity, cvss_score, title, description, exploit_available, first_detected, last_detected, status, risk_score) VALUES
    ('SCAN-001-001', 'SRV-001', 'Primary SCADA Server', 'VULN-12345', 'CVE-2024-1234', 'critical', 9.8, 'Remote Code Execution in SCADA Interface', 'An unauthenticated remote code execution vulnerability exists in the SCADA web interface.', true, NOW() - INTERVAL '7 days', NOW() - INTERVAL '1 day', 'open', 98),
    ('SCAN-001-002', 'SRV-001', 'Primary SCADA Server', 'VULN-12346', 'CVE-2024-1235', 'high', 8.1, 'SQL Injection in Data Logging Module', 'SQL injection vulnerability allows unauthorized database access.', false, NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 day', 'open', 85),
    ('SCAN-002-001', 'NET-001', 'Core Switch', 'VULN-12347', 'CVE-2024-1236', 'medium', 6.5, 'Default Credentials in Management Interface', 'Default administrative credentials are still active.', false, NOW() - INTERVAL '3 days', NOW() - INTERVAL '6 hours', 'open', 70);

-- Sample firewall logs
INSERT INTO firewall_logs (timestamp, source_ip, source_port, destination_ip, destination_port, protocol, action, threat_detected, threat_type, threat_severity, risk_score) VALUES
    (NOW() - INTERVAL '30 minutes', '203.0.113.45', 45123, '10.0.1.10', 502, 'TCP', 'deny', true, 'port_scan', 'high', 85),
    (NOW() - INTERVAL '25 minutes', '203.0.113.45', 45124, '10.0.1.11', 502, 'TCP', 'deny', true, 'port_scan', 'high', 85),
    (NOW() - INTERVAL '20 minutes', '198.51.100.30', 33445, '10.0.1.10', 22, 'TCP', 'deny', true, 'brute_force', 'critical', 95),
    (NOW() - INTERVAL '15 minutes', '10.0.1.100', 50234, '10.0.1.10', 502, 'TCP', 'allow', false, NULL, NULL, 5),
    (NOW() - INTERVAL '10 minutes', '192.0.2.100', 12345, '10.0.1.10', 502, 'TCP', 'deny', true, 'unauthorized_access', 'high', 90);
