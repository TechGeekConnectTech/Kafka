# Server Demise Pipeline System - Complete Documentation

## 🚀 System Overview

The **Server Demise Pipeline System** is a Kafka-based microservices architecture designed for automated server decommissioning workflows. The system implements a **sequential processing pipeline** where all processors communicate through a **single Kafka topic**, with message routing based on action types.

### 🏗️ Architecture Highlights

- **Single Topic Architecture**: All processors read/write to the same Kafka topic (`server-demise-pipeline`)
- **Sequential Processing**: Messages flow through processors in a specific order based on action type
- **Multi-threaded Processing**: Each processor supports multiple concurrent workers
- **Automatic Routing**: Messages are automatically routed to the correct processor based on action field
- **Error Handling**: Comprehensive error handling with pipeline termination on failures
- **State Management**: Each message maintains pipeline state and progress tracking

## 📋 Pipeline Flow

```
API Request → Kafka Topic → Processor 1 → Kafka Topic → Processor 2 → Kafka Topic → Processor 3 → Complete
     ↓              ↓             ↓              ↓             ↓              ↓             ↓
 check_server  →  Portal     →  poweroff_  →   IPMI     →  demise_   →   Asset    →   Complete
   action        Verification   server action   Power Off   server action  Cleanup      Response
```

### 🔄 Message Flow Details

1. **API Initiates Pipeline** (`action: check_server`)
   - Client sends server demise request to REST API
   - API creates initial message with `action: check_server`
   - Message sent to `server-demise-pipeline` topic

2. **Step 1: Server Check** (`action: check_server`)
   - **ServerCheckProcessor** reads message
   - Verifies server exists in portal/database
   - **Success**: Creates `action: poweroff_server` message
   - **Failure**: Creates `action: demise_complete` with error status

3. **Step 2: Power Off** (`action: poweroff_server`)
   - **ServerPowerOffProcessor** reads message
   - Executes server power off via IPMI/BMC
   - **Success**: Creates `action: demise_server` message
   - **Failure**: Creates `action: demise_complete` with error status

4. **Step 3: Decommission** (`action: demise_server`)
   - **ServerDemiseProcessor** reads message
   - Executes full decommission workflow
   - **Success**: Creates `action: demise_complete` with success status
   - **Failure**: Creates `action: demise_complete` with error status

5. **Pipeline Complete** (`action: demise_complete`)
   - Final message indicates pipeline completion
   - Contains full processing history and results
   - No further processing required

## 🔧 Configuration

### Kafka Configuration (`config/config.json`)

```json
{
    "kafka": {
        "bootstrap_servers": ["localhost:9092"],
        "client_id": "kafka-processors",
        "group_id": "demise-processor-group",
        "auto_offset_reset": "earliest",
        "enable_auto_commit": true,
        "auto_commit_interval_ms": 1000,
        "session_timeout_ms": 30000,
        "max_poll_records": 100,
        "max_poll_interval_ms": 300000,
        "consumer_timeout_ms": 5000
    },
    "topics": {
        "server_demise_pipeline": {
            "name": "server-demise-pipeline",
            "partitions": 3,
            "replication_factor": 1
        }
    },
    "processors": {
        "server_check_processor": {
            "enabled": true,
            "max_workers": 3,
            "consumer_timeout": 1000
        },
        "server_poweroff_processor": {
            "enabled": true,
            "max_workers": 3,
            "consumer_timeout": 1000
        },
        "server_demise_processor": {
            "enabled": true,
            "max_workers": 3,
            "consumer_timeout": 1000
        }
    }
}
```

### Processor Configuration

Each processor supports **multiple concurrent workers** to handle high throughput:
- **3 workers per processor** = **9 total workers**
- Each worker can process **10 messages per poll**
- **Concurrent processing** within each processor type
- **Sequential execution** across processor types

## 🔌 API Documentation

### Base URL
```
http://195.35.6.88:8082
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-11-02T08:30:00.000Z",
    "services": {
        "api": "online",
        "kafka_producer": "connected",
        "pipeline_processors": "active"
    }
}
```

#### 2. Single Server Demise
```http
POST /demise-server
```

