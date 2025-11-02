#!/usr/bin/env python3
"""
Test script for Kafka Processors System
Tests all processors with sample data
"""

import requests
import json
import time
import uuid
from datetime import datetime

# API endpoint
API_BASE_URL = "http://localhost:8082"

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health: {health_data['status']}")
            print(f"   Services: {health_data['services']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def send_test_event(action, data, message_id=None):
    """Send a test event to the API"""
    payload = {
        "action": action,
        "data": data
    }
    if message_id:
        payload["id"] = message_id
    
    try:
        response = requests.post(f"{API_BASE_URL}/send-event", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sent {action} event - ID: {result['message_id']}")
            return result['message_id']
        else:
            print(f"❌ Failed to send {action} event: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error sending {action} event: {e}")
        return None

def test_show_details():
    """Test show_details processor"""
    print("\n📋 Testing show_details processor...")
    
    test_data = {
        "name": "Test Record 001",
        "description": "This is a test record for show_details",
        "created_date": "2024-01-15T10:30:00"
    }
    
    message_id = send_test_event("show_details", test_data)
    return message_id

def test_create_details():
    """Test create_details processor"""
    print("\n📝 Testing create_details processor...")
    
    test_data = {
        "name": "New Test Record",
        "description": "This is a newly created test record",
        "category": "test",
        "email": "test@example.com"
    }
    
    message_id = send_test_event("create_details", test_data)
    return message_id

def test_update_details():
    """Test update_details processor"""
    print("\n✏️ Testing update_details processor...")
    
    test_data = {
        "name": "Updated Test Record",
        "description": "This record has been updated",
        "status": "modified",
        "version": 1,
        "update_count": 5
    }
    
    message_id = send_test_event("update_details", test_data)
    return message_id

def test_batch_events():
    """Test batch event processing"""
    print("\n📦 Testing batch event processing...")
    
    batch_events = [
        {
            "action": "create_details",
            "data": {"name": "Batch Record 1", "category": "batch"}
        },
        {
            "action": "show_details", 
            "data": {"name": "Batch Record 2", "description": "Show details batch test"}
        },
        {
            "action": "update_details",
            "data": {"name": "Batch Record 3", "status": "batch_updated"}
        }
    ]
    
    try:
        response = requests.post(f"{API_BASE_URL}/send-batch", json=batch_events)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch processing complete: {result['successful']}/{result['total_events']} events sent")
            return True
        else:
            print(f"❌ Batch processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False

def test_invalid_events():
    """Test error handling with invalid events"""
    print("\n⚠️ Testing error handling...")
    
    # Test invalid action
    print("  Testing invalid action...")
    invalid_action_result = send_test_event("invalid_action", {"test": "data"})
    
    # Test missing required data for create
    print("  Testing missing required data...")
    missing_data_result = send_test_event("create_details", {})
    
    return True

def monitor_kafka_topics():
    """Monitor Kafka topics for processed messages"""
    print("\n📡 Monitoring processed messages...")
    print("   (In a real setup, you would consume from the output topic)")
    print("   Check the processor logs for processing results:")
    print("   tail -f /root/kafka/kafka-processors/logs/kafka-processors.log")

def main():
    """Main test function"""
    print("🚀 Starting Kafka Processors Test Suite")
    print("=" * 50)
    
    # Test API health first
    if not test_api_health():
        print("❌ API is not healthy, exiting tests")
        return
    
    print("\n📊 Running processor tests...")
    
    # Test individual processors
    show_id = test_show_details()
    create_id = test_create_details()
    update_id = test_update_details()
    
    # Test batch processing
    test_batch_events()
    
    # Test error handling
    test_invalid_events()
    
    # Give processors time to process
    print(f"\n⏱️ Waiting 5 seconds for processing to complete...")
    time.sleep(5)
    
    # Show monitoring instructions
    monitor_kafka_topics()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nTo view processing results:")
    print("1. Check processor logs: tail -f logs/kafka-processors.log")
    print("2. Monitor Kafka topics: ")
    print("   cd /root/kafka")
    print("   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64")
    print("   bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic details-output --from-beginning")

if __name__ == "__main__":
    main()