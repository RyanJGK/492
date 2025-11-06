#!/usr/bin/env python3
"""
Test password hashing to verify the hash in init.sql is correct
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The password we want to test
password = "admin123"

# The hash from init.sql
stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lk3PqXZO0Oju"

# Test if password matches
if pwd_context.verify(password, stored_hash):
    print("✅ Password 'admin123' MATCHES the stored hash")
    print("✅ Login credentials should work")
else:
    print("❌ Password 'admin123' DOES NOT MATCH the stored hash")
    print("❌ This is why login is failing")
    print("\nGenerating new hash...")
    new_hash = pwd_context.hash(password)
    print(f"\nNew hash for 'admin123':")
    print(new_hash)
    print("\nUpdate init.sql with this hash")
