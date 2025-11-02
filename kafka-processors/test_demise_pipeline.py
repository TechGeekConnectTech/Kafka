#!/usr/bin/env python3
"""
Test script for Server Demise Pipeline
Tests the complete flow: API → check_server → poweroff_server → demise_server
"""

import requests
import json
import time
import uuid

# API Configuration
API_BASE_URL = "http://localhost:8082"

def test_api_health():
    """Test API health endpoint"""
    print("🏥 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health: {health_data['status']}")
            return True
        else:
            print(f"❌ API Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health check error: {e}")
        return False

def test_single_server_demise():
    """Test single server demise request"""
    print("\n🖥️  Testing single server demise...")
    
    # Test with a valid server ID (100-999 range)
    server_request = {
        "server_id": "150",
        "reason": "End of life - planned decommission",
        "priority": "normal",
        "requester": "test_user",
        "additional_data": {
            "department": "IT Operations",
            "approval_ticket": "TICK-12345"
        }
    }
    
    try:
        print(f"📤 Sending demise request for server {server_request['server_id']}...")
        response = requests.post(
            f"{API_BASE_URL}/demise-server",
            json=server_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline initiated successfully!")
            print(f"   Message ID: {result['message_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Pipeline: {result['pipeline_initiated']}")
            return result
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_invalid_server_demise():
    """Test demise request with invalid server ID"""
    print("\n❌ Testing invalid server demise...")
    
    # Test with invalid server ID (outside 100-999 range)
    server_request = {
        "server_id": "999999",  # Invalid server ID
        "reason": "Test invalid server",
        "priority": "low",
        "requester": "test_user"
    }
    
    try:
        print(f"📤 Sending demise request for invalid server {server_request['server_id']}...")
        response = requests.post(
            f"{API_BASE_URL}/demise-server",
            json=server_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request accepted (will fail in pipeline):")
            print(f"   Message ID: {result['message_id']}")
            return result
        else:
            print(f"❌ Request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_batch_server_demise():
    """Test batch server demise requests"""
    print("\n📦 Testing batch server demise...")
    
    batch_request = {
        "servers": [
            {
                "server_id": "200",
                "reason": "Batch decommission - datacenter migration",
                "priority": "high",
                "requester": "datacenter_ops"
            },
            {
                "server_id": "201", 
                "reason": "Batch decommission - datacenter migration",
                "priority": "high",
                "requester": "datacenter_ops"
            },
            {
                "server_id": "202",
                "reason": "Batch decommission - datacenter migration", 
                "priority": "high",
                "requester": "datacenter_ops"
            }
        ],
        "batch_id": f"BATCH-{int(time.time())}"
    }
    
    try:
        print(f"📤 Sending batch demise request for {len(batch_request['servers'])} servers...")
        response = requests.post(
            f"{API_BASE_URL}/batch-demise-servers",
            json=batch_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch request initiated successfully!")
            print(f"   Batch ID: {result['batch_id']}")
            print(f"   Total Servers: {result['total_servers']}")
            
            for response_item in result['responses']:
                status_icon = "✅" if response_item['pipeline_initiated'] else "❌"
                print(f"   {status_icon} Server {response_item['server_id']}: {response_item['status']}")
            
            return result
        else:
            print(f"❌ Batch request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Batch request error: {e}")
        return None

def test_pipeline_info():
    """Test pipeline information endpoint"""
    print("\n📋 Getting pipeline information...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/pipeline-status")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Pipeline Information:")
            print(f"   Name: {info['pipeline_name']}")
            print(f"   Topic: {info['topic']}")
            print(f"   Processors:")
            for proc in info['processors']:
                print(f"     {proc['step']}. {proc['name']} ({proc['action']})")
                print(f"        {proc['description']}")
            return info
        else:
            print(f"❌ Failed to get pipeline info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Pipeline info error: {e}")
        return None

def test_server_name_formats():
    """Test different server ID formats"""
    print("\n🔤 Testing different server name formats...")
    
    test_servers = [
        {"server_id": "SRV001", "expected": "valid"},
        {"server_id": "HOST-WEB-01", "expected": "valid"},
        {"server_id": "VM-TEST-123", "expected": "valid"},
        {"server_id": "250", "expected": "valid"},
        {"server_id": "PROD-DB-PRIMARY", "expected": "valid"},
        {"server_id": "invalid-server", "expected": "invalid"},
        {"server_id": "50", "expected": "invalid"}  # Below valid range
    ]
    
    results = []
    for test in test_servers:
        server_request = {
            "server_id": test["server_id"],
            "reason": f"Test {test['expected']} server format",
            "priority": "low",
            "requester": "format_tester"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/demise-server",
                json=server_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📤 {test['server_id']}: Request sent (ID: {result['message_id'][:8]}...)")
                results.append({"server_id": test["server_id"], "status": "sent", "expected": test["expected"]})
            else:
                print(f"   ❌ {test['server_id']}: Request failed")
                results.append({"server_id": test["server_id"], "status": "failed", "expected": test["expected"]})
        except Exception as e:
            print(f"   ❌ {test['server_id']}: Error - {e}")
            results.append({"server_id": test["server_id"], "status": "error", "expected": test["expected"]})
        
        time.sleep(0.5)  # Small delay between requests
    
    return results

def main():
    """Run all tests"""
    print("🎯 Starting Server Demise Pipeline Tests")
    print("=" * 50)
    
    # Test API health first
    if not test_api_health():
        print("❌ API not healthy, stopping tests")
        return
    
    # Get pipeline information
    test_pipeline_info()
    
    # Test single server demise
    single_result = test_single_server_demise()
    
    # Test invalid server demise  
    invalid_result = test_invalid_server_demise()
    
    # Test different server name formats
    format_results = test_server_name_formats()
    
    # Test batch server demise
    batch_result = test_batch_server_demise()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"✅ Single Server Test: {'PASSED' if single_result else 'FAILED'}")
    print(f"✅ Invalid Server Test: {'PASSED' if invalid_result else 'FAILED'}")
    print(f"✅ Format Tests: {len([r for r in format_results if r['status'] == 'sent'])}/{len(format_results)} sent")
    print(f"✅ Batch Server Test: {'PASSED' if batch_result else 'FAILED'}")
    
    print("\n📊 Pipeline Processing:")
    print("   The processors will now handle these requests in sequence:")
    print("   1️⃣  ServerCheckProcessor will verify servers in portal")
    print("   2️⃣  ServerPowerOffProcessor will power off valid servers")
    print("   3️⃣  ServerDemiseProcessor will execute decommission")
    print("\n💡 Monitor the processor logs to see the pipeline in action!")
    
    print(f"\n📋 Valid server formats tested:")
    for result in format_results:
        status_icon = "✅" if result['status'] == 'sent' else "❌"
        print(f"   {status_icon} {result['server_id']} (expected: {result['expected']})")

if __name__ == "__main__":
    main()