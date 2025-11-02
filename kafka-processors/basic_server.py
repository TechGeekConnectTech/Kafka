#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8093
os.chdir('/root/kafka/kafka-processors')

print(f"🌐 Starting documentation server on port {PORT}")
print(f"📂 Serving from: {os.getcwd()}")
print(f"🔗 Access: http://195.35.6.88:{PORT}")

with socketserver.TCPServer(("0.0.0.0", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()