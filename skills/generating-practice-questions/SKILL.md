---
name: generating-practice-questions
description: Generate educational practice questions from lecture notes to test student understanding. Use when users request practice questions, exam preparation materials, study guides, or assessment items based on lecture content.
license: MIT
compatibility: Python (pdfplumber, LaTeX parsing, Markdown processing)
allowed-tools: run_code run_command read_file write_to_file create_file list_directory make_directory

goal: >
  Generate high-quality, structured educational practice questions from lecture notes
  to assess student comprehension, conceptual understanding, and practical application
  across multiple difficulty levels and assessment formats.

capabilities:
  - lecture_content_parsing
  - learning_objective_extraction
  - concept_identification
  - educational_question_generation
  - multi_difficulty_assessment_design
  - coding_problem_generation
  - real_world_use_case_design
  - multi_format_output_generation

input:
  supported_formats:
    - pdf
    - latex
    - markdown
    - plain_text
  extraction_rules:
    pdf:
      tool: pdfplumber
      behavior: Extract readable text
    latex:
      behavior:
        - Strip preamble before \begin{document}
        - Preserve math environments ($...$, \[...\], equation blocks)
    markdown_text:
      behavior: Read as-is
  content_targets:
    - learning_objectives
    - main_topics
    - definitions
    - algorithms
    - examples

question_structure:
  order:
    - true_false
    - explanatory
    - coding
    - use_case

question_guidelines:
  true_false:
    coverage:
      - One per learning objective
      - Or 3–5 if objectives absent
    difficulty_progression:
      - 1–2 definitional
      - 2–3 reasoning-based
    quality_criteria:
      - Single correct interpretation
      - Clear language
      - Reveals common misconceptions

  explanatory:
    count: 3–5
    coverage:
      - Key concepts
      - Algorithms
      - Advantages & limitations
      - Concept relationships
    formulation:
      - Explain
      - Compare and contrast
      - Why does
      - What are advantages/disadvantages
      - Describe the steps
    quality_criteria:
      - Focused
      - Open-ended
      - Requires 3–5 sentences

  coding:
    scope:
      - Algorithm implementation
      - Concept simulation
    constraints:
      - Solvable with lecture knowledge
      - 15–30 minute difficulty
    structure:
      - Objective
      - Steps (3–5)
      - Function signature
      - Input/output examples
      - Optional hints
    language:
      default: python
      allowed_libraries:
        - numpy
        - pandas
        - matplotlib
        - scikit-learn

  use_case:
    components:
      - context
      - data_description
      - task
      - optional_constraints
      - hints
      - allowed_libraries
    data_generation:
      - Provide simple reproducible code if needed

output_format:
  supported:
    - latex
    - markdown
    - pdf
    - plain_text
  general_structure:
    - title
    - instructions
    - part_1_true_false
    - part_2_explanatory
    - part_3_coding
    - part_4_use_case
  templates:
    latex: assets/questions_template.tex
    markdown: assets/markdown_template.md

best_practices:
  - Never include answer keys
  - Maintain logical difficulty progression
  - Avoid topic repetition across question types
  - Base all questions strictly on provided lecture content
  - Ensure clarity, fairness, and pedagogical soundness

common_pitfalls:
  - Including solutions
  - Generating vague questions
  - Overlapping concepts across question sections
  - Excessive difficulty beyond lecture scope

supporting_resources:
  references:
    - references/examples_by_topic.md

dependencies:
  - pdfplumber
  - python-docx
  - pypandoc
---