**Request Body:**
```json
{
    "server_id": "SRV001",
    "reason": "End of life decommission",
    "priority": "normal",
    "requester": "admin_user",
    "additional_data": {
        "department": "IT Operations",
        "approval_ticket": "TICK-12345"
    }
}
```

**Response:**
```json
{
    "message_id": "uuid-here",
    "status": "initiated",
    "message": "Server demise pipeline initiated for server SRV001",
    "timestamp": "2025-11-02T08:30:00.000Z",
    "pipeline_initiated": true
}
```

#### 3. Batch Server Demise
```http
POST /batch-demise-servers
```

**Request Body:**
```json
{
    "servers": [
        {
            "server_id": "SRV001",
            "reason": "Datacenter migration",
            "priority": "high",
            "requester": "ops_team"
        },
        {
            "server_id": "SRV002", 
            "reason": "Datacenter migration",
            "priority": "high",
            "requester": "ops_team"
        }
    ],
    "batch_id": "BATCH-2025-001"
}
```

**Response:**
```json
{
    "batch_id": "BATCH-2025-001",
    "total_servers": 2,
    "responses": [
        {
            "server_id": "SRV001",
            "message_id": "uuid-1",
            "status": "initiated",
            "pipeline_initiated": true
        },
        {
            "server_id": "SRV002",
            "message_id": "uuid-2", 
            "status": "initiated",
            "pipeline_initiated": true
        }
    ],
    "timestamp": "2025-11-02T08:30:00.000Z"
}
```

#### 4. Pipeline Status
```http
GET /pipeline-status
```

**Response:**
```json
{
    "pipeline_name": "Server Demise Pipeline",
    "topic": "server-demise-pipeline",
    "processors": [
        {
            "step": 1,
            "name": "ServerCheckProcessor",
            "action": "check_server",
            "description": "Verify server existence in portal/database"
        },
        {
            "step": 2,
            "name": "ServerPowerOffProcessor",
            "action": "poweroff_server",
            "description": "Power off the server using IPMI/BMC"
        },
        {
            "step": 3,
            "name": "ServerDemiseProcessor",
            "action": "demise_server",
            "description": "Execute decommission request and cleanup"
        }
    ]
}
```

## 🏭 Processors

### 1. ServerCheckProcessor

**Purpose**: Verify server existence in portal/database  
**Input Action**: `check_server`  
**Output Action**: `poweroff_server` (success) or `demise_complete` (error)  

**Business Logic**:
- Checks if server ID exists in portal/database
- Validates server ID format (numeric 100-999 or valid prefixes)
- Retrieves server details (hostname, IP, location)
- Simulates portal API call with network delay

**Valid Server Formats**:
- Numeric IDs: 100-999 (e.g., "150", "500")
- Named servers: SRV*, HOST*, VM*, PROD*, TEST* prefixes

### 2. ServerPowerOffProcessor

**Purpose**: Power off the server using IPMI/BMC  
**Input Action**: `poweroff_server`  
**Output Action**: `demise_server` (success) or `demise_complete` (error)  

**Business Logic**:
- Connects to server management interface
- Checks current power status
- Executes power off command
- Verifies power off completion
- Simulates IPMI operations with realistic delays

**Success Rate**: 90% (configurable for testing)

### 3. ServerDemiseProcessor

**Purpose**: Execute complete decommission workflow  
**Input Action**: `demise_server`  
**Output Action**: `demise_complete` (always)  

**Decommission Steps**:
1. Remove from monitoring systems
2. Update inventory database
3. Remove DNS/DHCP entries
4. Update asset management
5. Remove from load balancers
6. Update configuration management
7. Generate decommission ticket

**Success Rate**: 95% (configurable for testing)

## 💾 Message Format

### Standard Message Structure
```json
{
    "id": "unique-message-uuid",
    "original_request_id": "original-request-uuid",
    "action": "check_server|poweroff_server|demise_server|demise_complete",
    "status": "pending|completed|failed|error",
    "processor": "processor-class-name",
    "processor_id": "processor-instance-uuid",
    "timestamp": "2025-11-02T08:30:00.000Z",
    "data": {
        "server_id": "required-server-identifier",
        "server_details": {},
        "processing_results": {},
        "original_request": {}
    },
    "message": "human-readable-status",
    "pipeline_step": 0,
    "next_step": "next-processor-action",
    "pipeline_complete": false
}
```

