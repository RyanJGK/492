"""Generate realistic cybersecurity datasets for 5 attack scenarios."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


def generate_scenario1_scada_brute_force():
    """
    Scenario 1: SCADA Brute Force Attack
    847 failed login attempts across 3 SCADA hosts over 4 hours (2 AM - 6 AM)
    """
    print("Generating Scenario 1: SCADA Brute Force Attack...")
    
    base_time = datetime(2024, 11, 1, 2, 0, 0)  # 2 AM start
    events = []
    
    # Botnet IPs from different countries
    attacker_ips = [
        ("45.32.12.8", "Nigeria"),
        ("103.45.67.89", "China"),
        ("185.220.101.23", "Russia"),
        ("190.12.45.78", "Brazil"),
        ("41.78.123.45", "Kenya"),
        ("202.134.56.78", "Indonesia"),
        ("87.120.45.67", "Ukraine"),
        ("213.45.123.89", "Romania"),
        ("112.78.45.123", "Vietnam"),
        ("195.34.89.12", "Bulgaria"),
        ("177.89.45.123", "Argentina"),
        ("91.234.56.78", "Kazakhstan")
    ]
    
    # SCADA hosts being targeted
    scada_hosts = ["SCADA-01", "SCADA-02", "SCADA-03"]
    
    # Common usernames for enumeration
    usernames = ["admin", "scada", "operator", "supervisor", "engineer", 
                 "root", "administrator", "control", "manager", "hmi"]
    
    # Generate 847 failed login attempts
    for i in range(847):
        ip, geo = random.choice(attacker_ips)
        username = random.choice(usernames)
        host = random.choice(scada_hosts)
        
        # Add some time variation (not perfectly sequential)
        time_offset = timedelta(minutes=random.randint(0, 240))
        event_time = base_time + time_offset
        
        events.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": ip,
            "username": username,
            "event_type": "failed_login",
            "failure_reason": "Invalid credentials",
            "geolocation": geo,
            "is_suspicious": True,
            "target_host": host
        })
    
    # Add 2 successful logins after 6 hours (weak password compromised)
    success_time = base_time + timedelta(hours=6)
    events.append({
        "timestamp": success_time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip": "45.32.12.8",
        "username": "scada",
        "event_type": "successful_login",
        "failure_reason": None,
        "geolocation": "Nigeria",
        "is_suspicious": True,
        "target_host": "SCADA-02"
    })
    
    events.append({
        "timestamp": (success_time + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip": "45.32.12.8",
        "username": "scada",
        "event_type": "successful_login",
        "failure_reason": None,
        "geolocation": "Nigeria",
        "is_suspicious": True,
        "target_host": "SCADA-01"
    })
    
    df = pd.DataFrame(events)
    df = df.sort_values("timestamp")
    df.to_csv("/workspace/datasets/scenario1_scada_brute_force.csv", index=False)
    print(f"Generated {len(df)} authentication events")
    return df


def generate_scenario2_eternalblue():
    """
    Scenario 2: Unpatched EternalBlue Vulnerability
    23 Windows servers missing MS17-010 patch, ransomware spreads over 5 days
    """
    print("Generating Scenario 2: EternalBlue Vulnerability...")
    
    base_time = datetime(2024, 11, 1, 0, 0, 0)
    
    # Patch status records
    patch_records = []
    network_records = []
    vuln_records = []
    
    unpatched_servers = [f"WIN-SRV-{i:02d}" for i in range(1, 24)]
    
    # Day 0: Vulnerability scan detects unpatched systems
    for server in unpatched_servers:
        criticality = random.choice(["operational_technology", "corporate", "corporate", "dmz"])
        patch_records.append({
            "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "hostname": server,
            "os_type": "Windows Server 2012 R2",
            "missing_patches": "MS17-010,MS17-008,MS17-006",
            "severity": "critical",
            "days_unpatched": 0,
            "affected_service": criticality
        })
        
        vuln_records.append({
            "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "asset_id": server,
            "cve_id": "CVE-2017-0144",
            "cvss_score": 9.3,
            "exploit_available": True,
            "asset_criticality": criticality,
            "remediation_status": "open"
        })
    
    # Day 3: Network anomaly - SMB traffic spike
    day3 = base_time + timedelta(days=3)
    for i in range(500):
        source = random.choice(unpatched_servers[:10])
        dest = random.choice(unpatched_servers)
        time_offset = timedelta(minutes=random.randint(0, 1440))
        
        network_records.append({
            "timestamp": (day3 + time_offset).strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": f"192.168.10.{random.randint(10, 200)}",
            "destination_ip": f"192.168.10.{random.randint(10, 200)}",
            "port": 445,
            "protocol": "SMB",
            "bytes_transferred": random.randint(50000, 500000),
            "packet_count": random.randint(100, 1000),
            "is_encrypted": False,
            "threat_indicator": "lateral_movement"
        })
    
    # Update patch records for days 1-5
    for day in range(1, 6):
        check_time = base_time + timedelta(days=day)
        for server in unpatched_servers:
            criticality = random.choice(["operational_technology", "corporate", "corporate", "dmz"])
            patch_records.append({
                "timestamp": check_time.strftime("%Y-%m-%d %H:%M:%S"),
                "hostname": server,
                "os_type": "Windows Server 2012 R2",
                "missing_patches": "MS17-010,MS17-008,MS17-006",
                "severity": "critical",
                "days_unpatched": day,
                "affected_service": criticality
            })
    
    # Save datasets
    pd.DataFrame(patch_records).to_csv("/workspace/datasets/scenario2_patch_status.csv", index=False)
    pd.DataFrame(network_records).to_csv("/workspace/datasets/scenario2_network_logs.csv", index=False)
    pd.DataFrame(vuln_records).to_csv("/workspace/datasets/scenario2_vulnerabilities.csv", index=False)
    print(f"Generated {len(patch_records)} patch records, {len(network_records)} network logs, {len(vuln_records)} vulnerability records")


def generate_scenario3_dns_tunneling():
    """
    Scenario 3: DNS Tunneling Data Exfiltration
    1.2 GB exfiltrated over 6 days via DNS queries
    """
    print("Generating Scenario 3: DNS Tunneling Data Exfiltration...")
    
    base_time = datetime(2024, 11, 1, 0, 0, 0)
    network_records = []
    
    # Workstation doing exfiltration
    source_ip = "192.168.1.45"
    attacker_domain = "attacker.evil.com"
    
    # Generate 1.2 GB of exfiltration over 6 days (about 8500 queries)
    total_queries = 8500
    bytes_per_query = int((1.2 * 1024 * 1024 * 1024) / total_queries)
    
    for i in range(total_queries):
        # Spread queries over 6 days, mostly during off-hours
        day = random.randint(0, 6)
        hour = random.choice([0, 1, 2, 3, 4, 5, 22, 23])  # Off-hours
        minute = random.randint(0, 59)
        
        event_time = base_time + timedelta(days=day, hours=hour, minutes=minute)
        
        # Generate long DNS query (base64-encoded data)
        query_length = random.randint(150, 250)
        
        network_records.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": source_ip,
            "destination_ip": "8.8.8.8",
            "port": 53,
            "protocol": "DNS",
            "bytes_transferred": bytes_per_query,
            "packet_count": 1,
            "is_encrypted": False,
            "threat_indicator": "dns_tunneling",
            "query_length": query_length,
            "destination_domain": attacker_domain
        })
    
    df = pd.DataFrame(network_records)
    df = df.sort_values("timestamp")
    df.to_csv("/workspace/datasets/scenario3_dns_tunneling.csv", index=False)
    print(f"Generated {len(df)} DNS tunneling events")


def generate_scenario4_port_scan():
    """
    Scenario 4: Reconnaissance Port Scan
    Systematic scan of OT network targeting ICS ports
    """
    print("Generating Scenario 4: Port Scan Reconnaissance...")
    
    base_time = datetime(2024, 11, 1, 14, 30, 0)
    network_records = []
    
    attacker_ip = "203.45.67.89"
    
    # ICS-specific ports
    ics_ports = [
        (502, "Modbus"),
        (44818, "EtherNet/IP"),
        (2404, "IEC-104"),
        (20000, "DNP3"),
        (102, "S7"),
        (47808, "BACnet")
    ]
    
    # Scan 192.168.10.0/24 network
    for ip in range(1, 255):
        for port, protocol in ics_ports:
            # Fast scan - complete in 40 minutes
            time_offset = timedelta(seconds=random.randint(0, 2400))
            event_time = base_time + time_offset
            
            network_records.append({
                "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": attacker_ip,
                "destination_ip": f"192.168.10.{ip}",
                "port": port,
                "protocol": protocol,
                "bytes_transferred": 64,
                "packet_count": 1,
                "is_encrypted": False,
                "threat_indicator": "port_scan"
            })
    
    # 72 hours later - exploit attempts on discovered services
    exploit_time = base_time + timedelta(hours=72)
    live_hosts = [f"192.168.10.{ip}" for ip in [15, 23, 45, 67, 89, 123]]
    
    for i in range(200):
        time_offset = timedelta(minutes=random.randint(0, 120))
        host = random.choice(live_hosts)
        port, protocol = random.choice(ics_ports)
        
        network_records.append({
            "timestamp": (exploit_time + time_offset).strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": attacker_ip,
            "destination_ip": host,
            "port": port,
            "protocol": protocol,
            "bytes_transferred": random.randint(500, 5000),
            "packet_count": random.randint(5, 50),
            "is_encrypted": False,
            "threat_indicator": "exploit_attempt"
        })
    
    df = pd.DataFrame(network_records)
    df = df.sort_values("timestamp")
    df.to_csv("/workspace/datasets/scenario4_port_scan.csv", index=False)
    print(f"Generated {len(df)} port scan events")


def generate_scenario5_phishing():
    """
    Scenario 5: Phishing Campaign with Credential Harvesting
    43 phishing emails, 8 clicks, 3 credential compromises
    """
    print("Generating Scenario 5: Phishing Campaign...")
    
    base_time = datetime(2024, 11, 1, 9, 15, 0)
    auth_records = []
    network_records = []
    
    # 43 employees received phishing email
    employees = [f"employee{i:02d}" for i in range(1, 44)]
    
    # 8 employees clicked the link (simulated by network log)
    clicked_users = random.sample(employees, 8)
    
    for i, user in enumerate(clicked_users):
        click_time = base_time + timedelta(minutes=random.randint(10, 120))
        
        network_records.append({
            "timestamp": click_time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": f"192.168.1.{random.randint(10, 200)}",
            "destination_ip": "185.220.102.45",
            "port": 443,
            "protocol": "HTTPS",
            "bytes_transferred": random.randint(5000, 15000),
            "packet_count": random.randint(10, 30),
            "is_encrypted": True,
            "threat_indicator": "phishing_click",
            "user": user
        })
    
    # 3 users entered credentials
    compromised_users = random.sample(clicked_users, 3)
    
    for user in compromised_users:
        # Attacker logs in 1 hour after credential compromise
        compromise_time = base_time + timedelta(hours=random.randint(1, 3))
        
        auth_records.append({
            "timestamp": compromise_time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": "185.220.102.45",
            "username": user,
            "event_type": "successful_login",
            "failure_reason": None,
            "geolocation": "Russia",
            "is_suspicious": True
        })
        
        # Attacker accesses SCADA interface
        scada_access_time = compromise_time + timedelta(minutes=random.randint(5, 30))
        network_records.append({
            "timestamp": scada_access_time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": "185.220.102.45",
            "destination_ip": "192.168.10.5",
            "port": 443,
            "protocol": "HTTPS",
            "bytes_transferred": random.randint(50000, 150000),
            "packet_count": random.randint(100, 300),
            "is_encrypted": True,
            "threat_indicator": "unauthorized_scada_access",
            "user": user
        })
    
    # Save datasets
    pd.DataFrame(auth_records).to_csv("/workspace/datasets/scenario5_phishing_auth.csv", index=False)
    pd.DataFrame(network_records).to_csv("/workspace/datasets/scenario5_phishing_network.csv", index=False)
    print(f"Generated {len(auth_records)} auth events, {len(network_records)} network events")


if __name__ == "__main__":
    # Create datasets directory if it doesn't exist
    os.makedirs("/workspace/datasets", exist_ok=True)
    
    print("=" * 60)
    print("Energy Defense - Dataset Generation")
    print("=" * 60)
    
    generate_scenario1_scada_brute_force()
    generate_scenario2_eternalblue()
    generate_scenario3_dns_tunneling()
    generate_scenario4_port_scan()
    generate_scenario5_phishing()
    
    print("\n" + "=" * 60)
    print("Dataset generation complete!")
    print("Files created in /workspace/datasets/")
    print("=" * 60)
