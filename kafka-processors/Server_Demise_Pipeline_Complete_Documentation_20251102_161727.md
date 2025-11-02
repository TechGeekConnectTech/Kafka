# Server Demise Pipeline System - Complete Documentation

**Generated:** 2025-11-02 16:17:27
**Version:** 3.1.0 with ServerCoolingPeriodProcessor  

## Project Overview

The Server Demise Pipeline System is a comprehensive Kafka-based event processing system with:

- **4-Stage Processing Pipeline:** PoweroffProcessor → ServerCoolingPeriodProcessor → DemiseProcessor → RepurposeProcessor
- **48-Hour Cooling Period:** Mandatory cooling time after server poweroff with continuous power monitoring
- **Health Monitoring:** Multi-layer health checks including Docker, Kafka, and processor status
- **Docker Containerization:** Complete Docker Compose setup with auto-restart and health checks
- **Production Ready:** Full deployment and integration documentation for company environments

## Architecture Overview

### Processing Flow
1. **PoweroffProcessor** - Handles server poweroff events and initiates pipeline
2. **ServerCoolingPeriodProcessor** - Enforces 48-hour cooling period with power monitoring every 2 hours
3. **DemiseProcessor** - Manages server demise process after successful cooling period
4. **RepurposeProcessor** - Handles server repurposing and cleanup workflow

### Container Architecture
- **Zookeeper** (Port 2181) - Kafka coordination and cluster management
- **Kafka** (Port 9092) - Message broker for event streaming
- **Kafka UI** (Port 8080) - Web-based Kafka management interface
- **Kafka Processors** (Port 8000) - Main application with health API endpoints
- **Docs Server** (Port 8081) - Documentation and monitoring server

## Quick Start Deployment

### For Your Company Environment

```bash
# 1. Clone and setup project
git clone <repository-url> kafka-processors
cd kafka-processors

# 2. Make scripts executable
chmod +x *.sh

# 3. Start all services with one command
./start_all.sh

# 4. Wait for services to initialize (2-3 minutes)
sleep 180

# 5. Verify deployment health
curl http://localhost:8000/health
curl http://localhost:8000/health/processors
```

### Access Points After Deployment
- **Health API:** http://localhost:8000/health
- **Kafka Management UI:** http://localhost:8080
- **System Documentation:** http://localhost:8081

## Key System Components

### Main Application Files

**processor_manager_new.py** - Primary application orchestrator
- Manages 4-processor sequential pipeline with cooling period enforcement
- Thread pool executor with 11 total workers (3+3+2+3 distribution)
- Comprehensive signal handling and graceful shutdown capabilities
- Automated status file updates every 30 seconds for monitoring

**processors/server_cooling_processor.py** - Core cooling period management
- Enforces mandatory 48-hour cooling period after server poweroff events
- Monitors server power status every 2 hours during cooling period
- Background threading system for concurrent cooling session management
- Power violation detection with automatic alerting and escalation

**api/main.py** - Health monitoring and status API
- Comprehensive system health checks via /health endpoint
- Detailed processor status monitoring via /health/processors endpoint
- Docker container health verification and reporting
- Kafka broker connectivity testing and validation

### Configuration and Deployment

**docker-compose.yml** - Complete container orchestration
- Multi-container setup with inter-service dependencies
- Automated health checks with configurable intervals and retries
- Automatic restart policies for production reliability
- Proper port mapping and volume mounts for data persistence

**config/processor_config.json** - System configuration management
- Individual processor worker counts and batch processing sizes
- Kafka connection parameters and security settings
- Cooling period duration and power monitoring intervals
- Comprehensive logging configuration and output destinations

**requirements.txt** - Python dependency management
- confluent-kafka==2.3.0 for Kafka client functionality
- fastapi==0.104.1 for health API endpoints
- uvicorn[standard]==0.24.0 for ASGI server
- Additional supporting libraries for system functionality

### Deployment and Management Scripts

**start_all.sh** - Complete service startup automation
**docker-manage.sh** - Docker container management utilities
**setup-topics.sh** - Kafka topic creation and configuration
**deploy-docker.sh** - Production deployment orchestration

## Health Monitoring System

### Available Health Endpoints

