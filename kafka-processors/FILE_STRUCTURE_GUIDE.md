# Kafka Processors System - File Structure & Configuration Guide

## 📁 Complete Project Structure

```
/root/kafka/kafka-processors/
├── 📁 api/
│   └── 📄 main.py                               # FastAPI REST API Server
├── 📁 config/
│   ├── 📄 __init__.py                           # Configuration Management Classes  
│   ├── 📄 config.json                          # Main Configuration File
│   └── 📄 config.docker.json                   # Docker-Specific Configuration
├── 📁 processors/
│   ├── 📄 __init__.py                           # Processor Module Exports
│   ├── 📄 base_processor.py                    # Abstract Base Processor Class
│   ├── 📄 show_details_processor.py            # Show Details Business Logic
│   ├── 📄 update_details_processor.py          # Update Details Business Logic
│   └── 📄 create_details_processor.py          # Create Details Business Logic
├── 📁 utils/
│   ├── 📄 __init__.py                           # Utility Module Exports
│   └── 📄 kafka_manager.py                     # Kafka Producer/Consumer Wrappers
├── 📁 logs/
│   └── 📄 kafka-processors.log                 # Application Log File
├── 📄 Dockerfile                                # Docker Container Definition
├── 📄 docker-compose.yml                       # Multi-Service Docker Orchestration
├── 📄 .dockerignore                            # Docker Build Ignore Patterns
├── 📄 docker-manage.sh                         # Docker Management Utility
├── 📄 setup-topics.sh                          # Kafka Topic Creation Script
├── 📄 start_all.sh                             # Local System Startup Script
├── 📄 processor_manager.py                     # Main Processor Orchestrator
├── 📄 test_system.py                           # Comprehensive Test Suite
├── 📄 requirements.txt                         # Python Dependencies
├── 📄 README.md                                # Project Documentation
├── 📄 COMPLETE_DOCUMENTATION.md                # Detailed System Documentation
├── 📄 create_html_doc.py                       # Documentation HTML Generator
└── 📄 Kafka_Processors_System_Documentation.html # Generated HTML Documentation
```

---

## 🔧 Configuration Files & Topic Management

### Current Kafka Topics

#### 📊 **details-input** Topic
- **Purpose**: Receives incoming messages from REST API
- **Partitions**: 3 (for load distribution)
- **Replication Factor**: 1 (single broker setup)
- **Consumer Group**: `details-processor-group`

#### 📊 **details-output** Topic  
- **Purpose**: Stores processed results from processors
- **Partitions**: 3 (matching input topic)
- **Replication Factor**: 1
- **Message Format**: Standardized JSON response

---

## 📝 Key Configuration Files to Modify

### 1. **Topic Configuration** - `config/config.json`

**Current Configuration:**
```json
{
    "topics": {
        "input": "details-input",
        "output": "details-output"
    }
}
```

**To Change Topics:**
1. **Update Configuration File**:
```json
{
    "topics": {
        "input": "your-new-input-topic",
        "output": "your-new-output-topic"  
    }
}
```

2. **Create New Topics** (Local Installation):
```bash
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64

# Create input topic
bin/kafka-topics.sh --create --topic your-new-input-topic \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1

# Create output topic  
bin/kafka-topics.sh --create --topic your-new-output-topic \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1
```

3. **Update Docker Topic Script** - `setup-topics.sh`:
```bash
# Replace existing topic names
docker-compose exec kafka kafka-topics --create \
    --topic your-new-input-topic \
    --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1 --if-not-exists
```

### 2. **Processor Configuration** - `config/config.json`

**Current Settings:**
```json
{
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
    }
}
```

**Modifications:**
- **Enable/Disable Processors**: Change `"enabled": false`
- **Adjust Thread Count**: Change `"threads": 4` for more concurrent processing
- **Add New Processors**: Add new processor configurations

### 3. **API Configuration** - `config/config.json`

**Current Settings:**
```json
{
    "api": {
        "host": "0.0.0.0",
        "port": 8082,
        "debug": true
    }
}
```

**Port Change**: Update `"port": 9000` to use different port

### 4. **Kafka Connection** - `config/config.json`

