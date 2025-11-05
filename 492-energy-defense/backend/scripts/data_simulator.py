"""
Data Ingestion Simulator
Generates realistic SOC environment data for demonstration
"""
import asyncio
import random
import logging
from datetime import datetime, timedelta
from uuid import uuid4
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSimulator:
    """Simulates realistic security event data"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.engine = None
        self.AsyncSessionLocal = None
        
        # Simulation parameters
        self.threat_ips = [
            "192.0.2.1", "198.51.100.42", "203.0.113.99",
            "45.33.32.156", "104.131.206.57"
        ]
        self.internal_ips = [
            f"10.0.{random.randint(1,255)}.{random.randint(1,255)}"
            for _ in range(20)
        ]
        self.cve_ids = [
            "CVE-2023-12345", "CVE-2023-23456", "CVE-2023-34567",
            "CVE-2024-00123", "CVE-2024-00456"
        ]
        self.systems = [
            "SCADA-01", "SCADA-02", "HMI-Control-01", "HMI-Control-02",
            "PLC-01", "PLC-02", "Historian-DB", "Engineering-Workstation"
        ]
    
    async def initialize(self):
        """Initialize database connection"""
        self.engine = create_async_engine(self.database_url)
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Data Simulator initialized")
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
        logger.info("Data Simulator connections closed")
    
    async def simulate_firewall_logs(self, count: int = 10):
        """Generate simulated firewall logs"""
        from api.models import FirewallLog, SeverityLevel
        
        async with self.AsyncSessionLocal() as session:
            for _ in range(count):
                is_threat = random.random() < 0.15  # 15% threat probability
                
                log = FirewallLog(
                    log_timestamp=datetime.utcnow() - timedelta(seconds=random.randint(0, 3600)),
                    source_ip=random.choice(self.threat_ips if is_threat else self.internal_ips),
                    destination_ip=random.choice(self.internal_ips),
                    source_port=random.randint(1024, 65535),
                    destination_port=random.choice([22, 80, 443, 3389, 502, 2404]),
                    protocol=random.choice(["TCP", "UDP"]),
                    action=random.choice(["allow", "deny", "drop"]),
                    rule_id=f"FW-RULE-{random.randint(100, 999)}",
                    packet_size=random.randint(64, 1500),
                    severity=random.choice(list(SeverityLevel)),
                    threat_indicator=is_threat,
                    country_code=random.choice(["US", "CN", "RU", "KP", "IR"]) if is_threat else "US"
                )
                session.add(log)
            
            await session.commit()
            logger.info(f"Generated {count} firewall logs")
    
    async def simulate_vulnerabilities(self, count: int = 5):
        """Generate simulated vulnerability scans"""
        from api.models import VulnerabilityScan, SeverityLevel, EventStatus
        
        async with self.AsyncSessionLocal() as session:
            for _ in range(count):
                vuln = VulnerabilityScan(
                    scan_id=uuid4(),
                    target_system=random.choice(self.systems),
                    scan_type=random.choice(["network", "application", "infrastructure"]),
                    severity=random.choice(list(SeverityLevel)),
                    vulnerability_name=f"Vulnerability-{random.randint(1000, 9999)}",
                    vulnerability_description="Simulated vulnerability for demonstration",
                    cve_id=random.choice(self.cve_ids),
                    cvss_score=round(random.uniform(0.0, 10.0), 1),
                    affected_component=random.choice(["Web Server", "Database", "SCADA", "HMI"]),
                    remediation_steps="Apply security patches and update system",
                    scan_timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
                    status=random.choice(list(EventStatus))
                )
                session.add(vuln)
            
            await session.commit()
            logger.info(f"Generated {count} vulnerability scans")
    
    async def simulate_patch_levels(self, count: int = 5):
        """Generate simulated patch level data"""
        from api.models import PatchLevel, SeverityLevel
        
        async with self.AsyncSessionLocal() as session:
            for _ in range(count):
                is_outdated = random.random() < 0.3  # 30% outdated
                
                patch = PatchLevel(
                    system_name=random.choice(self.systems),
                    component_name=random.choice([
                        "Operating System", "Security Software", "SCADA Software",
                        "Firewall Firmware", "Database Engine"
                    ]),
                    current_version=f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    latest_version=f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    patch_status="outdated" if is_outdated else "up_to_date",
                    severity=random.choice(list(SeverityLevel)) if is_outdated else SeverityLevel.INFO,
                    cve_ids=[random.choice(self.cve_ids)] if is_outdated else [],
                    last_patched=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                    next_scheduled_patch=datetime.utcnow() + timedelta(days=random.randint(1, 30))
                )
                session.add(patch)
            
            await session.commit()
            logger.info(f"Generated {count} patch level records")
    
    async def run_simulation_cycle(self):
        """Run one complete simulation cycle"""
        try:
            await self.simulate_firewall_logs(random.randint(5, 15))
            await asyncio.sleep(2)
            
            await self.simulate_vulnerabilities(random.randint(2, 5))
            await asyncio.sleep(2)
            
            await self.simulate_patch_levels(random.randint(2, 5))
            
            logger.info("Simulation cycle completed")
        except Exception as e:
            logger.error(f"Simulation error: {e}")


async def main():
    """Main simulation loop"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL not set")
        return
    
    simulator = DataSimulator(database_url)
    
    try:
        await simulator.initialize()
        logger.info("Starting data simulation...")
        
        # Wait for database to be ready
        await asyncio.sleep(10)
        
        # Run simulation every 5 minutes
        while True:
            await simulator.run_simulation_cycle()
            logger.info("Waiting 5 minutes until next simulation...")
            await asyncio.sleep(300)  # 5 minutes
            
    except KeyboardInterrupt:
        logger.info("Stopping data simulator...")
    finally:
        await simulator.close()


if __name__ == "__main__":
    asyncio.run(main())
