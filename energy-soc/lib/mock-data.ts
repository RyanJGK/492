import { Alert, SecurityLog, Vulnerability, Patch, ThreatIntelligence, SystemMetrics } from './types'

/**
 * Mock data generator for simulating live SOC environment
 * In production, this would be replaced by Supabase edge functions
 */

const ALERT_TYPES = [
  'Intrusion Detection',
  'Malware Detection',
  'Unauthorized Access',
  'DDoS Attack',
  'Port Scan',
  'Brute Force Attempt',
  'Data Exfiltration',
  'Anomalous Network Traffic',
  'Suspicious Login',
  'Configuration Change',
  'SCADA Protocol Violation',
  'ICS Command Injection'
]

const SOURCES = [
  'Firewall-01',
  'IDS-Gateway',
  'SCADA-Monitor',
  'Substation-Alpha',
  'Substation-Beta',
  'Substation-Gamma',
  'Distribution-Controller',
  'External-Perimeter',
  'VPN-Gateway',
  'Authentication-Server'
]

const DESCRIPTIONS = [
  'Multiple failed authentication attempts detected',
  'Suspicious network traffic pattern identified',
  'Unauthorized access attempt to SCADA system',
  'Malicious payload detected in network stream',
  'Abnormal data transfer volume detected',
  'Unknown device attempting connection',
  'Critical system file modification detected',
  'Port scanning activity from external IP',
  'SQL injection attempt on web interface',
  'Privilege escalation attempt detected',
  'Unusual SCADA command sequence',
  'DNP3 protocol anomaly detected'
]

export function generateMockAlert(): Alert {
  const severities: Array<'critical' | 'high' | 'medium' | 'low'> = ['critical', 'high', 'medium', 'low']
  const statuses: Array<'new' | 'investigating' | 'resolved' | 'false_positive'> = ['new', 'investigating', 'resolved', 'false_positive']
  
  // Weight towards new and investigating
  const statusWeighted = Math.random()
  let status: Alert['status']
  if (statusWeighted < 0.4) status = 'new'
  else if (statusWeighted < 0.7) status = 'investigating'
  else if (statusWeighted < 0.9) status = 'resolved'
  else status = 'false_positive'

  return {
    id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
    severity: severities[Math.floor(Math.random() * severities.length)],
    type: ALERT_TYPES[Math.floor(Math.random() * ALERT_TYPES.length)],
    source: SOURCES[Math.floor(Math.random() * SOURCES.length)],
    description: DESCRIPTIONS[Math.floor(Math.random() * DESCRIPTIONS.length)],
    status: status,
    ai_score: Math.random(),
    ai_confidence: 0.6 + Math.random() * 0.35,
    metadata: {
      source_ip: `10.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      destination_port: [22, 80, 443, 3389, 502, 20000][Math.floor(Math.random() * 6)]
    }
  }
}

export function generateMockSecurityLog(): SecurityLog {
  const eventTypes = ['CONNECTION', 'AUTHENTICATION', 'FIREWALL', 'IDS', 'VPN', 'SCADA']
  const actions = ['ALLOW', 'DENY', 'ALERT', 'BLOCK']
  const protocols = ['TCP', 'UDP', 'ICMP', 'DNP3', 'MODBUS', 'IEC104']

  return {
    id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date(Date.now() - Math.random() * 300000).toISOString(),
    event_type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
    source_ip: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    destination_ip: `10.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    protocol: protocols[Math.floor(Math.random() * protocols.length)],
    action: actions[Math.floor(Math.random() * actions.length)],
    details: 'Network event logged',
    severity: ['info', 'warning', 'error'][Math.floor(Math.random() * 3)]
  }
}

export function generateMockVulnerability(): Vulnerability {
  const severities: Array<'critical' | 'high' | 'medium' | 'low'> = ['critical', 'high', 'medium', 'low']
  const statuses: Array<'open' | 'in_progress' | 'patched' | 'mitigated' | 'accepted'> = ['open', 'in_progress', 'patched', 'mitigated', 'accepted']

  return {
    id: `vuln_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    cve_id: `CVE-2024-${Math.floor(10000 + Math.random() * 90000)}`,
    title: 'Security Vulnerability Detected',
    description: 'A security vulnerability has been identified in the system',
    severity: severities[Math.floor(Math.random() * severities.length)],
    cvss_score: 4.0 + Math.random() * 6.0,
    affected_systems: [SOURCES[Math.floor(Math.random() * SOURCES.length)]],
    discovered_date: new Date(Date.now() - Math.random() * 30 * 24 * 3600000).toISOString(),
    status: statuses[Math.floor(Math.random() * statuses.length)],
    patch_available: Math.random() > 0.3
  }
}

export function generateMockPatch(): Patch {
  const priorities: Array<'critical' | 'high' | 'medium' | 'low'> = ['critical', 'high', 'medium', 'low']
  const statuses: Array<'available' | 'scheduled' | 'deployed' | 'failed'> = ['available', 'scheduled', 'deployed', 'failed']

  return {
    id: `patch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    patch_id: `PATCH-2024-${Math.floor(1000 + Math.random() * 9000)}`,
    title: 'Security Patch',
    description: 'Critical security update for system components',
    release_date: new Date(Date.now() - Math.random() * 15 * 24 * 3600000).toISOString(),
    applies_to: [SOURCES[Math.floor(Math.random() * SOURCES.length)]],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    priority: priorities[Math.floor(Math.random() * priorities.length)],
    vulnerabilities_fixed: [`CVE-2024-${Math.floor(10000 + Math.random() * 90000)}`]
  }
}

export function generateMockThreatIntel(): ThreatIntelligence {
  const indicatorTypes: Array<'ip' | 'domain' | 'hash' | 'url' | 'email'> = ['ip', 'domain', 'hash', 'url', 'email']
  const severities: Array<'critical' | 'high' | 'medium' | 'low'> = ['critical', 'high', 'medium', 'low']

  return {
    id: `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    indicator: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    indicator_type: indicatorTypes[Math.floor(Math.random() * indicatorTypes.length)],
    threat_type: 'Malicious Activity',
    severity: severities[Math.floor(Math.random() * severities.length)],
    first_seen: new Date(Date.now() - Math.random() * 60 * 24 * 3600000).toISOString(),
    last_seen: new Date(Date.now() - Math.random() * 7 * 24 * 3600000).toISOString(),
    confidence: 0.5 + Math.random() * 0.5,
    source: 'ThreatFeed-' + Math.floor(Math.random() * 5),
    tags: ['malware', 'botnet', 'c2'][Math.floor(Math.random() * 3)] as any
  }
}

export function generateMockSystemMetrics(): SystemMetrics {
  return {
    timestamp: new Date().toISOString(),
    cpu_usage: 20 + Math.random() * 60,
    memory_usage: 40 + Math.random() * 40,
    network_in: Math.random() * 1000,
    network_out: Math.random() * 800,
    active_connections: Math.floor(100 + Math.random() * 400),
    threat_events_per_minute: Math.floor(5 + Math.random() * 20),
    ai_processing_time_ms: 50 + Math.random() * 200
  }
}

// Generate initial dataset
export function generateInitialDataset() {
  return {
    alerts: Array.from({ length: 50 }, () => generateMockAlert()),
    logs: Array.from({ length: 100 }, () => generateMockSecurityLog()),
    vulnerabilities: Array.from({ length: 20 }, () => generateMockVulnerability()),
    patches: Array.from({ length: 15 }, () => generateMockPatch()),
    threatIntel: Array.from({ length: 30 }, () => generateMockThreatIntel())
  }
}
