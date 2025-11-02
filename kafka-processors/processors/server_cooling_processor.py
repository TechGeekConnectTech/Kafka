import json
import time
import logging
import uuid
import threading
from datetime import datetime, timedelta
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class ServerCoolingPeriodProcessor(BaseProcessor):
    """
    Processor 2.5: Server Cooling Period Monitor
    Handles 48-hour cooling period after server poweroff
    Checks every 2 hours if server is powered on
    Sends error if server powers on during cooling period
    Proceeds to demise after 48 hours if server remains off
    """
    
    def __init__(self, config):
        super().__init__(config, "server_cooling_processor")
        self.processor_name = "ServerCoolingPeriodProcessor"
        
        # Cooling period configuration (in hours)
        self.cooling_period_hours = 48
        self.check_interval_hours = 2
        
        # Active cooling sessions (server_id -> cooling_info)
        self.cooling_sessions = {}
        self.cooling_threads = {}
        
        # Lock for thread-safe operations
        self.sessions_lock = threading.Lock()
        
        logger.info(f"🕒 {self.processor_name} initialized with {self.cooling_period_hours}h cooling period")
        
    def should_process_message(self, message_data):
        """Check if this processor should handle the message"""
        action = message_data.get('action')
        status = message_data.get('status')
        
        # Handle messages from poweroff processor
        return (action == 'start_cooling_period' and status == 'pending')
    
    def process_message(self, message_data):
        """
        Start cooling period monitoring for a server
        """
        try:
            server_data = message_data.get('data', {})
            server_id = server_data.get('server_id')
            
            if not server_id:
                return self._create_error_response(message_data, "Server ID is required for cooling period")
            
            logger.info(f"🕒 Starting 48-hour cooling period for server: {server_id}")
            
            # Check if server is already in cooling period
            with self.sessions_lock:
                if server_id in self.cooling_sessions:
                    logger.warning(f"⚠️ Server {server_id} already in cooling period")
                    return self._create_status_response(message_data, "Server already in cooling period")
            
            # Start cooling period monitoring
            cooling_info = {
                'server_id': server_id,
                'server_details': server_data.get('server_details', {}),
                'poweroff_timestamp': server_data.get('poweroff_timestamp', datetime.now().isoformat()),
                'cooling_start': datetime.now(),
                'cooling_end': datetime.now() + timedelta(hours=self.cooling_period_hours),
                'original_message': message_data,
                'check_count': 0,
                'last_check': None,
                'status': 'monitoring'
            }
            
            with self.sessions_lock:
                self.cooling_sessions[server_id] = cooling_info
            
            # Start monitoring thread
            self._start_cooling_monitor(server_id, cooling_info)
            
            # Return immediate response
            response_data = {
                "id": str(uuid.uuid4()),
                "original_request_id": message_data.get('original_request_id', message_data.get('id')),
                "action": "cooling_period_started",
                "status": "monitoring",
                "processor": self.processor_name,
                "processor_id": self.processor_id,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "server_id": server_id,
                    "server_details": cooling_info['server_details'],
                    "cooling_start": cooling_info['cooling_start'].isoformat(),
                    "cooling_end": cooling_info['cooling_end'].isoformat(),
                    "cooling_period_hours": self.cooling_period_hours,
                    "check_interval_hours": self.check_interval_hours,
                    "poweroff_timestamp": cooling_info['poweroff_timestamp']
                },
                "message": f"Server {server_id} entered 48-hour cooling period. Monitoring every 2 hours.",
                "pipeline_step": "2.5",
                "next_step": "cooling_monitor"
            }
            
            logger.info(f"✅ Cooling period monitoring started for server {server_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"❌ Error starting cooling period: {str(e)}")
            return self._create_error_response(message_data, f"Cooling period start failed: {str(e)}")
    
    def _start_cooling_monitor(self, server_id, cooling_info):
        """Start background thread to monitor server during cooling period"""
        def monitor_cooling_period():
            logger.info(f"🔍 Starting cooling period monitor thread for server {server_id}")
            
            try:
                while True:
                    current_time = datetime.now()
                    
                    # Check if cooling period is complete
                    if current_time >= cooling_info['cooling_end']:
                        logger.info(f"⏰ Cooling period complete for server {server_id}")
                        self._handle_cooling_complete(server_id, cooling_info)
                        break
                    
                    # Perform power status check
                    self._perform_power_check(server_id, cooling_info)
                    
                    # Wait for next check interval
                    sleep_seconds = self.check_interval_hours * 3600
                    logger.info(f"😴 Next check for server {server_id} in {self.check_interval_hours} hours")
                    time.sleep(sleep_seconds)
                    
            except Exception as e:
                logger.error(f"❌ Error in cooling monitor for server {server_id}: {e}")
                self._handle_cooling_error(server_id, cooling_info, str(e))
            finally:
                # Cleanup thread reference
                with self.sessions_lock:
                    if server_id in self.cooling_threads:
                        del self.cooling_threads[server_id]
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_cooling_period, daemon=True)
        monitor_thread.start()
        
        with self.sessions_lock:
            self.cooling_threads[server_id] = monitor_thread
    
    def _perform_power_check(self, server_id, cooling_info):
        """Check if server is powered on during cooling period"""
        try:
            cooling_info['check_count'] += 1
            cooling_info['last_check'] = datetime.now()
            
            logger.info(f"🔍 Performing power check #{cooling_info['check_count']} for server {server_id}")
            
            # Simulate power status check
            power_status = self._check_server_power_status(server_id, cooling_info['server_details'])
            
            if power_status['is_powered_on']:
                logger.error(f"🚨 VIOLATION: Server {server_id} powered on during cooling period!")
                self._handle_cooling_violation(server_id, cooling_info, power_status)
            else:
                logger.info(f"✅ Server {server_id} remains powered off (check #{cooling_info['check_count']})")
                self._send_status_update(server_id, cooling_info, power_status)
                
        except Exception as e:
            logger.error(f"❌ Error checking power status for server {server_id}: {e}")
    
    def _check_server_power_status(self, server_id, server_details):
        """
        Check server power status
        Replace this with actual server management API calls (IPMI, BMC, etc.)
        """
        try:
            logger.info(f"Connecting to server {server_id} for power status check")
            time.sleep(0.5)  # Simulate connection time
            
            # Simulate IPMI/BMC power status query
            logger.info(f"Querying power status via IPMI for server {server_id}")
            time.sleep(1)  # Simulate query time
            
            # Simulate power status result
            # In real implementation: query actual server power status
            import random
            
            # 95% chance server remains off during cooling (5% chance of violation)
            is_powered_on = random.random() < 0.05
            
            power_info = {
                'is_powered_on': is_powered_on,
                'power_state': 'on' if is_powered_on else 'off',
                'check_method': 'IPMI',
                'check_timestamp': datetime.now().isoformat(),
                'response_time_ms': 1500,
                'server_ip': server_details.get('ip_address', 'unknown')
            }
            
            if is_powered_on:
                power_info.update({
                    'boot_time': (datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat(),
                    'power_on_reason': random.choice(['manual_power_on', 'wake_on_lan', 'scheduled_task', 'hardware_event'])
                })
            
            return power_info
            
        except Exception as e:
            return {
                'is_powered_on': False,  # Assume off if check fails
                'power_state': 'unknown',
                'check_method': 'IPMI',
                'error': str(e),
                'check_timestamp': datetime.now().isoformat()
            }
    
    def _handle_cooling_violation(self, server_id, cooling_info, power_status):
        """Handle server powering on during cooling period (violation)"""
        logger.error(f"🚨 COOLING PERIOD VIOLATION for server {server_id}")
        
        # Create violation error message
        error_response = {
            "id": str(uuid.uuid4()),
            "original_request_id": cooling_info['original_message'].get('original_request_id', cooling_info['original_message'].get('id')),
            "action": "cooling_violation_error",
            "status": "violation_error",
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "server_id": server_id,
                "server_details": cooling_info['server_details'],
                "violation_details": {
                    "power_status": power_status,
                    "violation_time": datetime.now().isoformat(),
                    "cooling_elapsed_hours": (datetime.now() - cooling_info['cooling_start']).total_seconds() / 3600,
                    "remaining_hours": (cooling_info['cooling_end'] - datetime.now()).total_seconds() / 3600,
                    "check_number": cooling_info['check_count']
                },
                "cooling_period_info": {
                    "cooling_start": cooling_info['cooling_start'].isoformat(),
                    "cooling_end": cooling_info['cooling_end'].isoformat(),
                    "total_checks_performed": cooling_info['check_count']
                }
            },
            "error": f"Server {server_id} powered on during mandatory cooling period",
            "message": f"CRITICAL: Server {server_id} violated cooling period by powering on. Demise process terminated.",
            "pipeline_step": "2.5",
            "pipeline_complete": True,
            "violation": True
        }
        
        # Send violation error message
        self._send_response(error_response)
        
        # Remove from cooling sessions
        with self.sessions_lock:
            if server_id in self.cooling_sessions:
                del self.cooling_sessions[server_id]
        
        logger.error(f"🛑 Demise process terminated for server {server_id} due to cooling violation")
    
    def _handle_cooling_complete(self, server_id, cooling_info):
        """Handle successful completion of cooling period"""
        logger.info(f"🎉 Cooling period successfully completed for server {server_id}")
        
        # Create completion message to proceed to demise
        completion_response = {
            "id": str(uuid.uuid4()),
            "original_request_id": cooling_info['original_message'].get('original_request_id', cooling_info['original_message'].get('id')),
            "action": "demise_server",  # Proceed to demise processor
            "status": "pending",
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "server_id": server_id,
                "server_details": cooling_info['server_details'],
                "cooling_completion": {
                    "cooling_start": cooling_info['cooling_start'].isoformat(),
                    "cooling_end": cooling_info['cooling_end'].isoformat(),
                    "actual_completion": datetime.now().isoformat(),
                    "total_checks_performed": cooling_info['check_count'],
                    "cooling_duration_hours": self.cooling_period_hours
                },
                "poweroff_timestamp": cooling_info['poweroff_timestamp'],
                "original_request": cooling_info['original_message'].get('data', {}).get('original_request', {})
            },
            "message": f"Server {server_id} completed 48-hour cooling period successfully. Proceeding to demise.",
            "pipeline_step": "2.5",
            "next_step": "demise_server"
        }
        
        # Send completion message
        self._send_response(completion_response)
        
        # Remove from cooling sessions
        with self.sessions_lock:
            if server_id in self.cooling_sessions:
                del self.cooling_sessions[server_id]
        
        logger.info(f"✅ Server {server_id} ready for demise process")
    
    def _handle_cooling_error(self, server_id, cooling_info, error_msg):
        """Handle errors during cooling period monitoring"""
        logger.error(f"❌ Cooling period error for server {server_id}: {error_msg}")
        
        error_response = {
            "id": str(uuid.uuid4()),
            "original_request_id": cooling_info['original_message'].get('original_request_id', cooling_info['original_message'].get('id')),
            "action": "cooling_error",
            "status": "error",
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "server_id": server_id,
                "server_details": cooling_info['server_details'],
                "error_details": {
                    "error_message": error_msg,
                    "error_time": datetime.now().isoformat(),
                    "checks_completed": cooling_info['check_count'],
                    "last_successful_check": cooling_info.get('last_check', {})
                }
            },
            "error": error_msg,
            "message": f"Cooling period monitoring failed for server {server_id}: {error_msg}",
            "pipeline_step": "2.5",
            "pipeline_complete": True
        }
        
        # Send error message
        self._send_response(error_response)
        
        # Remove from cooling sessions
        with self.sessions_lock:
            if server_id in self.cooling_sessions:
                del self.cooling_sessions[server_id]
    
    def _send_status_update(self, server_id, cooling_info, power_status):
        """Send periodic status update during cooling"""
        remaining_hours = (cooling_info['cooling_end'] - datetime.now()).total_seconds() / 3600
        
        status_response = {
            "id": str(uuid.uuid4()),
            "original_request_id": cooling_info['original_message'].get('original_request_id', cooling_info['original_message'].get('id')),
            "action": "cooling_status_update",
            "status": "monitoring",
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "server_id": server_id,
                "cooling_status": {
                    "remaining_hours": round(remaining_hours, 1),
                    "check_number": cooling_info['check_count'],
                    "power_status": power_status,
                    "next_check_in_hours": self.check_interval_hours
                }
            },
            "message": f"Server {server_id} cooling check #{cooling_info['check_count']}: OFF (✅) - {round(remaining_hours, 1)}h remaining",
            "pipeline_step": "2.5"
        }
        
        # Send status update (optional - for monitoring/logging)
        # self._send_response(status_response)
        logger.info(f"📊 Status update: Server {server_id} - {round(remaining_hours, 1)}h remaining")
    
    def get_cooling_status(self):
        """Get status of all cooling sessions (for monitoring)"""
        with self.sessions_lock:
            return {
                "total_sessions": len(self.cooling_sessions),
                "active_servers": list(self.cooling_sessions.keys()),
                "sessions": {
                    server_id: {
                        "cooling_start": info['cooling_start'].isoformat(),
                        "cooling_end": info['cooling_end'].isoformat(),
                        "remaining_hours": (info['cooling_end'] - datetime.now()).total_seconds() / 3600,
                        "check_count": info['check_count'],
                        "status": info['status']
                    }
                    for server_id, info in self.cooling_sessions.items()
                }
            }
    
    def stop(self):
        """Stop the processor and cleanup cooling sessions"""
        logger.info(f"🛑 Stopping {self.processor_name}")
        
        # Stop all cooling threads
        with self.sessions_lock:
            for server_id, thread in self.cooling_threads.items():
                logger.info(f"Stopping cooling monitor for server {server_id}")
                # Note: threads are daemon threads, they'll stop when main process stops
            
            self.cooling_threads.clear()
            self.cooling_sessions.clear()
        
        # Call parent stop method
        super().stop()
    
    def _create_error_response(self, original_message, error_msg, final_status="error"):
        """Create error response message"""
        return {
            "id": str(uuid.uuid4()),
            "original_request_id": original_message.get('original_request_id', original_message.get('id')),
            "action": "cooling_error",
            "status": final_status,
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": original_message.get('data', {}),
            "error": error_msg,
            "message": f"Cooling period failed: {error_msg}",
            "pipeline_step": "2.5",
            "pipeline_complete": True
        }
    
    def _create_status_response(self, original_message, status_msg):
        """Create status response message"""
        return {
            "id": str(uuid.uuid4()),
            "original_request_id": original_message.get('original_request_id', original_message.get('id')),
            "action": "cooling_status",
            "status": "info",
            "processor": self.processor_name,
            "processor_id": self.processor_id,
            "timestamp": datetime.now().isoformat(),
            "data": original_message.get('data', {}),
            "message": status_msg,
            "pipeline_step": "2.5"
        }