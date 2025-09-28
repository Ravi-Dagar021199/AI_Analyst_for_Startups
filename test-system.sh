#!/bin/bash

# Enhanced AI Startup Analyst - System Test Script
echo "🧪 Testing Enhanced AI Startup Analyst System"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
API_GATEWAY="http://localhost:3000"
ENHANCED_INGESTION="http://localhost:8002"
DATA_CURATION="http://localhost:3003"

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="$3"
    
    echo -e "${BLUE}Testing: $name${NC}"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" == "200" ] || [ "$http_code" == "201" ]; then
        echo -e "${GREEN}✅ $name: SUCCESS (HTTP $http_code)${NC}"
        if [ ${#body} -lt 200 ]; then
            echo "   Response: $body"
        else
            echo "   Response: ${body:0:100}..."
        fi
    else
        echo -e "${RED}❌ $name: FAILED (HTTP $http_code)${NC}"
        echo "   Response: $body"
    fi
    echo ""
}

echo -e "${YELLOW}🔍 Testing Core Services${NC}"
echo "========================="

# Test API Gateway
test_endpoint "API Gateway Root" "$API_GATEWAY/" "GET"
test_endpoint "API Gateway Health" "$API_GATEWAY/health" "GET"
test_endpoint "System Info" "$API_GATEWAY/api/system-info" "GET"

# Test Enhanced Ingestion Service
test_endpoint "Enhanced Ingestion Root" "$ENHANCED_INGESTION/" "GET"
test_endpoint "Enhanced Ingestion Health" "$ENHANCED_INGESTION/health" "GET"

# Test Data Curation Service
test_endpoint "Data Curation Root" "$DATA_CURATION/" "GET" 
test_endpoint "Data Curation Health" "$DATA_CURATION/health" "GET"

echo -e "${YELLOW}📊 Testing API Endpoints${NC}"
echo "========================="

# Test dataset listing (should work even if empty)
test_endpoint "List Datasets" "$DATA_CURATION/datasets/" "GET"

# Test file upload with a simple text file
echo -e "${BLUE}Testing File Upload${NC}"
echo "Creating test file..."
echo "This is a test startup pitch document. Our company, TestCorp Inc, is seeking Series A funding for our innovative AI platform." > /tmp/test-startup.txt

# Test single file upload via API Gateway
echo "Testing file upload via API Gateway..."
upload_response=$(curl -s -w "\n%{http_code}" \
    -X POST "$API_GATEWAY/api/enhanced-ingestion/upload/single" \
    -F "file=@/tmp/test-startup.txt" \
    -F "title=Test Startup Document" \
    -F "context=Test upload for system validation" \
    -F "extract_external_data=false")

upload_http_code=$(echo "$upload_response" | tail -n1)
upload_body=$(echo "$upload_response" | head -n -1)

if [ "$upload_http_code" == "200" ] || [ "$upload_http_code" == "201" ]; then
    echo -e "${GREEN}✅ File Upload: SUCCESS (HTTP $upload_http_code)${NC}"
    echo "   Response: $upload_body"
    
    # Extract file_id if available
    file_id=$(echo "$upload_body" | grep -o '"file_id":"[^"]*' | cut -d'"' -f4)
    if [ ! -z "$file_id" ]; then
        echo "   File ID: $file_id"
        
        # Test file status check
        sleep 2
        echo "Checking file status..."
        test_endpoint "File Status" "$ENHANCED_INGESTION/files/status/$file_id" "GET"
    fi
else
    echo -e "${RED}❌ File Upload: FAILED (HTTP $upload_http_code)${NC}"
    echo "   Response: $upload_body"
fi

# Clean up test file
rm -f /tmp/test-startup.txt

echo ""
echo -e "${YELLOW}🐳 Docker Services Status${NC}"
echo "=========================="

# Check if Docker Compose services are running
if command -v docker-compose &> /dev/null; then
    echo "Docker Compose services:"
    docker-compose ps 2>/dev/null || echo "No docker-compose.yml found or services not running"
    
    if [ -f "docker-compose.enhanced.yml" ]; then
        echo ""
        echo "Enhanced Docker services:"
        docker-compose -f docker-compose.enhanced.yml ps 2>/dev/null || echo "Enhanced services not running"
    fi
else
    echo "Docker Compose not available"
fi

echo ""
echo -e "${YELLOW}📈 Database Connection Test${NC}"
echo "============================"

# Test database connection (if PostgreSQL is accessible)
if command -v psql &> /dev/null; then
    echo "Testing PostgreSQL connection..."
    if PGPASSWORD=password psql -h localhost -U postgres -d ai_startup_analyst -c "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✅ Database: Connected${NC}"
        
        # Check tables
        table_count=$(PGPASSWORD=password psql -h localhost -U postgres -d ai_startup_analyst -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
        echo "   Tables in database: $table_count"
    else
        echo -e "${RED}❌ Database: Connection failed${NC}"
    fi
else
    echo "psql not available for database testing"
fi

echo ""
echo -e "${YELLOW}🎯 Test Summary${NC}"
echo "==============="

# Overall system health assessment
healthy_services=0
total_services=3

# Count healthy services based on previous tests
if curl -s "$API_GATEWAY/health" &> /dev/null; then
    ((healthy_services++))
fi

if curl -s "$ENHANCED_INGESTION/health" &> /dev/null; then
    ((healthy_services++))
fi

if curl -s "$DATA_CURATION/health" &> /dev/null; then
    ((healthy_services++))
fi

echo "Services Status: $healthy_services/$total_services healthy"

if [ $healthy_services -eq $total_services ]; then
    echo -e "${GREEN}🎉 System Status: ALL SYSTEMS OPERATIONAL${NC}"
    echo ""
    echo -e "${GREEN}✅ Enhanced AI Startup Analyst is ready for use!${NC}"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:5173"
    echo "   API Gateway: http://localhost:3000"
    echo "   Enhanced Ingestion: http://localhost:8002"
    echo "   Data Curation: http://localhost:3003"
    echo ""
    echo "📚 Documentation:"
    echo "   Setup Guide: ./ENHANCED_SETUP.md"
    echo "   Implementation Summary: ./IMPLEMENTATION_SUMMARY.md"
elif [ $healthy_services -gt 0 ]; then
    echo -e "${YELLOW}⚠️  System Status: PARTIALLY OPERATIONAL${NC}"
    echo "Some services are running but not all systems are available."
    echo "Check docker-compose logs for more details."
else
    echo -e "${RED}❌ System Status: SERVICES DOWN${NC}"
    echo "No services are responding. Please check:"
    echo "1. Start services: docker-compose -f docker-compose.enhanced.yml up -d"
    echo "2. Check service logs: docker-compose logs"
    echo "3. Verify environment configuration"
fi

echo ""
echo "🧪 Test completed at $(date)"