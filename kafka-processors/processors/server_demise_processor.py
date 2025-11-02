import json
import time
import logging
import uuid
from datetime import datetime
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class ServerDemiseProcessor(BaseProcessor):
    """
    Processor 3: Execute server demise/decommission request
    Processes messages with action: 'demise_server'
    """
    
    def __init__(self, config):
        super().__init__(config, "server_demise_processor")
        self.processor_name = "ServerDemiseProcessor"
        
    def should_process_message(self, message_data):
        """Check if this processor should handle the message"""
        return (message_data.get('action') == 'demise_server' and 
                message_data.get('status') == 'pending')
    
    def process_message(self, message_data):
        """
        Execute server demise/decommission request
        """
        try:
            server_data = message_data.get('data', {})
            server_id = server_data.get('server_id')
            server_details = server_data.get('server_details', {})
            poweroff_result = server_data.get('poweroff_result', {})
            
            if not server_id:
                return self._create_error_response(message_data, "Server ID is required")
            
            logger.info(f"🗑️ Initiating demise request for server: {server_id}")
            
            # Execute server demise process
            demise_result = self._execute_server_demise(server_id, server_details, poweroff_result)
            
            if demise_result['success']:
                # Server demise completed successfully - end pipeline
                response_data = {
                    "id": str(uuid.uuid4()),
                    "original_request_id": message_data.get('original_request_id', message_data.get('id')),
                    "action": "demise_complete",
                    "status": "completed",
                    "processor": self.processor_name,
                    "processor_id": self.processor_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "server_id": server_id,
                        "server_details": server_details,
                        "poweroff_result": poweroff_result,
                        "demise_result": demise_result,
                        "completion_timestamp": datetime.now().isoformat(),
                        "pipeline_summary": {
                            "step_1": "Server found in portal",
                            "step_2": "Server powered off successfully",
                            "step_3": "Server demise request completed"
                        },
                        "original_request": server_data.get('original_request', {})
                    },
                    "message": f"Server {server_id} demise process completed successfully.",
                    "pipeline_step": 3,
                    "pipeline_complete": True,
                    "total_processing_time": self._calculate_processing_time(message_data)
                }
                
                logger.info(f"✅ Server {server_id} demise process completed successfully")
                return response_data
            else:
                # Demise failed - end pipeline with error
                return self._create_error_response(
                    message_data, 
                    f"Failed to demise server {server_id}: {demise_result.get('error')}",
                    final_status="failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in server demise: {str(e)}")
            return self._create_error_response(message_data, f"Server demise failed: {str(e)}")
    
    def _execute_server_demise(self, server_id, server_details, poweroff_result):
        """
        Simulate server demise/decommission execution
        Replace this with actual demise system API calls
        """
        try:
            logger.info(f"Processing demise request for server {server_id}")
            
            # Step 1: Remove from monitoring systems
            time.sleep(0.5)
            logger.info(f"Removed server {server_id} from monitoring systems")
            
            # Step 2: Update inventory database
            time.sleep(0.5)
            logger.info(f"Updated inventory status for server {server_id}")
            
            # Step 3: Remove from DNS/DHCP
            time.sleep(0.3)
            logger.info(f"Removed DNS/DHCP entries for server {server_id}")
            
            # Step 4: Update asset management
            time.sleep(0.7)
            logger.info(f"Updated asset management for server {server_id}")
            
            # Step 5: Remove from load balancers
            time.sleep(0.4)
            logger.info(f"Removed server {server_id} from load balancers")
            
            # Step 6: Update configuration management
            time.sleep(0.3)
            logger.info(f"Updated configuration management for server {server_id}")
            
            # Step 7: Generate decommission ticket
            time.sleep(0.4)
            logger.info(f"Generated decommission ticket for server {server_id}")
            
            # Simulate success/failure (95% success rate)
            import random
            if random.random() > 0.05:  # 95% success rate
                ticket_id = f"DM-{int(time.time())}-{server_id}"
                return {
                    "success": True,
                    "demise_ticket_id": ticket_id,
                    "status": "decommissioned",
                    "steps_completed": [
                        "removed_from_monitoring",
                        "inventory_updated", 
                        "dns_dhcp_removed",
                        "asset_management_updated",
                        "load_balancer_updated",
                        "config_management_updated",
                        "decommission_ticket_created"
                    ],
                    "execution_time": "3.1s",
                    "decommission_date": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Asset management system unavailable",
                    "status": "partial_demise",
                    "steps_completed": ["removed_from_monitoring", "inventory_updated"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "demise_failed"
            }
    
    def _calculate_processing_time(self, original_message):
        """Calculate total processing time from original request"""
        try:
            if 'timestamp' in original_message:
                original_time = datetime.fromisoformat(original_message['timestamp'].replace('Z', '+00:00'))
                current_time = datetime.now()
                delta = current_time - original_time.replace(tzinfo=None)
                return f"{delta.total_seconds():.2f}s"
        except:
            pass
        return "unknown"
    
    def _create_error_response(self, original_message, error_msg, final_status="error"):
        """Create error response message"""
        return {
            "id": str(uuid.uuid4()),
            "original_request_id": original_message.get('original_request_id', original_message.get('id')),
            "action": "demise_complete",
            "status": final_status,
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": original_message.get('data', {}),
            "error": error_msg,
            "message": f"Pipeline terminated: {error_msg}",
            "pipeline_step": 3,
            "pipeline_complete": True
        }