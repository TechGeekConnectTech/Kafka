import json
import logging
import os
from typing import Dict, Any

class Config:
    """Configuration manager for Kafka processors"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        with open(config_path, 'r') as f:
            self._config = json.load(f)
        
        # Override with environment variables if running in Docker
        self._override_with_env()
    
    @property
    def kafka(self) -> Dict[str, Any]:
        return self._config['kafka']
    
    @property
    def topics(self) -> Dict[str, str]:
        return self._config['topics']
    
    @property
    def processors(self) -> Dict[str, Any]:
        return self._config['processors']
    
    @property
    def api(self) -> Dict[str, Any]:
        return self._config['api']
    
    @property
    def logging(self) -> Dict[str, Any]:
        return self._config['logging']
    
    def get_processor_config(self, processor_name: str) -> Dict[str, Any]:
        return self.processors.get(processor_name, {})
    
    def _override_with_env(self):
        """Override configuration with environment variables for Docker"""
        # Override Kafka bootstrap servers
        kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        if kafka_servers:
            self._config['kafka']['bootstrap_servers'] = kafka_servers.split(',')
        
        # Override API host/port
        api_host = os.getenv('API_HOST')
        if api_host:
            self._config['api']['host'] = api_host
            
        api_port = os.getenv('API_PORT')
        if api_port:
            self._config['api']['port'] = int(api_port)

def setup_logging(config: Config):
    """Setup logging configuration"""
    log_config = config.logging
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get('file', 'logs/kafka-processors.log')
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)