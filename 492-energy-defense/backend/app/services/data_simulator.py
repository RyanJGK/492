"""
Data simulation service for live SOC activity
Generates realistic security events for demonstration
"""

import asyncio
import random
from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import List
from uuid import uuid4

from faker import Faker
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import get_settings
from app.db.models import (
    AuthEvent, FirewallLog, VulnerabilityScan, Vulnerability, Patch, AIThreatAnalysis
)

logger = structlog.get_logger()
fake = Faker()
settings = get_settings()


def get_database_url() -> str:
    """Convert PostgreSQL URL to async format"""
    url = str(settings.DATABASE_URL)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class DataSimulator:
    """Simulates live SOC security data"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        
        # Realistic data pools
        self.usernames = ["admin", "jsmith", "mjones", "tkhan", "dbrown", "rwilson"]
        self.systems = [
            "scada-primary", "scada-backup", "hmi-station-1", "hmi-station-2",
            "plc-zone-a", "plc-zone-b", "rtu-north", "rtu-south",
            "dc-server-01", "dc-server-02", "workstation-ops"
        ]
        self.firewall_names = ["edge-fw-01", "zone-fw-01", "dmz-fw-01"]
        self.scanner_names = ["nessus-scanner", "qualys-cloud", "openvas-01"]
        
    async def initialize(self):
        """Initialize database connection"""
        database_url = get_database_url()
        self.engine = create_async_engine(database_url, echo=False)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("data_simulator_initialized")
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("data_simulator_closed")
    
    def generate_ip(self, external: bool = False) -> str:
        """Generate random IP address"""
        if external:
            # External IPs (not private ranges)
            return str(IPv4Address(random.randint(167772160, 4294967295)))
        else:
            # Internal private IP ranges
            return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    
    async def simulate_auth_events(self, session: AsyncSession, count: int = 5):
        """Generate authentication events"""
        events = []
        
        for _ in range(count):
            event_type = random.choices(
                ["login_success", "login_failure", "logout", "token_refresh"],
                weights=[70, 15, 10, 5]
            )[0]
            
            success = event_type != "login_failure"
            severity = "critical" if not success and random.random() < 0.2 else "info"
            
            event = AuthEvent(
                event_time=datetime.utcnow() - timedelta(seconds=random.randint(0, 300)),
                event_type=event_type,
                username=random.choice(self.usernames),
                source_ip=self.generate_ip(external=random.random() < 0.1),
                user_agent=fake.user_agent(),
                session_id=uuid4(),
                success=success,
                failure_reason="Invalid credentials" if not success else None,
                severity=severity,
                metadata={"simulated": True},
            )
            events.append(event)
        
        session.add_all(events)
        logger.info("auth_events_simulated", count=count)
    
    async def simulate_firewall_logs(self, session: AsyncSession, count: int = 20):
        """Generate firewall logs"""
        logs = []
        
        for _ in range(count):
            action = random.choices(
                ["allow", "deny", "drop"],
                weights=[70, 20, 10]
            )[0]
            
            threat_level = "low"
            if action in ["deny", "drop"]:
                threat_level = random.choices(
                    ["low", "medium", "high", "critical"],
                    weights=[50, 30, 15, 5]
                )[0]
            
            log = FirewallLog(
                log_time=datetime.utcnow() - timedelta(seconds=random.randint(0, 300)),
                firewall_name=random.choice(self.firewall_names),
                action=action,
                source_ip=self.generate_ip(external=action in ["deny", "drop"]),
                source_port=random.randint(1024, 65535),
                dest_ip=self.generate_ip(),
                dest_port=random.choice([22, 80, 443, 3389, 502, 20000]),
                protocol=random.choice(["TCP", "UDP", "ICMP"]),
                bytes_sent=random.randint(100, 10000),
                bytes_received=random.randint(100, 10000),
                threat_level=threat_level,
                metadata={"simulated": True},
            )
            logs.append(log)
        
        session.add_all(logs)
        logger.info("firewall_logs_simulated", count=count)
    
    async def simulate_vulnerability_scan(self, session: AsyncSession):
        """Generate a vulnerability scan with findings"""
        target_system = random.choice(self.systems)
        
        scan = VulnerabilityScan(
            scan_time=datetime.utcnow(),
            scanner_name=random.choice(self.scanner_names),
            target_system=target_system,
            target_ip=self.generate_ip(),
            scan_type=random.choice(["network", "application", "configuration"]),
            status="completed",
            scan_duration_seconds=random.randint(60, 600),
            metadata={"simulated": True},
        )
        
        session.add(scan)
        await session.flush()
        
        # Generate vulnerabilities
        vuln_count = random.randint(2, 8)
        vulnerabilities = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for i in range(vuln_count):
            severity = random.choices(
                ["critical", "high", "medium", "low"],
                weights=[5, 15, 40, 40]
            )[0]
            severity_counts[severity] += 1
            
            vuln = Vulnerability(
                scan_id=scan.scan_id,
                vuln_id=f"VULN-{fake.bothify('####')}",
                title=f"Security issue in {target_system}",
                description=fake.text(max_nb_chars=200),
                severity=severity,
                cvss_score=random.uniform(2.0, 10.0),
                cve_id=f"CVE-{random.randint(2020, 2024)}-{random.randint(1000, 9999)}",
                affected_system=target_system,
                affected_component=random.choice(["OS", "Service", "Application"]),
                port=random.choice([22, 80, 443, 3389, 502]),
                status="open",
                detected_at=datetime.utcnow(),
                metadata={"simulated": True},
            )
            vulnerabilities.append(vuln)
        
        # Update scan counts
        scan.total_vulnerabilities = vuln_count
        scan.critical_count = severity_counts["critical"]
        scan.high_count = severity_counts["high"]
        scan.medium_count = severity_counts["medium"]
        scan.low_count = severity_counts["low"]
        
        session.add_all(vulnerabilities)
        logger.info("vulnerability_scan_simulated", count=vuln_count)
    
    async def simulate_patches(self, session: AsyncSession, count: int = 3):
        """Generate patch records"""
        patches = []
        
        for _ in range(count):
            severity = random.choices(
                ["critical", "high", "medium", "low"],
                weights=[10, 25, 40, 25]
            )[0]
            
            status = random.choices(
                ["pending", "scheduled", "installed"],
                weights=[50, 30, 20]
            )[0]
            
            patch = Patch(
                patch_id=f"PATCH-{fake.bothify('######')}",
                system_name=random.choice(self.systems),
                system_type=random.choice(["scada", "hmi", "plc", "server"]),
                patch_name=f"Security Update {fake.bothify('##.##.##')}",
                patch_version=fake.bothify('##.##.####'),
                severity=severity,
                status=status,
                release_date=datetime.utcnow().date() - timedelta(days=random.randint(1, 30)),
                scheduled_date=datetime.utcnow() + timedelta(days=random.randint(1, 14)) if status == "scheduled" else None,
                requires_downtime=random.random() < 0.3,
                metadata={"simulated": True},
            )
            patches.append(patch)
        
        session.add_all(patches)
        logger.info("patches_simulated", count=count)
    
    async def run_simulation_cycle(self):
        """Execute one simulation cycle"""
        async with self.session_factory() as session:
            try:
                # Generate different types of events
                await self.simulate_auth_events(session, count=random.randint(3, 8))
                await self.simulate_firewall_logs(session, count=random.randint(15, 30))
                
                # Periodically generate scans and patches (less frequent)
                if random.random() < 0.2:  # 20% chance
                    await self.simulate_vulnerability_scan(session)
                
                if random.random() < 0.1:  # 10% chance
                    await self.simulate_patches(session, count=random.randint(1, 3))
                
                await session.commit()
                logger.info("simulation_cycle_completed")
                
            except Exception as e:
                await session.rollback()
                logger.error("simulation_cycle_failed", error=str(e))
    
    async def run_forever(self, interval_seconds: int = 30):
        """Run simulation continuously"""
        logger.info("data_simulator_started", interval=interval_seconds)
        
        while True:
            try:
                await self.run_simulation_cycle()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error("simulation_error", error=str(e))
                await asyncio.sleep(5)


async def main():
    """Main entry point for data simulator service"""
    # Configure logging
    from app.core.logging_config import setup_logging
    setup_logging()
    
    simulator = DataSimulator()
    
    try:
        await simulator.initialize()
        interval = int(settings.__dict__.get("SIMULATION_INTERVAL", 30))
        await simulator.run_forever(interval_seconds=interval)
    finally:
        await simulator.close()


if __name__ == "__main__":
    asyncio.run(main())
