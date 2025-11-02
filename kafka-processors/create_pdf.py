#!/usr/bin/env python3
"""
Convert Markdown documentation to PDF
"""

import markdown
from weasyprint import HTML, CSS
import os

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF"""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables', 'toc'])
    html_content = md.convert(md_content)
    
    # CSS styles for better PDF formatting
    css_styles = """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10px;
            color: #666;
        }
    }
    
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 100%;
    }
    
    h1 {
        color: #2c5aa0;
        border-bottom: 3px solid #2c5aa0;
        padding-bottom: 10px;
        page-break-before: always;
    }
    
    h1:first-child {
        page-break-before: avoid;
    }
    
    h2 {
        color: #2c5aa0;
        border-bottom: 2px solid #ddd;
        padding-bottom: 5px;
        margin-top: 30px;
    }
    
    h3 {
        color: #444;
        margin-top: 25px;
    }
    
    h4, h5, h6 {
        color: #666;
        margin-top: 20px;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    
    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.85em;
        line-height: 1.4;
    }
    
    pre code {
        background: none;
        padding: 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
    }
    
    table, th, td {
        border: 1px solid #ddd;
    }
    
    th, td {
        padding: 10px;
        text-align: left;
    }
    
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    
    blockquote {
        border-left: 4px solid #2c5aa0;
        margin: 20px 0;
        padding: 10px 20px;
        background-color: #f9f9f9;
    }
    
    ul, ol {
        margin: 10px 0;
        padding-left: 25px;
    }
    
    li {
        margin: 5px 0;
    }
    
    .toc {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .toc h2 {
        margin-top: 0;
        color: #2c5aa0;
    }
    
    .toc ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .toc li {
        margin: 8px 0;
    }
    
    .toc a {
        text-decoration: none;
        color: #2c5aa0;
    }
    
    .toc a:hover {
        text-decoration: underline;
    }
    
    /* Prevent page breaks in code blocks and tables */
    pre, table {
        page-break-inside: avoid;
    }
    
    /* Keep headings with following content */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }
    """
    
    # Create complete HTML document
    complete_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Kafka Processors System - Complete Documentation</title>
        <style>{css_styles}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    try:
        HTML(string=complete_html, base_url=os.path.dirname(os.path.abspath(md_file))).write_pdf(pdf_file)
        print(f"✅ Successfully converted {md_file} to {pdf_file}")
        return True
    except Exception as e:
        print(f"❌ Error converting to PDF: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    md_file = "/root/kafka/kafka-processors/COMPLETE_DOCUMENTATION.md"
    pdf_file = "/root/kafka/kafka-processors/Kafka_Processors_System_Documentation.pdf"
    
    if os.path.exists(md_file):
        success = markdown_to_pdf(md_file, pdf_file)
        if success:
            print(f"📄 PDF documentation created: {pdf_file}")
            print(f"📊 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        else:
            sys.exit(1)
    else:
        print(f"❌ Markdown file not found: {md_file}")
        sys.exit(1)