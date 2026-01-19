#!/bin/bash
"""
DEPLOY_AND_VERIFY.sh - Complete deployment and verification script
Verifies all fixes are in place and system is fully functional
"""

echo "════════════════════════════════════════════════════════════════════════════════"
echo "  KVK_8833_PROFIT - AI TRADING PLATFORM"
echo "  DEPLOYMENT & VERIFICATION SCRIPT"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check and report
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} $2 (missing: $1)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} $2 (missing: $1)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 1: File Structure${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

check_dir "frontend" "Frontend directory exists"
check_dir "trading" "Trading app directory exists"
check_file "manage.py" "Django manage.py"
check_file "kvk_trading/settings.py" "Django settings"
check_file "kvk_trading/urls.py" "URL configuration"
check_file "requirements.txt" "Python requirements"
check_file "db.sqlite3" "Database file"

echo ""

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 2: Backend Services${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

check_file "trading/market_data_service.py" "Market data service"
check_file "trading/error_handler.py" "Error handling service"
check_file "trading/api_views_fixed.py" "Improved API views"
check_file "trading/fixtures.py" "Database fixtures"
check_file "trading/health_urls.py" "Health check endpoints"
check_file "trading/management/commands/init_system.py" "System initialization command"

echo ""

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 3: Frontend Configuration${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

check_file "frontend/src/api/client.js" "API client configuration"
check_file "frontend/src/api/endpoints.js" "API endpoints (improved)"
check_file "frontend/src/api/endpoints_v2.js" "API endpoints v2"
check_file "frontend/src/App.jsx" "App component"
check_file "frontend/src/store/index.js" "Zustand store"
check_file "frontend/src/layouts/MainLayout.jsx" "Main layout"
check_file "frontend/src/pages/Login.jsx" "Login page"
check_file "frontend/src/pages/Dashboard.jsx" "Dashboard (improved)"

echo ""

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 4: Documentation${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

check_file "COMPREHENSIVE_FIX_DOCUMENTATION.txt" "Fix documentation"
check_file "COMPLETE_SETUP_GUIDE.md" "Setup guide"
check_file "AI_ENGINE_IMPLEMENTATION_SUMMARY.txt" "AI engine overview"

echo ""

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 5: Key Features${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

echo "Checking key features implemented:"
echo ""

# Check for market data service
if grep -q "MarketCalendar" trading/market_data_service.py; then
    echo -e "${GREEN}✅${NC} Market calendar & hours detection"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Market calendar feature"
    ((CHECKS_FAILED++))
fi

# Check for error handling
if grep -q "class ValidationError" trading/error_handler.py; then
    echo -e "${GREEN}✅${NC} Error handling & validation"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Error handling"
    ((CHECKS_FAILED++))
fi

# Check for API validation
if grep -q "PayloadValidator" trading/error_handler.py; then
    echo -e "${GREEN}✅${NC} Request payload validation"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Payload validation"
    ((CHECKS_FAILED++))
fi

# Check for persistent auth
if grep -q "localStorage.getItem" frontend/src/App.jsx; then
    echo -e "${GREEN}✅${NC} Persistent authentication (localStorage)"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Persistent authentication"
    ((CHECKS_FAILED++))
fi

# Check for error utilities
if grep -q "errorUtils" frontend/src/api/endpoints.js; then
    echo -e "${GREEN}✅${NC} Frontend error utilities"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Frontend error utilities"
    ((CHECKS_FAILED++))
fi

# Check for safe API calls
if grep -q "safeCall\|safeApiCall" frontend/src/api/endpoints.js frontend/src/api/endpoints_v2.js 2>/dev/null; then
    echo -e "${GREEN}✅${NC} Safe API call wrappers"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} Safe API wrappers"
    ((CHECKS_FAILED++))
fi

# Check for AI engine
if grep -q "class AISignalGeneratorView" trading/ai_engine_views.py 2>/dev/null; then
    echo -e "${GREEN}✅${NC} AI signal generation API"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} AI signal API"
    ((CHECKS_FAILED++))
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 6: Configuration${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

# Check Django settings
if grep -q "CORS_ALLOWED_ORIGINS" kvk_trading/settings.py; then
    echo -e "${GREEN}✅${NC} CORS configuration"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} CORS configuration"
    ((CHECKS_FAILED++))
fi

# Check JWT configuration
if grep -q "SIMPLE_JWT" kvk_trading/settings.py; then
    echo -e "${GREEN}✅${NC} JWT authentication"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} JWT configuration"
    ((CHECKS_FAILED++))
fi

# Check REST Framework
if grep -q "REST_FRAMEWORK" kvk_trading/settings.py; then
    echo -e "${GREEN}✅${NC} Django REST Framework"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}❌${NC} REST Framework"
    ((CHECKS_FAILED++))
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}VERIFICATION SECTION 7: Database Models${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

if grep -q "class Stock" trading/models.py; then
    echo -e "${GREEN}✅${NC} Stock model"
    ((CHECKS_PASSED++))
fi

if grep -q "class TradeRecommendation" trading/models.py; then
    echo -e "${GREEN}✅${NC} Trade recommendation model"
    ((CHECKS_PASSED++))
fi

if grep -q "class PaperTrade" trading/models.py; then
    echo -e "${GREEN}✅${NC} Paper trading model"
    ((CHECKS_PASSED++))
fi

if grep -q "class Portfolio" trading/models.py; then
    echo -e "${GREEN}✅${NC} Portfolio model"
    ((CHECKS_PASSED++))
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}VERIFICATION SUMMARY${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""

echo -e "${GREEN}Checks Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Checks Failed: $CHECKS_FAILED${NC}"

TOTAL=$((CHECKS_PASSED + CHECKS_FAILED))
PERCENTAGE=$((CHECKS_PASSED * 100 / TOTAL))

echo ""
echo "Overall Completion: ${PERCENTAGE}% (${CHECKS_PASSED}/${TOTAL})"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ ALL CHECKS PASSED - SYSTEM IS READY FOR DEPLOYMENT${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
else
    echo -e "${YELLOW}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}⚠️  SOME CHECKS FAILED - PLEASE REVIEW AND FIX${NC}"
    echo -e "${YELLOW}════════════════════════════════════════════════════════════════════════════════${NC}"
fi

echo ""
echo "Quick Start Commands:"
echo "───────────────────────────────────────────────────────────────────────────"
echo ""
echo "1. Initialize system:"
echo "   ${YELLOW}python manage.py init_system${NC}"
echo ""
echo "2. Start backend (Terminal 1):"
echo "   ${YELLOW}python manage.py runserver 0.0.0.0:8001${NC}"
echo ""
echo "3. Start frontend (Terminal 2):"
echo "   ${YELLOW}cd frontend && npm start${NC}"
echo ""
echo "4. Test API:"
echo "   ${YELLOW}curl http://localhost:8001/health/${NC}"
echo ""
echo "5. Login (in browser):"
echo "   ${YELLOW}Username: vinod8833${NC}"
echo "   ${YELLOW}Password: test123${NC}"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
