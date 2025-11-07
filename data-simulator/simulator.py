"""
Data ingestion simulator for 492-Energy-Defense.
Generates realistic security event data to simulate a live SOC environment.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import httpx
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

fake = Faker()

# Configuration
BACKEND_API_URL = "http://backend:8000"
SIMULATION_INTERVAL = 30  # seconds
API_USERNAME = "analyst1"
API_PASSWORD = "demo123"

# Energy sector specific assets
SCADA_SERVERS = ["SRV-001", "SRV-002", "SRV-003"]
ICS_COMPONENTS = ["ICS-001", "ICS-002", "ICS-003", "ICS-004"]
NETWORK_DEVICES = ["NET-001", "NET-002", "NET-003"]
WORKSTATIONS = ["WS-001", "WS-002", "WS-003", "WS-004"]

# Common vulnerabilities
VULNERABILITIES = [
    {
        "title": "Remote Code Execution in SCADA Interface",
        "severity": "critical",
        "cvss": 9.8,
        "cve_pattern": "CVE-2024-"
    },
    {
        "title": "SQL Injection in Data Logging Module",
        "severity": "high",
        "cvss": 8.1,
        "cve_pattern": "CVE-2024-"
    },
    {
        "title": "Default Credentials in Management Interface",
        "severity": "high",
        "cvss": 7.5,
        "cve_pattern": "CVE-2024-"
    },
    {
        "title": "Cross-Site Scripting in Web Dashboard",
        "severity": "medium",
        "cvss": 6.5,
        "cve_pattern": "CVE-2023-"
    },
    {
        "title": "Privilege Escalation Vulnerability",
        "severity": "high",
        "cvss": 8.8,
        "cve_pattern": "CVE-2024-"
    }
]

# Threat patterns
THREAT_TYPES = [
    "port_scan", "brute_force", "unauthorized_access",
    "data_exfiltration", "malware", "ddos_attempt"
]

# Internal network ranges
INTERNAL_IPS = [
    "10.0.1.10", "10.0.1.11", "10.0.1.12", "10.0.1.20",
    "10.0.2.10", "10.0.2.11", "192.168.1.10", "192.168.1.11"
]

# External threat IPs
THREAT_IPS = [
    "203.0.113.45", "198.51.100.30", "192.0.2.100",
    "185.220.101.50", "89.248.174.10"
]


class SecurityDataSimulator:
    """Simulates security data ingestion for SOC environment."""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.token = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def authenticate(self):
        """Authenticate with the backend API."""
        try:
            response = await self.client.post(
                f"{self.backend_url}/api/v1/auth/login",
                json={"username": API_USERNAME, "password": API_PASSWORD}
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            logger.info("Successfully authenticated with backend")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def _get_headers(self):
        """Get authentication headers."""
        return {"Authorization": f"Bearer {self.token}"}
    
    async def generate_auth_events(self) -> List[Dict[str, Any]]:
        """Generate authentication event data."""
        events = []
        
        # Generate 1-3 auth events
        for _ in range(random.randint(1, 3)):
            success = random.random() > 0.2  # 80% success rate
            
            event = {
                "event_type": "login_success" if success else "login_failure",
                "ip_address": random.choice(INTERNAL_IPS + THREAT_IPS[:2]),
                "user_agent": fake.user_agent(),
                "success": success,
                "risk_score": random.randint(5, 15) if success else random.randint(50, 85)
            }
            
            if not success:
                event["failure_reason"] = random.choice([
                    "Invalid credentials",
                    "Account locked",
                    "Expired password",
                    "MFA required"
                ])
            
            events.append(event)
        
        return events
    
    async def generate_patch_levels(self) -> List[Dict[str, Any]]:
        """Generate patch level data."""
        patches = []
        
        # Update patch status for some assets
        assets = random.sample(
            SCADA_SERVERS + ICS_COMPONENTS + NETWORK_DEVICES + WORKSTATIONS,
            k=random.randint(1, 3)
        )
        
        for asset_id in assets:
            asset_type = self._get_asset_type(asset_id)
            
            missing_critical = random.randint(0, 3)
            missing_high = random.randint(0, 5)
            
            if missing_critical > 0:
                compliance = "critical"
                criticality = random.randint(85, 100)
            elif missing_high > 2:
                compliance = "at_risk"
                criticality = random.randint(70, 85)
            else:
                compliance = random.choice(["compliant", "non_compliant"])
                criticality = random.randint(50, 70)
            
            patch = {
                "asset_id": asset_id,
                "asset_name": f"{asset_type.title()} {asset_id}",
                "asset_type": asset_type,
                "operating_system": random.choice([
                    "Windows Server 2019",
                    "Ubuntu 22.04 LTS",
                    "Cisco IOS 15.7",
                    "Proprietary"
                ]),
                "current_patch_level": f"2024.{random.randint(8, 10)}",
                "latest_patch_level": "2024.11",
                "missing_critical_patches": missing_critical,
                "missing_high_patches": missing_high,
                "missing_medium_patches": random.randint(0, 8),
                "missing_low_patches": random.randint(0, 15),
                "last_patched": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                "compliance_status": compliance,
                "criticality_score": criticality
            }
            
            patches.append(patch)
        
        return patches
    
    async def generate_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Generate vulnerability scan data."""
        vulns = []
        
        # Generate 1-2 new vulnerabilities
        for _ in range(random.randint(1, 2)):
            vuln_template = random.choice(VULNERABILITIES)
            asset = random.choice(SCADA_SERVERS + ICS_COMPONENTS + NETWORK_DEVICES)
            
            vuln = {
                "scan_id": f"SCAN-{fake.uuid4()}",
                "asset_id": asset,
                "asset_name": f"Asset {asset}",
                "vulnerability_id": f"VULN-{random.randint(10000, 99999)}",
                "cve_id": f"{vuln_template['cve_pattern']}{random.randint(1000, 9999)}",
                "severity": vuln_template["severity"],
                "cvss_score": vuln_template["cvss"] + random.uniform(-0.5, 0.5),
                "title": vuln_template["title"],
                "description": fake.paragraph(),
                "solution": fake.sentence(),
                "exploit_available": random.random() > 0.7,
                "exploited_in_wild": random.random() > 0.9,
                "patch_available": random.random() > 0.4,
                "affected_software": fake.word(),
                "first_detected": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
                "last_detected": datetime.utcnow().isoformat(),
                "status": "open",
                "risk_score": random.randint(70, 98) if vuln_template["severity"] in ["critical", "high"] else random.randint(40, 70)
            }
            
            vulns.append(vuln)
        
        return vulns
    
    async def generate_firewall_logs(self) -> List[Dict[str, Any]]:
        """Generate firewall log data."""
        logs = []
        
        # Generate 5-10 firewall logs
        for _ in range(random.randint(5, 10)):
            threat_detected = random.random() > 0.7  # 30% threat detection rate
            
            if threat_detected:
                source_ip = random.choice(THREAT_IPS)
                action = random.choice(["deny", "drop", "reject"])
                threat_type = random.choice(THREAT_TYPES)
                threat_severity = random.choice(["critical", "high", "medium"])
                risk_score = random.randint(70, 95)
            else:
                source_ip = random.choice(INTERNAL_IPS)
                action = random.choice(["allow", "allow", "allow", "deny"])
                threat_type = None
                threat_severity = None
                risk_score = random.randint(5, 20)
            
            log = {
                "timestamp": datetime.utcnow().isoformat(),
                "source_ip": source_ip,
                "source_port": random.randint(1024, 65535),
                "destination_ip": random.choice(INTERNAL_IPS),
                "destination_port": random.choice([22, 80, 443, 502, 3389, 8080]),
                "protocol": random.choice(["TCP", "UDP", "ICMP"]),
                "action": action,
                "rule_id": f"RULE-{random.randint(100, 999)}",
                "bytes_sent": random.randint(0, 100000),
                "bytes_received": random.randint(0, 100000),
                "threat_detected": threat_detected,
                "threat_type": threat_type,
                "threat_severity": threat_severity,
                "risk_score": risk_score
            }
            
            logs.append(log)
        
        return logs
    
    def _get_asset_type(self, asset_id: str) -> str:
        """Determine asset type from ID."""
        if asset_id.startswith("SRV"):
            return "scada_system"
        elif asset_id.startswith("ICS"):
            return "ics_component"
        elif asset_id.startswith("NET"):
            return "network_device"
        else:
            return "workstation"
    
    async def ingest_data(self):
        """Generate and ingest all types of security data."""
        try:
            # Generate data
            auth_events = await self.generate_auth_events()
            patch_levels = await self.generate_patch_levels()
            vulnerabilities = await self.generate_vulnerabilities()
            firewall_logs = await self.generate_firewall_logs()
            
            headers = self._get_headers()
            
            # Ingest auth events
            if auth_events:
                response = await self.client.post(
                    f"{self.backend_url}/api/v1/ingest/auth-events/bulk",
                    json=auth_events,
                    headers=headers
                )
                response.raise_for_status()
                logger.info(f"Ingested {len(auth_events)} auth events")
            
            # Ingest patch levels
            if patch_levels:
                response = await self.client.post(
                    f"{self.backend_url}/api/v1/ingest/patch-levels/bulk",
                    json=patch_levels,
                    headers=headers
                )
                response.raise_for_status()
                logger.info(f"Ingested {len(patch_levels)} patch levels")
            
            # Ingest vulnerabilities
            if vulnerabilities:
                response = await self.client.post(
                    f"{self.backend_url}/api/v1/ingest/vulnerabilities/bulk",
                    json=vulnerabilities,
                    headers=headers
                )
                response.raise_for_status()
                logger.info(f"Ingested {len(vulnerabilities)} vulnerabilities")
            
            # Ingest firewall logs
            if firewall_logs:
                response = await self.client.post(
                    f"{self.backend_url}/api/v1/ingest/firewall-logs/bulk",
                    json=firewall_logs,
                    headers=headers
                )
                response.raise_for_status()
                logger.info(f"Ingested {len(firewall_logs)} firewall logs")
            
            logger.info("Data ingestion cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
    
    async def run(self, interval: int = SIMULATION_INTERVAL):
        """Run the simulator continuously."""
        logger.info(f"Starting data simulator (interval: {interval}s)")
        
        # Wait for backend to be ready
        await asyncio.sleep(10)
        
        # Authenticate
        await self.authenticate()
        
        # Run simulation loop
        while True:
            await self.ingest_data()
            await asyncio.sleep(interval)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def main():
    """Main entry point."""
    simulator = SecurityDataSimulator(BACKEND_API_URL)
    
    try:
        await simulator.run()
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
    except Exception as e:
        logger.error(f"Simulator error: {e}", exc_info=True)
    finally:
        await simulator.close()


if __name__ == "__main__":
    asyncio.run(main())
