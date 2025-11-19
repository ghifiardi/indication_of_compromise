# Understanding "Endpoints" in Day 1-2 Data Collection Setup

## Clarification: Endpoints = Infrastructure Assets (NOT GATRA Agents)

### What Are "Endpoints" in This Context?

**Endpoints** refer to **existing infrastructure assets** in your environment that **generate logs and telemetry data**. These are NOT the GATRA AI agents we're building.

### The 7 Telemetry Sources Are Infrastructure Endpoints:

#### 1. API Audit Logs Endpoint
**What it is:** Your API gateway, API server, or application server that logs API requests
- **Examples:**
  - Elasticsearch cluster storing API logs: `https://elasticsearch.company.com:9200`
  - Splunk instance: `https://splunk.company.com:8089`
  - API Gateway (AWS API Gateway, Kong, etc.)
  - Application server logs (Nginx, Apache, etc.)

**What GATRA does:** Connects to this endpoint to read API audit logs

---

#### 2. Network Flow Data Endpoint
**What it is:** Your NetFlow/sFlow collector that captures network traffic
- **Examples:**
  - NetFlow collector server: `netflow-collector.company.com:2055`
  - sFlow collector: `sflow-collector.company.com:6343`
  - Network monitoring tool (PRTG, SolarWinds, etc.)

**What GATRA does:** Connects to this endpoint to read network flow data

---

#### 3. Database Audit Logs Endpoint
**What it is:** Your database servers that log database access and queries
- **Examples:**
  - PostgreSQL server: `postgresql://db-server.company.com:5432/audit_db`
  - MySQL server: `mysql://db-server.company.com:3306/audit_db`
  - Oracle database: `oracle://db-server.company.com:1521/audit`
  - MongoDB: `mongodb://db-server.company.com:27017/audit`

**What GATRA does:** Connects to these databases to read audit logs

---

#### 4. Authentication/Authorization Logs Endpoint
**What it is:** Your authentication servers or syslog servers that log login attempts
- **Examples:**
  - Syslog server: `syslog://auth-server.company.com:514`
  - LDAP/Active Directory server: `ldap://ad-server.company.com:389`
  - SSO provider logs (Okta, Auth0, etc.)
  - Linux/Unix system logs

**What GATRA does:** Connects to this endpoint to read authentication logs

---

#### 5. File System Access Logs Endpoint
**What it is:** Your file servers or Filebeat agents that log file access
- **Examples:**
  - Filebeat agent on file servers: `filebeat://file-server-01.company.com`
  - Windows Event Logs (file access events)
  - Network File System (NFS) logs
  - SMB/CIFS access logs

**What GATRA does:** Connects to Filebeat or file server logs to read file access events

---

#### 6. Interactive Session Logs Endpoint
**What it is:** Your Kafka cluster or streaming platform that handles session logs
- **Examples:**
  - Kafka brokers: `kafka://kafka-01.company.com:9092,kafka-02.company.com:9092`
  - AWS Kinesis: `kinesis://stream-name`
  - RabbitMQ: `rabbitmq://mq-server.company.com:5672`
  - Session management system logs

**What GATRA does:** Connects to Kafka/Kinesis to read session logs

---

#### 7. Cloud API Audit Logs Endpoint
**What it is:** Your cloud provider's audit logging service
- **Examples:**
  - AWS CloudTrail: `aws://cloudtrail` (requires AWS credentials)
  - Azure Activity Logs: `azure://activity-logs` (requires Azure credentials)
  - GCP Audit Logs: `gcp://audit-logs` (requires GCP credentials)
  - CloudWatch, Azure Monitor, etc.

**What GATRA does:** Connects to cloud provider APIs to read audit logs

---

## Visual Flow

```
┌─────────────────────────────────────────────────────────┐
│         YOUR EXISTING INFRASTRUCTURE                    │
│  (These are the "endpoints" we're connecting to)       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [API Gateway] ────┐                                    │
│  [Database] ───────┼───┐                                │
│  [Auth Server] ────┼───┼───┐                            │
│  [File Server] ────┼───┼───┼───┐                        │
│  [Kafka] ──────────┼───┼───┼───┼───┐                    │
│  [NetFlow] ────────┼───┼───┼───┼───┼───┐                │
│  [Cloud APIs] ─────┼───┼───┼───┼───┼───┼───┐            │
│                    │   │   │   │   │   │   │            │
│                    └───┴───┴───┴───┴───┴───┴───┘         │
│                            │                             │
│                            ▼                             │
│                    [Data Collection Layer]               │
│                    (GATRA connects here)                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              GATRA PLATFORM                              │
│  (What we're BUILDING - these are the AI agents)        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Agent 1: Tempo Detector ────┐                          │
│  Agent 2: Phase Tracker ─────┼───┐                      │
│  Agent 3: Exfil Analyzer ─────┼───┼───┐                  │
│  Agent 4: Lateral Movement ──┼───┼───┼───┐              │
│  Agent 5: MCP Detector ───────┼───┼───┼───┼───┐          │
│                              │   │   │   │   │          │
│                              └───┴───┴───┴───┴───┘       │
│                                    │                     │
│                                    ▼                     │
│                          [Correlation Engine]            │
│                          [Response Automation]           │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

### Endpoints (Infrastructure Assets) = DATA SOURCES
- **What they are:** Existing servers, databases, APIs, log collectors in your environment
- **What they do:** Generate logs and telemetry data
- **Where they are:** Already running in your infrastructure
- **What we do:** Connect GATRA to read from them

### GATRA Agents = DATA CONSUMERS & ANALYZERS
- **What they are:** AI agents we're building (Agent 1-5)
- **What they do:** Analyze the data from endpoints to detect attacks
- **Where they are:** Being deployed as part of GATRA platform
- **What we do:** Build and deploy them

---

## Example Configuration

When you configure `config.yaml`, you're telling GATRA **where to find** your existing infrastructure:

```yaml
data_collection:
  api_audit_logs:
    source: "elasticsearch://your-elasticsearch-server:9200"  # ← Your existing Elasticsearch
    # This is where YOUR API logs are stored
  
  database_audit_logs:
    sources:
      - "postgresql://your-db-server:5432/audit"  # ← Your existing database
      # This is where YOUR database audit logs are stored
```

**You're not creating these endpoints** - you're pointing GATRA to your **existing infrastructure** that already generates logs.

---

## Questions to Identify Your Endpoints

To complete Day 1-2, you need to identify:

1. **Where are your API logs stored?** (Elasticsearch? Splunk? CloudWatch?)
2. **Where is your NetFlow collector?** (What server/port?)
3. **Where are your database audit logs?** (Which databases? What connection strings?)
4. **Where are your authentication logs?** (Syslog server? AD server?)
5. **Where are your file access logs?** (Filebeat? Windows Event Logs?)
6. **Where are your session logs?** (Kafka? Kinesis? What brokers?)
7. **Where are your cloud audit logs?** (AWS? Azure? GCP? What regions?)

These are all **existing assets** in your infrastructure that GATRA will connect to.

