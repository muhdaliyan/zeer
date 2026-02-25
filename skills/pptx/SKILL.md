---
name: pptx
description: Use this skill any time a .pptx file is involved — creating, editing, reading, parsing, extracting, modifying, merging, splitting, or generating slide decks. Trigger whenever the user mentions slides, presentations, decks, or .pptx files.
license: Proprietary
compatibility: Python + Node.js (pptxgenjs) + LibreOffice + Poppler
allowed-tools: run_code run_command read_file write_to_file create_file list_directory make_directory

goal: >
  Create professional, visually stunning PowerPoint presentations with modern design,
  consistent branding, and engaging layouts. NEVER create basic, text-heavy slides.
  Always aim for production-quality presentations with strong visual identity,
  professional color schemes, and polished design elements.

quality_standards:
  ALWAYS create presentations with:
    - Professional, modern design with consistent visual theme
    - Engaging color palettes (not just black/white/blue)
    - Visual hierarchy with proper typography
    - Images, icons, charts, and visual elements (not just text)
    - Consistent layouts with breathing room and proper spacing
    - Smooth transitions and professional animations
    - Branded headers/footers with page numbers
    - High-impact title slides with visual interest
    - Data visualization using charts and infographics
  
  AVOID:
    - Text-heavy slides with bullet points only
    - Generic templates with no personality
    - Inconsistent styling across slides
    - Plain white backgrounds with black text
    - Cluttered layouts with poor spacing

capabilities:
  - pptx_text_extraction
  - pptx_visual_preview
  - pptx_raw_xml_unpacking
  - pptx_editing_and_modification
  - pptx_creation_from_scratch
  - pptx_template_based_generation
  - pptx_merging_and_splitting
  - pptx_quality_assurance
  - slide_visual_design_guidance

quick_reference:
  read_analyze: python -m markitdown presentation.pptx
  visual_overview: python scripts/thumbnail.py presentation.pptx
  raw_xml: python scripts/office/unpack.py presentation.pptx unpacked/
  edit_template: Read editing.md
  create_from_scratch: Read pptxgenjs.md

reading_content:
  - Extract text using: python -m markitdown presentation.pptx
  - Generate slide thumbnails using: python scripts/thumbnail.py presentation.pptx
  - Unpack raw XML using: python scripts/office/unpack.py presentation.pptx unpacked/

editing_workflow:
  - Analyze template using thumbnail.py
  - Unpack pptx to raw XML
  - Manipulate slide XML and assets
  - Edit content and layout
  - Clean unused assets
  - Repack into pptx

creation_workflow:
  - Use pptxgenjs when no template or reference deck exists
  - Programmatically generate slides, layouts, text, images, and charts

design_principles:
  palette_selection:
    - Pick topic-specific color palette
    - Use dominant color (60–70% weight)
    - Limit to 1–2 supporting tones + 1 accent
    - Apply dark/light sandwich structure or fully dark theme
  visual_motif:
    - Choose one distinctive repeating element
    - Apply consistently across all slides
  layout_guidelines:
    - Avoid text-only slides
    - Prefer two-column, grids, half-bleed images, or card layouts
    - Use large stat callouts and visual data presentation
  typography:
    header_fonts: [Georgia, Arial Black, Cambria, Trebuchet MS, Impact, Palatino, Consolas]
    body_fonts: [Calibri, Calibri Light, Garamond, Arial]
    sizing:
      title: 36-44pt
      section_header: 20-24pt
      body: 14-16pt
      captions: 10-12pt
  spacing:
    margins: ">= 0.5 inch"
    block_spacing: "0.3 – 0.5 inch"
  avoid:
    - repetitive layouts
    - centered body text
    - low contrast colors
    - default blue themes
    - text-only slides
    - accent lines under titles
    - uneven spacing
    - placeholder text

color_palettes:
  midnight_executive: [ "#1E2761", "#CADCFC", "#FFFFFF" ]
  forest_moss: [ "#2C5F2D", "#97BC62", "#F5F5F5" ]
  coral_energy: [ "#F96167", "#F9E795", "#2F3C7E" ]
  warm_terracotta: [ "#B85042", "#E7E8D1", "#A7BEAE" ]
  ocean_gradient: [ "#065A82", "#1C7293", "#21295C" ]
  charcoal_minimal: [ "#36454F", "#F2F2F2", "#212121" ]
  teal_trust: [ "#028090", "#00A896", "#02C39A" ]
  berry_cream: [ "#6D2E46", "#A26769", "#ECE2D0" ]
  sage_calm: [ "#84B59F", "#69A297", "#50808E" ]
  cherry_bold: [ "#990011", "#FCF6F5", "#2F3C7E" ]

quality_assurance:
  text_validation:
    - Run: python -m markitdown output.pptx
    - Check for missing text, typos, incorrect ordering
    - Detect placeholders using:
        python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
  visual_validation:
    - Convert slides to images
    - Inspect for overlaps, misalignment, low contrast, clipping, uneven spacing
    - Use independent inspection agents for visual review
  verification_loop:
    - Generate → Inspect → Identify issues → Fix → Re-inspect → Repeat
    - Do not declare completion until at least one fix-and-verify cycle passes

image_conversion:
  - Convert to PDF:
      python scripts/office/soffice.py --headless --convert-to pdf output.pptx
  - Convert to images:
      pdftoppm -jpeg -r 150 output.pdf slide
  - Re-render specific slides:
      pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed

dependencies:
  - pip install "markitdown[pptx]"
  - pip install Pillow
  - npm install -g pptxgenjs
  - LibreOffice (soffice)
  - Poppler (pdftoppm)
---