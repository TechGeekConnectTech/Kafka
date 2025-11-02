#!/bin/bash
# Persistent Documentation Server Manager
# Ensures web server runs in background and survives terminal closure

SERVER_NAME="docs-server"
PORT=8093
WORK_DIR="/root/kafka/kafka-processors"
LOG_FILE="/tmp/docs_server.log"
PID_FILE="/tmp/docs_server.pid"

start_server() {
    echo "🚀 Starting persistent documentation server..."
    
    # Kill any existing server
    stop_server 2>/dev/null
    
    # Change to working directory
    cd "$WORK_DIR" || {
        echo "❌ Cannot access $WORK_DIR"
        exit 1
    }
    
    # Start server with nohup for persistence
    nohup python3 << 'EOF' > "$LOG_FILE" 2>&1 &
import http.server, socketserver, os, sys, signal
import time

PORT = 8093
WORK_DIR = "/root/kafka/kafka-processors"

class DocHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORK_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/documentation.html'
        super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {self.address_string()} - {format % args}")
        sys.stdout.flush()

os.chdir(WORK_DIR)
print(f"🌐 Documentation Server Starting on Port {PORT}")
print(f"📂 Working Directory: {WORK_DIR}")
print(f"🔗 Local Access: http://localhost:{PORT}")
print(f"🌍 Remote Access: http://YOUR_IP:{PORT}")
print(f"📄 Serving: documentation.html, README.md, QUICK_REFERENCE.md")
print("=" * 60)

def shutdown_handler(signum, frame):
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

try:
    with socketserver.TCPServer(("0.0.0.0", PORT), DocHandler) as httpd:
        httpd.serve_forever()
except Exception as e:
    print(f"❌ Server error: {e}")
    sys.exit(1)
EOF
    
    # Save PID
    echo $! > "$PID_FILE"
    SERVER_PID=$!
    
    # Wait a moment and check if server started
    sleep 2
    
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "✅ Documentation server started successfully!"
        echo "📡 PID: $SERVER_PID"
        echo "🔗 URL: http://localhost:$PORT"
        echo "🌍 External: http://$(hostname -I | awk '{print $1}'):$PORT"
        echo "📝 Logs: tail -f $LOG_FILE"
        echo "🛑 Stop: $0 stop"
        echo ""
        echo "🎯 Server will keep running even if you close this terminal!"
        return 0
    else
        echo "❌ Failed to start server"
        return 1
    fi
}

stop_server() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "🛑 Stopping documentation server (PID: $PID)..."
            kill "$PID"
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                echo "🔨 Force killing server..."
                kill -9 "$PID"
            fi
            rm -f "$PID_FILE"
            echo "✅ Server stopped"
        else
            echo "❌ Server not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ Server not running (no PID file)"
    fi
    
    # Also kill any python servers on our port
    pkill -f "PORT = $PORT" 2>/dev/null || true
}

status_server() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✅ Documentation server is running"
            echo "📡 PID: $PID"
            echo "🔗 URL: http://localhost:$PORT"
            echo "🌍 External: http://$(hostname -I | awk '{print $1}'):$PORT"
            echo "📝 Logs: tail -f $LOG_FILE"
            
            # Test if server responds
            if curl -s -I "http://localhost:$PORT" | grep -q "200 OK"; then
                echo "🟢 Server responding correctly"
            else
                echo "🟡 Server process running but not responding"
            fi
        else
            echo "❌ Server not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ Server not running"
    fi
}

restart_server() {
    echo "🔄 Restarting documentation server..."
    stop_server
    sleep 2
    start_server
}

show_help() {
    echo "📋 Documentation Server Manager"
    echo "Usage: $0 {start|stop|restart|status|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the documentation server"
    echo "  stop    - Stop the documentation server"
    echo "  restart - Restart the documentation server"
    echo "  status  - Check server status"
    echo "  help    - Show this help"
    echo ""
    echo "🔗 Server URL: http://localhost:$PORT"
}

# Main script logic
case "${1:-start}" in
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
        status_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac