export interface Alert {
  id: string
  timestamp: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  type: string
  source: string
  description: string
  status: 'new' | 'investigating' | 'resolved' | 'false_positive'
  ai_score?: number
  ai_confidence?: number
  assigned_to?: string
  metadata?: Record<string, any>
}

export interface SecurityLog {
  id: string
  timestamp: string
  event_type: string
  source_ip: string
  destination_ip?: string
  protocol: string
  action: string
  details: string
  severity: string
  raw_log?: string
}

export interface Vulnerability {
  id: string
  cve_id?: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  cvss_score?: number
  affected_systems: string[]
  discovered_date: string
  status: 'open' | 'in_progress' | 'patched' | 'mitigated' | 'accepted'
  remediation?: string
  patch_available: boolean
}

export interface Patch {
  id: string
  patch_id: string
  title: string
  description: string
  release_date: string
  applies_to: string[]
  status: 'available' | 'scheduled' | 'deployed' | 'failed'
  priority: 'critical' | 'high' | 'medium' | 'low'
  deployment_date?: string
  vulnerabilities_fixed: string[]
}

export interface AIAnalysis {
  id: string
  timestamp: string
  alert_id?: string
  analysis_type: string
  threat_score: number
  confidence: number
  findings: string
  recommendations: string[]
  false_positive_probability: number
  related_incidents?: string[]
  model_version: string
}

export interface AIModelWeights {
  id?: string
  model_name: string
  weights: {
    severity_weight: number
    frequency_weight: number
    source_reputation_weight: number
    pattern_match_weight: number
    anomaly_score_weight: number
  }
  threshold_settings: {
    critical_threshold: number
    high_threshold: number
    medium_threshold: number
    auto_escalate_threshold: number
  }
  last_updated: string
  updated_by: string
}

export interface ThreatIntelligence {
  id: string
  indicator: string
  indicator_type: 'ip' | 'domain' | 'hash' | 'url' | 'email'
  threat_type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  first_seen: string
  last_seen: string
  confidence: number
  source: string
  tags: string[]
  description?: string
}

export interface SystemMetrics {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  network_in: number
  network_out: number
  active_connections: number
  threat_events_per_minute: number
  ai_processing_time_ms: number
}
