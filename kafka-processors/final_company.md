Essential Files for Company Environment (Kafka Topic Provided)
1. Core Application Files (Must Copy)
2. 📁 kafka-processors/
├── 📄 processor_manager_company.py     # Modified main application (see below)
├── 📁 api/
│   └── 📄 main.py                      # FastAPI REST API server
├── 📁 processors/
│   ├── 📄 __init__.py
│   ├── 📄 base_processor.py
│   ├── 📄 server_check_processor.py
│   ├── 📄 server_poweroff_processor.py
│   ├── 📄 server_cooling_processor.py
│   └── 📄 server_demise_processor.py
├── 📁 utils/
│   ├── 📄 __init__.py
│   ├── 📄 config_manager.py
│   ├── 📄 kafka_producer.py
│   └── 📄 kafka_consumer.py
└── 📁 config/
    └── 📄 company_config.json          # Company-specific config (see below)

   2. Modified Configuration for Company Environment
Create config/company_config.json:
{
    "kafka": {
        "bootstrap_servers": ["your-company-kafka-broker:9092"],
        "topics": {
            "server_demise_pipeline": {
                "name": "your-company-provided-topic-name",
                "partitions": 3,
                "replication_factor": 1
            }
        },
        "consumer_group": "server-demise-processors",
        "security": {
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            "sasl_username": "your-company-username",
            "sasl_password": "your-company-password"
        }
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8082
    },
    "processors": {
        "server_check_processor": {
            "enabled": true,
            "max_workers": 2,
            "consumer_timeout": 1000
        },
        "server_poweroff_processor": {
            "enabled": true,
            "max_workers": 2,
            "consumer_timeout": 1000
        },
        "server_cooling_processor": {
            "enabled": true,
            "max_workers": 2,
            "consumer_timeout": 1000,
            "cooling_period_hours": 48,
            "check_interval_hours": 2
        },
        "server_demise_processor": {
            "enabled": true,
            "max_workers": 2,
            "consumer_timeout": 1000
        }
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
3. Simplified Main Application
Create processor_manager_company.py (modified version without Kafka setup):
#!/usr/bin/env python3
"""
Company Version - Server Demise Pipeline System
No Kafka setup required - uses company-provided Kafka topics
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

class CompanyServerDemisePipeline:
    """
    Company Version - Server Demise Pipeline Manager
    Uses company-provided Kafka infrastructure
    """
    
    def __init__(self, config_file='config/company_config.json'):
        self.config = ConfigManager(config_file).get_config()
        self.status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor_status.json')
        self.start_time = None
        self.processors = []
        self.executor = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Validate company Kafka connection
        self._validate_company_kafka()
        
    def _validate_company_kafka(self):
        """Validate connection to company Kafka infrastructure"""
        try:
            bootstrap_servers = self.config['kafka']['bootstrap_servers']
            topic_name = self.config['kafka']['topics']['server_demise_pipeline']['name']
            
            logger.info("🏢 Company Kafka Configuration:")
            logger.info(f"   📡 Brokers: {bootstrap_servers}")
            logger.info(f"   📝 Topic: {topic_name}")
            logger.info(f"   👥 Consumer Group: {self.config['kafka']['consumer_group']}")
            
            # Test connection (optional - remove if not needed)
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                security_protocol=self.config['kafka'].get('security', {}).get('security_protocol', 'PLAINTEXT'),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            producer.close()
            logger.info("✅ Successfully connected to company Kafka infrastructure")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not validate Kafka connection: {e}")
            logger.info("   This may be normal if Kafka requires VPN or special network access")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📝 Received signal {signum}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
    
    def _update_status_file(self, status: str, additional_info: dict = None):
        """Update processor status file"""
        try:
            status_data = {
                'status': status,
                'pid': os.getpid(),
                'timestamp': datetime.now().isoformat(),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'processors': len(self.processors),
                'executor_active': self.executor is not None and not self.executor._shutdown,
                'company_deployment': True
            }
            
            if additional_info:
                status_data.update(additional_info)
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update status file: {e}")
    
    def initialize_processors(self):
        """Initialize all pipeline processors for company environment"""
        try:
            logger.info("🔧 Initializing Company Server Demise Pipeline...")
            
            # Initialize processors
            self.processors = [
                ServerCheckProcessor(self.config),         # Step 1: Verify server in company portal
                ServerPowerOffProcessor(self.config),      # Step 2: Power off via company IPMI
                ServerCoolingPeriodProcessor(self.config), # Step 2.5: 48-hour cooling period
                ServerDemiseProcessor(self.config)         # Step 3: Company asset management
            ]
            
            logger.info(f"✅ Initialized {len(self.processors)} processors for company environment")
            
            # Display company pipeline flow
            logger.info("📋 Company Server Demise Pipeline Flow:")
            logger.info("   Company API → check_server → poweroff_server → cooling_period → demise_server → complete")
            logger.info("   1️⃣  Verify server in company portal/CMDB")
            logger.info("   2️⃣  Power off via company IPMI/BMC systems")
            logger.info("   2️⃣.5️⃣ 48-hour cooling period with monitoring")
            logger.info("   3️⃣  Execute company decommission workflow")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processors: {e}")
            return False
    
    def start(self):
        """Start the company pipeline"""
        self.start_time = datetime.now()
        self._update_status_file('starting')
        
        if not self.initialize_processors():
            logger.error("❌ Failed to initialize processors")
            return False
        
        try:
            self.running = True
            max_workers = sum(
                self.config['processors'][proc.processor_config_key]['max_workers'] 
                for proc in self.processors
            )
            
            logger.info(f"🚀 Starting Company Server Demise Pipeline with {max_workers} workers")
            
            # Create thread pool
            self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="CompanyDemise")
            
            # Start processor workers
            for processor in self.processors:
                logger.info(f"▶️  Starting {processor.__class__.__name__}...")
                processor_workers = self.config['processors'][processor.processor_config_key]['max_workers']
                
                for i in range(processor_workers):
                    self.executor.submit(self._run_processor, processor, i)
            
            logger.info("✅ Company pipeline started successfully!")
            logger.info("🏢 Ready to process company server decommission requests")
            
            self._update_status_file('running')
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start pipeline: {e}")
            return False
    
    def _run_processor(self, processor, worker_id):
        """Run processor worker"""
        processor_name = f"{processor.__class__.__name__}-Worker-{worker_id}"
        logger.info(f"🏃 {processor_name} started")
        
        try:
            while self.running:
                try:
                    processor.run_once()
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"❌ Error in {processor_name}: {e}")
                    time.sleep(1)
        except Exception as e:
            logger.error(f"❌ Fatal error in {processor_name}: {e}")
        finally:
            logger.info(f"🛑 {processor_name} stopped")
    
    def stop(self):
        """Stop the pipeline"""
        logger.info("🛑 Stopping Company Server Demise Pipeline...")
        self.running = False
        self._update_status_file('stopping')
        
        # Stop processors
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
        
        logger.info("🎯 Company pipeline stopped successfully")
        try:
            os.remove(self.status_file)
        except:
            pass

def main():
    """Main entry point for company deployment"""
    logger.info("🏢 Starting Company Server Demise Pipeline System")
    
    pipeline_manager = CompanyServerDemisePipeline()
    
    if pipeline_manager.start():
        try:
            logger.info("⏰ Company pipeline running... Press Ctrl+C to stop")
            
            while pipeline_manager.running:
                time.sleep(30)
                logger.info("💓 Company pipeline heartbeat - system running normally")
                pipeline_manager._update_status_file('running')
                
        except KeyboardInterrupt:
            logger.info("⌨️  Keyboard interrupt received")
        finally:
            pipeline_manager.stop()
    else:
        logger.error("❌ Failed to start company pipeline system")
        sys.exit(1)

if __name__ == "__main__":
    main()

    4. Simple Requirements File
Create requirements.txt:
kafka-python==2.0.2
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0

🚀 Step-by-Step Company Setup
Step 1: Environment Setup

# Create project directory
mkdir kafka-processors
cd kafka-processors

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

Step 2: Configure Company Kafka
Edit config/company_config.json with your company's:
Kafka broker addresses
Topic name (provided by your company)
Security credentials (username/password/certificates)
Consumer group name
Step 3: Customize Business Logic
Modify these files for your company's systems:

processors/server_check_processor.py - Connect to company CMDB/portal
processors/server_poweroff_processor.py - Use company IPMI/BMC systems
processors/server_demise_processor.py - Integrate with company asset management

Step 4: Start Application

# Start processors
python3 processor_manager_company.py

# In another terminal, start API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8082

# Health check
curl http://localhost:8082/health

# Test server demise
curl -X POST "http://localhost:8082/demise-server" \
  -H "Content-Type: application/json" \
  -d '{"server_id": "your-company-server-id", "reason": "Decommission"}'

  
