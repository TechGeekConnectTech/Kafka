#!/usr/bin/env python3
"""
Robust Documentation Server - Runs persistently in background
"""

import http.server
import socketserver
import os
import sys
import time
import signal
import subprocess

PORT = 8093
WORK_DIR = '/root/kafka/kafka-processors'
LOG_FILE = '/tmp/docs_server.log'
PID_FILE = '/tmp/docs_server.pid'

class DocumentationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORK_DIR, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with custom HTML generation"""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/documentation.html'
        elif self.path == '/readme':
            self.serve_markdown_as_html('README.md', 'README - Server Demise Pipeline')
            return
        elif self.path == '/quick':
            self.serve_markdown_as_html('QUICK_REFERENCE.md', 'Quick Reference - Server Demise Pipeline')
            return
        
        super().do_GET()
    
    def serve_markdown_as_html(self, filename, title):
        """Convert markdown file to HTML with navigation"""
        try:
            filepath = os.path.join(WORK_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple markdown to HTML conversion
            html_content = self.convert_markdown_to_html(content, title)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', str(len(html_content.encode())))
            self.end_headers()
            self.wfile.write(html_content.encode())
            
        except FileNotFoundError:
            self.send_error(404, f"File {filename} not found")
        except Exception as e:
            self.send_error(500, f"Error serving {filename}: {str(e)}")
    
    def convert_markdown_to_html(self, markdown_content, title):
        """Convert markdown content to styled HTML"""
        # Simple markdown to HTML conversion
        html_content = markdown_content
        
        # Convert headers
        html_content = html_content.replace('# ', '<h1>').replace('\n## ', '</h1>\n<h2>').replace('\n### ', '</h2>\n<h3>')
        html_content = html_content.replace('\n#### ', '</h3>\n<h4>').replace('\n##### ', '</h4>\n<h5>')
        
        # Convert code blocks
        import re
        html_content = re.sub(r'```bash\n(.*?)\n```', r'<div class="code-block">\1</div>', html_content, flags=re.DOTALL)
        html_content = re.sub(r'```(.*?)\n(.*?)\n```', r'<div class="code-block">\2</div>', html_content, flags=re.DOTALL)
        html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
        
        # Convert lists
        html_content = re.sub(r'\n- (.*?)(?=\n[^-]|\n$)', r'\n<li>\1</li>', html_content)
        html_content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html_content, flags=re.DOTALL)
        
        # Convert bold and italic
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        
        # Convert line breaks
        html_content = html_content.replace('\n\n', '</p>\n<p>')
        
        # Wrap in proper HTML structure
        full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
        .navbar {{ background: #2c3e50; color: white; padding: 15px 20px; position: sticky; top: 0; z-index: 100; }}
        .navbar h1 {{ margin: 0; display: inline-block; }}
        .navbar .nav-links {{ float: right; margin-top: 5px; }}
        .navbar .nav-links a {{ color: white; text-decoration: none; margin-left: 20px; padding: 8px 15px; border-radius: 3px; transition: background 0.3s; }}
        .navbar .nav-links a:hover {{ background: #34495e; }}
        .navbar .nav-links a.active {{ background: #3498db; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .code-block {{ background: #1e1e1e; color: #ddd; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Courier New', monospace; margin: 15px 0; white-space: pre-wrap; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        h1, h2, h3, h4, h5 {{ color: #2c3e50; margin-top: 30px; }}
        h1 {{ color: #3498db; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; }}
        ul {{ margin: 15px 0; }}
        li {{ margin: 5px 0; }}
        p {{ margin: 15px 0; }}
        .back-to-top {{ position: fixed; bottom: 20px; right: 20px; background: #3498db; color: white; padding: 10px 15px; border-radius: 50px; text-decoration: none; }}
        .back-to-top:hover {{ background: #2980b9; }}
        .alert {{ background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 15px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
        .error {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
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
            <p>{html_content}</p>
        </div>
    </div>
    
    <a href="#" class="back-to-top" onclick="window.scrollTo(0,0); return false;">↑ Top</a>
    
    <script>
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
        
        // Auto-hide back to top button
        window.addEventListener('scroll', function() {{
            const backToTop = document.querySelector('.back-to-top');
            if (window.scrollY > 300) {{
                backToTop.style.display = 'block';
            }} else {{
                backToTop.style.display = 'none';
            }}
        }});
    </script>
</body>
</html>'''
        return full_html
    
    def end_headers(self):
        """Add headers for better compatibility"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Custom logging to file"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {self.address_string()} - {format % args}\n"
        
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry)
        except:
            pass  # Ignore logging errors
        
        # Also print to stdout for immediate feedback
        print(log_entry.strip())
        sys.stdout.flush()

def start_server_daemon():
    """Start server as a true background daemon"""
    
    # Change to working directory
    os.chdir(WORK_DIR)
    
    # Save our PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the server
    print(f"🌐 Documentation Server Starting")
    print(f"📡 Port: {PORT}")
    print(f"📂 Directory: {WORK_DIR}")
    print(f"🔗 Local: http://localhost:{PORT}")
    print(f"🌍 Remote: http://YOUR_IP:{PORT}")
    print(f"📝 Logs: {LOG_FILE}")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), DocumentationHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Server error: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(1)

if __name__ == "__main__":
    start_server_daemon()