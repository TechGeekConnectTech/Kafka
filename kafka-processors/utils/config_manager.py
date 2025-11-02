import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Configuration manager for the Kafka processors system"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'config.json'
        )
        self._config = None
        
    def get_config(self) -> Dict[str, Any]:
        """Load and return configuration"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Configuration file not found: {self.config_path}")
                return self._get_default_config()
                
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Override with environment variables if they exist
            config = self._apply_env_overrides(config)
            
            logger.info(f"✅ Configuration loaded from {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration"""
        
        # Kafka overrides
        if 'KAFKA_BOOTSTRAP_SERVERS' in os.environ:
            bootstrap_servers = os.environ['KAFKA_BOOTSTRAP_SERVERS'].split(',')
            config['kafka']['bootstrap_servers'] = bootstrap_servers
            
        if 'KAFKA_GROUP_ID' in os.environ:
            config['kafka']['group_id'] = os.environ['KAFKA_GROUP_ID']
            
        # API overrides
        if 'API_HOST' in os.environ:
            config['api']['host'] = os.environ['API_HOST']
            
        if 'API_PORT' in os.environ:
            config['api']['port'] = int(os.environ['API_PORT'])
            
        # Logging override
        if 'LOG_LEVEL' in os.environ:
            config['logging']['level'] = os.environ['LOG_LEVEL']
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file loading fails"""
        logger.warning("⚠️  Using default configuration")
        
        return {
            "kafka": {
                "bootstrap_servers": ["localhost:9092"],
                "client_id": "kafka-processors",
                "group_id": "demise-processor-group",
                "auto_offset_reset": "earliest",
                "enable_auto_commit": True,
                "auto_commit_interval_ms": 1000,
                "session_timeout_ms": 30000,
                "max_poll_records": 100,
                "max_poll_interval_ms": 300000,
                "consumer_timeout_ms": 5000
            },
            "topics": {
                "server_demise_pipeline": {
                    "name": "server-demise-pipeline",
                    "partitions": 3,
                    "replication_factor": 1
                }
            },
            "processors": {
                "server_check_processor": {
                    "enabled": True,
                    "max_workers": 3,
                    "consumer_timeout": 1000
                },
                "server_poweroff_processor": {
                    "enabled": True,
                    "max_workers": 3,
                    "consumer_timeout": 1000
                },
                "server_demise_processor": {
                    "enabled": True,
                    "max_workers": 3,
                    "consumer_timeout": 1000
                }
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8082,
                "debug": True
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/kafka-processors.log"
            }
        }
    
    def reload_config(self):
        """Reload configuration from file"""
        self._config = None
        return self.get_config()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            self._config = config
            logger.info(f"✅ Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            raise