import json
import time
import logging
import uuid
from datetime import datetime
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class ServerPowerOffProcessor(BaseProcessor):
    """
    Processor 2: Power off the server
    Processes messages with action: 'poweroff_server'
    """
    
    def __init__(self, config):
        super().__init__(config, "server_poweroff_processor")
        self.processor_name = "ServerPowerOffProcessor"
        
    def should_process_message(self, message_data):
        """Check if this processor should handle the message"""
        return (message_data.get('action') == 'poweroff_server' and 
                message_data.get('status') == 'pending')
    
    def process_message(self, message_data):
        """
        Power off the server
        """
        try:
            server_data = message_data.get('data', {})
            server_id = server_data.get('server_id')
            server_details = server_data.get('server_details', {})
            
            if not server_id:
                return self._create_error_response(message_data, "Server ID is required")
            
            logger.info(f"🔌 Initiating power off for server: {server_id}")
            
            # Simulate server power off process
            poweroff_result = self._execute_server_poweroff(server_id, server_details)
            
            if poweroff_result['success']:
                # Server powered off successfully - proceed to demise request
                response_data = {
                    "id": str(uuid.uuid4()),
                    "original_request_id": message_data.get('original_request_id', message_data.get('id')),
                    "action": "demise_server",  # Next action for Processor 3
                    "status": "pending",
                    "processor": self.processor_name,
                    "processor_id": self.processor_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "server_id": server_id,
                        "server_details": server_details,
                        "poweroff_result": poweroff_result,
                        "poweroff_timestamp": datetime.now().isoformat(),
                        "original_request": server_data.get('original_request', {})
                    },
                    "message": f"Server {server_id} powered off successfully. Ready for demise request.",
                    "pipeline_step": 2,
                    "next_step": "demise_server"
                }
                
                logger.info(f"✅ Server {server_id} powered off successfully")
                return response_data
            else:
                # Power off failed - end pipeline with error
                return self._create_error_response(
                    message_data, 
                    f"Failed to power off server {server_id}: {poweroff_result.get('error')}",
                    final_status="failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in server power off: {str(e)}")
            return self._create_error_response(message_data, f"Server power off failed: {str(e)}")
    
    def _execute_server_poweroff(self, server_id, server_details):
        """
        Simulate server power off execution
        Replace this with actual server management API calls (IPMI, BMC, etc.)
        """
        try:
            logger.info(f"Connecting to server {server_id} at {server_details.get('ip_address')}")
            time.sleep(1)  # Simulate connection time
            
            # Simulate power status check
            logger.info(f"Checking current power status for server {server_id}")
            time.sleep(0.5)
            
            # Simulate power off command
            logger.info(f"Executing power off command for server {server_id}")
            time.sleep(2)  # Simulate power off execution
            
            # Simulate verification
            logger.info(f"Verifying power off status for server {server_id}")
            time.sleep(1)
            
            # Simulate success/failure (90% success rate)
            import random
            if random.random() > 0.1:  # 90% success rate
                return {
                    "success": True,
                    "power_status": "off",
                    "poweroff_method": "IPMI",
                    "execution_time": "4.5s",
                    "verification": "confirmed_off"
                }
            else:
                return {
                    "success": False,
                    "error": "IPMI connection timeout",
                    "power_status": "unknown",
                    "attempted_method": "IPMI"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "power_status": "unknown"
            }
    
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
            "pipeline_step": 2,
            "pipeline_complete": True
        }