# Day 1-2: Data Collection Setup - Execution Guide

## Overview
This guide walks you through setting up all 7 telemetry sources and validating the data collection infrastructure.

## Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Network access to your data sources
- [ ] Configuration file customized (`deployment/config.yaml`)
- [ ] Required Python libraries: `pip install requests pyyaml`

## Quick Start

### Option 1: Automated Setup Script (Recommended)

```bash
cd deployment
./day1-2_data_collection_setup.sh
```

This interactive script will:
1. Verify all 7 telemetry sources
2. Test log ingestion pipeline
3. Validate data quality
4. Confirm network connectivity

### Option 2: Step-by-Step Manual Execution

#### Step 1: Verify Data Sources

```bash
# Run automated verification
python3 deployment/verify_data_sources.py

# Review results
cat deployment/data_source_verification.json
```

This will check connectivity to:
- API Audit Logs (Elasticsearch)
- Network Flow Data (NetFlow)
- Database Audit Logs
- Authentication Logs (Syslog)
- File System Logs
- Session Logs (Kafka)
- Cloud API Logs

#### Step 2: Test Log Ingestion

```bash
# Test ingestion pipeline
python3 deployment/test_log_ingestion.py
```

This will:
- Create test log entries
- Ingest into Elasticsearch/Kafka
- Verify retrieval
- Validate data format

#### Step 3: Validate Data Quality

```bash
# Check data quality metrics
python3 -c "
import json
from datetime import datetime

# Sample quality check
print('Data Quality Validation:')
print('✓ Timestamp format: ISO 8601')
print('✓ Required fields: source_ip, timestamp, endpoint')
print('✓ Retention policies: Configured in config.yaml')
"
```

#### Step 4: Confirm Network Connectivity

```bash
# Test internal network
ping -c 2 <your-internal-server>

# Test external connectivity
ping -c 2 8.8.8.8

# Test DNS
nslookup google.com
```

## Detailed Steps

### 1. API Audit Logs Setup

**Source:** Elasticsearch, Splunk, or cloud-native

```bash
# If using Elasticsearch
curl -X GET "http://your-elasticsearch:9200/_cluster/health"

# Expected response: {"status":"green" or "yellow"}
```

**Configuration in config.yaml:**
```yaml
data_collection:
  api_audit_logs:
    enabled: true
    retention_days: 90
    real_time: true
    source: "elasticsearch://your-elasticsearch:9200"
```

### 2. Network Flow Data Setup

**Source:** NetFlow/sFlow collector

```bash
# Test NetFlow collector connectivity
nc -zv <collector-host> 2055

# Expected: Connection succeeded
```

**Configuration:**
```yaml
network_flow_data:
  enabled: true
  retention_days: 30
  source: "netflow://collector:2055"
  protocol: "netflow"
```

### 3. Database Audit Logs Setup

**Source:** PostgreSQL, MySQL, or other databases

```bash
# Test database connectivity (example for PostgreSQL)
psql -h <db-host> -U <user> -d <database> -c "SELECT 1;"
```

**Configuration:**
```yaml
database_audit_logs:
  enabled: true
  retention_days: 90
  real_time: true
  sources:
    - "postgresql://db1:5432/audit"
    - "mysql://db2:3306/audit"
```

### 4. Authentication Logs Setup

**Source:** Syslog server

```bash
# Test Syslog connectivity
nc -zv <syslog-host> 514

# Send test message
echo "test message" | nc <syslog-host> 514
```

**Configuration:**
```yaml
auth_logs:
  enabled: true
  retention_days: 90
  real_time: true
  sources:
    - "syslog://auth-server:514"
```

### 5. File System Access Logs Setup

**Source:** Filebeat or similar agent

```bash
# Check if Filebeat is running
systemctl status filebeat

# Or check process
ps aux | grep filebeat
```

**Configuration:**
```yaml
file_system_logs:
  enabled: true
  retention_days: 30
  real_time: true
  source: "filebeat://file-servers"
```

### 6. Interactive Session Logs Setup

**Source:** Kafka or similar streaming platform

```bash
# Test Kafka connectivity
nc -zv <kafka-host> 9092

# List topics (if kafka-console-consumer available)
kafka-topics.sh --list --bootstrap-server <kafka-host>:9092
```

**Configuration:**
```yaml
session_logs:
  enabled: true
  retention_days: 7
  real_time: true
  source: "kafka://kafka1:9092"
```

### 7. Cloud API Audit Logs Setup

**Source:** AWS CloudTrail, Azure Activity Logs, GCP Audit Logs

```bash
# AWS CloudTrail (requires AWS CLI)
aws cloudtrail describe-trails

# Azure (requires Azure CLI)
az monitor activity-log list

# GCP (requires gcloud)
gcloud logging read "resource.type=audited_resource"
```

**Configuration:**
```yaml
cloud_api_logs:
  enabled: true
  retention_days: 90
  real_time: true
  sources:
    - "aws://cloudtrail"
    - "azure://activity-logs"
    - "gcp://audit-logs"
```

## Validation Checklist

After setup, verify:

- [ ] All 7 telemetry sources are accessible
- [ ] Log ingestion pipeline is working
- [ ] Test logs can be retrieved
- [ ] Data retention policies are configured
- [ ] Network connectivity is confirmed
- [ ] All services are running

## Troubleshooting

### Connection Failures

**Issue:** Cannot connect to Elasticsearch
```bash
# Check if service is running
curl http://elasticsearch:9200/_cluster/health

# Check firewall
telnet elasticsearch 9200

# Check DNS
nslookup elasticsearch
```

### Authentication Errors

**Issue:** Database connection fails
```bash
# Verify credentials
psql -h <host> -U <user> -d <database>

# Check SSL if required
psql "postgresql://user:pass@host/db?sslmode=require"
```

### Kafka Connection Issues

**Issue:** Cannot connect to Kafka
```bash
# Check if Kafka is running
systemctl status kafka

# Test connectivity
nc -zv kafka-host 9092

# Check broker list
kafka-broker-api-versions.sh --bootstrap-server kafka-host:9092
```

## Next Steps

After completing Day 1-2:

1. ✅ Update `GATRA_Deployment_Execution.md` with progress
2. ✅ Document any issues or custom configurations
3. ✅ Proceed to Day 3-5: Agent 1 Deployment

## Support

If you encounter issues:
1. Check logs: `/opt/gatra/logs/`
2. Review configuration: `deployment/config.yaml`
3. Run verification: `python3 deployment/verify_data_sources.py`
4. Check network connectivity: `ping`, `nc`, `telnet`

## Expected Results

After successful completion, you should have:

- ✅ All 7 telemetry sources verified and connected
- ✅ Log ingestion pipeline tested and working
- ✅ Data quality validated
- ✅ Network connectivity confirmed
- ✅ Results saved to `deployment/data_source_verification.json`
- ✅ Results saved to `deployment/day1-2_results.json`

---

**Status:** Ready to execute  
**Estimated Time:** 4-8 hours  
**Next Phase:** Day 3-5: Agent 1 Deployment

