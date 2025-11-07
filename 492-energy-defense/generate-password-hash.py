#!/usr/bin/env python3
"""
Generate correct bcrypt password hash for admin123
Run this inside the backend container or with passlib installed
"""

try:
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    password = "admin123"
    correct_hash = pwd_context.hash(password)
    
    print("=" * 60)
    print("CORRECT PASSWORD HASH FOR init.sql")
    print("=" * 60)
    print("")
    print(f"Password: {password}")
    print("")
    print("New hash:")
    print(correct_hash)
    print("")
    print("=" * 60)
    print("UPDATE INIT.SQL")
    print("=" * 60)
    print("")
    print("Replace line 178 in backend/database/init.sql with:")
    print("")
    print(f"    ('admin', 'admin@energy-defense.local', '{correct_hash}', 'admin'),")
    print("")
    print("Apply to all 3 users (admin, analyst, observer)")
    print("")
    
except ImportError:
    print("ERROR: passlib not installed")
    print("")
    print("Run inside Docker container:")
    print("  docker-compose exec backend python3 generate-password-hash.py")
    print("")
    print("Or install locally:")
    print("  pip3 install 'passlib[bcrypt]'")
