# Kafka Processors System

A complete Kafka-based message processing system with REST API and concurrent processors for handling `show_details`, `update_details`, and `create_details` operations.

## 🏗️ Architecture

### Components

1. **Kafka Server** - Message broker for event streaming
2. **REST API** - FastAPI-based endpoint for sending events
3. **Processor Manager** - Coordinates multiple processor instances
4. **Processors** - Handle specific business logic for each action type
5. **Configuration System** - Centralized configuration management

### Message Flow

# Server Demise Pipeline

A Kafka-based sequential processing system for automated server decommissioning workflow.

## 🚀 Quick Start

```bash
# Start Kafka & Zookeeper
cd /root/kafka
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
bin/kafka-server-start.sh -daemon config/server.properties

# Create topic
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
bin/kafka-topics.sh --create --topic server-demise-pipeline --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Start system
cd kafka-processors
python3 processor_manager_new.py &  # Start processors
python3 -m uvicorn api.main_new:app --host 0.0.0.0 --port 8082 &  # Start API
```

## 📋 API Endpoints

### Single Server Decommission
```bash
curl -X POST "http://localhost:8082/demise-server" \
  -H "Content-Type: application/json" \
  -d '{"server_id": "150", "reason": "End of life", "requester": "ops_team"}'
```

### Batch Server Decommission
```bash
curl -X POST "http://localhost:8082/batch-demise-servers" \
  -H "Content-Type: application/json" \
  -d '{"server_ids": ["SRV001", "HOST-WEB-01"], "reason": "Migration", "requester": "admin"}'
```

### Health Check
```bash
curl http://localhost:8082/health
```

### Pipeline Status
```bash
curl http://localhost:8082/pipeline-status
```

## 🔄 Pipeline Flow

```
API Request → Kafka Topic → Check Server → Power Off → Demise → Complete
     ↓              ↓             ↓           ↓          ↓         ↓
  REST API    server-demise-  Processor 1  Processor 2  Processor 3  Done
             pipeline topic
```

## 🏗️ Architecture

- **Single Topic Design**: All processors use `server-demise-pipeline` topic
- **Action-Based Routing**: Messages filtered by `action` field
- **Sequential Processing**: Each stage waits for previous completion
- **Multi-threaded**: 3 workers per processor (9 total)

## � Message Format

```json
{
  "id": "unique-message-id",
  "action": "check_server|poweroff_server|demise_server|demise_complete",
  "status": "pending|completed|failed|error",
  "processor": "processor-name",
  "pipeline_step": 0,
  "timestamp": "2025-11-02T10:17:27.952063Z",
  "data": {
    "server_id": "150",
    "reason": "End of life",
    "requester": "ops_team"
  }
}
```

## 🎯 Processor Details

| Step | Processor | Action | Purpose |
|------|-----------|--------|---------|
| 1 | ServerCheckProcessor | `check_server` | Verify server exists in portal |
| 2 | ServerPowerOffProcessor | `poweroff_server` | Execute IPMI/BMC power off |
| 3 | ServerDemiseProcessor | `demise_server` | Complete decommission workflow |

## 📊 Supported Server Formats

- **Numeric**: `100-999` (e.g., `150`, `250`)
- **Named**: `SRV*`, `HOST*`, `VM*`, `PROD*`, `TEST*`
- **Examples**: `SRV001`, `HOST-WEB-01`, `VM-TEST-123`, `PROD-DB-PRIMARY`

## 🏗️ System Architecture

### Core Design Principles
- **Single Topic Architecture**: All processors use `server-demise-pipeline` topic
- **Action-Based Message Routing**: Messages filtered by `action` field
- **Sequential Processing**: Each stage waits for previous completion
- **Fault Tolerance**: Kafka ensures message durability and replay capability
- **Horizontal Scalability**: Multiple workers per processor type

### Message Flow
```
HTTP Request → API → Kafka Topic → Check → PowerOff → Demise → Complete
     ↓           ↓        ↓          ↓        ↓         ↓         ↓
  FastAPI   JSON→Kafka  Consumer  Validate  IPMI    Cleanup   Done
```

## 📂 Complete Project Structure

```
kafka-processors/
├── 📁 api/
│   └── 📄 main_new.py              # FastAPI REST server for decommission requests
├── 📁 processors/
│   ├── 📄 base_processor.py        # Abstract base class for all processors  
│   ├── 📄 server_check_processor.py    # Stage 1: Server validation processor
│   ├── 📄 server_poweroff_processor.py # Stage 2: Server power-off processor
│   └── 📄 server_demise_processor.py   # Stage 3: Decommission workflow processor
├── 📁 config/
│   └── 📄 config.json              # System configuration and settings
├── 📁 utils/
│   └── 📄 config_manager.py        # Configuration management utility
├── 📄 processor_manager_new.py     # Main orchestrator for all processors
├── 📄 test_demise_pipeline.py      # Comprehensive test suite
├── 📄 README.md                    # This documentation
├── 📄 QUICK_REFERENCE.md           # Quick start and reference guide
├── 📄 documentation.html           # Web-based comprehensive documentation
├── 📄 manage_docs.sh               # Documentation server management script
└── 📄 persistent_docs_server.py    # Web server for documentation hosting
```

### 📋 File Descriptions

