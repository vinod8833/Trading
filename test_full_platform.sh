#!/bin/bash

# KVK Trading Platform - Full System Test
# Tests all major components and sections

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        KVK Trading Platform - System Test Suite            ║"
echo "║        Testing All 6 Major Sections                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test an endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -ne "${BLUE}Testing: $name...${NC} "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Backend Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BACKEND SYSTEM CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_endpoint "Backend Server Health" "GET" "http://localhost:8001/health/"

# API Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API ENDPOINT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_endpoint "Stock Analysis" "GET" "http://localhost:8001/api/stocks/" ""

test_endpoint "Portfolio" "GET" "http://localhost:8001/api/portfolio/" ""

test_endpoint "Recommendations" "GET" "http://localhost:8001/api/recommendations/" ""

test_endpoint "Active Signals" "GET" "http://localhost:8001/api/recommendations/active/" ""

test_endpoint "Intraday Signals" "GET" "http://localhost:8001/api/intraday-signals/" ""

# Generate Recommendation
echo ""
test_endpoint "Generate Recommendation" "POST" "http://localhost:8001/api/recommendations/generate/" \
    '{"stock_symbol":"INFY","trading_style":"SWING","capital":100000}'

# Frontend Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FRONTEND SYSTEM CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_endpoint "Frontend Server" "GET" "http://localhost:3001/" ""

# CORS Configuration
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CORS CONFIGURATION CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cors_check=$(curl -s -I -H "Origin: http://localhost:3001" \
    http://localhost:8001/api/stocks/ | grep -i "access-control-allow-origin")

if [ ! -z "$cors_check" ]; then
    echo -e "${GREEN}✓ CORS Configured${NC}"
    echo "  Headers: $cors_check"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ CORS Not Configured${NC}"
    ((TESTS_FAILED++))
fi

# Database Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DATABASE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

stock_count=$(curl -s http://localhost:8001/api/stocks/ | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
echo -e "${BLUE}Stocks in Database:${NC} ${GREEN}$stock_count stocks${NC}"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED - SYSTEM READY! ✓    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ SOME TESTS FAILED - CHECK LOGS ✗      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
    exit 1
fi
