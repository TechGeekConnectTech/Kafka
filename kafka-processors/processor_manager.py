#!/usr/bin/env python3
"""
Kafka Processors Manager
Main entry point for running all Kafka processors simultaneously
"""

import sys
import os
import threading
import time
import signal
import logging
import json
from datetime import datetime
from typing import List, Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config, setup_logging
from utils.kafka_manager import KafkaManager
from processors import ShowDetailsProcessor, UpdateDetailsProcessor, CreateDetailsProcessor

class ProcessorManager:
    """Manages all Kafka processors"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.kafka_manager = KafkaManager(config.kafka)
        self.processors = []
        self.consumer_threads = []
        self.running = False
        self.status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor_status.json')
        self.start_time = None
        
        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown()
    
    def _update_status_file(self, status: str, additional_info: Dict = None):
        """Update the processor status file"""
        try:
            status_data = {
                'status': status,
                'pid': os.getpid(),
                'timestamp': datetime.now().isoformat(),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'processors': len(self.processors),
                'consumer_threads': len([t for t in self.consumer_threads if t.is_alive()]),
                'total_threads': len(self.consumer_threads)
            }
            
            if additional_info:
                status_data.update(additional_info)
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update status file: {e}")
    
    def _remove_status_file(self):
        """Remove the status file on shutdown"""
        try:
            if os.path.exists(self.status_file):
                os.remove(self.status_file)
        except Exception as e:
            self.logger.error(f"Failed to remove status file: {e}")
    
    def initialize_processors(self):
        """Initialize all processors"""
        try:
            output_topic = self.config.topics['output']
            
            # Create processor instances
            self.processors = [
                ShowDetailsProcessor(self.kafka_manager, output_topic),
                UpdateDetailsProcessor(self.kafka_manager, output_topic),
                CreateDetailsProcessor(self.kafka_manager, output_topic)
            ]
            
            self.logger.info(f"Initialized {len(self.processors)} processors")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize processors: {e}")
            raise
    
    def create_message_handler(self, processors: List):
        """Create a message handler that routes to appropriate processors"""
        def handle_message(message: Dict[str, Any]):
            """Handle incoming message by routing to appropriate processor"""
            try:
                action = message.get('action')
                self.logger.debug(f"Handling message with action: {action}")
                
                # Route message to all processors (they'll filter themselves)
                for processor in processors:
                    try:
                        processor.process_message(message)
                    except Exception as e:
                        self.logger.error(f"Error in processor {processor.__class__.__name__}: {e}")
                        
            except Exception as e:
                self.logger.error(f"Error handling message: {e}")
        
        return handle_message
    
    def start_consumers(self):
        """Start Kafka consumers for each processor type"""
        try:
            input_topic = self.config.topics['input']
            
            # Create consumer for all processors
            message_handler = self.create_message_handler(self.processors)
            
            # Get max workers from config
            total_workers = sum(
                proc_config.get('threads', 2) 
                for proc_config in self.config.processors.values()
                if proc_config.get('enabled', True)
            )
            
            consumer = self.kafka_manager.create_consumer(
                'all_processors',
                [input_topic],
                message_handler,
                max_workers=total_workers
            )
            
            # Start consumer in separate thread
            consumer_thread = self.kafka_manager.start_consumer('all_processors')
            if consumer_thread:
                self.consumer_threads.append(consumer_thread)
                self.logger.info(f"Started consumer for topic: {input_topic} with {total_workers} workers")
            
        except Exception as e:
            self.logger.error(f"Failed to start consumers: {e}")
            raise
    
    def start(self):
        """Start the processor manager"""
        try:
            self.logger.info("Starting Kafka Processor Manager...")
            self.start_time = datetime.now()
            
            # Update status file - starting
            self._update_status_file('starting')
            
            # Initialize processors
            self.initialize_processors()
            
            # Start consumers
            self.start_consumers()
            
            self.running = True
            self.logger.info("Kafka Processor Manager started successfully")
            
            # Update status file - running
            self._update_status_file('running')
            
            # Keep the main thread alive
            self._keep_alive()
            
        except Exception as e:
            self.logger.error(f"Failed to start processor manager: {e}")
            self.shutdown()
            raise
    
    def _keep_alive(self):
        """Keep the main thread alive while processors are running"""
        try:
            last_update = time.time()
            
            while self.running:
                time.sleep(1)
                
                # Update status file every 30 seconds with heartbeat
                current_time = time.time()
                if current_time - last_update >= 30:
                    self._update_status_file('running')
                    last_update = current_time
                
                # Check if consumer threads are still alive
                alive_threads = [t for t in self.consumer_threads if t.is_alive()]
                if len(alive_threads) != len(self.consumer_threads):
                    self.logger.warning("Some consumer threads have died, shutting down...")
                    self._update_status_file('degraded', {'message': 'Some consumer threads died'})
                    break
                    
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in keep_alive loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all processors"""
        if not self.running:
            return
            
        self.logger.info("Shutting down processor manager...")
        self.running = False
        
        # Update status file - shutting down
        self._update_status_file('stopping')
        
        try:
            # Stop Kafka manager
            self.kafka_manager.close_all()
            
            # Wait for consumer threads to finish
            for thread in self.consumer_threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            self.logger.info("Processor manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            # Remove status file on shutdown
            self._remove_status_file()
    
    def status(self) -> Dict[str, Any]:
        """Get status of all processors"""
        return {
            'running': self.running,
            'processors': len(self.processors),
            'consumer_threads': len([t for t in self.consumer_threads if t.is_alive()]),
            'total_threads': len(self.consumer_threads)
        }

def main():
    """Main entry point"""
    try:
        # Load configuration
        config = Config()
        logger = setup_logging(config)
        
        logger.info("=" * 50)
        logger.info("KAFKA PROCESSORS MANAGER")
        logger.info("=" * 50)
        
        # Create and start processor manager
        manager = ProcessorManager(config)
        manager.start()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()