**Current Settings:**
```json
{
    "kafka": {
        "bootstrap_servers": ["localhost:9092"],
        "group_id": "details-processor-group",
        "auto_offset_reset": "earliest"
    }
}
```

**Modifications:**
- **Change Kafka Server**: Update `"bootstrap_servers": ["your-kafka-host:9092"]`
- **Consumer Group**: Change `"group_id": "your-consumer-group"`
- **Offset Strategy**: Change `"auto_offset_reset": "latest"`

---

## 📄 Detailed File Descriptions

### 🏗️ **Core Application Files**

#### `processor_manager.py` - Main Orchestrator
- **Lines of Code**: ~200
- **Key Functions**:
  - `initialize_processors()`: Creates processor instances
  - `start_consumers()`: Starts Kafka message consumption  
  - `_keep_alive()`: Maintains service lifecycle
- **Dependencies**: All processor classes, Kafka manager
- **Configuration**: Uses processor thread counts from config

#### `api/main.py` - REST API Server  
- **Lines of Code**: ~300
- **Key Endpoints**:
  - `POST /send-event`: Single message processing
  - `POST /send-batch`: Bulk message processing
  - `GET /health`: System health check
- **Dependencies**: FastAPI, Pydantic, Kafka manager
- **Port**: 8082 (configurable in config.json)

### 🔄 **Processor Implementation Files**

#### `processors/base_processor.py` - Abstract Base Class
- **Lines of Code**: ~150
- **Key Methods**:
  - `process_message()`: Main processing workflow
  - `_validate_message()`: Input validation
  - `_create_response()`: Standardized response formatting
- **Purpose**: Defines common processor interface and behavior

#### `processors/show_details_processor.py` - Show Processor
- **Lines of Code**: ~100
- **Business Logic**: Simulates database record retrieval
- **Processing Time**: ~0.1 seconds (configurable)
- **Output**: Structured record information with metadata

#### `processors/update_details_processor.py` - Update Processor  
- **Lines of Code**: ~120
- **Business Logic**: Validates and processes record updates
- **Validation**: Field length, email format checks
- **Processing Time**: ~0.15 seconds (configurable)

#### `processors/create_details_processor.py` - Create Processor
- **Lines of Code**: ~130  
- **Business Logic**: Creates new records with validation
- **Required Fields**: `name` field is mandatory
- **Processing Time**: ~0.12 seconds (configurable)

### 🛠️ **Utility & Infrastructure Files**

#### `utils/kafka_manager.py` - Kafka Client Wrapper
- **Lines of Code**: ~250
- **Classes**:
  - `KafkaProducerWrapper`: Thread-safe message publishing
  - `KafkaConsumerWrapper`: Concurrent message consumption  
  - `KafkaManager`: Unified producer/consumer management
- **Thread Safety**: Full concurrent operation support

#### `config/__init__.py` - Configuration Management
- **Lines of Code**: ~80
- **Features**:
  - JSON configuration loading
  - Environment variable overrides
  - Type-safe configuration access
- **Docker Support**: Automatic environment variable detection

### 🐳 **Docker & Deployment Files**

#### `Dockerfile` - Container Definition
- **Base Image**: `python:3.11-slim`
- **Java Version**: OpenJDK 17
- **Exposed Port**: 8082
- **Health Check**: HTTP endpoint monitoring
- **Startup Script**: `/app/docker-start.sh`

#### `docker-compose.yml` - Service Orchestration
- **Services**: 4 (Zookeeper, Kafka, Kafka-UI, Processors)
- **Networks**: Internal Docker networking
- **Volumes**: Persistent data storage
- **Dependencies**: Service startup ordering

#### `docker-manage.sh` - Management Utility
- **Commands**: 8 management functions
- **Features**: Build, start, stop, logs, status, cleanup
- **Usage**: `./docker-manage.sh <command>`

### 🧪 **Testing & Utility Scripts**

#### `test_system.py` - Comprehensive Test Suite
- **Lines of Code**: ~200
- **Test Cases**:
  - API health verification
  - Individual processor testing  
  - Batch processing validation
  - Error handling verification
- **Dependencies**: requests library

