import json
import logging
from typing import Dict, Any, List, Callable
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import threading
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class KafkaProducerWrapper:
    """Thread-safe Kafka producer wrapper"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config['bootstrap_servers'],
            client_id=config['client_id'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None,
            acks='all',
            retries=3,
            batch_size=16384,
            linger_ms=10,
            buffer_memory=33554432
        )
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None) -> bool:
        """Send a message to Kafka topic"""
        try:
            future = self.producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent to {topic} - partition: {record_metadata.partition}, offset: {record_metadata.offset}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to {topic}: {e}")
            return False
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close()

class KafkaConsumerWrapper:
    """Thread-safe Kafka consumer wrapper with concurrent message processing"""
    
    def __init__(self, config: Dict[str, Any], topics: List[str], message_handler: Callable, max_workers: int = 2):
        self.config = config
        self.topics = topics
        self.message_handler = message_handler
        self.max_workers = max_workers
        self.running = False
        self.consumer = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def start_consuming(self):
        """Start consuming messages from Kafka topics"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.config['bootstrap_servers'],
                group_id=self.config['group_id'],
                auto_offset_reset=self.config['auto_offset_reset'],
                enable_auto_commit=self.config['enable_auto_commit'],
                auto_commit_interval_ms=self.config['auto_commit_interval_ms'],
                session_timeout_ms=self.config['session_timeout_ms'],
                max_poll_records=self.config['max_poll_records'],
                max_poll_interval_ms=self.config['max_poll_interval_ms'],
                consumer_timeout_ms=self.config['consumer_timeout_ms'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            
            self.running = True
            logger.info(f"Started consuming from topics: {self.topics}")
            
            while self.running:
                try:
                    message_batch = self.consumer.poll(timeout_ms=1000)
                    
                    if message_batch:
                        # Process messages concurrently
                        for topic_partition, messages in message_batch.items():
                            for message in messages:
                                if self.running:
                                    self.executor.submit(self._process_message, message)
                                    
                except Exception as e:
                    logger.error(f"Error while polling messages: {e}")
                    time.sleep(1)  # Brief pause before retrying
                    
        except Exception as e:
            logger.error(f"Failed to start consumer: {e}")
        finally:
            self.stop_consuming()
    
    def _process_message(self, message):
        """Process a single message"""
        try:
            logger.info(f"Processing message from {message.topic} - partition: {message.partition}, offset: {message.offset}")
            self.message_handler(message.value)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        self.executor.shutdown(wait=True)
        logger.info("Stopped consuming messages")

class KafkaManager:
    """Unified Kafka manager for producers and consumers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.producer = KafkaProducerWrapper(config)
        self.consumers = {}
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None) -> bool:
        """Send message using the producer"""
        return self.producer.send_message(topic, message, key)
    
    def create_consumer(self, consumer_id: str, topics: List[str], message_handler: Callable, max_workers: int = 2):
        """Create a new consumer"""
        consumer = KafkaConsumerWrapper(self.config, topics, message_handler, max_workers)
        self.consumers[consumer_id] = consumer
        return consumer
    
    def start_consumer(self, consumer_id: str):
        """Start a consumer by ID"""
        if consumer_id in self.consumers:
            thread = threading.Thread(target=self.consumers[consumer_id].start_consuming)
            thread.daemon = True
            thread.start()
            return thread
        return None
    
    def stop_consumer(self, consumer_id: str):
        """Stop a consumer by ID"""
        if consumer_id in self.consumers:
            self.consumers[consumer_id].stop_consuming()
    
    def close_all(self):
        """Close all producers and consumers"""
        self.producer.close()
        for consumer in self.consumers.values():
            consumer.stop_consuming()