# Server Demise Pipeline - Quick Reference

## 🚀 Start System
```bash
cd /root/kafka

# 1. Start Kafka services
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
bin/kafka-server-start.sh -daemon config/server.properties

# 2. Set Java environment
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64

# 3. Create topic
bin/kafka-topics.sh --create --topic server-demise-pipeline \
  --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# 4. Start pipeline
cd kafka-processors
python3 processor_manager_new.py &
python3 -m uvicorn api.main_new:app --host 0.0.0.0 --port 8082 &
```

## 📡 API Examples

### Single Server
```bash
curl -X POST "http://localhost:8082/demise-server" \
  -H "Content-Type: application/json" \
  -d '{"server_id": "SRV001", "reason": "EOL", "requester": "ops"}'
```

### Batch Servers  
```bash
curl -X POST "http://localhost:8082/batch-demise-servers" \
  -H "Content-Type: application/json" \
  -d '{"server_ids": ["150","250"], "reason": "Migration", "requester": "admin"}'
```

### Health Check
```bash
curl http://localhost:8082/health
```

## 🔄 Pipeline Flow
```
API → check_server → poweroff_server → demise_server → complete
```

## 📋 Server ID Formats
- **Numeric**: `100-999` ✅ Valid
- **Named**: `SRV*`, `HOST*`, `VM*`, `PROD*`, `TEST*` ✅ Valid
- **Examples**: `150`, `SRV001`, `HOST-WEB-01`, `PROD-DB-PRIMARY`

## 🎯 Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/demise-server` | POST | Single server decommission |
| `/batch-demise-servers` | POST | Multiple server decommission |
| `/health` | GET | System health check |
| `/pipeline-status` | GET | Pipeline information |
| `/docs` | GET | API documentation |

## 🛠️ Quick Troubleshooting
```bash
# Check if Kafka is running
jps | grep -E "QuorumPeerMain|Kafka"

# List topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Kill API if port busy
pkill -f "uvicorn.*8082"

# Test system
python3 test_demise_pipeline.py
```

## ⚡ System Info
- **API Port**: 8082
- **Topic**: server-demise-pipeline  
- **Workers**: 9 total (3 per processor)
- **Processors**: ServerCheck → ServerPowerOff → ServerDemise