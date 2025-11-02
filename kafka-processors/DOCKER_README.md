# Kafka Processors - Docker Deployment Guide

A containerized Kafka-based server decommissioning pipeline with comprehensive health monitoring.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- 4GB+ RAM available for containers
- Ports 8080, 8082, 8090, 9092 available

### Launch the System
```bash
# Build and start all services
./docker-manage.sh build
./docker-manage.sh up

# Or in one command
docker-compose up --build -d
```

## 🌐 Service Endpoints

Once running, access these services:

| Service | URL | Description |
|---------|-----|-------------|
| **API Server** | http://localhost:8082 | Main application API |
| **API Documentation** | http://localhost:8082/docs | Interactive API docs |
| **System Health** | http://localhost:8082/health | Overall system status |
| **Processor Health** | http://localhost:8082/health/processors | Kafka processor status |
| **Kafka UI** | http://localhost:8080 | Kafka management interface |
| **Documentation** | http://localhost:8090 | Project documentation |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/API    │───▶│  Kafka Broker   │───▶│   Processors    │
│   (Port 8082)   │    │   (Port 9092)   │    │   (Container)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────▶│   Kafka UI      │◀─────────────┘
                        │   (Port 8080)   │
                        └─────────────────┘
```

## 🔧 Container Services

### kafka-processors
- **Main Application Container**
- Runs both API server and processor manager
- Health checks every 30 seconds
- Auto-restarts on failure

### kafka
- **Confluent Kafka Broker**
- Persistent data storage
- JMX monitoring enabled

### zookeeper  
- **Kafka Coordination Service**
- Persistent configuration storage

### kafka-ui
- **Web-based Kafka Management**
- Topic monitoring and management
- Consumer group tracking

### docs-server
- **Documentation Web Server**
- Serves project documentation
- Simple HTTP server

## 🛠️ Management Commands

Use the `docker-manage.sh` script for easy operations:

```bash
# View all services status
./docker-manage.sh status

# View logs (follow mode)
./docker-manage.sh logs [service-name]

# Run health checks
./docker-manage.sh test

# Open shell in container
./docker-manage.sh shell kafka-processors

# Restart all services  
./docker-manage.sh restart

# Clean shutdown
./docker-manage.sh down

# Complete cleanup (removes volumes)
./docker-manage.sh clean
```

## 📊 Health Monitoring

The system includes comprehensive health monitoring:

### System Health Check
```bash
curl http://localhost:8082/health | jq
```

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T14:35:39.627170",
  "services": {
    "kafka": "healthy",
    "processors": "healthy", 
    "api": "healthy"
  }
}
```

### Processor Health Check
```bash
curl http://localhost:8082/health/processors | jq
```

**Response Example:**
```json
{
  "status": "healthy",
  "processor_status": "healthy",
  "processor_info": {
    "status": "running",
    "pid": 123,
    "start_time": "2025-11-02T14:35:24.580216",
    "processors": 3,
    "executor_active": true
  },
  "message": "Kafka processors are running normally"
}
```

## 🔍 Health Status Meanings

| Status | Description |
|--------|-------------|
| `healthy` | All systems operational |
| `starting` | Services initializing |  
| `stopping` | Graceful shutdown in progress |
| `degraded` | Running but with issues |
| `not_running` | Service not detected |
| `stale` | Status not updated recently |

## 🐞 Troubleshooting

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f kafka-processors
```

### Restart Services
```bash
# Restart specific service
docker-compose restart kafka-processors

# Restart all
./docker-manage.sh restart
```

### Common Issues

**Port Already in Use:**
```bash
# Check what's using the port
sudo lsof -i :8082

# Kill conflicting process or change port in docker-compose.yml
```

**Kafka Connection Failed:**
```bash
# Check Kafka is running
docker-compose logs kafka

# Verify network connectivity
docker-compose exec kafka-processors nc -z kafka 29092
```

**Processors Not Starting:**
```bash
# Check processor manager logs
docker-compose logs kafka-processors | grep processor

# Check health endpoint
curl http://localhost:8082/health/processors
```

## 🔧 Configuration

### Environment Variables

Set in `docker-compose.yml` or `.env` file:

```env
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_HOST=kafka  
KAFKA_PORT=29092
PYTHONPATH=/app
```

### Volume Mounts

- `./logs:/app/logs` - Log file persistence
- `./config:/app/config` - Configuration files
- Named volumes for Kafka/Zookeeper data

### Custom Configuration

1. **Modify Kafka Settings**: Edit `docker-compose.yml` Kafka environment
2. **Change API Port**: Update ports mapping in `kafka-processors` service  
3. **Add Environment Variables**: Add to environment section
4. **Persistent Storage**: Volumes are configured for data persistence

## 📈 Scaling

### Scale Processors
```bash
# Scale processor workers (edit docker-compose.yml)
docker-compose up -d --scale kafka-processors=2
```

### Add Kafka Brokers
```bash
# Add additional Kafka services to docker-compose.yml
# Update KAFKA_BROKER_ID for each instance
```

## 🛡️ Security Notes

- **Development Setup**: Current configuration is for development
- **Production**: Add authentication, SSL, firewalls
- **Network**: Services communicate on Docker internal network
- **Data**: Persistent volumes store Kafka data

## 📚 Additional Resources

- **API Documentation**: http://localhost:8082/docs
- **Kafka UI**: http://localhost:8080  
- **Health Monitoring**: http://localhost:8082/health
- **Project Docs**: http://localhost:8090

---

**Built with:** Python 3.11, Apache Kafka 7.4.0, FastAPI, Docker Compose
**Developer:** Mahesh Gavandar