#### `setup-topics.sh` - Topic Creation (Docker)
- **Purpose**: Creates Kafka topics in Docker environment
- **Topics Created**: details-input, details-output
- **Partition Count**: 3 per topic
- **Replication Factor**: 1

#### `start_all.sh` - Local System Startup
- **Services Started**: Processor manager, REST API
- **Background Processes**: 2 (with PID tracking)
- **Shutdown**: Ctrl+C signal handling

---

## 🔄 Adding New Processors

### Step 1: Create Processor Class
**File**: `processors/new_processor.py`
```python
from .base_processor import BaseProcessor

class NewProcessor(BaseProcessor):
    def _should_process(self, message):
        return message.get('action') == 'new_action'
    
    def _process_business_logic(self, message):
        # Your business logic here
        return {
            'status': 'success',
            'data': {'processed': True},
            'message': 'New action completed'
        }
```

### Step 2: Update Configuration
**File**: `config/config.json`
```json
{
    "processors": {
        "show_details": {"enabled": true, "threads": 2},
        "update_details": {"enabled": true, "threads": 2},
        "create_details": {"enabled": true, "threads": 2},
        "new_processor": {"enabled": true, "threads": 2}
    }
}
```

### Step 3: Register Processor
**File**: `processor_manager.py`
```python
# Add import
from processors import NewProcessor

# Add to initialize_processors method
self.processors = [
    ShowDetailsProcessor(self.kafka_manager, output_topic),
    UpdateDetailsProcessor(self.kafka_manager, output_topic), 
    CreateDetailsProcessor(self.kafka_manager, output_topic),
    NewProcessor(self.kafka_manager, output_topic)  # Add this line
]
```

### Step 4: Update Module Exports
**File**: `processors/__init__.py`
```python
from .new_processor import NewProcessor

__all__ = ['ShowDetailsProcessor', 'UpdateDetailsProcessor', 
           'CreateDetailsProcessor', 'NewProcessor', 'BaseProcessor']
```

---

## 🚀 Quick Start Commands

### Local Development
```bash
# Start system
cd /root/kafka/kafka-processors
./start_all.sh

# Test system  
python3 test_system.py

# View logs
tail -f logs/kafka-processors.log
```

### Docker Deployment
```bash  
# Build and start
./docker-manage.sh build
./docker-manage.sh up

# Create topics
./setup-topics.sh

# Test system
./docker-manage.sh test

# View logs
./docker-manage.sh logs kafka-processors
```

### Manual Topic Management
```bash
cd /root/kafka
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64

# List topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe topic
bin/kafka-topics.sh --describe --topic details-input --bootstrap-server localhost:9092

# Delete topic (if needed)
bin/kafka-topics.sh --delete --topic old-topic --bootstrap-server localhost:9092
```

---

## 📊 Performance Configuration

### Processor Threading
- **Current**: 2 threads per processor type (6 total)
- **Recommendation**: Adjust based on CPU cores and workload
- **Configuration**: `config/config.json` → `processors[].threads`

### Kafka Consumer Settings
- **Batch Size**: `max_poll_records: 100`
- **Timeout**: `consumer_timeout_ms: 5000`
- **Session**: `session_timeout_ms: 30000`

### API Server Settings
- **Workers**: Single process (development)
- **Production**: Use Gunicorn with multiple workers
- **Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app`

---

## 🔧 Troubleshooting File References

### Log Files
- **Application**: `/root/kafka/kafka-processors/logs/kafka-processors.log`
- **Kafka**: `/root/kafka/logs/kafka.log` 
- **Zookeeper**: `/root/kafka/logs/zookeeper.log`

### Configuration Files
- **Main Config**: `/root/kafka/kafka-processors/config/config.json`
- **Kafka Config**: `/root/kafka/config/server.properties`
- **Zookeeper Config**: `/root/kafka/config/zookeeper.properties`

### Key Directories
- **Kafka Installation**: `/root/kafka/`
- **Project Root**: `/root/kafka/kafka-processors/`
- **Python Packages**: Check with `pip list`

---

*This file structure guide provides complete information for understanding, configuring, and extending the Kafka Processors System. All file paths are relative to the project root unless otherwise specified.*