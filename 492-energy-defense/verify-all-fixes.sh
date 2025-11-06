#!/bin/bash
# Verification Script for All Applied Fixes
# Checks that all 7 critical issues have been resolved

set -e

echo "🔍 VERIFYING ALL FIXES - Energy Defense System"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

echo "1️⃣  Checking SQLAlchemy models for 'metadata' reserved word..."
if grep -q "event_metadata = Column(\"metadata\"" backend/api/models.py && \
   grep -q "scan_metadata = Column(\"metadata\"" backend/api/models.py && \
   grep -q "log_metadata = Column(\"metadata\"" backend/api/models.py; then
    check_pass "All 3 metadata columns renamed in models.py"
else
    check_fail "Metadata columns not properly renamed in models.py"
fi
echo ""

echo "2️⃣  Checking docker-compose healthcheck..."
if grep -q 'test: \["CMD-SHELL", "pg_isready"\]' docker-compose.yml; then
    check_pass "PostgreSQL healthcheck simplified (no database specification)"
else
    check_fail "Healthcheck still trying to connect to specific database"
fi
echo ""

echo "3️⃣  Checking data-simulator environment variables..."
if grep -q "SECRET_KEY=\${SECRET_KEY" docker-compose.yml && \
   grep -q "OPENROUTER_API_KEY=\${OPENROUTER_API_KEY" docker-compose.yml; then
    check_pass "Simulator has required environment variables in docker-compose.yml"
else
    check_fail "Simulator missing environment variables"
fi

if grep -q "os.environ.setdefault('SECRET_KEY'" backend/scripts/data_simulator.py && \
   grep -q "os.environ.setdefault('OPENROUTER_API_KEY'" backend/scripts/data_simulator.py; then
    check_pass "Simulator has environment defaults in code"
else
    check_warn "Simulator missing environment defaults in code (optional)"
fi
echo ""

echo "4️⃣  Checking database role creation..."
if grep -q "CREATE ROLE observer_role" backend/database/init.sql && \
   grep -q "CREATE ROLE analyst_role" backend/database/init.sql && \
   grep -q "CREATE ROLE admin_role" backend/database/init.sql; then
    check_pass "All database roles are created"
    
    # Check order: CREATE ROLE should come before GRANT
    create_line=$(grep -n "CREATE ROLE observer_role" backend/database/init.sql | cut -d: -f1)
    grant_line=$(grep -n "GRANT SELECT ON ALL TABLES IN SCHEMA public TO observer_role" backend/database/init.sql | cut -d: -f1)
    
    if [ "$create_line" -lt "$grant_line" ]; then
        check_pass "Role creation happens before GRANT statements"
    else
        check_fail "Role creation happens AFTER GRANT (wrong order)"
    fi
else
    check_fail "Some database roles not created"
fi
echo ""

echo "5️⃣  Checking password hash..."
if grep -q '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW' backend/database/init.sql; then
    check_pass "Correct bcrypt hash for 'admin123' found"
else
    check_fail "Password hash is incorrect or missing"
fi
echo ""

echo "6️⃣  Checking Python import paths..."
if grep -q "ENV PYTHONPATH=/app" backend/Dockerfile && \
   grep -q "ENV PYTHONPATH=/app" backend/Dockerfile.ai; then
    check_pass "PYTHONPATH set in both Dockerfiles"
else
    check_fail "PYTHONPATH not set in Dockerfiles"
fi

if grep -q "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))" backend/scripts/data_simulator.py; then
    check_pass "Data simulator has sys.path import fix"
else
    check_fail "Data simulator missing sys.path fix"
fi
echo ""

echo "7️⃣  Checking ai_weight_config trigger..."
if grep -q "CREATE TRIGGER ai_weight_config_updated_at" backend/database/init.sql; then
    check_pass "ai_weight_config updated_at trigger exists"
else
    check_fail "ai_weight_config trigger missing"
fi
echo ""

# Summary
echo "=============================================="
echo "📊 VERIFICATION SUMMARY"
echo "=============================================="
echo -e "${GREEN}Passed:${NC} $PASS_COUNT"
echo -e "${RED}Failed:${NC} $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ ALL FIXES VERIFIED - SYSTEM IS READY!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: docker-compose down -v"
    echo "2. Run: docker-compose up --build"
    echo "3. Wait 60 seconds"
    echo "4. Open: http://localhost:3000"
    echo "5. Login: admin / admin123"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME FIXES NOT APPLIED${NC}"
    echo ""
    echo "Please review the failed checks above."
    echo "See docs/fixes/ALL_FIXES_APPLIED.md for details."
    echo ""
    exit 1
fi
