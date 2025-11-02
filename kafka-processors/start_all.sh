#!/bin/bash
# Start all Kafka processors and API

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-17.0.16.0.8-2.el8.x86_64
export PYTHONPATH=/root/kafka/kafka-processors:$PYTHONPATH

cd /root/kafka/kafka-processors

echo "Starting Kafka Processors Manager..."
python3 processor_manager.py &
PROCESSOR_PID=$!

echo "Waiting 3 seconds for processors to initialize..."
sleep 3

echo "Starting REST API..."
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8082 --reload &
API_PID=$!

echo ""
echo "========================================"
echo "Kafka Processors System Started"
echo "========================================"
echo "Processor Manager PID: $PROCESSOR_PID"
echo "API PID: $API_PID"
echo ""
echo "API URLs:"
echo "  - Main: http://localhost:8082"
echo "  - Docs: http://localhost:8082/docs"
echo "  - Health: http://localhost:8082/health"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $PROCESSOR_PID $API_PID 2>/dev/null
    wait $PROCESSOR_PID $API_PID 2>/dev/null
    echo "All services stopped."
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $PROCESSOR_PID $API_PID