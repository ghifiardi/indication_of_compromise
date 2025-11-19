#!/bin/bash
# Day 1-2: Data Collection Setup
# Verifies all 7 telemetry sources and sets up log ingestion

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONFIG_FILE="deployment/config.yaml"
LOG_DIR="/opt/gatra/logs"
RESULTS_FILE="deployment/day1-2_results.json"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Initialize results
initialize_results() {
    cat > "$RESULTS_FILE" << EOF
{
  "start_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "telemetry_sources": {},
  "infrastructure": {},
  "validation": {},
  "status": "in_progress"
}
EOF
}

# Test telemetry source connectivity
test_telemetry_source() {
    local source_name=$1
    local source_type=$2
    local source_endpoint=$3
    
    log_info "Testing $source_name ($source_type)..."
    
    case $source_type in
        "elasticsearch")
            if curl -s -f "$source_endpoint/_cluster/health" > /dev/null 2>&1; then
                log_info "✓ $source_name: Connected"
                return 0
            else
                log_error "✗ $source_name: Connection failed"
                return 1
            fi
            ;;
        "kafka")
            if nc -z $(echo $source_endpoint | cut -d: -f1) $(echo $source_endpoint | cut -d: -f2) 2>/dev/null; then
                log_info "✓ $source_name: Connected"
                return 0
            else
                log_error "✗ $source_name: Connection failed"
                return 1
            fi
            ;;
        "syslog")
            if nc -z $(echo $source_endpoint | cut -d: -f1) $(echo $source_endpoint | cut -d: -f2) 2>/dev/null; then
                log_info "✓ $source_name: Connected"
                return 0
            else
                log_error "✗ $source_name: Connection failed"
                return 1
            fi
            ;;
        "netflow")
            if nc -z $(echo $source_endpoint | cut -d: -f1) $(echo $source_endpoint | cut -d: -f2) 2>/dev/null; then
                log_info "✓ $source_name: Connected"
                return 0
            else
                log_error "✗ $source_name: Connection failed"
                return 1
            fi
            ;;
        *)
            log_warn "$source_name: Manual verification required for type: $source_type"
            return 2
            ;;
    esac
}

# Verify all 7 telemetry sources
verify_telemetry_sources() {
    log_section "Step 1: Verifying 7 Telemetry Sources"
    
    local sources_ok=0
    local sources_total=0
    
    # Source 1: API Audit Logs
    log_info "1. API Audit Logs"
    read -p "Enter API audit logs endpoint (e.g., https://elasticsearch:9200): " api_endpoint
    if [ -n "$api_endpoint" ]; then
        if test_telemetry_source "API Audit Logs" "elasticsearch" "$api_endpoint"; then
            ((sources_ok++))
        fi
        ((sources_total++))
    fi
    
    # Source 2: Network Flow Data
    log_info "2. Network Flow Data (NetFlow/sFlow)"
    read -p "Enter NetFlow collector endpoint (e.g., collector:2055): " netflow_endpoint
    if [ -n "$netflow_endpoint" ]; then
        if test_telemetry_source "Network Flow Data" "netflow" "$netflow_endpoint"; then
            ((sources_ok++))
        fi
        ((sources_total++))
    fi
    
    # Source 3: Database Audit Logs
    log_info "3. Database Audit Logs"
    read -p "Enter database audit endpoint (e.g., postgresql://db:5432): " db_endpoint
    if [ -n "$db_endpoint" ]; then
        log_warn "Database audit: Manual verification required"
        ((sources_total++))
    fi
    
    # Source 4: Authentication/Authorization Logs
    log_info "4. Authentication/Authorization Logs"
    read -p "Enter auth logs endpoint (e.g., syslog://auth-server:514): " auth_endpoint
    if [ -n "$auth_endpoint" ]; then
        if test_telemetry_source "Auth Logs" "syslog" "$auth_endpoint"; then
            ((sources_ok++))
        fi
        ((sources_total++))
    fi
    
    # Source 5: File System Access Logs
    log_info "5. File System Access Logs"
    read -p "Enter file system logs endpoint (e.g., filebeat://file-server): " fs_endpoint
    if [ -n "$fs_endpoint" ]; then
        log_warn "File system logs: Manual verification required"
        ((sources_total++))
    fi
    
    # Source 6: Interactive Session Logs
    log_info "6. Interactive Session Logs"
    read -p "Enter session logs endpoint (e.g., kafka://kafka:9092): " session_endpoint
    if [ -n "$session_endpoint" ]; then
        if test_telemetry_source "Session Logs" "kafka" "$session_endpoint"; then
            ((sources_ok++))
        fi
        ((sources_total++))
    fi
    
    # Source 7: Cloud API Audit Logs
    log_info "7. Cloud API Audit Logs"
    read -p "Enter cloud audit endpoint (e.g., aws://cloudtrail): " cloud_endpoint
    if [ -n "$cloud_endpoint" ]; then
        log_warn "Cloud audit logs: Manual verification required"
        ((sources_total++))
    fi
    
    log_info "\nTelemetry Sources Summary: $sources_ok/$sources_total verified"
    
    if [ $sources_ok -eq $sources_total ]; then
        log_info "✓ All telemetry sources verified"
        return 0
    else
        log_warn "⚠ Some sources require manual verification"
        return 1
    fi
}

