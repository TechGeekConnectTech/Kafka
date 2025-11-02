#!/bin/bash

# Complete System Startup Script
# Ensures all servers (API, Documentation) are running

echo "🚀 Starting Complete Kafka Processors System..."
echo "================================================"

# Set Java environment
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64

# Change to project directory
cd /root/kafka/kafka-processors

# 1. Check and start Documentation Server (Port 8090)
echo "📚 Checking Documentation Server (Port 8090)..."
if ! ss -tulpn | grep -q ":8090 "; then
    echo "🚀 Starting Documentation Server on port 8090..."
    ./docs_server_manager.sh start
else
    echo "✅ Documentation Server already running on port 8090"
fi

# 2. Check and start API Server (Port 8082)
echo ""
echo "🌐 Checking API Server (Port 8082)..."
if ! ss -tulpn | grep -q ":8082 "; then
    echo "🚀 Starting API Server on port 8082..."
    nohup python3 -m uvicorn api.main_new:app --host 0.0.0.0 --port 8082 > /tmp/api_server.log 2>&1 &
    sleep 3
    if ss -tulpn | grep -q ":8082 "; then
        echo "✅ API Server started successfully on port 8082"
    else
        echo "❌ Failed to start API Server"
    fi
else
    echo "✅ API Server already running on port 8082"
fi

# 3. Check and start Standard Documentation (Port 8093)
echo ""
echo "📖 Checking Standard Documentation Server (Port 8093)..."
if ! ss -tulpn | grep -q ":8093 "; then
    echo "🚀 Starting Standard Documentation Server on port 8093..."
    nohup python3 -m http.server 8093 > /tmp/std_docs.log 2>&1 &
    sleep 3
    if ss -tulpn | grep -q ":8093 "; then
        echo "✅ Standard Documentation Server started on port 8093"
    else
        echo "❌ Failed to start Standard Documentation Server"
    fi
else
    echo "✅ Standard Documentation Server already running on port 8093"
fi

# 4. Check Processor Manager
echo ""
echo "⚙️ Checking Processor Manager..."
if ! pgrep -f "processor_manager_new.py" > /dev/null; then
    echo "🚀 Starting Processor Manager..."
    nohup python3 processor_manager_new.py > /tmp/processor_manager.log 2>&1 &
    sleep 2
    if pgrep -f "processor_manager_new.py" > /dev/null; then
        echo "✅ Processor Manager started successfully"
    else
        echo "❌ Failed to start Processor Manager"
    fi
else
    echo "✅ Processor Manager already running"
fi

echo ""
echo "🏁 System Status Summary:"
echo "========================"

# Status check for all services
echo "📚 Documentation Server (8090): $(ss -tulpn | grep -q ':8090 ' && echo '✅ RUNNING' || echo '❌ DOWN')"
echo "🌐 API Server (8082): $(ss -tulpn | grep -q ':8082 ' && echo '✅ RUNNING' || echo '❌ DOWN')"  
echo "📖 Standard Docs (8093): $(ss -tulpn | grep -q ':8093 ' && echo '✅ RUNNING' || echo '❌ DOWN')"
echo "⚙️ Processor Manager: $(pgrep -f 'processor_manager_new.py' > /dev/null && echo '✅ RUNNING' || echo '❌ DOWN')"

echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "📚 Enhanced Documentation Hub: http://195.35.6.88:8090/"
echo "📋 System Documentation: http://195.35.6.88:8090/Kafka_Processors_System_Documentation.html"
echo "🌐 API Documentation: http://195.35.6.88:8082/docs"
echo "📖 Standard Documentation: http://195.35.6.88:8093/documentation.html"
echo "⚡ Quick Reference: http://195.35.6.88:8093/quick.html"

echo ""
echo "✨ System is ready! All services are configured to auto-restart."
echo "🔄 Monitoring: Cron job checks every 5 minutes and auto-restarts if needed."