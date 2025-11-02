#!/usr/bin/env python3
"""
Persistent Documentation Server for Server Demise Pipeline
Runs as a daemon in the background, survives terminal closure
"""

import http.server
import socketserver
import os
import sys
import signal
import daemon
from daemon import pidfile
import logging

# Configuration
PORT = 8093
WORKING_DIR = '/root/kafka/kafka-processors'
PID_FILE = '/tmp/docs_server.pid'
LOG_FILE = '/tmp/docs_server.log'

class PersistentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with proper routing"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKING_DIR, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with custom routing"""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/documentation.html'
        elif self.path == '/main':
            self.path = '/documentation.html'
        elif self.path == '/readme':
            self.path = '/README.md'
        elif self.path == '/quick':
            self.path = '/QUICK_REFERENCE.md'
        
        super().do_GET()
    
    def end_headers(self):
        """Add CORS headers for better accessibility"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        logging.info(f"📡 {self.address_string()} - {format % args}")

def setup_logging():
    """Setup logging for the daemon"""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def start_server():
    """Start the HTTP server"""
    try:
        os.chdir(WORKING_DIR)
        
        # Create server
        with socketserver.TCPServer(("0.0.0.0", PORT), PersistentHTTPRequestHandler) as httpd:
            logging.info(f"🌐 Documentation server started on port {PORT}")
            logging.info(f"📂 Serving files from: {WORKING_DIR}")
            logging.info(f"🔗 Access URL: http://localhost:{PORT}")
            
            # Handle shutdown gracefully
            def signal_handler(signum, frame):
                logging.info("🛑 Received shutdown signal, stopping server...")
                httpd.shutdown()
                sys.exit(0)
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Serve forever
            httpd.serve_forever()
            
    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        sys.exit(1)

def run_daemon():
    """Run server as a daemon"""
    setup_logging()
    
    # Check if already running
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            os.kill(pid, 0)  # This will raise OSError if process doesn't exist
            print(f"❌ Server already running with PID {pid}")
            print(f"🛑 Stop it first: kill {pid}")
            sys.exit(1)
            
        except (OSError, ValueError):
            # Process not running, remove stale PID file
            os.remove(PID_FILE)
    
    # Start as daemon
    print(f"🚀 Starting documentation server daemon on port {PORT}")
    print(f"📂 Working directory: {WORKING_DIR}")
    print(f"📝 Log file: {LOG_FILE}")
    print(f"🔗 Access URL: http://localhost:{PORT}")
    print(f"🌍 External URL: http://YOUR_IP:{PORT}")
    print(f"🛑 Stop with: python3 {__file__} stop")
    
    try:
        # Note: daemon module may not be available, fallback to nohup approach
        start_server()
    except ImportError:
        print("⚠️  Daemon module not available, running with nohup...")
        os.system(f"nohup python3 -c 'exec(open(\"{__file__}\").read().replace(\"run_daemon()\", \"start_server()\"))' > {LOG_FILE} 2>&1 & echo $! > {PID_FILE}")

def stop_daemon():
    """Stop the daemon"""
    if not os.path.exists(PID_FILE):
        print("❌ Server not running (no PID file found)")
        return
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        print(f"✅ Server stopped (PID {pid})")
        
    except (OSError, ValueError) as e:
        print(f"❌ Error stopping server: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def status_daemon():
    """Check daemon status"""
    if not os.path.exists(PID_FILE):
        print("❌ Server not running")
        return
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        os.kill(pid, 0)  # Check if process exists
        print(f"✅ Server running with PID {pid}")
        print(f"🔗 URL: http://localhost:{PORT}")
        print(f"📝 Log: tail -f {LOG_FILE}")
        
    except (OSError, ValueError):
        print("❌ Server not running (stale PID file)")
        os.remove(PID_FILE)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "stop":
            stop_daemon()
        elif command == "status":
            status_daemon()
        elif command == "restart":
            stop_daemon()
            run_daemon()
        else:
            print("Usage: python3 docs_daemon.py [start|stop|status|restart]")
    else:
        run_daemon()