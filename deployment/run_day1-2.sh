#!/bin/bash
# Simplified Day 1-2 Execution Script
# Runs verification with virtual environment

cd "$(dirname "$0")"

echo "=========================================="
echo "GATRA Day 1-2: Data Collection Setup"
echo "=========================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source venv/bin/activate
else
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install requests pyyaml --quiet
fi

echo ""
echo "Step 1: Verifying Data Sources"
echo "--------------------------------"
python3 verify_data_sources.py

echo ""
echo "Step 2: Testing Log Ingestion"
echo "--------------------------------"
python3 test_log_ingestion.py

echo ""
echo "=========================================="
echo "Day 1-2 Execution Complete"
echo "=========================================="
echo ""
echo "Review results:"
echo "  - deployment/data_source_verification.json"
echo ""
echo "Next: Configure endpoints in config.yaml if needed"
echo "      Then proceed to Day 3-5: Agent 1 Deployment"

