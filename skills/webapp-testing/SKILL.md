---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: MIT
compatibility: Python + Playwright (local web servers)
allowed-tools: run_code run_command read_file write_to_file create_file list_directory make_directory

goal: >
  Enable reliable automation and testing of local web applications using Playwright,
  providing structured workflows for UI interaction, verification, debugging, and inspection.

capabilities:
  - frontend_ui_testing
  - dynamic_dom_inspection
  - screenshot_capture
  - browser_console_logging
  - automated_user_flows
  - server_lifecycle_management
  - multi_server_testing

helper_scripts:
  - name: scripts/with_server.py
    purpose: Manage lifecycle of one or more local servers before executing Playwright automation.
    usage_policy:
      - Always run with --help before usage
      - Treat as a black-box utility
      - Do not read source unless customization is absolutely required

decision_tree:
  static_html:
    - Read HTML file directly
    - Identify selectors
    - Write Playwright automation script
    - If inspection fails or is incomplete:
        - Treat application as dynamic
  dynamic_webapp:
    - Check if server is running
    - If not running:
        - Run: python scripts/with_server.py --help
        - Launch server using helper script
    - Navigate to application
    - Wait for full JS execution using networkidle
    - Inspect rendered DOM
    - Identify selectors
    - Execute automation actions

procedure:
  - Determine application type (static HTML or dynamic webapp)
  - If static:
      - Read HTML file
      - Identify selectors
      - Write Playwright automation script
  - If dynamic:
      - Check if server is running
      - If not:
          - Inspect helper script usage via --help
          - Launch required servers
      - Navigate to application URL
      - Wait for page.wait_for_load_state("networkidle")
      - Inspect rendered DOM
      - Identify selectors
      - Execute actions
      - Capture screenshots and logs if required
      - Close browser

execution_examples:
  single_server: >
    python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
  multi_server: >
    python scripts/with_server.py
      --server "cd backend && python server.py" --port 3000
      --server "cd frontend && npm run dev" --port 5173
      -- python your_automation.py

playwright_template: |
  from playwright.sync_api import sync_playwright

  with sync_playwright() as p:
      browser = p.chromium.launch(headless=True)
      page = browser.new_page()
      page.goto("http://localhost:5173")
      page.wait_for_load_state("networkidle")
      # automation logic
      browser.close()

reconnaissance_then_action:
  - Inspect rendered DOM:
      - Capture screenshot
      - Dump page content
      - Enumerate visible elements
  - Identify selectors from rendered state
  - Execute actions using discovered selectors

best_practices:
  - Always wait for networkidle before DOM inspection
  - Use helper scripts as black-box utilities
  - Prefer descriptive selectors (text=, role=, CSS selectors, IDs)
  - Add explicit waits when needed
  - Always close browser after execution
  - Capture screenshots for debugging

common_pitfalls:
  - Inspecting DOM before JavaScript execution
  - Using brittle selectors
  - Forgetting to close browser

reference_files:
  examples:
    - element_discovery.py: Discovering buttons, links, and inputs on a page
    - static_html_automation.py: Using file:// URLs for local HTML
    - console_logging.py: Capturing console logs during automation
---