**GET /health** - Comprehensive system health status
- Real-time Kafka broker connectivity verification
- Processor manager operational status checking
- Docker container health assessment
- Overall system health determination and reporting

**GET /health/processors** - Detailed processor monitoring
- Individual processor health and operational status
- Processor status file freshness and validity checking
- Processing statistics and performance metrics
- Error rates and violation tracking

### Monitoring Integration Points
- **Primary Health API:** http://localhost:8000/health
- **Kafka Management Interface:** http://localhost:8080
- **Documentation Portal:** http://localhost:8081
- **Log File Monitoring:** logs/processor_manager.log

## Docker Container Configuration

### Service Architecture

The system uses Docker Compose for orchestration with the following services:

**Zookeeper Service:**
- Image: confluentinc/cp-zookeeper:7.4.0
- Port: 2181
- Role: Kafka cluster coordination
- Health checks every 30 seconds

**Kafka Broker Service:**
- Image: confluentinc/cp-kafka:7.4.0
- Port: 9092 (external), 29092 (internal)
- Role: Event streaming and message persistence
- JMX monitoring on port 9997

**Kafka UI Service:**
- Image: provectuslabs/kafka-ui:latest
- Port: 8080
- Role: Web-based Kafka management
- Real-time cluster monitoring

**Kafka Processors Service:**
- Custom build from project Dockerfile
- Port: 8000 (health API)
- Role: Main application processing
- Auto-restart with health monitoring

**Documentation Server:**
- Custom build from project Dockerfile
- Port: 8081
- Role: System documentation hosting
- Real-time documentation serving

### Health Check Configuration
- **Check Interval:** 30 seconds for all services
- **Timeout:** 10 seconds per check
- **Retry Count:** 3 attempts before marking unhealthy
- **Auto-restart:** Enabled unless manually stopped

## ServerCoolingPeriodProcessor Details

### Core Functionality

**Cooling Period Management:**
- Mandatory 48-hour cooling period after any server poweroff event
- Configurable cooling duration via processor_config.json
- Session-based tracking with persistent state management
- Thread-safe operations for concurrent cooling periods

**Power Status Monitoring:**
- Automated power status checks every 2 hours during cooling
- Configurable monitoring intervals for different environments
- Integration points for IPMI, SNMP, or custom power monitoring
- Violation detection with immediate alerting capabilities

**Session Management:**
- Active cooling session tracking with unique identifiers
- Violation counting and escalation procedures
- Status reporting for monitoring and debugging
- Clean shutdown procedures with session preservation

**Thread Safety and Concurrency:**
- Background monitoring threads for each cooling session
- Thread-safe session management with proper locking
- Concurrent cooling period handling for multiple servers
- Resource cleanup and memory management

### Configuration Options

**Cooling Period Settings:**
```json
{
  "server_cooling_processor": {
    "cooling_period_hours": 48,
    "check_interval_hours": 2,
    "max_sessions": 100,
    "worker_count": 3
  }
}
```

## Company Integration Guide

### Pre-Deployment Requirements

**Infrastructure Prerequisites:**
- Docker Engine 20.10+ with Docker Compose 2.0+
- Minimum system resources: 4GB RAM, 2 CPU cores
- Network connectivity for Kafka broker access
- Firewall configuration for ports: 8000, 8080, 8081, 9092

**Security and Compliance:**
- Review and approve Kafka security configuration
- Configure authentication mechanisms if required
- Setup SSL/TLS encryption for production environments
- Implement network segmentation and firewall rules

### Step-by-Step Company Deployment

**1. Environment Preparation**
```bash
# Create dedicated project directory
sudo mkdir -p /opt/kafka-processors
cd /opt/kafka-processors

# Clone repository with appropriate permissions
git clone <repository-url> .
sudo chown -R $(whoami):$(whoami) .
```

**2. Configuration Customization**
```bash
# Review and customize processor configuration
cat config/processor_config.json
vim config/processor_config.json

# Review Docker Compose configuration
cat docker-compose.yml
vim docker-compose.yml  # Adjust resource limits if needed
```

**3. Service Deployment**
```bash
# Make deployment scripts executable
chmod +x *.sh

# Execute complete service deployment
./start_all.sh

# Monitor startup process (typically 2-3 minutes)
sleep 180

# Verify all containers are healthy
docker-compose ps
```

