# Kafka Processors System - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation Guide](#installation-guide)
4. [Project Structure](#project-structure)
5. [File Descriptions](#file-descriptions)
6. [Configuration](#configuration)
7. [Topic Management](#topic-management)
8. [API Documentation](#api-documentation)
9. [Processor Details](#processor-details)
10. [Docker Setup](#docker-setup)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)

---

## System Overview

The Kafka Processors System is a comprehensive message processing platform built with Apache Kafka, Python, and FastAPI. It provides:

- **Real-time message processing** with concurrent handling
- **REST API** for sending events to Kafka topics
- **Three specialized processors** for different business operations
- **Docker containerization** for easy deployment
- **Thread-safe concurrent processing** with configurable workers
- **Comprehensive logging and monitoring**

### Key Features
- ✅ Concurrent message processing (multiple threads per processor)
- ✅ Thread-safe Kafka producer/consumer wrappers
- ✅ REST API with automatic OpenAPI documentation
- ✅ Docker support with multi-service orchestration
- ✅ Configuration management with environment variable support
- ✅ Comprehensive error handling and logging
- ✅ Batch processing capabilities
- ✅ Health monitoring endpoints

---

## Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │───▶│   Kafka Broker  │───▶│   Processors    │
│   (Port 8082)   │    │   (Port 9092)   │    │   (3 Workers)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │ Output Topic    │
         │                       │              │ (Processed)     │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Kafka UI      │
│   (HTTP/JSON)   │    │   (Port 8080)   │
└─────────────────┘    └─────────────────┘
```

### Message Flow
1. **Client** sends HTTP request to REST API
2. **API** validates request and publishes to `details-input` topic
3. **Processors** consume from `details-input` topic concurrently
4. **Business Logic** executes based on message action type
5. **Results** are published to `details-output` topic
6. **Monitoring** systems can consume from output topic

### Components
- **Zookeeper**: Coordination service for Kafka
- **Kafka Broker**: Message streaming platform
- **REST API**: FastAPI-based HTTP interface
- **Processor Manager**: Orchestrates all message processors
- **Kafka Manager**: Thread-safe Kafka client wrapper
- **Configuration System**: JSON-based configuration with env overrides

---

## Installation Guide

### Prerequisites
- **Docker & Docker Compose** (recommended) OR
- **Java 17+** (for local Kafka installation)
- **Python 3.8+**
- **pip** (Python package manager)

### Option 1: Docker Installation (Recommended)

```bash
# Navigate to project directory
cd /root/kafka/kafka-processors

# Build and start all services
./docker-manage.sh build
./docker-manage.sh up

# Create Kafka topics
./setup-topics.sh

# Test the system
./docker-manage.sh test
```

### Option 2: Local Installation

```bash
# 1. Install Kafka (already done in /root/kafka/)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64

# Start Zookeeper
cd /root/kafka
nohup bin/zookeeper-server-start.sh config/zookeeper.properties > logs/zookeeper.log 2>&1 &

# Start Kafka
nohup bin/kafka-server-start.sh config/server.properties > logs/kafka.log 2>&1 &

# 2. Install Python dependencies
cd /root/kafka/kafka-processors
pip install -r requirements.txt

# 3. Start processors and API
./start_all.sh
```

---

## Project Structure

```
/root/kafka/kafka-processors/
├── api/
│   └── main.py                      # FastAPI REST API server
├── config/
│   ├── __init__.py                  # Configuration management classes
│   ├── config.json                  # Main configuration file
│   └── config.docker.json           # Docker-specific configuration
├── processors/
│   ├── __init__.py                  # Processor module exports
│   ├── base_processor.py            # Abstract base processor class
│   ├── show_details_processor.py    # Show details business logic
│   ├── update_details_processor.py  # Update details business logic
│   └── create_details_processor.py  # Create details business logic
├── utils/
│   ├── __init__.py                  # Utility module exports
│   └── kafka_manager.py             # Kafka producer/consumer wrappers
├── logs/                            # Application log files
│   └── kafka-processors.log         # Main application log
├── Dockerfile                       # Docker container definition
├── docker-compose.yml               # Multi-service Docker orchestration
├── .dockerignore                    # Docker build ignore patterns
├── docker-manage.sh                 # Docker management utility
├── setup-topics.sh                  # Kafka topic creation script
├── start_all.sh                     # Local system startup script
├── processor_manager.py             # Main processor orchestrator
├── test_system.py                   # Comprehensive test suite
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

---

## File Descriptions

### Core Application Files

#### `processor_manager.py`
**Purpose**: Main entry point that orchestrates all Kafka processors
**Key Functions**:
- Initializes all three processors (show, update, create)
- Manages Kafka consumers with configurable thread pools
- Handles graceful shutdown with signal handling
- Routes incoming messages to appropriate processors

#### `api/main.py`
**Purpose**: FastAPI REST API server for receiving HTTP requests
**Key Features**:
- `/send-event` endpoint for single message processing
- `/send-batch` endpoint for bulk message processing
- `/health` endpoint for system health monitoring
- Automatic OpenAPI documentation generation
- Request validation with Pydantic models

### Processor Files

#### `processors/base_processor.py`
**Purpose**: Abstract base class defining processor interface
**Key Methods**:
- `process_message()`: Main message processing workflow
- `_should_process()`: Abstract method for message filtering
- `_process_business_logic()`: Abstract method for business logic
- `_create_response()`: Standardized response formatting

#### `processors/show_details_processor.py`
**Purpose**: Handles `show_details` action messages
**Business Logic**:
- Simulates database record retrieval
- Adds metadata and processing timestamps
- Returns structured record information

#### `processors/update_details_processor.py`
**Purpose**: Handles `update_details` action messages  
**Business Logic**:
- Validates update data requirements
- Simulates database record updates
- Tracks version numbers and update history
- Performs field-level validation

#### `processors/create_details_processor.py`
**Purpose**: Handles `create_details` action messages
**Business Logic**:
- Validates required fields for new records
- Generates unique record identifiers
- Simulates database record creation
- Adds computed fields and metadata

### Utility Files

#### `utils/kafka_manager.py`
**Purpose**: Thread-safe Kafka client management
**Key Classes**:
- `KafkaProducerWrapper`: Thread-safe message publishing
- `KafkaConsumerWrapper`: Concurrent message consumption
- `KafkaManager`: Unified producer/consumer management

#### `config/__init__.py`
**Purpose**: Configuration management system
**Key Features**:
- JSON configuration file loading
- Environment variable overrides for Docker
- Type-safe configuration access methods

### Configuration Files

#### `config/config.json`
**Purpose**: Main application configuration
**Sections**:
- Kafka connection settings
- Topic names and partitioning
- Processor thread configuration
- API server settings
- Logging configuration

#### `requirements.txt`
**Purpose**: Python package dependencies
**Key Dependencies**:
- `kafka-python`: Kafka client library
- `fastapi`: REST API framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation

### Docker Files

#### `Dockerfile`
**Purpose**: Container image definition
**Features**:
- Multi-stage build optimization
- Java and Python runtime setup
- Health check configuration
- Startup script integration

#### `docker-compose.yml`
**Purpose**: Multi-service orchestration
**Services**:
- `zookeeper`: Kafka coordination service
- `kafka`: Message broker
- `kafka-ui`: Web-based Kafka management
- `kafka-processors`: Main application

### Utility Scripts

#### `docker-manage.sh`
**Purpose**: Docker container management utility
**Commands**:
- `build`: Build Docker images
- `up`/`down`: Start/stop services
- `logs`: View service logs
- `status`: Check service health
- `clean`: Remove containers and volumes

#### `setup-topics.sh`
**Purpose**: Kafka topic creation for Docker environment
**Functions**:
- Creates `details-input` topic with 3 partitions
- Creates `details-output` topic with 3 partitions
- Verifies topic creation success

#### `start_all.sh`
**Purpose**: Local development startup script
**Functions**:
- Starts processor manager in background
- Starts FastAPI server on port 8082
- Displays service URLs and management info

#### `test_system.py`
**Purpose**: Comprehensive system testing
**Test Cases**:
- API health verification
- Individual processor testing
- Batch processing validation
- Error handling verification

---

## Configuration

### Main Configuration (`config/config.json`)

```json
{
    "kafka": {
        "bootstrap_servers": ["localhost:9092"],
        "client_id": "kafka-processors",
        "group_id": "details-processor-group",
        "auto_offset_reset": "earliest",
        "enable_auto_commit": true,
        "auto_commit_interval_ms": 1000,
        "session_timeout_ms": 30000,
        "max_poll_records": 100,
        "max_poll_interval_ms": 300000,
        "consumer_timeout_ms": 5000
    },
    "topics": {
        "input": "details-input",
        "output": "details-output"
    },
    "processors": {
        "show_details": {
            "enabled": true,
            "threads": 2
        },
        "update_details": {
            "enabled": true,
            "threads": 2
        },
        "create_details": {
            "enabled": true,
            "threads": 2
        }
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8082,
        "debug": true
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/kafka-processors.log"
    }
}
```

### Configuration Parameters

#### Kafka Settings
- `bootstrap_servers`: Kafka broker addresses
- `group_id`: Consumer group identifier
- `auto_offset_reset`: Offset reset strategy ("earliest" or "latest")
- `max_poll_records`: Maximum records per poll operation
- `consumer_timeout_ms`: Consumer polling timeout

#### Topic Configuration
- `input`: Topic name for incoming messages
- `output`: Topic name for processed results

#### Processor Settings
- `enabled`: Enable/disable individual processors
- `threads`: Thread pool size per processor type

#### API Configuration
- `host`: API server bind address
- `port`: API server port (8082 to avoid conflicts)
- `debug`: Enable debug mode with auto-reload

---

## Topic Management

### Current Topics

#### `details-input`
- **Purpose**: Receives incoming messages from REST API
- **Partitions**: 3 (for load distribution)
- **Replication Factor**: 1 (single broker setup)
- **Key Strategy**: Message ID for consistent routing

#### `details-output`
- **Purpose**: Stores processed results from processors
- **Partitions**: 3 (matching input topic)
- **Replication Factor**: 1
- **Key Strategy**: Original message ID for traceability

### Modifying Existing Topics

If you need to change topic configuration, modify these files:

#### 1. Update Configuration
**File**: `config/config.json`
```json
{
    "topics": {
        "input": "your-new-input-topic",
        "output": "your-new-output-topic"
    }
}
```

#### 2. Create New Topics (Local Installation)
**Command**:
```bash
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64

# Create new input topic
bin/kafka-topics.sh --create --topic your-new-input-topic \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1

# Create new output topic
bin/kafka-topics.sh --create --topic your-new-output-topic \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1
```

#### 3. Update Docker Topic Creation
**File**: `setup-topics.sh`
```bash
# Update topic names in the script
docker-compose exec kafka kafka-topics --create \
    --topic your-new-input-topic \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1 --if-not-exists
```

#### 4. Update Test Scripts
**File**: `test_system.py`
```python
# Update API base URL if needed
API_BASE_URL = "http://localhost:8082"
```

### Adding New Topics

To add additional topics for new processors:

1. **Add to configuration**:
```json
{
    "topics": {
        "input": "details-input",
        "output": "details-output",
        "notifications": "notification-events",
        "analytics": "analytics-events"
    }
}
```

2. **Create topics** using Kafka command-line tools or update `setup-topics.sh`

3. **Update processors** to use new topics as needed

---

## API Documentation

### Base URL
- **Local**: `http://localhost:8082`
- **Docker**: `http://localhost:8082`
- **Interactive Docs**: `http://localhost:8082/docs`

### Endpoints

#### GET `/`
**Purpose**: API information and available endpoints
**Response**:
```json
{
    "name": "Kafka Processors API",
    "version": "1.0.0",
    "description": "REST API for sending events to Kafka processors",
    "endpoints": {
        "health": "/health",
        "send_event": "/send-event",
        "docs": "/docs"
    }
}
```

#### GET `/health`
**Purpose**: System health check
**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2024-11-02T12:00:00.000000",
    "services": {
        "kafka": "healthy",
        "api": "healthy"
    }
}
```

#### POST `/send-event`
**Purpose**: Send single event for processing
**Request Body**:
```json
{
    "action": "show_details|update_details|create_details",
    "data": {
        "name": "Record Name",
        "description": "Record Description"
    },
    "id": "optional-message-id"
}
```
**Response**:
```json
{
    "message_id": "generated-uuid",
    "status": "sent",
    "message": "Event sent successfully for processing. Action: show_details",
    "timestamp": "2024-11-02T12:00:00.000000"
}
```

#### POST `/send-batch`
**Purpose**: Send multiple events for processing
**Request Body**:
```json
[
    {
        "action": "create_details",
        "data": {"name": "Record 1"}
    },
    {
        "action": "show_details",
        "data": {"name": "Record 2"}
    }
]
```
**Response**:
```json
{
    "total_events": 2,
    "successful": 2,
    "failed": 0,
    "results": [
        {
            "message_id": "uuid-1",
            "status": "sent",
            "message": "Event sent for action: create_details"
        }
    ],
    "timestamp": "2024-11-02T12:00:00.000000"
}
```

#### GET `/config`
**Purpose**: Get current API configuration (non-sensitive)
**Response**:
```json
{
    "kafka": {
        "topics": {
            "input": "details-input",
            "output": "details-output"
        },
        "bootstrap_servers": ["localhost:9092"]
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8082,
        "debug": true
    },
    "processors": {
        "show_details": {"enabled": true},
        "update_details": {"enabled": true},
        "create_details": {"enabled": true}
    }
}
```

---

## Processor Details

### Message Processing Workflow

1. **Message Reception**: Kafka consumer receives message from input topic
2. **Validation**: Base processor validates message structure and required fields
3. **Routing**: Message routed to appropriate processor based on action field
4. **Business Logic**: Processor-specific logic executes
5. **Response Creation**: Standardized response message created
6. **Output Publishing**: Result sent to output topic with original message ID

### Standardized Message Format

#### Input Message Format
```json
{
    "id": "unique-message-id",
    "action": "show_details|update_details|create_details",
    "data": {
        "field1": "value1",
        "field2": "value2"
    },
    "timestamp": "2024-11-02T12:00:00.000000",
    "source": "rest_api"
}
```

#### Output Message Format
```json
{
    "id": "original-message-id",
    "original_action": "show_details",
    "processor": "ShowDetailsProcessor",
    "processor_id": "processor-instance-uuid",
    "timestamp": "2024-11-02T12:00:00.000000",
    "status": "success|error",
    "data": {
        "processed_data": "results"
    },
    "message": "Processing completed successfully"
}
```

### Show Details Processor

#### Purpose
Retrieves and displays record information based on provided criteria.

#### Input Data Requirements
- `name` (optional): Record name for lookup
- `description` (optional): Additional context
- `created_date` (optional): Filter by creation date

#### Processing Logic
1. Simulates database lookup operation
2. Adds processing metadata and timestamps
3. Returns structured record information
4. Includes version and status information

#### Sample Output
```json
{
    "data": {
        "id": "record-uuid",
        "name": "Retrieved Record",
        "description": "Details for record",
        "created_date": "2024-01-01T00:00:00",
        "last_modified": "2024-11-02T12:00:00",
        "status": "active",
        "metadata": {
            "processed_by": "show_details_processor",
            "processing_time": 1699012800.0,
            "version": "1.0"
        }
    }
}
```

### Update Details Processor

#### Purpose
Modifies existing record information with provided updates.

#### Input Data Requirements
- `name` (optional): Updated record name
- `description` (optional): Updated description
- `status` (optional): New status value
- Additional fields as needed

#### Processing Logic
1. Validates update data presence
2. Performs field-level validation
3. Simulates database update operation
4. Tracks version numbers and update history
5. Returns updated record information

#### Validation Rules
- `name` must be at least 2 characters if provided
- `email` must contain '@' symbol if provided
- Updates increment version number

#### Sample Output
```json
{
    "data": {
        "id": "record-uuid",
        "name": "Updated Record Name",
        "updated_fields": ["name", "description"],
        "last_modified": "2024-11-02T12:00:00",
        "status": "updated",
        "version": 2,
        "metadata": {
            "processed_by": "update_details_processor",
            "processing_time": 1699012800.0,
            "update_count": 1
        }
    }
}
```

### Create Details Processor

#### Purpose
Creates new records with provided information.

#### Input Data Requirements
- `name` (required): Record name
- `description` (optional): Record description
- `category` (optional): Record category
- `email` (optional): Contact email

#### Processing Logic
1. Validates required fields presence
2. Generates unique record identifier
3. Performs business rule validation
4. Simulates database creation operation
5. Adds computed fields and metadata

#### Validation Rules
- `name` is required and must be at least 2 characters
- `email` must contain '@' symbol if provided
- Generated fields include slug and search keywords

#### Sample Output
```json
{
    "data": {
        "id": "new-record-uuid",
        "original_request_id": "request-uuid",
        "name": "New Record",
        "description": "New record description",
        "category": "general",
        "created_date": "2024-11-02T12:00:00",
        "status": "active",
        "version": 1,
        "computed_fields": {
            "slug": "new-record",
            "search_keywords": ["new", "record"],
            "creation_source": "kafka_processor"
        }
    }
}
```

---

## Docker Setup

### Services Overview

#### Zookeeper Service
- **Image**: `confluentinc/cp-zookeeper:7.4.0`
- **Port**: 2181
- **Purpose**: Kafka coordination and metadata management
- **Data Persistence**: Named volume for data and logs

#### Kafka Service
- **Image**: `confluentinc/cp-kafka:7.4.0`
- **Ports**: 9092 (external), 29092 (internal)
- **Purpose**: Message streaming and topic management
- **Dependencies**: Zookeeper
- **Configuration**: Single broker with replication factor 1

#### Kafka UI Service
- **Image**: `provectuslabs/kafka-ui:latest`
- **Port**: 8080
- **Purpose**: Web-based Kafka cluster management
- **Features**: Topic visualization, message browsing, consumer group monitoring

#### Kafka Processors Service
- **Build**: Local Dockerfile
- **Port**: 8082
- **Purpose**: Main application (processors + REST API)
- **Dependencies**: Kafka service
- **Health Check**: HTTP endpoint monitoring

### Docker Commands

```bash
# Build services
./docker-manage.sh build

# Start all services
./docker-manage.sh up

# View service status
./docker-manage.sh status

# View logs
./docker-manage.sh logs [service-name]

# Stop services
./docker-manage.sh down

# Clean up resources
./docker-manage.sh clean

# Open shell in container
./docker-manage.sh shell [service-name]
```

### Environment Variables

The application supports environment variable overrides for Docker deployment:

- `KAFKA_BOOTSTRAP_SERVERS`: Override Kafka connection string
- `KAFKA_HOST`: Kafka hostname for Docker networking
- `KAFKA_PORT`: Kafka port for health checks
- `API_HOST`: API server bind address
- `API_PORT`: API server port

### Volume Mounts

- **Configuration**: `./config:/app/config` (configuration files)
- **Logs**: `./logs:/app/logs` (application logs)
- **Kafka Data**: Named volumes for persistence

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Conflicts
**Problem**: "Address already in use" error on port 8082
**Solution**:
```bash
# Find process using port
netstat -tulnp | grep :8082
# Kill process
kill <PID>
# Or change port in config/config.json
```

#### 2. Kafka Connection Failed
**Problem**: Cannot connect to Kafka broker
**Solutions**:
- Verify Kafka is running: `ps aux | grep kafka`
- Check port availability: `netstat -tulnp | grep :9092`
- Restart Kafka services:
```bash
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
bin/kafka-server-stop.sh
bin/kafka-server-start.sh config/server.properties
```

#### 3. Python Import Errors
**Problem**: Module not found errors
**Solutions**:
- Install dependencies: `pip install -r requirements.txt`
- Check Python path: `export PYTHONPATH=/root/kafka/kafka-processors:$PYTHONPATH`

#### 4. Docker Build Issues
**Problem**: Docker build failures
**Solutions**:
- Clean Docker cache: `./docker-manage.sh clean`
- Rebuild without cache: `docker-compose build --no-cache`
- Check Docker daemon: `systemctl status docker`

#### 5. Topic Not Found
**Problem**: Kafka topics don't exist
**Solutions**:
- Create topics manually:
```bash
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
bin/kafka-topics.sh --create --topic details-input \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```
- Or run setup script: `./setup-topics.sh` (Docker)

#### 6. Consumer Group Issues
**Problem**: Messages not being consumed
**Solutions**:
- Reset consumer group:
```bash
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --group details-processor-group --reset-offsets --to-earliest \
    --topic details-input --execute
```

#### 7. Java Version Issues
**Problem**: Kafka fails to start due to Java version
**Solution**:
```bash
# Set correct Java version
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
# Add to ~/.bashrc for persistence
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64' >> ~/.bashrc
```

### Debugging Commands

```bash
# Check service status
systemctl status docker
ps aux | grep -E "(kafka|zookeeper)" | grep -v grep

# View application logs
tail -f /root/kafka/kafka-processors/logs/kafka-processors.log

# Monitor Kafka topics
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
# Monitor input messages
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic details-input --from-beginning
# Monitor output messages  
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic details-output --from-beginning

# Check API health
curl http://localhost:8082/health

# Test message sending
curl -X POST "http://localhost:8082/send-event" \
  -H "Content-Type: application/json" \
  -d '{"action": "show_details", "data": {"name": "Test"}}'
```

---

## Examples

### Example 1: Show Details Request

**Request**:
```bash
curl -X POST "http://localhost:8082/send-event" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "show_details",
    "data": {
      "name": "Customer Record 001",
      "description": "Premium customer account",
      "created_date": "2024-01-15T10:30:00"
    }
  }'
```

**API Response**:
```json
{
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "sent",
    "message": "Event sent successfully for processing. Action: show_details",
    "timestamp": "2024-11-02T12:00:00.123456"
}
```

**Processor Output** (in `details-output` topic):
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "original_action": "show_details",
    "processor": "ShowDetailsProcessor",
    "processor_id": "proc-uuid-123",
    "timestamp": "2024-11-02T12:00:01.234567",
    "status": "success",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Customer Record 001",
        "description": "Premium customer account",
        "created_date": "2024-01-15T10:30:00",
        "last_modified": "2024-11-02T12:00:01",
        "status": "active",
        "metadata": {
            "processed_by": "show_details_processor",
            "processing_time": 1699012801.234,
            "version": "1.0"
        }
    },
    "message": "Details retrieved successfully for ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 2: Create Details Request

**Request**:
```bash
curl -X POST "http://localhost:8082/send-event" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_details",
    "data": {
      "name": "New Customer Account",
      "description": "Standard business account",
      "category": "business",
      "email": "contact@company.com"
    }
  }'
```

**Processor Output**:
```json
{
    "id": "req-uuid-456",
    "original_action": "create_details",
    "processor": "CreateDetailsProcessor",
    "processor_id": "proc-uuid-456",
    "timestamp": "2024-11-02T12:05:00.345678",
    "status": "success",
    "data": {
        "id": "rec-uuid-789",
        "original_request_id": "req-uuid-456",
        "name": "New Customer Account",
        "description": "Standard business account",
        "category": "business",
        "created_date": "2024-11-02T12:05:00",
        "last_modified": "2024-11-02T12:05:00",
        "status": "active",
        "version": 1,
        "metadata": {
            "processed_by": "create_details_processor",
            "processing_time": 1699012900.345,
            "created_from": "req-uuid-456"
        },
        "computed_fields": {
            "slug": "new-customer-account",
            "search_keywords": ["new", "customer", "account"],
            "creation_source": "kafka_processor"
        }
    },
    "message": "Record created successfully with ID: rec-uuid-789"
}
```

### Example 3: Update Details Request

**Request**:
```bash
curl -X POST "http://localhost:8082/send-event" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_details",
    "data": {
      "name": "Updated Customer Name",
      "status": "premium",
      "description": "Upgraded to premium account"
    }
  }'
```

**Processor Output**:
```json
{
    "id": "upd-uuid-321",
    "original_action": "update_details", 
    "processor": "UpdateDetailsProcessor",
    "processor_id": "proc-uuid-321",
    "timestamp": "2024-11-02T12:10:00.456789",
    "status": "success",
    "data": {
        "id": "upd-uuid-321",
        "name": "Updated Customer Name",
        "updated_fields": ["name", "status", "description"],
        "last_modified": "2024-11-02T12:10:00",
        "status": "premium",
        "version": 2,
        "metadata": {
            "processed_by": "update_details_processor",
            "processing_time": 1699013000.456,
            "update_count": 1,
            "original_data": {
                "name": "Updated Customer Name",
                "status": "premium",
                "description": "Upgraded to premium account"
            }
        }
    },
    "message": "Record updated successfully for ID: upd-uuid-321. Updated fields: name, status, description"
}
```

### Example 4: Batch Processing Request

**Request**:
```bash
curl -X POST "http://localhost:8082/send-batch" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "action": "create_details",
      "data": {"name": "Batch Record 1", "category": "test"}
    },
    {
      "action": "show_details", 
      "data": {"name": "Batch Record 2"}
    },
    {
      "action": "update_details",
      "data": {"name": "Updated Batch Record", "status": "active"}
    }
  ]'
```

**API Response**:
```json
{
    "total_events": 3,
    "successful": 3,
    "failed": 0,
    "results": [
        {
            "message_id": "batch-uuid-1",
            "status": "sent",
            "message": "Event sent for action: create_details"
        },
        {
            "message_id": "batch-uuid-2", 
            "status": "sent",
            "message": "Event sent for action: show_details"
        },
        {
            "message_id": "batch-uuid-3",
            "status": "sent", 
            "message": "Event sent for action: update_details"
        }
    ],
    "timestamp": "2024-11-02T12:15:00.567890"
}
```

### Example 5: Error Handling

**Invalid Request**:
```bash
curl -X POST "http://localhost:8082/send-event" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "invalid_action",
    "data": {"test": "data"}
  }'
