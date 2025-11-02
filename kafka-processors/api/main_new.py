from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import uuid
from datetime import datetime
import logging
import asyncio
from contextlib import asynccontextmanager

# Import our utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_manager import ConfigManager
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
kafka_producer = None
config = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global kafka_producer, config
    try:
        config = ConfigManager().get_config()
        kafka_producer = KafkaProducer(
            bootstrap_servers=config['kafka']['bootstrap_servers'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all',
            retries=3
        )
        logger.info("🚀 Kafka Producer initialized successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize Kafka Producer: {e}")
        raise
    finally:
        # Shutdown
        if kafka_producer:
            kafka_producer.close()
            logger.info("🔒 Kafka Producer closed")

app = FastAPI(
    title="Server Demise Pipeline API",
    description="REST API for Server Decommissioning Pipeline with Kafka Integration",
    version="1.0.0",
    lifespan=lifespan
)

# Pydantic models
class ServerDemiseRequest(BaseModel):
    server_id: str
    reason: Optional[str] = "Planned decommission"
    priority: Optional[str] = "normal"  # low, normal, high, urgent
    requester: Optional[str] = "system"
    additional_data: Optional[Dict[Any, Any]] = {}

class BatchServerDemiseRequest(BaseModel):
    servers: List[ServerDemiseRequest]
    batch_id: Optional[str] = None

class EventResponse(BaseModel):
    message_id: str
    status: str
    message: str
    timestamp: str
    pipeline_initiated: bool

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Server Demise Pipeline API",
        "version": "1.0.0",
        "description": "Kafka-based server decommissioning pipeline",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "demise_server": "/demise-server",
            "batch_demise": "/batch-demise-servers",
            "pipeline_status": "/pipeline-status"
        },
        "pipeline_flow": [
            "1. API receives demise request",
            "2. ServerCheckProcessor verifies server in portal", 
            "3. ServerPowerOffProcessor powers off server",
            "4. ServerDemiseProcessor executes decommission"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Kafka connection
        if kafka_producer:
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "api": "online",
                    "kafka_producer": "connected",
                    "pipeline_processors": "active"
                }
            }
        else:
            return {
                "status": "degraded", 
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "api": "online",
                    "kafka_producer": "disconnected",
                    "pipeline_processors": "unknown"
                }
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/demise-server", response_model=EventResponse)
async def initiate_server_demise(request: ServerDemiseRequest):
    """
    Initiate server decommissioning pipeline
    
    This will start the 3-step pipeline:
    1. Check server existence in portal
    2. Power off the server  
    3. Execute demise/decommission request
    """
    try:
        if not kafka_producer:
            raise HTTPException(status_code=503, detail="Kafka producer not available")
        
        # Create pipeline initiation message
        message_id = str(uuid.uuid4())
        pipeline_message = {
            "id": message_id,
            "action": "check_server",  # Start with first processor
            "status": "pending",
            "processor": "API",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "server_id": request.server_id,
                "reason": request.reason,
                "priority": request.priority,
                "requester": request.requester,
                "additional_data": request.additional_data
            },
            "message": f"Server demise pipeline initiated for server {request.server_id}",
            "pipeline_step": 0,
            "next_step": "check_server"
        }
        
        # Send to Kafka topic
        topic_name = config['topics']['server_demise_pipeline']['name']
        future = kafka_producer.send(topic_name, value=pipeline_message)
        future.get(timeout=10)  # Wait for send confirmation
        
        logger.info(f"✅ Pipeline initiated for server {request.server_id} with message ID: {message_id}")
        return EventResponse(
            message_id=message_id,
            status="initiated",
            message=f"Server demise pipeline initiated for server {request.server_id}",
            timestamp=datetime.now().isoformat(),
            pipeline_initiated=True
        )
            
    except Exception as e:
        logger.error(f"❌ Error initiating server demise: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline initiation failed: {str(e)}")

@app.post("/batch-demise-servers")
async def batch_server_demise(request: BatchServerDemiseRequest):
    """
    Initiate batch server decommissioning
    """
    try:
        if not kafka_producer:
            raise HTTPException(status_code=503, detail="Kafka producer not available")
        
        batch_id = request.batch_id or str(uuid.uuid4())
        responses = []
        topic_name = config['topics']['server_demise_pipeline']['name']
        
        for server_request in request.servers:
            message_id = str(uuid.uuid4())
            pipeline_message = {
                "id": message_id,
                "batch_id": batch_id,
                "action": "check_server",
                "status": "pending", 
                "processor": "API",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "server_id": server_request.server_id,
                    "reason": server_request.reason,
                    "priority": server_request.priority,
                    "requester": server_request.requester,
                    "additional_data": server_request.additional_data
                },
                "message": f"Batch server demise pipeline initiated for server {server_request.server_id}",
                "pipeline_step": 0,
                "next_step": "check_server"
            }
            
            try:
                future = kafka_producer.send(topic_name, value=pipeline_message)
                future.get(timeout=5)  # Wait for send confirmation
                success = True
            except Exception as e:
                logger.error(f"Failed to send message for server {server_request.server_id}: {e}")
                success = False
            
            responses.append({
                "server_id": server_request.server_id,
                "message_id": message_id,
                "status": "initiated" if success else "failed",
                "pipeline_initiated": success
            })
        
        return {
            "batch_id": batch_id,
            "total_servers": len(request.servers),
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in batch server demise: {e}")
        raise HTTPException(status_code=500, detail=f"Batch pipeline initiation failed: {str(e)}")

@app.get("/pipeline-status")
async def get_pipeline_info():
    """Get information about the pipeline configuration"""
    try:
        return {
            "pipeline_name": "Server Demise Pipeline",
            "topic": config['topics']['server_demise_pipeline']['name'],
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
            ],
            "message_format": {
                "id": "unique-message-id",
                "action": "check_server|poweroff_server|demise_server|demise_complete",
                "status": "pending|completed|failed|error",
                "processor": "processor-name",
                "pipeline_step": "0-3",
                "data": {"server_id": "required"}
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting pipeline info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pipeline information")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)