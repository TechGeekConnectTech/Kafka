#!/bin/bash
# Complete Docker deployment demonstration script

set -e

echo "🐳 Kafka Processors - Complete Docker Deployment Demo"
echo "======================================================"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker prerequisites met"
echo ""

# Build the images
echo "🔨 Building Docker images..."
./docker-manage.sh build

echo ""
echo "🚀 Starting all services..."
./docker-manage.sh up

echo ""
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "🧪 Running health checks..."
./docker-manage.sh test

echo ""
echo "📊 Checking service status..."
./docker-manage.sh status

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "🌐 Access Points:"
echo "=================="
echo "📡 Kafka UI:           http://localhost:8080"
echo "🔌 API Server:         http://localhost:8082"
echo "📖 API Documentation:  http://localhost:8082/docs"
echo "❤️  System Health:     http://localhost:8082/health"
echo "⚙️  Processor Health:  http://localhost:8082/health/processors"
echo "📚 Documentation:      http://localhost:8090"
echo ""
echo "🛠️  Management Commands:"
echo "========================="
echo "./docker-manage.sh logs    # View logs"
echo "./docker-manage.sh status  # Check status" 
echo "./docker-manage.sh down    # Stop services"
echo "./docker-manage.sh clean   # Complete cleanup"
echo ""
echo "🔍 Health Check Examples:"
echo "=========================="
echo "curl http://localhost:8082/health | jq"
echo "curl http://localhost:8082/health/processors | jq"
echo ""
echo "✨ System is ready for use!"