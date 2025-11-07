"""AI model service for anomaly detection and threat analysis."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pickle
import json

# TensorFlow imports
try:
    import tensorflow as tf
    from sklearn.ensemble import IsolationForest, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
except ImportError:
    # Graceful degradation for development
    logging.warning("TensorFlow or scikit-learn not available")

from sqlalchemy.orm import Session
from models.database import (
    AuthenticationEvent, NetworkLog, PatchStatus,
    VulnerabilityScan, AIAnalysis, ModelConfig
)

logger = logging.getLogger(__name__)


class AIModelService:
    """Service for running AI-powered threat detection."""
    
    def __init__(self, model_path: str = "./models"):
        """
        Initialize AI model service.
        
        Args:
            model_path: Directory containing pre-trained models
        """
        self.model_path = Path(model_path)
        self.models = {}
        self.scalers = {}
        self.feature_weights = {}
        
        # Load default feature weights
        self.load_default_weights()
    
    def load_default_weights(self):
        """Load default feature weights."""
        self.feature_weights = {
            'authentication': {
                'failed_login_rate': 0.35,
                'geo_velocity': 0.25,
                'time_anomaly': 0.20,
                'enumeration_score': 0.20
            },
            'network': {
                'data_volume': 0.30,
                'connection_pattern': 0.25,
                'port_entropy': 0.25,
                'protocol_anomaly': 0.20
            },
            'vulnerability': {
                'cvss_score': 0.40,
                'days_unpatched': 0.30,
                'exploit_available': 0.20,
                'asset_criticality': 0.10
            }
        }
    
    def update_weights(self, category: str, weights: Dict[str, float]):
        """
        Update feature weights for a category.
        
        Args:
            category: Weight category ('authentication', 'network', 'vulnerability')
            weights: Dictionary of feature weights
        """
        if category in self.feature_weights:
            self.feature_weights[category].update(weights)
            logger.info(f"Updated {category} weights: {weights}")
    
    def load_models(self):
        """Load pre-trained models from disk."""
        try:
            # Load Isolation Forest for authentication
            auth_model_path = self.model_path / "isolation_forest_auth.pkl"
            if auth_model_path.exists():
                with open(auth_model_path, 'rb') as f:
                    self.models['auth_isolation'] = pickle.load(f)
                logger.info("Loaded authentication Isolation Forest model")
            
            # Load LSTM Autoencoder for network traffic
            network_model_path = self.model_path / "lstm_autoencoder_network.h5"
            if network_model_path.exists():
                self.models['network_lstm'] = tf.keras.models.load_model(str(network_model_path))
                logger.info("Loaded network LSTM Autoencoder model")
            
            # Load Gradient Boosting for vulnerability risk
            vuln_model_path = self.model_path / "gradient_boosting_vuln.pkl"
            if vuln_model_path.exists():
                with open(vuln_model_path, 'rb') as f:
                    self.models['vuln_gb'] = pickle.load(f)
                logger.info("Loaded vulnerability Gradient Boosting model")
            
            # Load scalers
            scaler_path = self.model_path / "scalers.pkl"
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scalers = pickle.load(f)
                logger.info("Loaded feature scalers")
        
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
            logger.info("Using rule-based detection instead")
    
    def extract_auth_features(self, events: List[AuthenticationEvent]) -> np.ndarray:
        """
        Extract features from authentication events.
        
        Features:
        - Failed login rate per IP
        - Geographic velocity (impossible travel)
        - Time-of-day anomaly
        - Username enumeration patterns
        """
        if not events:
            return np.array([])
        
        df = pd.DataFrame([{
            'source_ip': e.source_ip,
            'username': e.username,
            'event_type': e.event_type,
            'geolocation': e.geolocation,
            'timestamp': e.timestamp,
            'is_suspicious': e.is_suspicious
        } for e in events])
        
        features = []
        
        # Group by source IP
        for ip, group in df.groupby('source_ip'):
            # Failed login rate (logins per hour)
            time_span = (group['timestamp'].max() - group['timestamp'].min()).total_seconds() / 3600
            if time_span == 0:
                time_span = 1
            failed_rate = len(group[group['event_type'] == 'failed_login']) / time_span
            
            # Geographic velocity (number of unique locations)
            geo_velocity = group['geolocation'].nunique()
            
            # Time-of-day anomaly (percentage in off-hours 0-6 AM)
            off_hours = sum(group['timestamp'].dt.hour.between(0, 6)) / len(group)
            
            # Username enumeration (unique usernames tried)
            enumeration_score = group['username'].nunique() / len(group)
            
            features.append([
                failed_rate,
                geo_velocity,
                off_hours,
                enumeration_score
            ])
        
        return np.array(features)
    
    def extract_network_features(self, logs: List[NetworkLog]) -> np.ndarray:
        """
        Extract features from network logs.
        
        Features:
        - Data volume per time window
        - Connection pattern anomalies
        - Port distribution entropy
        - Protocol ratio changes
        """
        if not logs:
            return np.array([])
        
        df = pd.DataFrame([{
            'source_ip': l.source_ip,
            'destination_ip': l.destination_ip,
            'port': l.port,
            'protocol': l.protocol,
            'bytes_transferred': l.bytes_transferred,
            'packet_count': l.packet_count,
            'timestamp': l.timestamp,
            'threat_indicator': l.threat_indicator
        } for l in logs])
        
        features = []
        
        # Group by source IP
        for ip, group in df.groupby('source_ip'):
            # Data volume (MB per hour)
            time_span = (group['timestamp'].max() - group['timestamp'].min()).total_seconds() / 3600
            if time_span == 0:
                time_span = 1
            data_volume = group['bytes_transferred'].sum() / (1024 * 1024 * time_span)
            
            # Connection pattern (unique destinations)
            connection_pattern = group['destination_ip'].nunique() / len(group)
            
            # Port entropy
            port_dist = group['port'].value_counts(normalize=True)
            port_entropy = -sum(port_dist * np.log2(port_dist + 1e-10))
            
            # Protocol anomaly (protocol diversity)
            protocol_anomaly = group['protocol'].nunique() / len(group)
            
            features.append([
                data_volume,
                connection_pattern,
                port_entropy,
                protocol_anomaly
            ])
        
        return np.array(features)
    
    def extract_vulnerability_features(self, vulns: List[VulnerabilityScan]) -> np.ndarray:
        """
        Extract features from vulnerability scans.
        
        Features:
        - CVSS score
        - Days unpatched (from patch_status)
        - Exploit availability
        - Asset criticality
        """
        if not vulns:
            return np.array([])
        
        features = []
        
        for vuln in vulns:
            # CVSS score (0-10)
            cvss = float(vuln.cvss_score) if vuln.cvss_score else 0.0
            
            # Exploit available (1 or 0)
            exploit = 1.0 if vuln.exploit_available else 0.0
            
            # Asset criticality (encoded)
            criticality_map = {
                'operational_technology': 1.0,
                'dmz': 0.7,
                'corporate': 0.5
            }
            criticality = criticality_map.get(vuln.asset_criticality, 0.5)
            
            features.append([cvss, exploit, criticality])
        
        return np.array(features)
    
    def calculate_weighted_score(
        self, 
        features: np.ndarray, 
        weights: Dict[str, float],
        feature_names: List[str]
    ) -> float:
        """
        Calculate weighted anomaly score.
        
        Args:
            features: Feature array
            weights: Feature weights dictionary
            feature_names: Names of features corresponding to array columns
        
        Returns:
            Weighted score between 0 and 1
        """
        if len(features) == 0:
            return 0.0
        
        # Normalize features to 0-1 range
        normalized = (features - features.min(axis=0)) / (features.max(axis=0) - features.min(axis=0) + 1e-10)
        
        # Apply weights
        weighted = np.zeros(len(normalized))
        for i, name in enumerate(feature_names):
            weight = weights.get(name, 1.0 / len(feature_names))
            weighted += normalized[:, i] * weight
        
        return float(np.mean(weighted))
    
    def analyze_authentication_events(
        self, 
        db: Session, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict:
        """
        Analyze authentication events for anomalies.
        
        Returns:
            Analysis results with threat level and recommendations
        """
        # Query events
        events = db.query(AuthenticationEvent).filter(
            AuthenticationEvent.timestamp.between(start_time, end_time)
        ).all()
        
        if not events:
            return {
                'threat_level': 'info',
                'confidence': 0.0,
                'indicators': [],
                'recommendation': 'No authentication events in time range'
            }
        
        # Extract features
        features = self.extract_auth_features(events)
        
        # Calculate weighted anomaly score
        feature_names = ['failed_login_rate', 'geo_velocity', 'time_anomaly', 'enumeration_score']
        weights = self.feature_weights['authentication']
        score = self.calculate_weighted_score(features, weights, feature_names)
        
        # Determine threat level
        if score > 0.8:
            threat_level = 'critical'
        elif score > 0.6:
            threat_level = 'high'
        elif score > 0.4:
            threat_level = 'medium'
        elif score > 0.2:
            threat_level = 'low'
        else:
            threat_level = 'info'
        
        # Generate indicators
        indicators = []
        suspicious_events = [e for e in events if e.is_suspicious]
        
        if suspicious_events:
            # Count failed logins by IP
            ip_counts = {}
            for event in suspicious_events:
                if event.event_type == 'failed_login':
                    ip_counts[event.source_ip] = ip_counts.get(event.source_ip, 0) + 1
            
            for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                indicators.append(f"{count} failed logins from {ip}")
            
            # Check for geographic anomalies
            geolocations = set(e.geolocation for e in suspicious_events if e.geolocation)
            if len(geolocations) > 3:
                indicators.append(f"Login attempts from {len(geolocations)} different countries")
            
            # Check for time anomalies
            off_hours = [e for e in suspicious_events if e.timestamp.hour < 6]
            if len(off_hours) > len(suspicious_events) * 0.3:
                indicators.append(f"{len(off_hours)} login attempts during off-hours (12 AM - 6 AM)")
        
        # Generate recommendation
        if threat_level in ['critical', 'high']:
            recommendation = "Block suspicious source IPs, enforce MFA on critical accounts, investigate credential compromise"
        elif threat_level == 'medium':
            recommendation = "Monitor authentication patterns, review account activity logs"
        else:
            recommendation = "Continue normal monitoring"
        
        # Identify affected systems
        affected_systems = list(set(e.username for e in suspicious_events if e.username))[:5]
        
        return {
            'threat_level': threat_level,
            'confidence': score,
            'indicators': indicators,
            'recommendation': recommendation,
            'affected_systems': affected_systems,
            'event_count': len(events),
            'suspicious_count': len(suspicious_events)
        }
    
    def analyze_network_traffic(
        self, 
        db: Session, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict:
        """Analyze network traffic for anomalies."""
        logs = db.query(NetworkLog).filter(
            NetworkLog.timestamp.between(start_time, end_time)
        ).all()
        
        if not logs:
            return {
                'threat_level': 'info',
                'confidence': 0.0,
                'indicators': [],
                'recommendation': 'No network traffic in time range'
            }
        
        features = self.extract_network_features(logs)
        feature_names = ['data_volume', 'connection_pattern', 'port_entropy', 'protocol_anomaly']
        weights = self.feature_weights['network']
        score = self.calculate_weighted_score(features, weights, feature_names)
        
        # Determine threat level
        if score > 0.8:
            threat_level = 'critical'
        elif score > 0.6:
            threat_level = 'high'
        elif score > 0.4:
            threat_level = 'medium'
        elif score > 0.2:
            threat_level = 'low'
        else:
            threat_level = 'info'
        
        # Generate indicators
        indicators = []
        threat_logs = [l for l in logs if l.threat_indicator]
        
        if threat_logs:
            # Group by threat type
            threat_types = {}
            for log in threat_logs:
                threat_types[log.threat_indicator] = threat_types.get(log.threat_indicator, 0) + 1
            
            for threat, count in sorted(threat_types.items(), key=lambda x: x[1], reverse=True):
                indicators.append(f"{count} events indicating {threat.replace('_', ' ')}")
        
        recommendation = "Investigate network anomalies, review firewall rules" if threat_level in ['critical', 'high'] else "Continue monitoring"
        
        affected_systems = list(set(l.source_ip for l in threat_logs if l.source_ip))[:5]
        
        return {
            'threat_level': threat_level,
            'confidence': score,
            'indicators': indicators,
            'recommendation': recommendation,
            'affected_systems': affected_systems,
            'log_count': len(logs),
            'threat_count': len(threat_logs)
        }
    
    def analyze_vulnerabilities(
        self, 
        db: Session, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict:
        """Analyze vulnerability scans for risk assessment."""
        vulns = db.query(VulnerabilityScan).filter(
            VulnerabilityScan.timestamp.between(start_time, end_time)
        ).order_by(VulnerabilityScan.cvss_score.desc()).all()
        
        if not vulns:
            return {
                'threat_level': 'info',
                'confidence': 0.0,
                'indicators': [],
                'recommendation': 'No vulnerabilities in time range'
            }
        
        # Calculate risk scores
        critical_vulns = [v for v in vulns if v.cvss_score and float(v.cvss_score) >= 9.0]
        high_vulns = [v for v in vulns if v.cvss_score and 7.0 <= float(v.cvss_score) < 9.0]
        exploitable = [v for v in vulns if v.exploit_available]
        
        # Determine threat level
        if len(critical_vulns) > 0 and len(exploitable) > 0:
            threat_level = 'critical'
            confidence = 0.95
        elif len(critical_vulns) > 5:
            threat_level = 'high'
            confidence = 0.85
        elif len(high_vulns) > 10:
            threat_level = 'medium'
            confidence = 0.70
        else:
            threat_level = 'low'
            confidence = 0.50
        
        # Generate indicators
        indicators = []
        if critical_vulns:
            indicators.append(f"{len(critical_vulns)} critical vulnerabilities (CVSS >= 9.0)")
        if exploitable:
            indicators.append(f"{len(exploitable)} vulnerabilities with available exploits")
        
        # Check for OT/SCADA systems
        ot_vulns = [v for v in vulns if v.asset_criticality == 'operational_technology']
        if ot_vulns:
            indicators.append(f"{len(ot_vulns)} vulnerabilities in operational technology systems")
        
        recommendation = "Prioritize patching critical vulnerabilities, isolate affected OT systems" if threat_level in ['critical', 'high'] else "Schedule regular patching"
        
        affected_systems = list(set(v.asset_id for v in critical_vulns if v.asset_id))[:5]
        
        return {
            'threat_level': threat_level,
            'confidence': confidence,
            'indicators': indicators,
            'recommendation': recommendation,
            'affected_systems': affected_systems,
            'total_vulns': len(vulns),
            'critical_vulns': len(critical_vulns),
            'exploitable': len(exploitable)
        }
    
    def save_analysis_result(
        self, 
        db: Session, 
        analysis_type: str, 
        result: Dict,
        timestamp: Optional[datetime] = None
    ) -> AIAnalysis:
        """
        Save analysis result to database.
        
        Args:
            db: Database session
            analysis_type: Type of analysis performed
            result: Analysis result dictionary
            timestamp: Analysis timestamp (defaults to now)
        
        Returns:
            Created AIAnalysis record
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        analysis = AIAnalysis(
            timestamp=timestamp,
            analysis_type=analysis_type,
            confidence_score=result.get('confidence', 0.0),
            threat_level=result.get('threat_level', 'info'),
            affected_systems=result.get('affected_systems', []),
            recommendation=result.get('recommendation', '')
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis
