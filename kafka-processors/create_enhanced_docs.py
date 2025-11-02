#!/usr/bin/env python3
"""
Enhanced HTML documentation generator with navigation and improved design
"""

import markdown2
import os
from datetime import datetime

def create_enhanced_html(md_file, html_file, title, is_main=True):
    """Create enhanced HTML with navigation and improved design"""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=['fenced-code-blocks', 'tables', 'toc'])
    
    # Enhanced CSS with navigation and better design
    css_styles = """
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        min-height: 100vh;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
    }
    
    /* Header Navigation */
    .header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .header h1 {
        margin: 0;
        font-size: 2.2em;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .nav-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    
    .nav-link {
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 20px;
        transition: all 0.3s ease;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .nav-link:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .nav-link.active {
        background: #ff6b6b;
        border-color: #ff6b6b;
    }
    
    /* Content Area */
    .content {
        padding: 40px;
        background: white;
    }
    
    /* Headings */
    h1 {
        color: #1e3c72;
        border-bottom: 3px solid #1e3c72;
        padding-bottom: 10px;
        margin: 30px 0 20px 0;
        font-size: 2.2em;
        position: relative;
    }
    
    h1:first-child {
        margin-top: 0;
    }
    
    h1::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 50px;
        height: 3px;
        background: #ff6b6b;
    }
    
    h2 {
        color: #2a5298;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 8px;
        margin: 25px 0 15px 0;
        font-size: 1.6em;
    }
    
    h3 {
        color: #444;
        margin: 20px 0 10px 0;
        font-size: 1.3em;
    }
    
    h4 {
        color: #666;
        margin: 15px 0 8px 0;
        font-size: 1.1em;
    }
    
    /* Paragraphs */
    p {
        margin: 12px 0;
        text-align: justify;
        line-height: 1.7;
    }
    
    /* Code styling */
    code {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 3px 6px;
        border-radius: 4px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.9em;
        color: #d63384;
        border: 1px solid #dee2e6;
    }
    
    pre {
        background: linear-gradient(135deg, #2d3748, #4a5568);
        color: #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        overflow-x: auto;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.85em;
        line-height: 1.5;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #ff6b6b;
    }
    
    pre code {
        background: none;
        padding: 0;
        color: #e2e8f0;
        border: none;
    }
    
    /* Tables */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }
    
    th {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        padding: 15px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 0.95em;
    }
    
    td {
        padding: 12px;
        border-bottom: 1px solid #e0e0e0;
        vertical-align: top;
    }
    
    tr:nth-child(even) {
        background: #f8f9fa;
    }
    
    tr:hover {
        background: #e3f2fd;
        transition: background 0.2s ease;
    }
    
    /* Lists */
    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }
    
    li {
        margin: 8px 0;
        line-height: 1.6;
    }
    
    ul li::marker {
        color: #2a5298;
    }
    
    ol li::marker {
        color: #2a5298;
        font-weight: bold;
    }
    
    /* Links */
    a {
        color: #2a5298;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    
    a:hover {
        color: #ff6b6b;
        text-decoration: underline;
    }
    
    /* Blockquotes */
    blockquote {
        border-left: 5px solid #ff6b6b;
        margin: 20px 0;
        padding: 15px 25px;
        background: linear-gradient(135deg, #fff5f5, #fed7d7);
        font-style: italic;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
        margin: 2px;
    }
    
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-error { background: #f8d7da; color: #721c24; }
    .badge-info { background: #d1ecf1; color: #0c5460; }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #2d3748, #4a5568);
        color: white;
        padding: 30px;
        text-align: center;
        margin-top: 50px;
    }
    
    .footer h3 {
        color: #ff6b6b;
        margin-bottom: 10px;
        font-size: 1.2em;
    }
    
    .footer p {
        margin: 8px 0;
        opacity: 0.9;
    }
    
    .footer .developer {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .footer .developer strong {
        color: #ff6b6b;
        font-size: 1.1em;
    }
    
    /* Back to top button */
    .back-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
        color: white;
        padding: 12px;
        border-radius: 50%;
        text-decoration: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        z-index: 1000;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    
    .back-to-top:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        background: linear-gradient(135deg, #ee5a5a, #dc4545);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .content {
            padding: 20px;
        }
        
        .header {
            padding: 15px;
        }
        
        .header h1 {
            font-size: 1.8em;
        }
        
        .nav-links {
            gap: 10px;
        }
        
        .nav-link {
            padding: 6px 12px;
            font-size: 0.9em;
        }
        
        h1 {
            font-size: 1.8em;
        }
        
        h2 {
            font-size: 1.4em;
        }
        
        table {
            font-size: 0.9em;
        }
        
        pre {
            padding: 15px;
            font-size: 0.8em;
        }
    }
    
    /* Print styles */
    @media print {
        body {
            background: white;
        }
        
        .header, .footer, .back-to-top {
            display: none;
        }
        
        .container {
            box-shadow: none;
        }
        
        .content {
            padding: 0;
        }
        
        h1 {
            page-break-before: always;
        }
        
        h1:first-child {
            page-break-before: avoid;
        }
        
        pre, table, blockquote {
            page-break-inside: avoid;
        }
    }
    </style>
    """
    
    # Navigation menu
    if is_main:
        nav_menu = '''
        <div class="nav-links">
            <a href="Kafka_Processors_System_Documentation.html" class="nav-link active">📋 Complete Documentation</a>
            <a href="File_Structure_Guide.html" class="nav-link">📁 File Structure Guide</a>
            <a href="#system-overview" class="nav-link">🏗️ Architecture</a>
            <a href="#api-documentation" class="nav-link">🔌 API Docs</a>
            <a href="#docker-setup" class="nav-link">🐳 Docker Setup</a>
            <a href="http://195.35.6.88:8082" class="nav-link" target="_blank">🚀 Live API</a>
            <a href="http://195.35.6.88:8082/docs" class="nav-link" target="_blank">📖 API Swagger</a>
        </div>
        '''
        page_title = "Complete Documentation"
    else:
        nav_menu = '''
        <div class="nav-links">
            <a href="Kafka_Processors_System_Documentation.html" class="nav-link">📋 Complete Documentation</a>
            <a href="File_Structure_Guide.html" class="nav-link active">📁 File Structure Guide</a>
            <a href="#project-structure" class="nav-link">📂 Structure</a>
            <a href="#configuration" class="nav-link">⚙️ Configuration</a>
            <a href="#topic-management" class="nav-link">📊 Topics</a>
            <a href="http://195.35.6.88:8082" class="nav-link" target="_blank">🚀 Live API</a>
            <a href="http://195.35.6.88:8080" class="nav-link" target="_blank">📊 Kafka UI</a>
        </div>
        '''
        page_title = "File Structure & Configuration Guide"
    
    # Create complete HTML document
    complete_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="author" content="Mahesh Gavandar">
        <meta name="description" content="Kafka Processors System - {page_title}">
        <title>Kafka Processors System - {page_title}</title>
        {css_styles}
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h1>🚀 Kafka Processors System</h1>
                <p style="text-align: center; margin: 5px 0; opacity: 0.9; font-size: 1.1em;">{page_title}</p>
                {nav_menu}
            </header>
            
            <main class="content">
                {html_content}
            </main>
            
            <footer class="footer">
                <h3>🎯 System Information</h3>
                <p><strong>Status:</strong> <span class="badge badge-success">✅ Fully Operational</span></p>
                <p><strong>Version:</strong> 1.0.0 | <strong>API Port:</strong> 8082 | <strong>Kafka Port:</strong> 9092</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                
                <div class="developer">
                    <p><strong>🎨 Designed & Developed by</strong></p>
                    <p><strong>Mahesh Gavandar</strong></p>
                    <p style="font-size: 0.9em; opacity: 0.8;">Full-Stack Kafka Systems Developer</p>
                </div>
                
                <div style="margin-top: 20px; font-size: 0.9em; opacity: 0.8;">
                    <p>📧 For support and inquiries about this Kafka Processors System</p>
                    <p>🔗 <a href="Kafka_Processors_System_Documentation.html" style="color: #ff6b6b;">Complete Documentation</a> | 
                       <a href="File_Structure_Guide.html" style="color: #ff6b6b;">File Structure Guide</a></p>
                </div>
            </footer>
        </div>
        
        <a href="#" class="back-to-top" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;">↑</a>
        
        <script>
            // Show/hide back to top button
            window.addEventListener('scroll', function() {{
                const backToTop = document.querySelector('.back-to-top');
                if (window.scrollY > 300) {{
                    backToTop.style.display = 'flex';
                }} else {{
                    backToTop.style.display = 'none';
                }}
            }});
            
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
            
            // Add copy functionality to code blocks
            document.querySelectorAll('pre').forEach(pre => {{
                const button = document.createElement('button');
                button.textContent = '📋 Copy';
                button.style.cssText = 'position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;';
                
                const wrapper = document.createElement('div');
                wrapper.style.position = 'relative';
                pre.parentNode.insertBefore(wrapper, pre);
                wrapper.appendChild(pre);
                wrapper.appendChild(button);
                
                button.addEventListener('click', () => {{
                    const code = pre.querySelector('code') || pre;
                    navigator.clipboard.writeText(code.textContent).then(() => {{
                        button.textContent = '✅ Copied!';
                        setTimeout(() => button.textContent = '📋 Copy', 2000);
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    # Write HTML file
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(complete_html)
        return True
    except Exception as e:
        print(f"❌ Error creating HTML: {e}")
        return False

def main():
    """Generate both enhanced HTML files"""
    
    files_to_process = [
        {
            'md': '/root/kafka/kafka-processors/COMPLETE_DOCUMENTATION.md',
            'html': '/root/kafka/kafka-processors/Kafka_Processors_System_Documentation.html',
            'title': 'Complete Documentation',
            'is_main': True
        },
        {
            'md': '/root/kafka/kafka-processors/FILE_STRUCTURE_GUIDE.md', 
            'html': '/root/kafka/kafka-processors/File_Structure_Guide.html',
            'title': 'File Structure Guide',
            'is_main': False
        }
    ]
    
    success_count = 0
    
    for file_info in files_to_process:
        if os.path.exists(file_info['md']):
            success = create_enhanced_html(
                file_info['md'], 
                file_info['html'], 
                file_info['title'],
                file_info['is_main']
            )
            if success:
                print(f"✅ Enhanced HTML created: {file_info['html']}")
                success_count += 1
            else:
                print(f"❌ Failed to create: {file_info['html']}")
        else:
            print(f"❌ Markdown file not found: {file_info['md']}")
    
    if success_count == len(files_to_process):
        print(f"")
        print(f"🎉 Successfully generated {success_count} enhanced HTML files!")
        print(f"🌐 Access via HTTP server: http://localhost:8090/")
        print(f"📋 Complete Documentation: http://localhost:8090/Kafka_Processors_System_Documentation.html")
        print(f"📁 File Structure Guide: http://localhost:8090/File_Structure_Guide.html")
        print(f"")
        print(f"✨ Features added:")
        print(f"   • Cross-navigation between pages")
        print(f"   • Enhanced visual design with gradients")
        print(f"   • Developer credit: Mahesh Gavandar")
        print(f"   • Copy-to-clipboard for code blocks")
        print(f"   • Smooth scrolling and back-to-top button")
        print(f"   • Responsive design for mobile devices")
        print(f"   • Direct links to live API and Kafka UI")

if __name__ == "__main__":
    main()