**4. System Verification**
```bash
# Test comprehensive health endpoints
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/health/processors | jq .

# Verify Kafka broker functionality
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check processor logs for successful startup
tail -f logs/processor_manager.log
```

**5. Monitoring Setup**
```bash
# Display service access URLs
echo "=== System Access Points ==="
echo "Health API: http://$(hostname -I | awk '{print $1}'):8000/health"
echo "Kafka UI: http://$(hostname -I | awk '{print $1}'):8080"
echo "Documentation: http://$(hostname -I | awk '{print $1}'):8081"

# Setup continuous monitoring
watch -n 30 'curl -s http://localhost:8000/health'
```

### Customization for Company Environment

**Cooling Period Configuration:**
- Default cooling period: 48 hours (configurable)
- Power monitoring interval: 2 hours (adjustable)
- Maximum concurrent cooling sessions: 100 (scalable)
- Worker thread allocation: 3 per cooling processor (tunable)

**Resource Scaling Options:**
- Container memory limits in docker-compose.yml
- CPU allocation and processing limits
- Kafka partition counts for increased parallelism
- Worker thread counts per processor type

**Integration Points:**
- Health endpoint integration: /health for load balancer checks
- Log aggregation: logs/processor_manager.log for centralized logging
- Metrics export: Extensible for Prometheus/Grafana integration
- Alert integration: Webhook endpoints for violation notifications

## Troubleshooting Guide

### Common Deployment Issues

**Issue: Kafka Connection Failures**
```bash
# Diagnose Kafka broker status
docker ps | grep kafka
docker logs kafka

# Test Kafka connectivity
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check network connectivity
docker network ls
docker network inspect kafka-processors_default
```

**Issue: Processor Startup Problems**
```bash
# Examine processor logs
tail -f logs/processor_manager.log

# Check processor status via API
curl -v http://localhost:8000/health/processors

# Verify status file generation
cat processor_status.json
ls -la processor_status.json
```

**Issue: Health Check Failures**
```bash
# Test health endpoints directly
curl -v http://localhost:8000/health
curl -v http://localhost:8000/health/processors

# Check API server startup
docker logs kafka-processors

# Verify port accessibility
netstat -tulpn | grep :8000
```

**Issue: Docker Container Problems**
```bash
# Restart complete service stack
docker-compose down
docker-compose up -d

# Check individual container health
docker-compose ps
docker-compose logs kafka
docker-compose logs kafka-processors

# Review container resource usage
docker stats
```

### Log Analysis and Monitoring

**Primary Log Locations:**
- **Processor Manager:** logs/processor_manager.log
- **Docker Services:** docker-compose logs [service-name]
- **System Status:** processor_status.json (updated every 30s)
- **Health API:** Integrated into processor manager logs

**Log Monitoring Commands:**
```bash
# Real-time processor log monitoring
tail -f logs/processor_manager.log

# Docker container log streaming
docker-compose logs -f

# System health monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq .'

# Processor status tracking
watch -n 10 'cat processor_status.json | jq .'
```

## Production Deployment Considerations

### Performance Optimization

**Memory Management:**
- Java heap size configuration for Kafka containers
- Python memory limits for processor containers
- Docker container memory constraints and limits
- System-level memory allocation and swap configuration

**Network Performance:**
- Kafka partition count optimization for parallel processing
- Consumer group configuration for load distribution
- Network buffer size tuning for high throughput
- Connection pooling and timeout configuration

**Processing Efficiency:**
- Worker thread count optimization per processor type
- Message batch processing sizes for throughput
- Timeout values for different processing stages
- Queue depth monitoring and alert thresholds

### Security Hardening

**Network Security:**
- Firewall rule configuration and port restrictions
- Network segmentation between service tiers
- VPN or private network connectivity requirements
- Load balancer SSL termination configuration

**Application Security:**
- Kafka SASL/SSL authentication and encryption
- API authentication and authorization (extensible)
- Container security scanning and vulnerability management
- Secrets management for sensitive configuration

### Backup and Recovery Procedures

**Configuration Backup:**
```bash
# Create configuration backup archive
tar -czf kafka-processors-config-$(date +%Y%m%d).tar.gz     config/ docker-compose.yml *.sh requirements.txt

# Store backup in secure location
# Implement regular backup scheduling via cron
```

