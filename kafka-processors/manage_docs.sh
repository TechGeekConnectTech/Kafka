#!/bin/bash
# Documentation Server Management Script
# Provides easy control of the persistent documentation web server

PID_FILE="/tmp/docs_server.pid"
LOG_FILE="/tmp/docs_server.log"
PORT=8093
SERVER_SCRIPT="/root/kafka/kafka-processors/persistent_docs_server.py"

show_status() {
    echo "📊 Documentation Server Status"
    echo "=============================="
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            echo "✅ Status: Running"
            echo "📡 PID: $PID"
            echo "🔗 Local URL: http://localhost:$PORT"
            echo "🌍 External URL: http://$(hostname -I | awk '{print $1}'):$PORT"
            echo "📝 Log file: $LOG_FILE"
            
            # Test server response
            if curl -s -I "http://localhost:$PORT" >/dev/null 2>&1; then
                echo "🟢 Server: Responding"
            else
                echo "🟡 Server: Process running but not responding"
            fi
            
            # Show recent activity
            if [[ -f "$LOG_FILE" ]]; then
                echo ""
                echo "📈 Recent Activity (last 5 lines):"
                tail -5 "$LOG_FILE" 2>/dev/null || echo "   No recent activity"
            fi
        else
            echo "❌ Status: Not running (stale PID file)"
            [[ -f "$PID_FILE" ]] && rm -f "$PID_FILE"
        fi
    else
        echo "❌ Status: Not running"
    fi
    
    echo ""
    echo "🛠️  Management:"
    echo "   Start: $0 start"
    echo "   Stop:  $0 stop"  
    echo "   Restart: $0 restart"
    echo "   Logs: $0 logs"
}

start_server() {
    echo "🚀 Starting Documentation Server..."
    
    # Check if already running
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            echo "⚠️  Server already running (PID: $PID)"
            echo "🔗 URL: http://localhost:$PORT"
            return 0
        fi
    fi
    
    # Clean up any existing processes
    pkill -f "persistent_docs_server.py" 2>/dev/null || true
    pkill -f "$PORT" 2>/dev/null || true
    
    # Start server with setsid for complete detachment
    cd /root/kafka/kafka-processors
    setsid python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
    
    # Wait for server to start
    sleep 3
    
    # Verify it started
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            echo "✅ Server started successfully!"
            echo "📡 PID: $PID"
            echo "🔗 Local: http://localhost:$PORT" 
            echo "🌍 External: http://$(hostname -I | awk '{print $1}'):$PORT"
            echo "📝 Logs: tail -f $LOG_FILE"
            echo ""
            echo "🎯 Server will keep running even after terminal closure!"
            return 0
        fi
    fi
    
    echo "❌ Failed to start server"
    if [[ -f "$LOG_FILE" ]]; then
        echo "📝 Last few log lines:"
        tail -10 "$LOG_FILE" 2>/dev/null
    fi
    return 1
}

stop_server() {
    echo "🛑 Stopping Documentation Server..."
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null
            sleep 2
            
            # Force kill if still running
            if kill -0 "$PID" 2>/dev/null; then
                echo "🔨 Force stopping server..."
                kill -9 "$PID" 2>/dev/null
            fi
            
            echo "✅ Server stopped"
        else
            echo "⚠️  Server was not running"
        fi
        
        rm -f "$PID_FILE"
    else
        echo "⚠️  Server was not running (no PID file)"
    fi
    
    # Clean up any remaining processes
    pkill -f "persistent_docs_server.py" 2>/dev/null || true
    pkill -f "$PORT" 2>/dev/null || true
}

restart_server() {
    echo "🔄 Restarting Documentation Server..."
    stop_server
    sleep 2
    start_server
}

show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        echo "📝 Documentation Server Logs:"
        echo "============================"
        echo "🔗 Server URL: http://localhost:$PORT"
        echo "📄 Log file: $LOG_FILE" 
        echo "Press Ctrl+C to exit log view"
        echo ""
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found at $LOG_FILE"
    fi
}

show_urls() {
    echo "🔗 Server Access URLs"
    echo "===================="
    echo "📄 Main Documentation: http://localhost:$PORT/"
    echo "📋 README: http://localhost:$PORT/readme"
    echo "⚡ Quick Reference: http://localhost:$PORT/quick"
    echo ""
    echo "🌍 External Access (replace with your server IP):"
    echo "📄 http://$(hostname -I | awk '{print $1}'):$PORT/"
    echo "📋 http://$(hostname -I | awk '{print $1}'):$PORT/readme"
    echo "⚡ http://$(hostname -I | awk '{print $1}'):$PORT/quick"
}

case "${1:-status}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    urls)
        show_urls
        ;;
    *)
        echo "📋 Documentation Server Manager"
        echo "Usage: $0 {start|stop|restart|status|logs|urls}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server" 
        echo "  status  - Show server status"
        echo "  logs    - Show/follow server logs"
        echo "  urls    - Show access URLs"
        echo ""
        echo "🔗 Server runs on: http://localhost:$PORT"
        exit 1
        ;;
esac