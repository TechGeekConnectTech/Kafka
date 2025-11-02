#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8091
os.chdir('/root/kafka/kafka-processors')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/documentation.html'
        super().do_GET()

print(f"🌐 Documentation server starting on port {PORT}")
print(f"📂 Serving from: {os.getcwd()}")
print(f"🔗 Access at: http://localhost:{PORT}")
print(f"🌍 External access: http://YOUR_IP:{PORT}")

with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
    httpd.serve_forever()