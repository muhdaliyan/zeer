---
name: pdf
description: Create, generate, and manipulate PDF documents. Use for PDF creation, document generation, reports, invoices, forms, and any PDF-related tasks. Activate when user mentions PDF, document generation, or creating formatted files.
license: MIT
compatibility: Requires file system access and Python with reportlab
allowed-tools: create_file write_to_file read_file run_code
---

## Goal

Create professional, visually appealing PDF documents with modern design, proper typography, and polished layouts. Generate production-quality reports, invoices, forms, and documentation that look professionally designed.

## Design Quality Standards

ALWAYS create PDFs with:
- **Professional typography**: Use proper font hierarchies, sizes, and spacing
- **Visual hierarchy**: Clear distinction between headers, subheaders, and body text
- **Color schemes**: Use professional color palettes, not just black and white
- **Spacing**: Generous margins, proper line spacing, and visual breathing room
- **Layout**: Well-structured sections with visual separation
- **Visual elements**: Use lines, boxes, backgrounds, and subtle design elements
- **Branding**: Include logos, headers, footers with consistent styling
- **Tables**: Well-formatted tables with headers, borders, and alternating row colors
- **Images**: Include relevant graphics, charts, or decorative elements where appropriate

DO NOT create basic, plain text PDFs. Aim for professional, polished documents.

## Capabilities

### PDF Creation
- Generate professional PDF documents with modern design
- Create formatted reports with visual hierarchy
- Generate invoices and receipts with branding
- Create forms and templates with professional styling
- Add text, tables, images, charts, and formatting

### Content Generation
- Generate appropriate, well-written content based on user requests
- Create structured documents with clear sections
- Add professionally formatted tables with data
- Include relevant images, charts, and graphics

### Document Formatting
- Use professional fonts (Helvetica, Times, custom fonts)
- Apply colors for headers, accents, and visual interest
- Create tables with styling (borders, backgrounds, alignment)
- Add headers and footers with page numbers
- Include logos and branding elements
- Use boxes, lines, and backgrounds for visual structure

## Procedure

1. When user requests a PDF:
   - Understand what content they want
   - Generate appropriate, professional content if not provided
   - Design a visually appealing layout with proper styling
   - Create Python code using reportlab with ADVANCED styling
   - Use `run_code` tool to execute the code and create the PDF

2. For content generation:
   - Generate relevant, well-written content based on the topic
   - Structure content with clear hierarchy (title, sections, paragraphs)
   - Add tables with realistic data if relevant
   - Make it informative, professional, and visually engaging

3. For PDF generation:
   - Use reportlab library (SimpleDocTemplate, Paragraph, Table, Spacer, etc.)
   - Apply professional styling with colors, fonts, and spacing
   - Use ParagraphStyle for custom text formatting
   - Add visual elements (lines, boxes, backgrounds)
   - Include headers/footers with page numbers
   - Set appropriate page size (letter, A4)
   - Add proper styling and formatting
   - Save with descriptive filename

## Best Practices

- Always generate content if user doesn't provide it
- Use standard page sizes (A4, Letter)
- Maintain consistent styling throughout
- Ensure text is readable (font size 10-12pt minimum)
- Include proper structure (title, sections, content)
- Add tables for structured data when appropriate
- Use `run_code` to execute the PDF generation immediately

## Examples

For detailed ReportLab code examples, see `references/reportlab_examples.md`

User: "Create a PDF intro to Lahore"
→ Generate content about Lahore (history, culture, landmarks)
→ Create Python code with reportlab
→ Use `run_code` to execute and generate the PDF
→ Include tables with key facts/statistics

User: "Make a PDF report with charts"
→ Generate report content
→ Create multi-page PDF with text, tables
→ Execute code to create the file

User: "Generate a PDF invoice"
→ Create invoice template with sample data
→ Generate PDF with proper formatting
→ Execute to create the file
