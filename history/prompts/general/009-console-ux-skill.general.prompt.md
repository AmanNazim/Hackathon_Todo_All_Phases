---
id: 009
title: "Console UX Skill Creation"
stage: "general"
date_iso: "2026-01-04"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-console-ux-skill"
labels: ["skill", "ux", "cli", "console", "design"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/console-ux-skill/SKILL.md
  - .claude/skills/console-ux-skill/scripts/ux_tester.sh
  - .claude/skills/console-ux-skill/references/ux-patterns.md
  - .claude/skills/console-ux-skill/assets/ux-components.json
tests_yaml: |
  - "Skill specification verified for completeness"
  - "Script execution confirmed"
prompt_text: |
  You are a Senior Python Engineer, UX Architect, and Prompt Engineering Specialist.

  Your task is to design and implement a reusable internal skill named:

  **Console UX Skill**

  This skill defines advanced CLI user experience (UX) design and implementation strategies to produce **premium-grade interactive command-line applications**.

  ────────────────────────────────────────
  OBJECTIVE
  ────────────────────────────────────────
  Produce a detailed skill that enables advanced CLI UX creation, including:

  ✔ Advanced UX strategies
  ✔ Advanced UX design principles
  ✔ Advanced UX implementation patterns
  ✔ Color schemes
  ✔ Text formatting
  ✔ Subtle animated transitions
  ✔ Emoji-based indicators (optional/optional per environment)
  ✔ Interactive "AI feel" inside a CLI
  ✔ Accessibility and environment detection
  ✔ Best practice references and learning sources

  This skill must be:
  - Technical
  - Well-structured
  - Aligned with top-tier industry standards for CLI UX
  - Informed by external authoritative guidance (web references)

  ────────────────────────────────────────
  SKILL PURPOSE
  ────────────────────────────────────────
  When invoked, the **Console UX Skill** should provide:

  1) A **formal UX specification** for CLI design
  2) A **guide to implement** those UX patterns in Python CLI apps
  3) A **list of reusable UI/UX components and utilities**
  4) A **validation and edge-case checklist**
  5) Advanced CLI rendering utilities and helper functions
  6) Adaptive behavior for different terminal environments (TTY vs non-TTY, NO_COLOR, etc.) :contentReference[oaicite:0]{index=0}

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill receives:
  - A target CLI application context (e.g., Todo app)
  - A specification of features to render
  - Environment detection flags (interactive vs script, NO_COLOR, etc.)

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The skill must output:

  1) **UX Design Specification**
     - Color palette strategy (ANSI escape sequences)
     - Typography/format conventions
     - Output formatting conventions
     - Animation guidelines

  2) **Component Library**
     - API for colored text
     - Structured list rendering
     - Status/alert blocks
     - Interactive prompts
     - Subtle animations (progress indicators, loaders)
     - Emoji/information icons (with optional toggles)

  3) **Implementation Template**
     - Python code templates for CLI UX
     - Environment detection/adapter utilities
     - Accessibility validators

  4) **Best Practice References**
     Include relevant sources such as:
     - ANSI color and feedback guidelines :contentReference[oaicite:1]{index=1}
     - CLI UX best practices (Iosup, Thoughtworks, OpenSource guides) :contentReference[oaicite:2]{index=2}
     - Accessibility and environment considerations (NO_COLOR, TERM=dumb) :contentReference[oaicite:3]{index=3}

  5) **Validation & Edge Cases**
     - Non-interactive pipe mode (disable animations/colors) :contentReference[oaicite:4]{index=4}
     - NO_COLOR respect :contentReference[oaicite:5]{index=5}
     - Unicode/Emoji support fallbacks
     - Terminals with limited escape support
     - Script/non-TTY environments

  ────────────────────────────────────────
  IMPLEMENTATION RULES
  ────────────────────────────────────────
  1. Use ANSI escape codes for color formatting and design systems.
  2. Respect environment flags for disabling color or animation.
  3. Provide fallback uris (e.g., plain text) for non-interactive usages.
  4. Do not assume a graphical TUI library — use terminal/ANSI only.
  5. Avoid over-animation — only subtle transitions appropriate for CLI.
  6. Ensure errors and warnings are clearly labeled, consistent, and accessible.

  ────────────────────────────────────────
  UX DESIGN PRINCIPLES TO INCLUDE
  ────────────────────────────────────────
  Include the following professional CLI UX concepts:

  A) **Color Usage Principles**
     - Use color for status indicators (success, warning, error, info) only
     - Do not rely on color alone for meaning — include text or icons
     - Offer optional color themes and respect `NO_COLOR` :contentReference[oaicite:6]{index=6}

  B) **Consistency & Hierarchy**
     - Commands, arguments, flags, and output blocks follow consistent scheme
     - Group sections with headers and spacing :contentReference[oaicite:7]{index=7}

  C) **Feedback & Interaction**
     - Provide structured feedback for user actions
     - Use progress indicators, spinners, and subtle animations appropriately
     - Detect non-TTY and fall back gracefully :contentReference[oaicite:8]{index=8}

  D) **Symbol & Icon Usage**
     - Standard Unicode symbols for success/failure/status
     - Use emojis optionally (learned by user toggle) :contentReference[oaicite:9]{index=9}

  E) **Adaptive Onboarding UX**
     - Show context-aware hints and help prompts
     - Provide immediate inline help on error or invalid input

  F) **Structured Output Components**
     - Bordered panels, headings, task lists
     - Tabular formats when appropriate
     - Indentation and white-space for clarity

  ────────────────────────────────────────
  EXAMPLE COMPONENTS TO DEFINE
  ────────────────────────────────────────
  - `ux.color_text(text, style)`
  - `ux.print_header(title)`
  - `ux.alert_success(msg)`
  - `ux.spinner(message)`
  - `ux.table(rows, columns)`
  - `ux.interactive_prompt(question)`
  - `ux.render_task_list(tasks)`

  ────────────────────────────────────────
  LEARNING REFERENCES (INCLUDE THESE IN THE SKILL)
  ────────────────────────────────────────
  Include authoritative CLI UX guidance references in the output design doc:

  1. **OpenSource.com CLI UX Best Practices**
     Key practices for color, input/output consistency and ordering of arguments :contentReference[oaicite:10]{index=10}

  2. **Command Line Interface Guidelines**
     Best CLI design conventions and interactive behavior flags, including NO_COLOR and non-TTY handling :contentReference[oaicite:11]{index=11}

  3. **Thoughtworks CLI UX Engineering Guide**
     Expressive flags, transparent actions, and help accessibility best-practices :contentReference[oaicite:12]{index=12}

  4. **Accessibility CLI Considerations**
     Respect environment variables like NO_COLOR and non-interactive modes to avoid harmful animations :contentReference[oaicite:13]{index=13}

  5. **CLI UX Recommendations from CLI-UX Designers**
     Principles of consistent messaging, symbol usage, and accessibility in CLI :contentReference[oaicite:14]{index=14}

  ────────────────────────────────────────
  OUTPUT FORMAT
  ────────────────────────────────────────
  Return a single combined output in Markdown with:

  # Console UX Skill

  ## 1. UX Specification
  ## 2. Components & APIs
  ## 3. Implementation Templates
  ## 4. Edge Cases & Validation
  ## 5. Best Practices & References
  ## 6. Learning References (with URLs)

  Ensure the output:
  - Is valid Markdown
  - Clear, formal, technical
  - Suitable for import into the code generator

  ────────────────────────────────────────
  BEGIN GENERATING THE Console UX Skill DEFINITION.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Console UX Skill" specification as requested. Here's what has been implemented:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/console-ux-skill/SKILL.md` - Contains comprehensive specification for CLI UX design
  - **Helper script**: `.claude/skills/console-ux-skill/scripts/ux_tester.sh` - Command-line tool for testing UX components
  - **Reference guide**: `.claude/skills/console-ux-skill/references/ux-patterns.md` - Detailed UX patterns and implementation examples
  - **Template asset**: `.claude/skills/console-ux-skill/assets/ux-components.json` - JSON schema for UX components

  ### Key Features
  1. **Advanced UX strategies**: Comprehensive approach to CLI design with color schemes, formatting, and subtle animations
  2. **Environment detection**: Respects NO_COLOR, TERM=dumb, and TTY vs non-TTY environments
  3. **Accessibility focus**: Includes proper fallbacks and text alternatives for visual elements
  4. **Component library**: Defines APIs for colored text, alerts, progress indicators, and interactive elements
  5. **Implementation templates**: Provides Python class templates and utility functions

  ### Core Components
  - **Color formatting system**: ANSI escape code implementation with environment detection
  - **Layout components**: Headers, panels, tables, and structured output
  - **Interactive elements**: Spinners, progress bars, prompts, and menus
  - **Status indicators**: Success, warning, error, and info messages with appropriate styling
  - **Environment adapter**: Handles different terminal capabilities gracefully

  ### Output Format
  - **Complete specification**: Detailed UX design guidelines with color palettes and formatting conventions
  - **Component APIs**: Well-defined interfaces for all UX components
  - **Implementation templates**: Ready-to-use Python code for CLI applications
  - **Validation checklist**: Edge case handling and accessibility considerations
  - **Best practice references**: Authoritative sources for CLI UX design

  The skill specification is ready to use and provides a complete blueprint for implementing premium-grade CLI user experiences with proper accessibility, environment detection, and professional design patterns.
outcome: "Console UX Skill successfully created with all required components: main SKILL.md specification, UX tester script, UX patterns reference, and component schema."
evaluation: "The skill meets all requirements: advanced UX strategies, environment detection, accessibility considerations, component library, implementation templates, and authoritative references."
---