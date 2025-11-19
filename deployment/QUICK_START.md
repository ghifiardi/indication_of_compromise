# GATRA Deployment Quick Start Guide

## Prerequisites

Before starting deployment, ensure you have:

- ✅ Python 3.8+ installed
- ✅ Access to all 7 telemetry sources
- ✅ Infrastructure access (servers, cloud resources)
- ✅ Network connectivity to data sources
- ✅ Configuration file (`config.yaml`) customized for your environment

## Day 1-2: Data Collection Setup

### Step 1: Verify Telemetry Sources

```bash
# Check each telemetry source
./deployment/verify_sources.sh
```

### Step 2: Configure Data Collection

1. Edit `deployment/config.yaml`
2. Update data collection sources for your environment
3. Set retention policies
4. Test connectivity to each source

### Step 3: Set Up Infrastructure

```bash
# Set up log aggregation (Elasticsearch example)
docker-compose up -d elasticsearch

# Set up streaming (Kafka example)
docker-compose up -d kafka

# Verify infrastructure
./deployment/verify_infrastructure.sh
```

## Day 3-5: Agent 1 Deployment

### Step 1: Deploy Agent 1

```bash
cd deployment
./deploy.sh
```

### Step 2: Configure Thresholds

Edit `config.yaml`:
```yaml
agent1_tempo_detector:
  tempo_threshold: 2.0  # ops/sec
  duration_threshold: 900  # 15 minutes
  investigate_threshold: 0.70
  isolate_threshold: 0.85
```

### Step 3: Test Agent 1

```bash
python3 test_framework.py
```

### Step 4: Monitor False Positives

```bash
# Monitor for 24 hours
./monitor_false_positives.sh --duration 24h
```

## Day 5-7: Agents 3 & 4 Deployment

### Step 1: Deploy Agents

```bash
# Deploy Agent 3 (Exfiltration Analyzer)
cp agent3_exfiltration_analyzer.py /opt/gatra/agents/

# Deploy Agent 4 (Lateral Movement Mapper)
# (Code to be added)
```

### Step 2: Configure Integration

1. Set up SOAR platform integration
2. Configure alerting rules
3. Test incident response workflows

## Testing

### Run All Tests

```bash
python3 deployment/test_framework.py
```

### Test Individual Agents

```python
from agent1_tempo_detector import AutonomousTempoDetector

detector = AutonomousTempoDetector(DEFAULT_CONFIG)
alerts = detector.detect_autonomous_activity(sample_logs)
```

## Monitoring

### Check Agent Status

```bash
# If using systemd
systemctl status gatra-agent1

# Check logs
tail -f /opt/gatra/logs/agent1.log
```

### View Metrics

- Detection speed: Target <5 minutes
- False positive rate: Target <3%
- System performance: CPU, Memory usage

## Troubleshooting

### Agent Not Starting

1. Check Python version: `python3 --version`
2. Verify dependencies: `pip list`
3. Check logs: `/opt/gatra/logs/`

### High False Positive Rate

1. Review threshold settings in `config.yaml`
2. Analyze false positive patterns
3. Adjust confidence thresholds
4. Re-test

### Performance Issues

1. Check resource utilization
2. Review auto-scaling configuration
3. Optimize query patterns
4. Scale infrastructure if needed

## Next Steps

After Week 1 completion:

1. ✅ Review deployment execution tracker
2. ✅ Validate all systems operational
3. ✅ Document any issues or adjustments
4. ✅ Proceed to Week 2: Agent 2 deployment

## Support

For issues or questions:
- Check deployment logs: `/opt/gatra/logs/`
- Review configuration: `deployment/config.yaml`
- Consult deployment tracker: `GATRA_Deployment_Execution.md`

