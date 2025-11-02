#!/usr/bin/env python3
"""
Simple HTTP server to serve the Server Demise Pipeline documentation
Accessible on port 8091 for easy sharing
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8091
HOST = "0.0.0.0"  # Listen on all interfaces for external access

class DocumentationHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving documentation with proper routing"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory="/root/kafka/kafka-processors", **kwargs)
    
    def do_GET(self):
        """Handle GET requests with custom routing"""
        if self.path == '/' or self.path == '/index.html':
            # Serve the main documentation page
            self.path = '/documentation.html'
        elif self.path == '/readme':
            # Serve README as HTML
            self.serve_markdown_as_html('README.md')
            return
        elif self.path == '/quick':
            # Serve quick reference as HTML
            self.serve_markdown_as_html('QUICK_REFERENCE.md')
            return
        elif self.path == '/api':
            # Redirect to API documentation
            self.send_response(302)
            self.send_header('Location', 'http://localhost:8082/docs')
            self.end_headers()
            return
        
        # Default handling for other files
        super().do_GET()
    
    def serve_markdown_as_html(self, filename):
        """Convert markdown to HTML and serve it"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple markdown to HTML conversion
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Demise Pipeline - {filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
        h1, h2, h3 {{ color: #333; }}
        .nav {{ background: #007bff; color: white; padding: 15px; margin: -40px -40px 20px -40px; }}
        .nav a {{ color: white; margin-right: 20px; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">🏠 Main Documentation</a>
        <a href="/readme">📋 README</a>
        <a href="/quick">⚡ Quick Reference</a>
        <a href="/api" target="_blank">🔗 API Docs</a>
    </div>
    <pre>{content}</pre>
</body>
</html>
"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', str(len(html_content.encode())))
            self.end_headers()
            self.wfile.write(html_content.encode())
            
        except FileNotFoundError:
            self.send_error(404, f"File {filename} not found")
        except Exception as e:
            self.send_error(500, f"Error serving {filename}: {str(e)}")
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"📡 [{self.date_time_string()}] {format % args}")

def start_server():
    """Start the documentation server"""
    try:
        # Change to the correct directory
        os.chdir("/root/kafka/kafka-processors")
        
        # Create the server
        with socketserver.TCPServer((HOST, PORT), DocumentationHandler) as httpd:
            print("🌐 Server Demise Pipeline Documentation Server")
            print("=" * 50)
            print(f"🚀 Starting server on http://{HOST}:{PORT}")
            print(f"📂 Serving files from: {os.getcwd()}")
            print()
            print("📋 Available URLs:")
            print(f"   🏠 Main Documentation: http://localhost:{PORT}/")
            print(f"   📖 README: http://localhost:{PORT}/readme")
            print(f"   ⚡ Quick Reference: http://localhost:{PORT}/quick")
            print(f"   🔗 API Docs (redirect): http://localhost:{PORT}/api")
            print()
            print("🌍 External Access:")
            print(f"   Replace 'localhost' with your server IP for external access")
            print(f"   Example: http://YOUR_SERVER_IP:{PORT}/")
            print()
            print("🛑 Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print(f"🔧 Kill existing process: lsof -ti:{PORT} | xargs kill -9")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_server()