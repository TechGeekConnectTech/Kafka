import abc
import logging
import uuid
import time
import json
from typing import Dict, Any
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class BaseProcessor(abc.ABC):
    """
    Base class for all processors in the server demise pipeline
    Handles Kafka communication and message processing flow
    """
    
    def __init__(self, config, processor_config_key):
        self.config = config
        self.processor_config_key = processor_config_key
        self.processor_id = str(uuid.uuid4())
        self.running = False
        
        # Get processor-specific config
        self.processor_config = config['processors'][processor_config_key]
        
        # Initialize Kafka consumer and producer
        self.consumer = None
        self.producer = None
        self.topic_name = config['topics']['server_demise_pipeline']['name']
        self._initialize_kafka()
        
        logger.info(f"✅ Initialized {self.__class__.__name__} with ID: {self.processor_id}")
    
    def _initialize_kafka(self):
        """Initialize Kafka consumer and producer"""
        try:
            # Create consumer for the pipeline topic
            self.consumer = KafkaConsumer(
                self.topic_name,
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                group_id=self.config['kafka']['group_id'],
                auto_offset_reset=self.config['kafka']['auto_offset_reset'],
                enable_auto_commit=self.config['kafka']['enable_auto_commit'],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=self.processor_config.get('consumer_timeout', 1000),
                max_poll_records=10,  # Process multiple messages at once
                session_timeout_ms=30000,
                heartbeat_interval_ms=3000
            )
            
            # Create producer for sending responses
            self.producer = KafkaProducer(
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10
            )
            
            logger.info(f"🔌 Kafka initialized for {self.__class__.__name__}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka for {self.__class__.__name__}: {e}")
            raise
    
    def run_once(self):
        """Run one iteration of message processing"""
        try:
            if not self.consumer:
                logger.error(f"❌ Consumer not initialized for {self.__class__.__name__}")
                return
            
            # Poll for messages with timeout
            message_batch = self.consumer.poll(timeout_ms=1000, max_records=10)
            
            if message_batch:
                # Process each partition's messages
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            self._handle_message(message.value)
                        except Exception as e:
                            logger.error(f"❌ Error processing message: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error in run_once for {self.__class__.__name__}: {e}")
            time.sleep(1)  # Back off on error
    
    def _handle_message(self, message_data):
        """Handle a single message"""
        try:
            # Check if this processor should handle this message
            if not self.should_process_message(message_data):
                return
            
            # Log message processing
            message_id = message_data.get('id', 'unknown')
            action = message_data.get('action', 'unknown')
            logger.info(f"🔄 Processing message {message_id} with action: {action}")
            
            # Process the message
            result = self.process_message(message_data)
            
            # Send response if processing generated a result
            if result:
                self._send_response(result)
                logger.info(f"✅ Processed and sent response for message {message_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            self._send_error_response(message_data, str(e))
    
    def _send_response(self, response_data):
        """Send response message to the pipeline topic"""
        try:
            if self.producer:
                future = self.producer.send(self.topic_name, value=response_data)
                # Wait for send to complete (with timeout)
                future.get(timeout=5)
                
        except Exception as e:
            logger.error(f"❌ Failed to send response: {e}")
    
    def _send_error_response(self, original_message, error_message):
        """Send error response"""
        try:
            error_response = {
                "id": str(uuid.uuid4()),
                "original_request_id": original_message.get('id', str(uuid.uuid4())),
                "action": "error",
                "status": "error",
                "processor": self.__class__.__name__,
                "processor_id": self.processor_id,
                "timestamp": datetime.now().isoformat(),
                "data": original_message.get('data', {}),
                "error": error_message,
                "message": f"Processing failed: {error_message}",
                "pipeline_complete": True
            }
            self._send_response(error_response)
            
        except Exception as e:
            logger.error(f"❌ Failed to send error response: {e}")
    
    def stop(self):
        """Stop the processor"""
        self.running = False
        try:
            if self.consumer:
                self.consumer.close()
            if self.producer:
                self.producer.close()
            logger.info(f"🛑 Stopped {self.__class__.__name__}")
        except Exception as e:
            logger.error(f"❌ Error stopping {self.__class__.__name__}: {e}")
    
    @abc.abstractmethod
    def should_process_message(self, message_data) -> bool:
        """
        Check if this processor should handle the message
        Each processor should implement this to filter messages
        """
        pass
    
    @abc.abstractmethod
    def process_message(self, message_data) -> Dict[str, Any]:
        """
        Process the message and return response data
        Each processor should implement its business logic here
        """
        pass