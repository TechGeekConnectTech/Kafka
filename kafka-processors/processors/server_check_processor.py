import json
import time
import logging
import uuid
from datetime import datetime
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class ServerCheckProcessor(BaseProcessor):
    """
    Processor 1: Check if server exists in portal/database
    Processes messages with action: 'check_server'
    """
    
    def __init__(self, config):
        super().__init__(config, "server_check_processor")
        self.processor_name = "ServerCheckProcessor"
        
    def should_process_message(self, message_data):
        """Check if this processor should handle the message"""
        return message_data.get('action') == 'check_server' and message_data.get('status') == 'pending'
    
    def process_message(self, message_data):
        """
        Check if server exists in portal/database
        """
        try:
            server_id = message_data.get('data', {}).get('server_id')
            
            if not server_id:
                return self._create_error_response(message_data, "Server ID is required")
            
            logger.info(f"🔍 Checking server existence for ID: {server_id}")
            
            # Simulate server existence check (replace with actual database/portal check)
            server_exists = self._check_server_in_portal(server_id)
            
            if server_exists:
                # Server found - proceed to next step (power off)
                response_data = {
                    "id": str(uuid.uuid4()),
                    "original_request_id": message_data.get('id'),
                    "action": "poweroff_server",  # Next action for Processor 2
                    "status": "pending",
                    "processor": self.processor_name,
                    "processor_id": self.processor_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "server_id": server_id,
                        "server_details": {
                            "hostname": f"server-{server_id}",
                            "ip_address": f"192.168.1.{server_id}",
                            "status": "active",
                            "location": "datacenter-1"
                        },
                        "check_result": "server_found",
                        "original_request": message_data.get('data', {})
                    },
                    "message": f"Server {server_id} found in portal. Ready for power off.",
                    "pipeline_step": 1,
                    "next_step": "poweroff_server"
                }
                
                logger.info(f"✅ Server {server_id} found in portal")
                return response_data
            else:
                # Server not found - end pipeline with error
                return self._create_error_response(
                    message_data, 
                    f"Server {server_id} not found in portal",
                    final_status="failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in server check: {str(e)}")
            return self._create_error_response(message_data, f"Server check failed: {str(e)}")
    
    def _check_server_in_portal(self, server_id):
        """
        Simulate checking server existence in portal/database
        Replace this with actual API call or database query
        """
        time.sleep(0.5)  # Simulate network delay
        
        # Simulate: servers with IDs 100-999 exist in portal
        try:
            server_num = int(server_id)
            return 100 <= server_num <= 999
        except ValueError:
            # For non-numeric IDs, check if they start with valid prefixes
            valid_prefixes = ['SRV', 'HOST', 'VM', 'PROD', 'TEST']
            return any(server_id.upper().startswith(prefix) for prefix in valid_prefixes)
    
    def _create_error_response(self, original_message, error_msg, final_status="error"):
        """Create error response message"""
        return {
            "id": str(uuid.uuid4()),
            "original_request_id": original_message.get('id'),
            "action": "demise_complete",
            "status": final_status,
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": original_message.get('data', {}),
            "error": error_msg,
            "message": f"Pipeline terminated: {error_msg}",
            "pipeline_step": 1,
            "pipeline_complete": True
        }