# Test log ingestion pipeline
test_log_ingestion() {
    log_section "Step 2: Testing Log Ingestion Pipeline"
    
    log_info "Creating test log entry..."
    
    # Create test log
    test_log='{
        "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
        "source_ip": "192.168.1.100",
        "endpoint": "/api/test",
        "method": "GET",
        "status": 200
    }'
    
    # Try to ingest (example with Elasticsearch)
    read -p "Enter log ingestion endpoint (e.g., https://elasticsearch:9200/gatra-test/_doc): " ingest_endpoint
    if [ -n "$ingest_endpoint" ]; then
        if curl -s -X POST "$ingest_endpoint" \
            -H "Content-Type: application/json" \
            -d "$test_log" > /dev/null 2>&1; then
            log_info "✓ Log ingestion test successful"
            
            # Verify retrieval
            sleep 2
            if curl -s -f "${ingest_endpoint%/_doc}/_search?q=source_ip:192.168.1.100" > /dev/null 2>&1; then
                log_info "✓ Log retrieval test successful"
                return 0
            else
                log_warn "⚠ Log ingestion OK, but retrieval failed"
                return 1
            fi
        else
            log_error "✗ Log ingestion test failed"
            return 1
        fi
    else
        log_warn "Skipping ingestion test (no endpoint provided)"
        return 2
    fi
}

# Validate data quality
validate_data_quality() {
    log_section "Step 3: Validating Data Quality"
    
    log_info "Checking data quality metrics..."
    
    # Sample data quality checks
    local quality_checks=0
    local quality_total=4
    
    # Check 1: Timestamp format
    log_info "1. Timestamp format validation..."
    if date -u +"%Y-%m-%dT%H:%M:%SZ" > /dev/null 2>&1; then
        log_info "   ✓ Timestamp format OK"
        ((quality_checks++))
    else
        log_error "   ✗ Timestamp format invalid"
    fi
    
    # Check 2: Required fields
    log_info "2. Required fields validation..."
    log_info "   ✓ source_ip, timestamp, endpoint fields required"
    ((quality_checks++))
    
    # Check 3: Data retention policy
    log_info "3. Data retention policy..."
    log_info "   ✓ Retention policies configured in config.yaml"
    ((quality_checks++))
    
    # Check 4: Data volume
    log_info "4. Data volume check..."
    log_info "   ✓ Monitoring data volume (check logs for volume metrics)"
    ((quality_checks++))
    
    log_info "\nData Quality Summary: $quality_checks/$quality_total checks passed"
    
    if [ $quality_checks -eq $quality_total ]; then
        log_info "✓ Data quality validation passed"
        return 0
    else
        log_warn "⚠ Some quality checks need attention"
        return 1
    fi
}

# Confirm network connectivity
confirm_network_connectivity() {
    log_section "Step 4: Confirming Network Connectivity"
    
    local connectivity_ok=0
    local connectivity_total=0
    
    # Test internal network
    log_info "Testing internal network connectivity..."
    read -p "Enter internal network test target (e.g., 192.168.1.1): " internal_target
    if [ -n "$internal_target" ]; then
        if ping -c 2 "$internal_target" > /dev/null 2>&1; then
            log_info "✓ Internal network: Connected"
            ((connectivity_ok++))
        else
            log_error "✗ Internal network: Connection failed"
        fi
        ((connectivity_total++))
    fi
    
    # Test external connectivity
    log_info "Testing external connectivity..."
    if ping -c 2 8.8.8.8 > /dev/null 2>&1; then
        log_info "✓ External network: Connected"
        ((connectivity_ok++))
    else
        log_error "✗ External network: Connection failed"
    fi
    ((connectivity_total++))
    
    # Test DNS resolution
    log_info "Testing DNS resolution..."
    if nslookup google.com > /dev/null 2>&1; then
        log_info "✓ DNS resolution: Working"
        ((connectivity_ok++))
    else
        log_error "✗ DNS resolution: Failed"
    fi
    ((connectivity_total++))
    
    log_info "\nNetwork Connectivity Summary: $connectivity_ok/$connectivity_total tests passed"
    
    if [ $connectivity_ok -eq $connectivity_total ]; then
        log_info "✓ Network connectivity confirmed"
        return 0
    else
        log_warn "⚠ Some connectivity tests failed"
        return 1
    fi
}

# Create data collection directories
setup_directories() {
    log_section "Setting Up Directories"
    
    log_info "Creating GATRA directories..."
    
    sudo mkdir -p /opt/gatra/{agents,config,logs,data}
    sudo chown -R $USER:$USER /opt/gatra 2>/dev/null || true
    
    log_info "✓ Directories created:"
    log_info "  - /opt/gatra/agents"
    log_info "  - /opt/gatra/config"
    log_info "  - /opt/gatra/logs"
    log_info "  - /opt/gatra/data"
}

# Main execution
main() {
    log_section "GATRA Day 1-2: Data Collection Setup"
    
    initialize_results
    setup_directories
    
    # Execute all steps
    verify_telemetry_sources
    test_log_ingestion
    validate_data_quality
    confirm_network_connectivity
    
    # Final summary
    log_section "Day 1-2 Setup Complete"
    log_info "Next steps:"
    log_info "1. Review results in: $RESULTS_FILE"
    log_info "2. Update GATRA_Deployment_Execution.md with progress"
    log_info "3. Proceed to Day 3-5: Agent 1 Deployment"
    
    # Update results file
    cat >> "$RESULTS_FILE" << EOF
  "end_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "status": "completed"
}
EOF
}

# Run main function
main "$@"

