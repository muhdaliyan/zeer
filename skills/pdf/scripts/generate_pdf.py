#!/usr/bin/env python3
"""
PDF Generation Script
Usage: python generate_pdf.py <output_file> <title> <content>
"""

import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(output_file, title, content):
    """Create a simple PDF document."""
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, title)
    
    # Add content
    c.setFont("Helvetica", 12)
    text_object = c.beginText(100, height - 150)
    text_object.setTextOrigin(100, height - 150)
    
    for line in content.split('\n'):
        text_object.textLine(line)
    
    c.drawText(text_object)
    c.save()
    print(f"PDF created: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_pdf.py <output_file> <title> <content>")
        sys.exit(1)
    
    output_file = sys.argv[1]
    title = sys.argv[2]
    content = sys.argv[3]
    
    create_pdf(output_file, title, content)
