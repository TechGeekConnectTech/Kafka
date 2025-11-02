#!/usr/bin/env python3
"""
Simple Documentation Server with HTML conversion
"""

import http.server
import socketserver
import os

PORT = 8093
WORK_DIR = '/root/kafka/kafka-processors'

class DocServer(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORK_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/documentation.html'
        elif self.path == '/readme':
            self.serve_markdown_as_html('README.md', 'README - Server Demise Pipeline')
            return
        elif self.path == '/quick':
            self.serve_markdown_as_html('QUICK_REFERENCE.md', 'Quick Reference - Server Demise Pipeline')
            return
        super().do_GET()
    
    def serve_markdown_as_html(self, filename, title):
        try:
            with open(os.path.join(WORK_DIR, filename), 'r', encoding='utf-8') as f:
                content = f.read()
            
            html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
        .navbar {{ background: #2c3e50; color: white; padding: 15px 20px; }}
        .navbar h1 {{ margin: 0; display: inline-block; }}
        .navbar .nav-links {{ float: right; margin-top: 5px; }}
        .navbar .nav-links a {{ color: white; text-decoration: none; margin-left: 20px; padding: 8px 15px; border-radius: 3px; }}
        .navbar .nav-links a:hover {{ background: #34495e; }}
        .navbar .nav-links a.active {{ background: #3498db; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 5px; }}
        pre {{ background: #1e1e1e; color: #ddd; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🔧 Server Demise Pipeline</h1>
        <div class="nav-links">
            <a href="/">🏠 Main Documentation</a>
            <a href="/readme" class="{'active' if 'README' in title else ''}">📋 README</a>
            <a href="/quick" class="{'active' if 'Quick' in title else ''}">⚡ Quick Reference</a>
            <a href="http://195.35.6.88:8082/docs" target="_blank">🔗 API Docs</a>
        </div>
        <div style="clear: both;"></div>
    </div>
    
    <div class="container">
        <div class="content">
            <pre>{content}</pre>
        </div>
    </div>
</body>
</html>'''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, f"File {filename} not found")
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")

if __name__ == "__main__":
    os.chdir(WORK_DIR)
    print(f"🌐 Documentation Server Starting on Port {PORT}")
    print(f"📂 Serving from: {WORK_DIR}")
    print(f"🔗 Access at: http://localhost:{PORT}")
    print(f"🌍 External: http://195.35.6.88:{PORT}")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), DocServer) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")