from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import logging
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, setup_logging
from utils.kafka_manager import KafkaManager

# Setup logging and configuration
config = Config()
logger = setup_logging(config)

# Initialize Kafka manager
kafka_manager = KafkaManager(config.kafka)

# Initialize FastAPI app
app = FastAPI(
    title="Kafka Processors API",
    description="REST API for sending events to Kafka processors",
    version="1.0.0"
)

# Pydantic models for request/response
class MessageRequest(BaseModel):
    action: str = Field(..., description="Action to perform: show_details, update_details, or create_details")
    data: Dict[str, Any] = Field(default={}, description="Data payload for the action")
    id: Optional[str] = Field(None, description="Optional message ID (will be generated if not provided)")

class MessageResponse(BaseModel):
    message_id: str
    status: str
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

class ProcessorHealthResponse(BaseModel):
    status: str
    timestamp: str
    processor_status: str
    processor_info: Optional[Dict[str, Any]] = None
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Kafka Processors API")
    try:
        # Test Kafka connection
        test_message = {"test": "connection", "timestamp": datetime.now().isoformat()}
        topic_name = config.topics.get('server_demise_pipeline', {}).get('name', 'server-demise-pipeline')
        success = kafka_manager.send_message(topic_name, test_message, key="health_check")
        if success:
            logger.info("Kafka connection test successful")
        else:
            logger.warning("Kafka connection test failed")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down Kafka Processors API")
    kafka_manager.close_all()

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Kafka Processors API",
        "version": "1.0.0",
        "description": "REST API for sending events to Kafka processors",
        "endpoints": {
            "health": "/health",
            "processor_health": "/health/processors",
            "send_event": "/send-event",
            "send_batch": "/send-batch",
            "config": "/config",
            "docs": "/docs"
        }
    }

def _check_processor_status():
    """Check if Kafka processors are running by reading status file"""
    status_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'processor_status.json')
    
    try:
        if not os.path.exists(status_file):
            return "not_running", None, "Processor status file not found"
        
        # Check if file was modified recently (within last 60 seconds)
        file_age = datetime.now().timestamp() - os.path.getmtime(status_file)
        if file_age > 60:
            return "stale", None, f"Status file is stale (last updated {file_age:.0f} seconds ago)"
        
        with open(status_file, 'r') as f:
            status_data = json.load(f)
        
        processor_status = status_data.get('status', 'unknown')
        
        if processor_status == 'running':
            return "healthy", status_data, "Kafka processors are running normally"
        elif processor_status == 'starting':
            return "starting", status_data, "Kafka processors are starting up"
        elif processor_status == 'stopping':
            return "stopping", status_data, "Kafka processors are shutting down"
        elif processor_status == 'degraded':
            return "degraded", status_data, "Kafka processors are running but degraded"
        else:
            return "unknown", status_data, f"Unknown processor status: {processor_status}"
            
    except json.JSONDecodeError:
        return "error", None, "Invalid JSON in processor status file"
    except Exception as e:
        return "error", None, f"Error reading processor status: {str(e)}"

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test Kafka connectivity
        test_message = {"health_check": True, "timestamp": datetime.now().isoformat()}
        topic_name = config.topics.get('server_demise_pipeline', {}).get('name', 'server-demise-pipeline')
        kafka_success = kafka_manager.send_message(topic_name, test_message, key="health_check")
        
        # Check processor status
        processor_status, _, _ = _check_processor_status()
        
        services_status = {
            "kafka": "healthy" if kafka_success else "unhealthy",
            "processors": "healthy" if processor_status == "healthy" else processor_status,
            "api": "healthy"
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            services=services_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            services={"kafka": "unknown", "processors": "unknown", "api": "unhealthy"}
        )

@app.get("/health/processors", response_model=ProcessorHealthResponse)
async def processor_health_check():
    """Dedicated health check endpoint for Kafka processors"""
    try:
        processor_status, processor_info, message = _check_processor_status()
        
        return ProcessorHealthResponse(
            status="healthy" if processor_status == "healthy" else "unhealthy",
            timestamp=datetime.now().isoformat(),
            processor_status=processor_status,
            processor_info=processor_info,
            message=message
        )
    except Exception as e:
        logger.error(f"Processor health check failed: {e}")
        return ProcessorHealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            processor_status="error",
            processor_info=None,
            message=f"Health check error: {str(e)}"
        )

@app.post("/send-event", response_model=MessageResponse)
async def send_event(request: MessageRequest, background_tasks: BackgroundTasks):
    """Send an event to Kafka for processing"""
    try:
        # Validate action
        valid_actions = ['show_details', 'update_details', 'create_details']
        if request.action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
            )
        
        # Generate message ID if not provided
        message_id = request.id or str(uuid.uuid4())
        
        # Create message payload
        message = {
            "id": message_id,
            "action": request.action,
            "data": request.data,
            "timestamp": datetime.now().isoformat(),
            "source": "rest_api"
        }
        
        # Send to Kafka
        topic_name = config.topics.get('server_demise_pipeline', {}).get('name', 'server-demise-pipeline')
        success = kafka_manager.send_message(
            topic_name, 
            message, 
            key=message_id
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send message to Kafka"
            )
        
        logger.info(f"Event sent successfully: {message_id} - Action: {request.action}")
        
        return MessageResponse(
            message_id=message_id,
            status="sent",
            message=f"Event sent successfully for processing. Action: {request.action}",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending event: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/send-batch", response_model=Dict[str, Any])
async def send_batch_events(requests: list[MessageRequest]):
    """Send multiple events to Kafka for processing"""
    try:
        if not requests:
            raise HTTPException(status_code=400, detail="No events provided")
        
        if len(requests) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 events allowed per batch")
        
        results = []
        
        for request in requests:
            # Validate action
            valid_actions = ['show_details', 'update_details', 'create_details']
            if request.action not in valid_actions:
                results.append({
                    "message_id": request.id or str(uuid.uuid4()),
                    "status": "error",
                    "message": f"Invalid action: {request.action}"
                })
                continue
            
            # Generate message ID if not provided
            message_id = request.id or str(uuid.uuid4())
            
            # Create message payload
            message = {
                "id": message_id,
                "action": request.action,
                "data": request.data,
                "timestamp": datetime.now().isoformat(),
                "source": "rest_api_batch"
            }
            
            # Send to Kafka
            topic_name = config.topics.get('server_demise_pipeline', {}).get('name', 'server-demise-pipeline')
            success = kafka_manager.send_message(
                topic_name, 
                message, 
                key=message_id
            )
            
            results.append({
                "message_id": message_id,
                "status": "sent" if success else "failed",
                "message": f"Event {'sent' if success else 'failed'} for action: {request.action}"
            })
        
        successful_count = sum(1 for r in results if r["status"] == "sent")
        
        logger.info(f"Batch processing complete: {successful_count}/{len(requests)} events sent")
        
        return {
            "total_events": len(requests),
            "successful": successful_count,
            "failed": len(requests) - successful_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current API configuration (non-sensitive parts)"""
    return {
        "kafka": {
            "topics": config.topics,
            "bootstrap_servers": config.kafka["bootstrap_servers"]
        },
        "api": config.api,
        "processors": {
            name: {"enabled": proc_config.get("enabled", False)}
            for name, proc_config in config.processors.items()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.api["host"],
        port=config.api["port"],
        reload=config.api.get("debug", False),
        log_level="info"
    )