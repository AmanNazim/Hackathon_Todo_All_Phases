---
id: 010
title: "Console UI Skill Creation"
stage: "general"
date_iso: "2026-01-04"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-console-ui-skill"
labels: ["skill", "ui", "cli", "console", "design"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/console-ui-skill/SKILL.md
  - .claude/skills/console-ui-skill/scripts/ui_tester.sh
  - .claude/skills/console-ui-skill/references/ui-patterns.md
  - .claude/skills/console-ui-skill/assets/ui-components.json
tests_yaml: |
  - "Skill specification verified for completeness"
  - "Script execution confirmed"
prompt_text: |
  You are an expert Software Engineer and Senior CLI UI Architect tasked with creating a reusable internal skill named:

  **“Console UI Skill”**

  This skill will teach an LLM how to design, specify, and implement **advanced, premium CLI user interfaces** for Python console applications.

  ────────────────────────────────────────
  PRIMARY PURPOSE
  ────────────────────────────────────────
  The Console UI Skill must instruct Claude Code (or other agents) in how to implement:

  ✔ Advanced CLI UI strategies
  ✔ Advanced CLI UI designs
  ✔ Advanced CLI UI implementations
  ✔ Modern color schemes
  ✔ Best thematic choices and palettes
  ✔ Appropriate formatting standards
  ✔ Subtle animated transitions
  ✔ Subtle emoji indicators
  ✔ Interactive CLI behaviors

  It must produce:
  - Detailed design guidelines
  - Implementation techniques
  - Code patterns
  - Best practices including UX patterns
  - References to authoritative CLI UI resources

  This is NOT a simple design spec — this is a **comprehensive CLI UI knowledge base and instruction generation skill** that can be reused across phases.

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill receives:
  - The name of the CLI app context (e.g., "todo console app")
  - Optional existing UI style guidelines
  - Optional CLI command grammar

  The skill must output a **structured Markdown guide** including:
  - UI strategies
  - UI design components
  - Implementation guidelines
  - Library recommendations
  - Edge cases
  - Visual formatting rules
  - Accessibility notes
  - Best practices references

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The output MUST be valid Markdown with the following sections:

  # Console UI Skill Documentation

  ## 1. Introduction
  - Purpose of the skill
  - Scope
  - When to apply

  ## 2. CLI UI Design Principles
  - Clarity, consistency, discoverability
  - UX best practices for CLIs (verbal clarity, argument order, flags) :contentReference[oaicite:0]{index=0}
  - Information hierarchy
  - Feedback timing

  ## 3. Interaction Models
  - Hybrid menu + natural commands
  - Progressive disclosure
  - Error-aware interaction flows

  ## 4. Color Schemes & Themes
  - Color palettes and semantic meanings (e.g., green for success, red for error) :contentReference[oaicite:1]{index=1}
  - Theme strategy (light/dark, accessibility, contrast)
  - Library support (Rich, colorama) :contentReference[oaicite:2]{index=2}

  ## 5. Output Formatting & Layout
  - Tables, panels, lists
  - Consistent spacing
  - Font effects (bold, underline)
  - Column alignment
  - Screen size sensitivity (responsive layout) :contentReference[oaicite:3]{index=3}

  ## 6. Animated Transitions & Feedback
  - Progress indicators (spinners, loading bars)
  - Subtle timing for UX delight
  - When NOT to animate (TTY detection) :contentReference[oaicite:4]{index=4}

  ## 7. Emoji & Iconography Usage
  - When to use emojis (success, warning, info) :contentReference[oaicite:5]{index=5}
  - Accessibility considerations
  - Turn-off flags

  ## 8. Interactive Prompts & Input Assistance
  - Auto-suggestions
  - Confirmation dialogs
  - Intelligent error feedback :contentReference[oaicite:6]{index=6}

  ## 9. Accessibility Considerations
  - Graceful degradation when colors/Unicode unsupported
  - Screen reader friendly output
  - Toggleable verbosity

  ## 10. Edge Cases & CLI UI Failures
  - Terminal width limitations
  - Unsupported terminals
  - UI chattiness controls
  - JSON/text output toggles

  ## 11. Recommended Libraries & Tools (Python)
  List of best Python tools for enhanced CLI UI:

  ### Rendering & Layout
  - **rich** – high level formatting and styles :contentReference[oaicite:7]{index=7}
  - **textual** – interactive widget-based UIs :contentReference[oaicite:8]{index=8}

  ### Prompting & Interaction
  - **Prompt Toolkit** – advanced input features :contentReference[oaicite:9]{index=9}
  - **questionary / InquirerPy** – interactive prompts :contentReference[oaicite:10]{index=10}

  ### Basic UI Helpers
  - `colorama`, `cli-ui` :contentReference[oaicite:11]{index=11}
  - Animated indicators and progress libraries :contentReference[oaicite:12]{index=12}

  ## 12. Detailed Implementation Patterns
  - Theme provider pattern
  - Centralized renderer module
  - UI context abstraction
  - Output builder functions
  - Interactive flow controllers

  ## 13. Code Snippet Templates
  Provide reusable CLI UI code templates using recommended libraries.

  ## 14. Learning References & Documentation
  Include links and references to authoritative CLI UI design resources and best practices:
  - CLI UX patterns and best practices guidelines :contentReference[oaicite:13]{index=13}
  - Python CLI UI articles and library docs (Rich, Prompt Toolkit) :contentReference[oaicite:14]{index=14}
  - Advanced CLI design principles publications :contentReference[oaicite:15]{index=15}

  ────────────────────────────────────────
  ANALYSIS GUARANTEES
  ────────────────────────────────────────
  The skill must:
  1. Focus on UX and UI design quality
  2. Avoid hallucinations
  3. Provide reasoned, evidence-backed UI heuristics
  4. Include references
  5. Use clear, non-ambiguous instructions
  6. Align with professional CLI design standards

  ────────────────────────────────────────
  OUTPUT STYLE
  ────────────────────────────────────────
  - Structured Markdown
  - Technical language
  - Example code
  - Visual layouts
  - Best practice patterns
  - Library citations
  - Real CLI UI guidelines
  - Categorized edge cases

  ────────────────────────────────────────
  EXCLUDED CONTENT
  ────────────────────────────────────────
  ❌ No API implementation for anything outside of CLI UI
  ❌ No backend logic generation
  ❌ No application business logic
  ❌ No non-CLI UI references

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  The generated skill must enable:
  - Premium CLI UI designs and implementations
  - Reuse across multiple CLI apps
  - High readability documentation
  - Professional UI output standards
  - Automatic learning references for Claude Code

  Begin generating the **Console UI Skill documentation** now.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Console UI Skill" specification as requested. Here's what has been implemented:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/console-ui-skill/SKILL.md` - Contains comprehensive documentation for CLI UI design
  - **Helper script**: `.claude/skills/console-ui-skill/scripts/ui_tester.sh` - Command-line tool for testing UI components
  - **Reference guide**: `.claude/skills/console-ui-skill/references/ui-patterns.md` - Detailed UI patterns and implementation examples
  - **Template asset**: `.claude/skills/console-ui-skill/assets/ui-components.json` - JSON schema for UI components

  ### Key Features
  1. **Advanced UI strategies**: Comprehensive approach to CLI design with color schemes, formatting, and subtle animations
  2. **Environment detection**: Respects NO_COLOR, TERM=dumb, and TTY vs non-TTY environments
  3. **Accessibility focus**: Includes proper fallbacks and text alternatives for visual elements
  4. **Component library**: Defines APIs for colored text, alerts, progress indicators, and interactive elements
  5. **Implementation templates**: Provides Python code templates for CLI applications
  6. **Library recommendations**: Includes guidance on using Rich, Textual, Prompt Toolkit, and other libraries

  ### Core Components
  - **Color formatting system**: ANSI escape code implementation with environment detection
  - **Layout components**: Headers, panels, tables, and structured output
  - **Interactive elements**: Spinners, progress bars, prompts, and menus
  - **Status indicators**: Success, warning, error, and info messages with appropriate styling
  - **Environment adapter**: Handles different terminal capabilities gracefully

  ### Output Format
  - **Complete specification**: Detailed UI design guidelines with color palettes and formatting conventions
  - **Component APIs**: Well-defined interfaces for all UI components
  - **Implementation templates**: Ready-to-use Python code for CLI applications
  - **Validation checklist**: Edge case handling and accessibility considerations
  - **Best practice references**: Authoritative sources for CLI UI design

  The skill specification is ready to use and provides a complete knowledge base for implementing premium CLI user interfaces with proper accessibility, environment detection, and professional design patterns.
outcome: "Console UI Skill successfully created with all required components: main SKILL.md documentation, UI tester script, UI patterns reference, and component schema."
evaluation: "The skill meets all requirements: advanced UI strategies, environment detection, accessibility considerations, component library, implementation templates, library recommendations, and authoritative references."
---