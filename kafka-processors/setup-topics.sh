#!/bin/bash
# Script to create Kafka topics for Server Demise Pipeline

set -e

echo "🔧 Setting up Kafka topics for Server Demise Pipeline..."

# Check if running in Docker or local environment
if command -v docker-compose &> /dev/null && docker-compose ps kafka &> /dev/null; then
    echo "� Using Docker environment..."
    KAFKA_CMD="docker-compose exec kafka kafka-topics"
    BOOTSTRAP_SERVER="localhost:9092"
    
    # Wait for Kafka to be ready
    echo "⏳ Waiting for Kafka to be ready..."
    until docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 >/dev/null 2>&1; do
        echo "Kafka is unavailable - sleeping"
        sleep 1
    done
else
    echo "🏠 Using local Kafka installation..."
    KAFKA_CMD="/root/kafka/bin/kafka-topics.sh"
    BOOTSTRAP_SERVER="localhost:9092"
    
    # Wait for Kafka to be ready
    echo "⏳ Waiting for Kafka to be ready..."
    sleep 5
fi

echo "✅ Kafka is ready!"

# Create server demise pipeline topic
echo "📝 Creating server-demise-pipeline topic..."
$KAFKA_CMD --create \
    --topic server-demise-pipeline \
    --bootstrap-server $BOOTSTRAP_SERVER \
    --partitions 3 \
    --replication-factor 1 \
    --if-not-exists

echo "✅ Topics created successfully!"

# List topics to verify
echo "📋 Current topics:"
$KAFKA_CMD --list --bootstrap-server $BOOTSTRAP_SERVER

echo "🎯 Server Demise Pipeline topic ready for processing!"