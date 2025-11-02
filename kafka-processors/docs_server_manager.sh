#!/bin/bash

# Documentation Server Management Script
# Keeps port 8090 documentation server running continuously

DOCS_PORT=8090
DOCS_DIR="/root/kafka/kafka-processors"
PID_FILE="/tmp/docs_server_8090.pid"
LOG_FILE="/tmp/docs_server_8090.log"

start_server() {
    echo "🚀 Starting documentation server on port $DOCS_PORT..."
    cd "$DOCS_DIR"
    
    # Kill any existing process on the port
    pkill -f "http.server $DOCS_PORT" 2>/dev/null || true
    
    # Wait a moment for cleanup
    sleep 2
    
    # Start the server with nohup for persistent background operation
    nohup python3 -m http.server $DOCS_PORT > "$LOG_FILE" 2>&1 &
    
    # Save the PID
    echo $! > "$PID_FILE"
    
    # Wait and verify it started
    sleep 3
    
    if ss -tulpn | grep -q ":$DOCS_PORT "; then
        echo "✅ Documentation server started successfully on port $DOCS_PORT"
        echo "📂 Serving directory: $DOCS_DIR"
        echo "📝 Log file: $LOG_FILE"
        echo "🆔 PID file: $PID_FILE"
        echo ""
        echo "🌐 Access URLs:"
        echo "   • Main Hub: http://195.35.6.88:$DOCS_PORT/"
        echo "   • System Docs: http://195.35.6.88:$DOCS_PORT/Kafka_Processors_System_Documentation.html"
        echo "   • File Structure: http://195.35.6.88:$DOCS_PORT/File_Structure_Guide.html"
        return 0
    else
        echo "❌ Failed to start documentation server"
        return 1
    fi
}

stop_server() {
    echo "🛑 Stopping documentation server..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PID_FILE"
            echo "✅ Server stopped (PID: $PID)"
        else
            echo "⚠️  PID file exists but process not running"
            rm -f "$PID_FILE"
        fi
    fi
    
    # Fallback: kill by process name
    pkill -f "http.server $DOCS_PORT" 2>/dev/null && echo "✅ Killed by process name"
}

status_server() {
    if ss -tulpn | grep -q ":$DOCS_PORT "; then
        PID=$(ss -tulpn | grep ":$DOCS_PORT " | awk '{print $7}' | cut -d'=' -f2 | cut -d',' -f1)
        echo "✅ Documentation server is RUNNING on port $DOCS_PORT (PID: $PID)"
        echo "🌐 Access: http://195.35.6.88:$DOCS_PORT/"
        return 0
    else
        echo "❌ Documentation server is NOT running on port $DOCS_PORT"
        return 1
    fi
}

restart_server() {
    echo "🔄 Restarting documentation server..."
    stop_server
    sleep 2
    start_server
}

case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    status)
        status_server
        ;;
    restart)
        restart_server
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Documentation Server Manager for Port $DOCS_PORT"
        echo "Commands:"
        echo "  start   - Start the documentation server"
        echo "  stop    - Stop the documentation server" 
        echo "  status  - Check server status"
        echo "  restart - Restart the server"
        exit 1
        ;;
esac

exit $?