**Data Recovery:**
```bash
# Kafka topic data backup (if required)
# Processor state recovery procedures
# Log file archival and retention policies
```

### Monitoring and Alerting Integration

**Key Performance Indicators:**
- Processor manager operational status
- Individual processor health metrics
- Kafka broker connectivity and performance
- Docker container resource utilization

**Alert Conditions:**
- Processor manager shutdown or failure
- Cooling period violations detected
- Kafka connectivity issues
- Container resource exhaustion

**Integration Points:**
- Health endpoint polling: /health
- Log file monitoring: processor_manager.log
- Metrics export: Extensible for monitoring systems
- Webhook notifications: For critical alerts

## System Maintenance

### Regular Maintenance Tasks

**Daily Operations:**
- Monitor health endpoint status
- Review processor logs for errors
- Check Docker container resource usage
- Verify Kafka topic message flow

**Weekly Maintenance:**
- Rotate and archive log files
- Review cooling period statistics
- Update security patches if available
- Performance metric analysis

**Monthly Procedures:**
- Configuration backup verification
- Security audit and review
- Capacity planning assessment
- Documentation updates

### Upgrade Procedures

**Component Upgrade Process:**
1. Create full system backup
2. Test upgrade in non-production environment
3. Schedule maintenance window
4. Perform rolling upgrade of containers
5. Verify system functionality post-upgrade
6. Monitor for 24 hours after upgrade

## Support and Contact Information

### Technical Support Resources

**Immediate Issues:**
- Check health endpoints: http://localhost:8000/health
- Review logs: tail -f logs/processor_manager.log
- Container status: docker-compose ps
- System documentation: http://localhost:8081

**Configuration Questions:**
- Processor settings: config/processor_config.json
- Docker configuration: docker-compose.yml
- This documentation for complete reference

### System Status Verification

**Quick Health Check Commands:**
```bash
# Overall system health
curl -s http://localhost:8000/health | jq '.status'

# Processor-specific health
curl -s http://localhost:8000/health/processors | jq '.healthy'

# Container status
docker-compose ps --format "table {{.Name}}	{{.Status}}"

# Recent log entries
tail -n 20 logs/processor_manager.log
```

## Summary

The Server Demise Pipeline System provides a comprehensive, production-ready solution for managing server lifecycle events with mandatory cooling period enforcement. This system offers:

✅ **Complete 4-stage sequential processing pipeline** with cooling period management  
✅ **Comprehensive health monitoring** with multi-layer status verification  
✅ **Full Docker containerization** with automatic restart and health checks  
✅ **Real-time system monitoring** through web interfaces and API endpoints  
✅ **Production deployment readiness** with complete documentation  
✅ **Company integration support** with step-by-step deployment guides  

### Key Benefits for Your Company

**Operational Reliability:**
- Automated server lifecycle management
- Enforced cooling periods prevent premature actions
- Comprehensive error detection and alerting
- Self-healing container architecture

**Monitoring and Visibility:**
- Real-time health status monitoring
- Web-based Kafka management interface
- Comprehensive logging and audit trails
- Configurable alerting and notifications

**Deployment Simplicity:**
- Single-command deployment process
- Complete Docker containerization
- Automated service orchestration
- Production-ready configuration

### Next Steps for Implementation

1. **Review system requirements** and ensure infrastructure compatibility
2. **Execute deployment steps** following the company integration guide
3. **Verify all health endpoints** are accessible and reporting correctly
4. **Integrate monitoring URLs** into your existing monitoring infrastructure
5. **Setup log aggregation** and alerting based on your company standards
6. **Test cooling period functionality** with simulated server poweroff events

### Post-Deployment Access Points

After successful deployment, access your system through:
- **Health Monitoring:** http://your-server:8000/health
- **Kafka Management:** http://your-server:8080
- **System Documentation:** http://your-server:8081

---

**Server Demise Pipeline System v3.1.0**  
**Complete Company Deployment Documentation**  
**Generated: 2025-11-02 16:17:27**

*This documentation provides complete information for deploying and managing the Server Demise Pipeline System in your company environment. All source code, configurations, and deployment procedures are included for successful implementation.*