### Message Routing Logic
```python
# Each processor implements this logic:
def should_process_message(self, message_data):
    return (
        message_data.get('action') == self.target_action and 
        message_data.get('status') == 'pending'
    )
```

## 🐳 Docker Setup

### Docker Compose Configuration
```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  demise-processors:
    build: .
    depends_on:
      - kafka
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    volumes:
      - ./logs:/app/logs

  demise-api:
    build: .
    depends_on:
      - kafka
    ports:
      - "8082:8082"
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    command: ["python", "-m", "uvicorn", "api.main_new:app", "--host", "0.0.0.0", "--port", "8082"]
```

### Build and Run Commands
```bash
# Setup topics
chmod +x setup-topics.sh
./setup-topics.sh

# Start processors
python3 processor_manager_new.py

# Start API (separate terminal)
python3 -m uvicorn api.main_new:app --host 0.0.0.0 --port 8082

# Or use Docker
docker-compose up -d
```

## 🧪 Testing

### Run Test Suite
```bash
# Make test script executable
chmod +x test_demise_pipeline.py

# Run comprehensive tests
python3 test_demise_pipeline.py
```

### Test Scenarios

1. **Valid Server Demise**: Server ID 100-999 or valid prefixes
2. **Invalid Server Demise**: Server ID outside valid range
3. **Batch Processing**: Multiple servers simultaneously
4. **Format Testing**: Various server ID formats
5. **Error Handling**: Pipeline failure scenarios

### Expected Test Flow
```
API Health Check → Pipeline Info → Single Server Test → Invalid Server Test → 
Format Tests → Batch Test → Monitor Processor Logs
```

## 🔍 Monitoring and Logging

### Log Levels
- **INFO**: Normal processing flow and status updates
- **ERROR**: Processing errors and failures
- **DEBUG**: Detailed message processing information

### Key Log Messages
```
✅ Initialized ServerCheckProcessor with ID: uuid
🔄 Processing message uuid with action: check_server
🔍 Checking server existence for ID: SRV001
✅ Server SRV001 found in portal
🔌 Initiating power off for server: SRV001
✅ Server SRV001 powered off successfully
🗑️ Initiating demise request for server: SRV001
✅ Server SRV001 demise process completed successfully
```

### Pipeline Monitoring
- Each message includes `pipeline_step` and processing timestamps
- Total processing time calculated from start to completion
- Error messages include full context and troubleshooting information
- Health check endpoints provide real-time system status

## 🚀 Production Deployment

### Prerequisites
- Java 17+ for Kafka
- Python 3.8+ with required packages
- Kafka cluster (single node or distributed)
- Network access between components

### Scaling Considerations
- **Horizontal Scaling**: Add more processor instances
- **Vertical Scaling**: Increase `max_workers` per processor
- **Topic Partitioning**: Scale Kafka partitions for higher throughput
- **Load Balancing**: Distribute API instances behind load balancer

### Performance Tuning
```json
{
    "kafka": {
        "max_poll_records": 50,
        "session_timeout_ms": 30000,
        "consumer_timeout_ms": 1000
    },
    "processors": {
        "server_check_processor": {"max_workers": 5},
        "server_poweroff_processor": {"max_workers": 5}, 
        "server_demise_processor": {"max_workers": 5}
    }
}
```

## 🔒 Security Considerations

- **API Authentication**: Implement JWT or API key authentication
- **Kafka Security**: Enable SASL/SSL for Kafka communication
- **Network Security**: Use VPN/private networks for component communication
- **Audit Logging**: Log all decommission requests and results
- **Access Control**: Implement role-based access for different operations

## 🎯 Key Benefits

1. **Fault Tolerance**: Each step is independent with error recovery
2. **Scalability**: Horizontal and vertical scaling capabilities
3. **Observability**: Comprehensive logging and monitoring
4. **Flexibility**: Easy to add new processors or modify workflow
5. **Reliability**: Kafka ensures message durability and delivery
6. **Concurrent Processing**: Multiple requests processed simultaneously
7. **State Management**: Full pipeline state tracking and history