```

**Error Response**:
```json
{
    "detail": "Invalid action. Must be one of: show_details, update_details, create_details"
}
```

**Validation Error** (create without required name):
```bash
curl -X POST "http://localhost:8082/send-event" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_details",
    "data": {"description": "Missing name field"}
  }'
```

**Processor Error Output**:
```json
{
    "id": "err-uuid-999",
    "original_action": "create_details",
    "processor": "CreateDetailsProcessor",
    "processor_id": "proc-uuid-999",
    "timestamp": "2024-11-02T12:20:00.678901",
    "status": "error",
    "data": {
        "missing_fields": ["name"]
    },
    "message": "Missing required fields: name"
}
```

---

## Monitoring and Maintenance

### Log Files
- **Application Logs**: `/root/kafka/kafka-processors/logs/kafka-processors.log`
- **Kafka Server Logs**: `/root/kafka/logs/kafka.log`
- **Zookeeper Logs**: `/root/kafka/logs/zookeeper.log`

### Health Monitoring
- **API Health**: `curl http://localhost:8082/health`
- **Kafka Topics**: Monitor via Kafka UI at `http://localhost:8080` (Docker)
- **System Resources**: Monitor CPU, memory, and disk usage

### Performance Tuning
- Adjust `threads` configuration per processor type
- Modify Kafka `max_poll_records` for batch size optimization
- Configure JVM memory settings for Kafka broker
- Use appropriate partition counts for load distribution

---

## Security Considerations

### Production Deployment
- Use environment variables for sensitive configuration
- Enable Kafka security features (SASL, SSL)
- Implement API authentication and rate limiting
- Use secure Docker image scanning
- Regular security updates for dependencies

### Network Security
- Restrict access to Kafka ports (9092, 2181)
- Use reverse proxy for API endpoints
- Implement network segmentation
- Monitor for unusual traffic patterns

---

*This documentation provides comprehensive guidance for deploying, configuring, and maintaining the Kafka Processors System. For additional support or questions, refer to the inline code comments and test examples.*