| File | Purpose | Key Components |
|------|---------|----------------|
| **api/main_new.py** | FastAPI server with decommission endpoints | /demise-server, /batch-demise-servers, /health, /pipeline-status |
| **processors/base_processor.py** | Abstract processor base class | Kafka consumer/producer, message filtering, threading |
| **processors/server_check_processor.py** | Stage 1: Server validation | Portal lookup, ID validation, success/failure handling |
| **processors/server_poweroff_processor.py** | Stage 2: Power management | IPMI/BMC simulation, power status verification |
| **processors/server_demise_processor.py** | Stage 3: Decommission workflow | 7-step cleanup process, monitoring removal, asset updates |
| **config/config.json** | System configuration | Kafka settings, worker counts, timeouts |
| **utils/config_manager.py** | Configuration management | JSON loading, environment overrides, defaults |
| **processor_manager_new.py** | Main orchestrator | ThreadPoolExecutor, 9 workers, signal handling |

## � Configuration

Edit `config/config.json`:

```json
{
  "kafka": {
    "bootstrap_servers": ["localhost:9092"],
    "topic": "server-demise-pipeline",
    "consumer_group": "demise-processor-group"
  },
  "processing": {
    "workers_per_processor": 3,
    "consumer_timeout_ms": 1000
  }
}
```

## � Monitoring

- **Logs**: Check processor logs for real-time processing
- **Health**: `GET /health` for API status
- **Pipeline**: `GET /pipeline-status` for system info

## ⚡ Performance

- **Throughput**: ~100 requests/minute per processor
- **Latency**: <5 seconds per pipeline stage
- **Concurrency**: 9 parallel workers
- **Reliability**: Kafka ensures message durability

## 🧪 Testing

```bash
# Run comprehensive tests
python3 test_demise_pipeline.py

# Test specific server
curl -X POST "http://localhost:8082/demise-server" \
  -H "Content-Type: application/json" \
  -d '{"server_id": "TEST-001", "reason": "Testing", "requester": "dev_team"}'
```

## 🛠️ Troubleshooting

### Common Issues

1. **Kafka Not Running**
   ```bash
   jps | grep -E "QuorumPeerMain|Kafka"  # Check if running
   ```

2. **Topic Not Found**
   ```bash
   bin/kafka-topics.sh --list --bootstrap-server localhost:9092
   ```

3. **Port 8082 In Use**
   ```bash
   pkill -f "uvicorn.*8082"  # Kill existing API
   ```

4. **Java Path Issues**
   ```bash
   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
   ```



---

**📞 Support**: Check logs in processor terminal for real-time debugging  
**🔗 API Docs**: Visit `http://localhost:8082/docs` for interactive API documentation

## ⚙️ Configuration

Configuration is managed in `config/config.json`:

```json
{
  "kafka": {
    "bootstrap_servers": ["localhost:9092"],
    "group_id": "details-processor-group",
    "consumer_timeout_ms": 5000
  },
  "topics": {
    "input": "details-input",
    "output": "details-output"
  },
  "processors": {
    "show_details": {"enabled": true, "threads": 2},
    "update_details": {"enabled": true, "threads": 2},
    "create_details": {"enabled": true, "threads": 2}
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true
  }
}
```

## 🔧 Key Features

### Concurrent Processing
- Each processor type can handle multiple messages simultaneously
- Configurable thread count per processor
- Thread-safe Kafka producers and consumers

### Error Handling
- Comprehensive error handling and logging
- Invalid message validation
- Graceful degradation

### Scalability
- Horizontal scaling through Kafka partitions
- Multiple consumer instances support
- Load balancing across processor threads

### Monitoring & Observability
- Structured logging with timestamps
- Health check endpoints
- Message tracing through IDs

## 🛑 Shutdown

To stop all services:

1. If using `start_all.sh`, press `Ctrl+C`
2. Or manually stop processes:

```bash
# Find and kill processes
ps aux | grep -E "(processor_manager|uvicorn)" | grep -v grep
kill <PID>

# Stop Kafka (if needed)
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
bin/kafka-server-stop.sh
bin/zookeeper-server-stop.sh
```

## � Docker Commands

### Quick Start
```bash
# Start everything
./docker-manage.sh up

# Setup topics
./setup-topics.sh

# Run tests
./docker-manage.sh test
```

### Management Commands
```bash
./docker-manage.sh build     # Build images
./docker-manage.sh up        # Start services  
./docker-manage.sh down      # Stop services
./docker-manage.sh restart   # Restart services
./docker-manage.sh logs      # View logs
./docker-manage.sh status    # Check status
./docker-manage.sh clean     # Clean up resources
./docker-manage.sh shell     # Open shell in container
```

### Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| zookeeper | 2181 | Zookeeper coordination service |
| kafka | 9092 | Kafka message broker |
| kafka-ui | 8080 | Web-based Kafka management UI |
| kafka-processors | 8082 | Main application (processors + API) |

## �📝 Development

### Adding New Processors

1. Create a new processor class inheriting from `BaseProcessor`
2. Implement `_should_process()` and `_process_business_logic()` methods
3. Add configuration to `config/config.json`
4. Register in `processor_manager.py`

### Extending the API

The FastAPI application supports automatic OpenAPI documentation at `/docs` for easy extension and testing.

### Docker Development

```bash
# Rebuild after code changes
./docker-manage.sh down
./docker-manage.sh build
./docker-manage.sh up

# View live logs during development
./docker-manage.sh logs kafka-processors
```

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Failed**
   - Check if Kafka services are running
   - Verify ports 9092 (Kafka) and 2181 (Zookeeper) are available

2. **Python Module Import Errors**
   - Ensure PYTHONPATH includes the project directory
   - Install all requirements: `pip install -r requirements.txt`

3. **Permission Denied**
   - Make scripts executable: `chmod +x start_all.sh test_system.py`

4. **Port Already in Use**
   - Change API port in `config/config.json`
   - Or kill existing process using the port

### Debug Mode

Enable debug logging by setting log level to "DEBUG" in `config/config.json`.

## 📄 License

This is a demonstration project for Kafka-based message processing systems.