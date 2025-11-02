#!/usr/bin/env python3
"""
Test script for ServerCoolingPeriodProcessor
Simulates the full pipeline flow
"""

import json
import uuid
import time
from datetime import datetime
from kafka import KafkaProducer

def create_test_message():
    """Create a test server demise request"""
    return {
        "id": str(uuid.uuid4()),
        "action": "check_server",
        "status": "pending",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "server_id": "test-server-001",
            "server_details": {
                "hostname": "test-srv-001.datacenter.com",
                "ip_address": "192.168.1.100",
                "location": "DC1-Rack-15-U20",
                "serial_number": "TST001234567"
            },
            "original_request": {
                "requested_by": "admin@company.com",
                "reason": "End of lifecycle - decommission",
                "priority": "standard"
            }
        },
        "message": "Test server demise request for cooling period processor"
    }

def send_test_message():
    """Send test message to Kafka"""
    try:
        # Initialize Kafka producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            client_id="cooling-period-test"
        )
        
        # Create test message
        test_message = create_test_message()
        
        print("🚀 Sending test server demise request to pipeline...")
        print(f"📋 Server ID: {test_message['data']['server_id']}")
        print(f"🕐 Timestamp: {test_message['timestamp']}")
        
        # Send message to topic
        future = producer.send(
            'server-demise-pipeline',
            value=test_message
        )
        
        # Wait for message to be sent
        result = future.get(timeout=10)
        
        print(f"✅ Message sent successfully!")
        print(f"📊 Topic: {result.topic}")
        print(f"🔢 Partition: {result.partition}")
        print(f"📍 Offset: {result.offset}")
        
        producer.close()
        
        print("\n🔍 Monitor the processor logs to see the cooling period in action:")
        print("   1️⃣  ServerCheckProcessor will verify the server")
        print("   2️⃣  ServerPowerOffProcessor will power off the server")
        print("   🕒  ServerCoolingPeriodProcessor will start 48-hour cooling period")
        print("       - Monitoring every 2 hours for power status")
        print("       - Will error if server powers on during cooling")
        print("       - Will proceed to demise after 48 hours if server stays off")
        print("   3️⃣  ServerDemiseProcessor will handle final decommission")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ServerCoolingPeriodProcessor")
    print("=" * 50)
    
    if send_test_message():
        print("\n✅ Test message sent successfully!")
        print("🔍 Check the processor logs for cooling period monitoring...")
    else:
        print("\n❌ Failed to send test message")