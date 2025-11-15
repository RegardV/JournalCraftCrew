#!/bin/bash

# Journal Craft Crew - Regression Prevention System
# Automated testing to prevent regression and ensure production readiness

set -e  # Exit on any error

echo "🛡️  REGRESSION PREVENTION SYSTEM - Journal Craft Crew"
echo "=================================================="

# Configuration
FRONTEND_URL="http://localhost:5100"
BACKEND_URL="http://localhost:8000"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="regression_test_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Logging function
log_test() {
    local test_name="$1"
    local result="$2"
    local details="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name"
        if [ -n "$details" ]; then
            echo -e "   ${YELLOW}Details:${NC} $details"
        fi
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo "[$TIMESTAMP] $result - $test_name: $details" >> "$LOG_FILE"
}

# Test HTTP endpoint
test_endpoint() {
    local endpoint="$1"
    local expected_status="$2"
    local test_name="$3"
    local method="${4:-GET}"
    local data="${5:-}"

    local response
    local status

    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BACKEND_URL$endpoint")
    else
        response=$(curl -s -w "%{http_code}" "$BACKEND_URL$endpoint")
    fi

    status="${response: -3}"

    if [ "$status" = "$expected_status" ]; then
        log_test "$test_name" "PASS" "Status $status"
        return 0
    else
        log_test "$test_name" "FAIL" "Expected $expected_status, got $status"
        return 1
    fi
}

# Test JSON response structure
test_json_response() {
    local endpoint="$1"
    local field="$2"
    local expected_value="$3"
    local test_name="$4"

    local response
    response=$(curl -s "$BACKEND_URL$endpoint")

    if echo "$response" | jq -e ".$field" > /dev/null 2>&1; then
        local actual_value
        actual_value=$(echo "$response" | jq -r ".$field")

        if [ "$actual_value" = "$expected_value" ]; then
            log_test "$test_name" "PASS" "$field = $actual_value"
            return 0
        else
            log_test "$test_name" "FAIL" "Expected $field = $expected_value, got $actual_value"
            return 1
        fi
    else
        log_test "$test_name" "FAIL" "Field '$field' not found in response"
        return 1
    fi
}

echo "Starting regression tests at $TIMESTAMP"
echo ""

# ==========================================
# CRITICAL INFRASTRUCTURE TESTS
# ==========================================

echo -e "${BLUE}🔧 Testing Critical Infrastructure...${NC}"

# Test 1: Backend Health Check
test_endpoint "/health" "200" "Backend Health Check"

# Test 2: Frontend Accessibility
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$frontend_status" = "200" ]; then
    log_test "Frontend Accessibility" "PASS" "Status $frontend_status"
else
    log_test "Frontend Accessibility" "FAIL" "Expected 200, got $frontend_status"
fi

# ==========================================
# API ENDPOINT TESTS
# ==========================================

echo ""
echo -e "${BLUE}🌐 Testing API Endpoints...${NC}"

# Authentication endpoints
test_endpoint "/api/auth/me" "200" "Auth Me (Development Mode)"

# AI Generation endpoints
test_endpoint "/api/ai/themes" "200" "AI Themes"
test_endpoint "/api/ai/title-styles" "200" "AI Title Styles"

# Library endpoints
test_endpoint "/api/library/llm-projects" "200" "Library Projects"
test_json_response "/api/library/llm-projects" "count" "0" "Demo Data Removal Check"

# Settings endpoints
test_endpoint "/api/settings/api-key" "200" "API Key Status"

# ==========================================
# PRODUCTION READINESS TESTS
# ==========================================

echo ""
echo -e "${BLUE}✅ Testing Production Readiness...${NC}"

# Test: No demo data contamination
library_response=$(curl -s "$BACKEND_URL/api/library/llm-projects")
projects_count=$(echo "$library_response" | jq -r '.count')
if [ "$projects_count" = "0" ]; then
    log_test "Demo Data Removal" "PASS" "Library is clean (0 projects)"
else
    log_test "Demo Data Removal" "FAIL" "Found $projects_count demo projects"
fi

# Test: Enhanced AI Workflow Page accessibility
workflow_status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/ai-workflow/test123")
if [ "$workflow_status" = "200" ]; then
    log_test "EnhancedAIWorkflowPage Accessibility" "PASS" "No 500 errors"
else
    log_test "EnhancedAIWorkflowPage Accessibility" "FAIL" "Got $workflow_status status"
fi

# Test: Content Library page accessibility
library_page_status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/content-library")
if [ "$library_page_status" = "200" ]; then
    log_test "Content Library Page" "PASS" "Page loads correctly"
else
    log_test "Content Library Page" "FAIL" "Got $library_page_status status"
fi

# ==========================================
# REGRESSION TEST RESULTS
# ==========================================

echo ""
echo "=================================================="
echo -e "${BLUE}📊 REGRESSION TEST RESULTS${NC}"
echo "=================================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED - System is regression-free!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  $FAILED_TESTS TESTS FAILED - Regression detected!${NC}"
    echo "Check log file: $LOG_FILE"
    exit 1
fi