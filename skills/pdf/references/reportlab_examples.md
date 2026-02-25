# ReportLab PDF Examples

## Basic PDF with Text

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=letter)
c.drawString(100, 750, "Hello World")
c.save()
```

## PDF with Tables

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

doc = SimpleDocTemplate("table.pdf", pagesize=letter)
data = [
    ["Name", "Age", "City"],
    ["Alice", 30, "NYC"],
    ["Bob", 25, "LA"]
]

table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))

doc.build([table])
```

## PDF with Multiple Pages

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("multi_page.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Page 1 Content", styles['h1']))
story.append(PageBreak())
story.append(Paragraph("Page 2 Content", styles['h1']))

doc.build(story)
```

## Common Patterns

- Use `SimpleDocTemplate` for multi-element PDFs
- Use `canvas.Canvas` for simple single-page PDFs
- Always set pagesize (letter, A4, etc.)
- Use `TableStyle` for formatting tables
- Use `Paragraph` with styles for formatted text
