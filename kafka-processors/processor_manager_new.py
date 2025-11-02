#!/usr/bin/env python3
"""
Main entry point for Server Demise Pipeline System
Starts all processors to handle the sequential pipeline flow
"""

import logging
import threading
import time
import signal
import sys
import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from utils.config_manager import ConfigManager
from processors.server_check_processor import ServerCheckProcessor
from processors.server_poweroff_processor import ServerPowerOffProcessor
from processors.server_cooling_processor import ServerCoolingPeriodProcessor
from processors.server_demise_processor import ServerDemiseProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServerDemisePipelineManager:
    """
    Manages the server demise pipeline with all three processors
    """
    
    def __init__(self):
        self.config = ConfigManager().get_config()
        self.status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor_status.json')
        self.start_time = None
        self.processors = []
        self.executor = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📝 Received signal {signum}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
        
    def _update_status_file(self, status: str, additional_info: dict = None):
        """Update the processor status file"""
        try:
            status_data = {
                'status': status,
                'pid': os.getpid(),
                'timestamp': datetime.now().isoformat(),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'processors': len(self.processors),
                'executor_active': self.executor is not None and not self.executor._shutdown
            }
            
            if additional_info:
                status_data.update(additional_info)
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update status file: {e}")
    
    def _remove_status_file(self):
        """Remove the status file on shutdown"""
        try:
            if os.path.exists(self.status_file):
                os.remove(self.status_file)
        except Exception as e:
            logger.error(f"Failed to remove status file: {e}")
        
    def initialize_processors(self):
        """Initialize all pipeline processors"""
        try:
            logger.info("🔧 Initializing Server Demise Pipeline processors...")
            
            # Initialize processors in order of pipeline
            self.processors = [
                ServerCheckProcessor(self.config),         # Step 1: Check server
                ServerPowerOffProcessor(self.config),      # Step 2: Power off
                ServerCoolingPeriodProcessor(self.config), # Step 2.5: 48-hour cooling period
                ServerDemiseProcessor(self.config)         # Step 3: Demise request
            ]
            
            logger.info(f"✅ Initialized {len(self.processors)} processors")
            
            # Display pipeline flow
            logger.info("📋 Server Demise Pipeline Flow:")
            logger.info("   API → check_server → poweroff_server → cooling_period → demise_server → complete")
            logger.info("   1️⃣  ServerCheckProcessor: Verify server in portal")
            logger.info("   2️⃣  ServerPowerOffProcessor: Power off server")
            logger.info("   2️⃣.5️⃣ ServerCoolingPeriodProcessor: 48-hour cooling period with monitoring")
            logger.info("   3️⃣  ServerDemiseProcessor: Execute decommission")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processors: {e}")
            return False
    
    def start(self):
        """Start all processors"""
        self.start_time = datetime.now()
        self._update_status_file('starting')
        
        if not self.initialize_processors():
            logger.error("❌ Failed to initialize processors, cannot start")
            self._update_status_file('failed', {'message': 'Failed to initialize processors'})
            return False
            
        try:
            self.running = True
            max_workers = sum(
                self.config['processors'][proc.processor_config_key]['max_workers'] 
                for proc in self.processors
            )
            
            logger.info(f"🚀 Starting Server Demise Pipeline with {max_workers} total workers")
            
            # Create thread pool for all processors
            self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="DemisePipeline")
            
            # Start each processor
            for processor in self.processors:
                logger.info(f"▶️  Starting {processor.__class__.__name__}...")
                processor_workers = self.config['processors'][processor.processor_config_key]['max_workers']
                
                # Start multiple worker threads for each processor
                for i in range(processor_workers):
                    self.executor.submit(self._run_processor, processor, i)
            
            logger.info("✅ All processors started successfully!")
            logger.info("🎯 Pipeline ready to process server demise requests")
            logger.info("📡 Send requests to API endpoint: /demise-server")
            
            self._update_status_file('running')
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start processors: {e}")
            return False
    
    def _run_processor(self, processor, worker_id):
        """Run a single processor worker"""
        processor_name = f"{processor.__class__.__name__}-Worker-{worker_id}"
        logger.info(f"🏃 {processor_name} started")
        
        try:
            while self.running:
                try:
                    processor.run_once()
                    time.sleep(0.1)  # Small delay to prevent CPU spinning
                except Exception as e:
                    logger.error(f"❌ Error in {processor_name}: {e}")
                    time.sleep(1)  # Longer delay on error
                    
        except Exception as e:
            logger.error(f"❌ Fatal error in {processor_name}: {e}")
        finally:
            logger.info(f"🛑 {processor_name} stopped")
    
    def stop(self):
        """Stop all processors gracefully"""
        logger.info("🛑 Stopping Server Demise Pipeline...")
        self.running = False
        self._update_status_file('stopping')
        
        # Stop all processors
        for processor in self.processors:
            try:
                processor.stop()
                logger.info(f"✅ {processor.__class__.__name__} stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping {processor.__class__.__name__}: {e}")
        
        # Shutdown executor
        if self.executor:
            logger.info("🔒 Shutting down thread pool...")
            self.executor.shutdown(wait=True, timeout=10)
            logger.info("✅ Thread pool shut down")
        
        logger.info("🎯 Server Demise Pipeline stopped successfully")
        self._remove_status_file()
    
    def get_status(self):
        """Get current pipeline status"""
        return {
            "running": self.running,
            "processors": [
                {
                    "name": proc.__class__.__name__,
                    "processor_id": proc.processor_id,
                    "config_key": proc.processor_config_key
                }
                for proc in self.processors
            ],
            "topic": self.config['topics']['server_demise_pipeline']['name']
        }

def main():
    """Main entry point"""
    logger.info("🎬 Starting Server Demise Pipeline System")
    
    pipeline_manager = ServerDemisePipelineManager()
    
    if pipeline_manager.start():
        try:
            logger.info("⏰ Pipeline running... Press Ctrl+C to stop")
            
            # Keep main thread alive and show periodic status
            while pipeline_manager.running:
                time.sleep(30)  # Status update every 30 seconds
                logger.info("💓 Pipeline heartbeat - system running normally")
                pipeline_manager._update_status_file('running')
                
        except KeyboardInterrupt:
            logger.info("⌨️  Keyboard interrupt received")
        finally:
            pipeline_manager.stop()
    else:
        logger.error("❌ Failed to start pipeline system")
        sys.exit(1)

if __name__ == "__main__":
    main()