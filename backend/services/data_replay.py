"""Data replay service for loading and replaying attack scenarios."""
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from pathlib import Path

from models.database import (
    AuthenticationEvent, NetworkLog, PatchStatus, 
    VulnerabilityScan
)

logger = logging.getLogger(__name__)


class DataReplayService:
    """Service for replaying pre-recorded attack scenarios."""
    
    def __init__(self, datasets_path: str = "/app/datasets", replay_speed: int = 100):
        """
        Initialize the data replay service.
        
        Args:
            datasets_path: Path to directory containing CSV datasets
            replay_speed: Speed multiplier for timestamp adjustment (100 = 100x faster)
        """
        self.datasets_path = Path(datasets_path)
        self.replay_speed = replay_speed
        self.replay_status = {
            "is_running": False,
            "current_scenario": None,
            "progress": 0.0
        }
    
    def adjust_timestamp(self, original_timestamp: str, base_time: Optional[datetime] = None) -> datetime:
        """
        Adjust timestamps to current time with replay speed multiplier.
        
        Args:
            original_timestamp: Original timestamp from dataset
            base_time: Base time to calculate offset from (defaults to now)
        
        Returns:
            Adjusted timestamp
        """
        original_dt = pd.to_datetime(original_timestamp)
        
        if base_time is None:
            base_time = datetime.now()
        
        # Calculate time difference from first event
        # This preserves relative timing but adjusts to current time
        return base_time
    
    def load_scenario1_scada_brute_force(self, db: Session, adjust_time: bool = True) -> int:
        """
        Load Scenario 1: SCADA Brute Force Attack.
        
        Args:
            db: Database session
            adjust_time: Whether to adjust timestamps to current time
        
        Returns:
            Number of events loaded
        """
        logger.info("Loading Scenario 1: SCADA Brute Force Attack")
        
        csv_path = self.datasets_path / "scenario1_scada_brute_force.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        base_time = datetime.now() if adjust_time else None
        first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
        
        events = []
        for _, row in df.iterrows():
            original_time = pd.to_datetime(row['timestamp'])
            
            if adjust_time:
                # Calculate offset from first event and apply replay speed
                time_diff = original_time - first_timestamp
                adjusted_diff = time_diff / self.replay_speed
                event_time = base_time + adjusted_diff
            else:
                event_time = original_time
            
            event = AuthenticationEvent(
                timestamp=event_time,
                source_ip=row['source_ip'],
                username=row['username'],
                event_type=row['event_type'],
                failure_reason=row.get('failure_reason'),
                geolocation=row['geolocation'],
                is_suspicious=bool(row['is_suspicious'])
            )
            events.append(event)
        
        db.bulk_save_objects(events)
        db.commit()
        
        logger.info(f"Loaded {len(events)} authentication events")
        return len(events)
    
    def load_scenario2_eternalblue(self, db: Session, adjust_time: bool = True) -> dict:
        """
        Load Scenario 2: EternalBlue Vulnerability.
        
        Returns:
            Dictionary with counts of each event type loaded
        """
        logger.info("Loading Scenario 2: EternalBlue Vulnerability")
        
        base_time = datetime.now() if adjust_time else None
        counts = {}
        
        # Load patch status
        patch_path = self.datasets_path / "scenario2_patch_status.csv"
        if patch_path.exists():
            df = pd.read_csv(patch_path)
            first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
            
            events = []
            for _, row in df.iterrows():
                original_time = pd.to_datetime(row['timestamp'])
                
                if adjust_time:
                    time_diff = original_time - first_timestamp
                    adjusted_diff = time_diff / self.replay_speed
                    event_time = base_time + adjusted_diff
                else:
                    event_time = original_time
                
                # Parse missing_patches string to array
                patches = row['missing_patches'].split(',') if pd.notna(row['missing_patches']) else []
                
                event = PatchStatus(
                    timestamp=event_time,
                    hostname=row['hostname'],
                    os_type=row['os_type'],
                    missing_patches=patches,
                    severity=row['severity'],
                    days_unpatched=int(row['days_unpatched']),
                    affected_service=row['affected_service']
                )
                events.append(event)
            
            db.bulk_save_objects(events)
            counts['patch_status'] = len(events)
        
        # Load network logs
        network_path = self.datasets_path / "scenario2_network_logs.csv"
        if network_path.exists():
            df = pd.read_csv(network_path)
            first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
            
            events = []
            for _, row in df.iterrows():
                original_time = pd.to_datetime(row['timestamp'])
                
                if adjust_time:
                    time_diff = original_time - first_timestamp
                    adjusted_diff = time_diff / self.replay_speed
                    event_time = base_time + adjusted_diff
                else:
                    event_time = original_time
                
                event = NetworkLog(
                    timestamp=event_time,
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    port=int(row['port']),
                    protocol=row['protocol'],
                    bytes_transferred=int(row['bytes_transferred']),
                    packet_count=int(row['packet_count']),
                    is_encrypted=bool(row['is_encrypted']),
                    threat_indicator=row['threat_indicator']
                )
                events.append(event)
            
            db.bulk_save_objects(events)
            counts['network_logs'] = len(events)
        
        # Load vulnerabilities
        vuln_path = self.datasets_path / "scenario2_vulnerabilities.csv"
        if vuln_path.exists():
            df = pd.read_csv(vuln_path)
            first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
            
            events = []
            for _, row in df.iterrows():
                original_time = pd.to_datetime(row['timestamp'])
                
                if adjust_time:
                    time_diff = original_time - first_timestamp
                    adjusted_diff = time_diff / self.replay_speed
                    event_time = base_time + adjusted_diff
                else:
                    event_time = original_time
                
                event = VulnerabilityScan(
                    timestamp=event_time,
                    asset_id=row['asset_id'],
                    cve_id=row['cve_id'],
                    cvss_score=float(row['cvss_score']),
                    exploit_available=bool(row['exploit_available']),
                    asset_criticality=row['asset_criticality'],
                    remediation_status=row['remediation_status']
                )
                events.append(event)
            
            db.bulk_save_objects(events)
            counts['vulnerabilities'] = len(events)
        
        db.commit()
        logger.info(f"Loaded scenario 2: {counts}")
        return counts
    
    def load_scenario3_dns_tunneling(self, db: Session, adjust_time: bool = True) -> int:
        """Load Scenario 3: DNS Tunneling."""
        logger.info("Loading Scenario 3: DNS Tunneling")
        
        csv_path = self.datasets_path / "scenario3_dns_tunneling.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        base_time = datetime.now() if adjust_time else None
        first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
        
        events = []
        for _, row in df.iterrows():
            original_time = pd.to_datetime(row['timestamp'])
            
            if adjust_time:
                time_diff = original_time - first_timestamp
                adjusted_diff = time_diff / self.replay_speed
                event_time = base_time + adjusted_diff
            else:
                event_time = original_time
            
            event = NetworkLog(
                timestamp=event_time,
                source_ip=row['source_ip'],
                destination_ip=row['destination_ip'],
                port=int(row['port']),
                protocol=row['protocol'],
                bytes_transferred=int(row['bytes_transferred']),
                packet_count=int(row['packet_count']),
                is_encrypted=bool(row['is_encrypted']),
                threat_indicator=row['threat_indicator']
            )
            events.append(event)
        
        db.bulk_save_objects(events)
        db.commit()
        
        logger.info(f"Loaded {len(events)} DNS tunneling events")
        return len(events)
    
    def load_scenario4_port_scan(self, db: Session, adjust_time: bool = True) -> int:
        """Load Scenario 4: Port Scan."""
        logger.info("Loading Scenario 4: Port Scan")
        
        csv_path = self.datasets_path / "scenario4_port_scan.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        base_time = datetime.now() if adjust_time else None
        first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
        
        events = []
        for _, row in df.iterrows():
            original_time = pd.to_datetime(row['timestamp'])
            
            if adjust_time:
                time_diff = original_time - first_timestamp
                adjusted_diff = time_diff / self.replay_speed
                event_time = base_time + adjusted_diff
            else:
                event_time = original_time
            
            event = NetworkLog(
                timestamp=event_time,
                source_ip=row['source_ip'],
                destination_ip=row['destination_ip'],
                port=int(row['port']),
                protocol=row['protocol'],
                bytes_transferred=int(row['bytes_transferred']),
                packet_count=int(row['packet_count']),
                is_encrypted=bool(row['is_encrypted']),
                threat_indicator=row['threat_indicator']
            )
            events.append(event)
        
        db.bulk_save_objects(events)
        db.commit()
        
        logger.info(f"Loaded {len(events)} port scan events")
        return len(events)
    
    def load_scenario5_phishing(self, db: Session, adjust_time: bool = True) -> dict:
        """Load Scenario 5: Phishing Campaign."""
        logger.info("Loading Scenario 5: Phishing Campaign")
        
        base_time = datetime.now() if adjust_time else None
        counts = {}
        
        # Load authentication events
        auth_path = self.datasets_path / "scenario5_phishing_auth.csv"
        if auth_path.exists():
            df = pd.read_csv(auth_path)
            first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
            
            events = []
            for _, row in df.iterrows():
                original_time = pd.to_datetime(row['timestamp'])
                
                if adjust_time:
                    time_diff = original_time - first_timestamp
                    adjusted_diff = time_diff / self.replay_speed
                    event_time = base_time + adjusted_diff
                else:
                    event_time = original_time
                
                event = AuthenticationEvent(
                    timestamp=event_time,
                    source_ip=row['source_ip'],
                    username=row['username'],
                    event_type=row['event_type'],
                    failure_reason=row.get('failure_reason'),
                    geolocation=row['geolocation'],
                    is_suspicious=bool(row['is_suspicious'])
                )
                events.append(event)
            
            db.bulk_save_objects(events)
            counts['auth_events'] = len(events)
        
        # Load network events
        network_path = self.datasets_path / "scenario5_phishing_network.csv"
        if network_path.exists():
            df = pd.read_csv(network_path)
            first_timestamp = pd.to_datetime(df['timestamp'].iloc[0])
            
            events = []
            for _, row in df.iterrows():
                original_time = pd.to_datetime(row['timestamp'])
                
                if adjust_time:
                    time_diff = original_time - first_timestamp
                    adjusted_diff = time_diff / self.replay_speed
                    event_time = base_time + adjusted_diff
                else:
                    event_time = original_time
                
                event = NetworkLog(
                    timestamp=event_time,
                    source_ip=row['source_ip'],
                    destination_ip=row['destination_ip'],
                    port=int(row['port']),
                    protocol=row['protocol'],
                    bytes_transferred=int(row['bytes_transferred']),
                    packet_count=int(row['packet_count']),
                    is_encrypted=bool(row['is_encrypted']),
                    threat_indicator=row['threat_indicator']
                )
                events.append(event)
            
            db.bulk_save_objects(events)
            counts['network_logs'] = len(events)
        
        db.commit()
        logger.info(f"Loaded scenario 5: {counts}")
        return counts
    
    def load_all_scenarios(self, db: Session, adjust_time: bool = True) -> dict:
        """
        Load all attack scenarios.
        
        Returns:
            Dictionary with results for each scenario
        """
        results = {}
        
        try:
            results['scenario1'] = self.load_scenario1_scada_brute_force(db, adjust_time)
        except Exception as e:
            logger.error(f"Error loading scenario 1: {e}")
            results['scenario1'] = f"Error: {e}"
        
        try:
            results['scenario2'] = self.load_scenario2_eternalblue(db, adjust_time)
        except Exception as e:
            logger.error(f"Error loading scenario 2: {e}")
            results['scenario2'] = f"Error: {e}"
        
        try:
            results['scenario3'] = self.load_scenario3_dns_tunneling(db, adjust_time)
        except Exception as e:
            logger.error(f"Error loading scenario 3: {e}")
            results['scenario3'] = f"Error: {e}"
        
        try:
            results['scenario4'] = self.load_scenario4_port_scan(db, adjust_time)
        except Exception as e:
            logger.error(f"Error loading scenario 4: {e}")
            results['scenario4'] = f"Error: {e}"
        
        try:
            results['scenario5'] = self.load_scenario5_phishing(db, adjust_time)
        except Exception as e:
            logger.error(f"Error loading scenario 5: {e}")
            results['scenario5'] = f"Error: {e}"
        
        return results
