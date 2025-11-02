#!/usr/bin/env python3
"""
Convert Markdown documentation to HTML (print-friendly)
"""

import markdown2
import os

def markdown_to_html(md_file, html_file):
    """Convert markdown file to HTML"""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML with extras
    html_content = markdown2.markdown(md_content, extras=['fenced-code-blocks', 'tables', 'toc'])
    
    # CSS styles for print-friendly HTML
    css_styles = """
    <style>
    @media print {
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            -webkit-print-color-adjust: exact;
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
        
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
        }
    }
    
    body {
        font-family: 'Arial', 'Helvetica', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background-color: #fff;
    }
    
    h1 {
        color: #1e4d72;
        border-bottom: 3px solid #1e4d72;
        padding-bottom: 10px;
        margin-top: 40px;
        font-size: 2.5em;
    }
    
    h1:first-child {
        margin-top: 0;
        text-align: center;
        border-bottom: none;
        color: #2c5aa0;
    }
    
    h2 {
        color: #2c5aa0;
        border-bottom: 2px solid #ddd;
        padding-bottom: 8px;
        margin-top: 35px;
        font-size: 1.8em;
    }
    
    h3 {
        color: #444;
        margin-top: 25px;
        font-size: 1.4em;
    }
    
    h4 {
        color: #666;
        margin-top: 20px;
        font-size: 1.2em;
    }
    
    h5, h6 {
        color: #666;
        margin-top: 15px;
        font-size: 1.1em;
    }
    
    p {
        margin: 12px 0;
        text-align: justify;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 3px 6px;
        border-radius: 3px;
        font-family: 'Courier New', 'Monaco', monospace;
        font-size: 0.9em;
        color: #c7254e;
    }
    
    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-left: 4px solid #2c5aa0;
        border-radius: 5px;
        padding: 15px;
        overflow-x: auto;
        font-family: 'Courier New', 'Monaco', monospace;
        font-size: 0.85em;
        line-height: 1.4;
        margin: 20px 0;
    }
    
    pre code {
        background: none;
        padding: 0;
        color: #333;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    table, th, td {
        border: 1px solid #ddd;
    }
    
    th {
        background-color: #2c5aa0;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    
    td {
        padding: 10px;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    tr:hover {
        background-color: #f5f5f5;
    }
    
    blockquote {
        border-left: 5px solid #2c5aa0;
        margin: 20px 0;
        padding: 15px 25px;
        background-color: #f9f9f9;
        font-style: italic;
    }
    
    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }
    
    li {
        margin: 8px 0;
    }
    
    ul li::marker {
        color: #2c5aa0;
    }
    
    ol li::marker {
        color: #2c5aa0;
        font-weight: bold;
    }
    
    a {
        color: #2c5aa0;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    hr {
        border: none;
        height: 2px;
        background-color: #ddd;
        margin: 30px 0;
    }
    
    .toc {
        background-color: #f0f7ff;
        border: 2px solid #2c5aa0;
        border-radius: 8px;
        padding: 20px;
        margin: 30px 0;
    }
    
    .toc h2 {
        margin-top: 0;
        color: #2c5aa0;
        border-bottom: none;
    }
    
    .highlight {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    
    /* Status indicators */
    .success {
        color: #28a745;
        font-weight: bold;
    }
    
    .warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .info {
        color: #17a2b8;
        font-weight: bold;
    }
    
    /* Header styling */
    .doc-header {
        text-align: center;
        margin-bottom: 50px;
        padding: 30px;
        background: linear-gradient(135deg, #2c5aa0, #1e4d72);
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .doc-header h1 {
        margin: 0;
        color: white;
        border: none;
        font-size: 2.8em;
    }
    
    .doc-header p {
        margin: 10px 0 0 0;
        font-size: 1.2em;
        opacity: 0.9;
    }
    </style>
    """
    
    # Create complete HTML document
    complete_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kafka Processors System - Complete Documentation</title>
        {css_styles}
    </head>
    <body>
        <div class="doc-header">
            <h1>Kafka Processors System</h1>
            <p>Complete Documentation & Implementation Guide</p>
        </div>
        
        {html_content}
        
        <hr>
        <footer style="text-align: center; color: #666; font-size: 0.9em; margin-top: 50px;">
            <p>Generated on {os.popen('date').read().strip()}</p>
            <p>Kafka Processors System - Production Ready Implementation</p>
        </footer>
    </body>
    </html>
    """
    
    # Write HTML file
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(complete_html)
        print(f"✅ Successfully converted {md_file} to {html_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating HTML: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    md_file = "/root/kafka/kafka-processors/COMPLETE_DOCUMENTATION.md"
    html_file = "/root/kafka/kafka-processors/Kafka_Processors_System_Documentation.html"
    
    if os.path.exists(md_file):
        success = markdown_to_html(md_file, html_file)
        if success:
            print(f"📄 HTML documentation created: {html_file}")
            print(f"📊 File size: {os.path.getsize(html_file) / 1024:.1f} KB")
            print("")
            print("🖨️  To convert to PDF:")
            print("   1. Open the HTML file in a web browser")
            print("   2. Press Ctrl+P (or Cmd+P on Mac)")
            print("   3. Select 'Save as PDF' as destination")
            print("   4. Choose appropriate settings and save")
            print("")
            print(f"🌐 HTML file location: {html_file}")
        else:
            sys.exit(1)
    else:
        print(f"❌ Markdown file not found: {md_file}")
        sys.exit(1)