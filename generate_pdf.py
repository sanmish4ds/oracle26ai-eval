#!/usr/bin/env python3
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# Read markdown
with open('WHITEPAPER.md', 'r') as f:
    content = f.read()

# Create PDF
pdf_file = "WHITEPAPER_arxiv.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
styles = getSampleStyleSheet()

# Create content
story = []

# Split by lines and process
lines = content.split('\n')
for line in lines:
    if not line.strip():
        story.append(Spacer(1, 6))
    elif line.startswith('# '):
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
        story.append(Paragraph(line.replace('# ', ''), title_style))
    elif line.startswith('## '):
        story.append(Paragraph(line.replace('## ', ''), styles['Heading2']))
        story.append(Spacer(1, 6))
    elif line.startswith('### '):
        story.append(Paragraph(line.replace('### ', ''), styles['Heading3']))
        story.append(Spacer(1, 4))
    else:
        # Limit line length for readability
        text = line[:500] if len(line) > 500 else line
        story.append(Paragraph(text, styles['Normal']))

# Build PDF
try:
    doc.build(story)
    print(f"✅ PDF successfully generated: {pdf_file}")
except Exception as e:
    print(f"❌ Error: {e}")
