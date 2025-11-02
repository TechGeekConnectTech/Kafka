#!/bin/bash
# Docker management script for Kafka Processors

set -e

ACTION=${1:-help}

case $ACTION in
    "build")
        echo "🔨 Building Docker images..."
        docker-compose build --no-cache
        echo "✅ Build complete!"
        ;;
    
    "up")
        echo "🚀 Starting all services..."
        docker-compose up -d
        echo ""
        echo "🎉 Services started!"
        echo "📡 Kafka UI: http://localhost:8080"
        echo "🔌 API Server: http://localhost:8082"
        echo "📖 API Documentation: http://localhost:8082/docs"
        echo "❤️  System Health: http://localhost:8082/health"
        echo "⚙️  Processor Health: http://localhost:8082/health/processors"
        echo "📚 Documentation: http://localhost:8090"
        echo ""
        echo "🔍 Use 'docker-compose logs -f' to view logs"
        echo "📊 Use './docker-manage.sh status' to check service status"
        ;;
    
    "down")
        echo "🛑 Stopping all services..."
        docker-compose down
        echo "✅ Services stopped!"
        ;;
    
    "restart")
        echo "🔄 Restarting services..."
        docker-compose restart
        echo "✅ Services restarted!"
        ;;
    
    "logs")
        SERVICE=${2:-kafka-processors}
        echo "📋 Showing logs for $SERVICE..."
        docker-compose logs -f $SERVICE
        ;;
    
    "status")
        echo "📊 Service status:"
        docker-compose ps
        ;;
    
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo "✅ Cleanup complete!"
        ;;
    
    "test")
        echo "🧪 Running health checks..."
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 15
        
        echo "🔍 Testing API health..."
        if curl -s http://localhost:8082/health | python3 -m json.tool; then
            echo "✅ API health check passed!"
        else
            echo "❌ API health check failed!"
            exit 1
        fi
        
        echo ""
        echo "⚙️  Testing processor health..."
        if curl -s http://localhost:8082/health/processors | python3 -m json.tool; then
            echo "✅ Processor health check passed!"
        else
            echo "❌ Processor health check failed!"
            exit 1
        fi
        
        echo ""
        echo "🎯 All health checks passed!"
        ;;
    
    "shell")
        SERVICE=${2:-kafka-processors}
        echo "🐚 Opening shell in $SERVICE..."
        docker-compose exec $SERVICE /bin/bash
        ;;
    
    "help"|*)
        echo "🐳 Kafka Processors Docker Management"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  build              Build Docker images"
        echo "  up                 Start all services"
        echo "  down               Stop all services"
        echo "  restart            Restart all services"
        echo "  logs [service]     Show logs (default: kafka-processors)"
        echo "  status             Show service status"
        echo "  clean              Clean up Docker resources"
        echo "  test               Run test suite"
        echo "  shell [service]    Open shell in service"
        echo "  help               Show this help"
        echo ""
        echo "Services:"
        echo "  - zookeeper        Zookeeper service"
        echo "  - kafka            Kafka broker"  
        echo "  - kafka-ui         Kafka Web UI (port 8080)"
        echo "  - kafka-processors Main application (port 8082)"
        echo "  - docs-server      Documentation server (port 8090)"
        echo ""
        echo "Health Endpoints:"
        echo "  - /health          Comprehensive system health"
        echo "  - /health/processors  Kafka processor status"
        ;;
esac