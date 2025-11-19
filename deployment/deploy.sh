#!/bin/bash
# GATRA Platform Deployment Script
# Week 1: Foundation Deployment

set -e  # Exit on error

echo "=========================================="
echo "GATRA Platform Deployment"
echo "Starting Week 1: Foundation Deployment"
echo "=========================================="

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${DEPLOYMENT_DIR}/config.yaml"
VENV_DIR="${DEPLOYMENT_DIR}/venv"
PYTHON_VERSION="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v $PYTHON_VERSION &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check config file
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        $PYTHON_VERSION -m venv "$VENV_DIR"
        log_info "Virtual environment created"
    fi
    
    source "${VENV_DIR}/bin/activate"
    pip install --upgrade pip --quiet
    pip install -q python-pptx pyyaml  # Add other dependencies as needed
    
    log_info "Virtual environment ready"
}

deploy_agent1() {
    log_info "Deploying Agent 1: Autonomous Tempo Detector..."
    
    # Copy agent code
    cp "${DEPLOYMENT_DIR}/agent1_tempo_detector.py" /opt/gatra/agents/
    
    # Create systemd service (if on Linux)
    if command -v systemctl &> /dev/null; then
        cat > /etc/systemd/system/gatra-agent1.service << EOF
[Unit]
Description=GATRA Agent 1: Autonomous Tempo Detector
After=network.target

[Service]
Type=simple
User=gatra
WorkingDirectory=/opt/gatra/agents
ExecStart=${VENV_DIR}/bin/python agent1_tempo_detector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable gatra-agent1
        systemctl start gatra-agent1
        log_info "Agent 1 service started"
    else
        log_warn "systemctl not available, manual service setup required"
    fi
}

deploy_agent3_4() {
    log_info "Deploying Agent 3: Data Exfiltration Analyzer..."
    cp "${DEPLOYMENT_DIR}/agent3_exfiltration_analyzer.py" /opt/gatra/agents/
    
    log_info "Deploying Agent 4: Lateral Movement Mapper..."
    # Agent 4 code would go here
    
    log_info "Agents 3 & 4 deployed"
}

validate_deployment() {
    log_info "Validating deployment..."
    
    # Check if agents are running
    if command -v systemctl &> /dev/null; then
        if systemctl is-active --quiet gatra-agent1; then
            log_info "Agent 1 is running"
        else
            log_error "Agent 1 is not running"
            return 1
        fi
    fi
    
    log_info "Deployment validation passed"
}

# Main execution
main() {
    log_info "Starting deployment process..."
    
    check_prerequisites
    setup_venv
    
    # Create deployment directories
    mkdir -p /opt/gatra/agents
    mkdir -p /opt/gatra/config
    mkdir -p /opt/gatra/logs
    
    # Copy configuration
    cp "$CONFIG_FILE" /opt/gatra/config/
    
    # Deploy agents (Week 1)
    deploy_agent1
    
    # Validate
    validate_deployment
    
    log_info "=========================================="
    log_info "Week 1 Foundation Deployment Complete"
    log_info "Next: Deploy Agents 3 & 4 (Days 5-7)"
    log_info "=========================================="
}

# Run main function
main "$@"

