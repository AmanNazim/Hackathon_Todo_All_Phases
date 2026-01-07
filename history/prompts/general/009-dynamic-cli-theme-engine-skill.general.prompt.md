---
id: 009
title: "Dynamic CLI Theme Engine Skill Creation"
stage: "general"
date_iso: "2026-01-04"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-dynamic-cli-theme-engine-skill"
labels: ["skill", "cli", "ux", "theme", "design"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/dynamic-cli-theme-engine/SKILL.md
  - .claude/skills/dynamic-cli-theme-engine/scripts/theme_validator.sh
  - .claude/skills/dynamic-cli-theme-engine/references/cli-ux-patterns.md
  - .claude/skills/dynamic-cli-theme-engine/assets/sample-themes.json
tests_yaml: |
  - "Skill specification verified for completeness"
  - "Script execution confirmed with theme validation"
  - "Sample themes validated with JSON format"
prompt_text: |
  You are a Senior Python Engineer, CLI UX Expert, and Spec-Driven Development Specialist.

  Your task is to create a reusable, advanced skill called:

  "DYNAMIC CLI THEME ENGINE SKILL"

  ────────────────────────────────────────
  PRIMARY OBJECTIVE
  ────────────────────────────────────────
  The skill must enable a Python CLI application to have **premium-level interactive themes**, including:

  - Advanced color schemes (foreground, background, accents)
  - Emoji-based indicators (subtle and informative)
  - Subtle animated transitions
  - Text formatting (bold, italic, underline, color highlights)
  - Theme-based layouts
  - Best practices in CLI design and usability
  - Dynamic theme selection and runtime customization
  - Intelligent asset generation and management (icons, text styles)
  - Advanced edge-case handling (terminal size, color support, OS differences)
  - Interactive CLI enhancement to feel "high-end" or "futuristic"
  - Adherence to top-tier CLI UX patterns (like Git, htop, pip, rich)

  The skill must **teach Claude how to implement advanced CLI themes** and include references, best practices, and examples for theme implementation.

  ────────────────────────────────────────
  LEARNING REFERENCES AND STRATEGIES (Top-Level Advanced CLI Resources)

  Claude must consider and integrate the following strategies, references, and inspiration:

  1. **Python CLI libraries and frameworks**
     - `Rich` library: https://rich.readthedocs.io/en/stable/
     - `Textual` library: https://textual.textualize.io/
     - `Prompt_toolkit`: https://python-prompt-toolkit.readthedocs.io/en/master/

  2. **Color Palettes and Schemes**
     - Solarized, Gruvbox, Dracula, Monokai
     - Terminal-friendly 16/256 color modes
     - Adaptive foreground/background contrast
     - Semantic color usage for status (success, warning, error, info)

  3. **Formatting & Layout Patterns**
     - Table-based output
     - Status bars
     - Hierarchical indentation
     - Panels, boxes, separators

  4. **Subtle Advanced Animations**
     - Loading spinners
     - Progress bars
     - Typing effects
     - Transition highlights between commands

  5. **Emoji Indicators**
     - Minimal, context-aware usage
     - Convey status without clutter
     - Examples: ✅, ❌, ⚠️, ℹ️, ✨

  6. **Advanced CLI UX Patterns**
     - Interactive menus
     - Prompt hints and contextual tips
     - Adaptive rendering based on terminal width/height
     - Responsive fallback for unsupported terminals
     - Theming consistency across all components

  7. **Assets Management**
     - Auto-download or generate icons/assets as needed
     - Can ask developer for giving assets if cannot auto-download or generate.
     - Local caching of assets
     - Integration with theme engine for dynamic application

  8. **Edge Cases**
     - Windows vs Linux vs MacOS terminal capabilities
     - Color depth support (16-color vs 256-color vs truecolor)
     - Terminal resize events
     - User-defined color overrides
     - Accessibility considerations (contrast, visibility)

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill must receive:

  2. User-selected theme preferences (optional)
  3. Current CLI context (menu, command, status)
  4. Optional custom asset URLs

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  1. Dynamic theme applied across CLI session
  2. Theme object exposing:
     - Colors
     - Formatting
     - Animation config
     - Emoji usage
     - Layout strategies
  3. Asset loader and manager
  4. CLI rendering API for other components
  5. Logs of theme application steps and fallbacks

  ────────────────────────────────────────
  ANALYSIS & IMPLEMENTATION RULES
  ────────────────────────────────────────
  - Must be reusable and maintainable
  - Must handle errors gracefully
  - Must fallback intelligently on unsupported terminals
  - Must allow runtime switching of themes
  - Must be compatible with hybrid menu + natural CLI interactions
  - Must include references to Rich, Textual, Prompt_toolkit, and modern CLI UX articles/examples
  - Must provide detailed theme design specifications
  - Must enumerate all edge cases
  - Must propose advanced strategies for premium CLI aesthetics

  ────────────────────────────────────────
  OUTPUT FORMAT
  ────────────────────────────────────────
  Return ONLY valid Markdown including:

  # Dynamic CLI Theme Engine Skill — Spec & Design

  ## 1. Skill Overview
  - Purpose
  - Scope
  - Benefits

  ## 2. Theme Strategies
  - Color palettes
  - Formatting strategies
  - Emoji usage policies
  - Animation patterns
  - Layout guidelines

  ## 3. Implementation Guidelines
  - CLI API design
  - Terminal capability handling
  - Theme objects & assets
  - Runtime dynamic theme application
  - Integration with commands

  ## 4. Learning References
  - Links to top CLI libraries
  - Examples of advanced CLI apps
  - Reference color palettes
  - Advanced UX guidelines

  ## 5. Edge Cases
  - Detailed edge case table
  - Handling strategies

  ## 6. Recommended Enhancements
  - Optional improvements
  - UX refinements
  - Accessibility considerations

  ## 7. Output Examples
  - Sample CLI renderings
  - Example color themes
  - Example emoji usage
  - Animated transition demo descriptions

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  - The skill is used to make a Python CLI app to look **premium** and highly interactive
  - Advanced theme strategies and designs are applied consistently
  - Edge cases and terminal differences are handled
  - Learning references and best practices are documented
  - Ensures the skill is reusable across all CLI modules

  BEGIN SKILL DESIGN NOW.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Dynamic CLI Theme Engine Skill" with all required components:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/dynamic-cli-theme-engine/SKILL.md` - Contains comprehensive specification for dynamic CLI theming
  - **Helper script**: `.claude/skills/dynamic-cli-theme-engine/scripts/theme_validator.sh` - Command-line tool for validating theme configurations
  - **Reference guide**: `.claude/skills/dynamic-cli-theme-engine/references/cli-ux-patterns.md` - Detailed CLI UX patterns and best practices
  - **Sample assets**: `.claude/skills/dynamic-cli-theme-engine/assets/sample-themes.json` - Sample theme configurations for reference

  ### Key Features
  1. **Advanced theme engine**: Enables premium-level interactive themes with color schemes, emoji indicators, and animations
  2. **Comprehensive styling**: Supports semantic color usage, hierarchical formatting, and responsive layouts
  3. **Cross-platform compatibility**: Handles different terminal capabilities and OS differences
  4. **Accessibility compliance**: Includes contrast optimization and screen reader compatibility
  5. **Runtime customization**: Supports dynamic theme switching and user preferences

  ### Core Components
  - **Theme strategies**: Color palettes (Solarized, Gruvbox, Dracula, etc.), formatting approaches, emoji policies
  - **Implementation guidelines**: API design, terminal capability handling, asset management
  - **Learning references**: Links to Rich, Textual, Prompt_toolkit libraries and advanced CLI apps
  - **Edge case handling**: Comprehensive table of terminal compatibility issues with solutions
  - **UX enhancements**: Accessibility considerations and recommended improvements

  ### Sample Themes
  - **Dark Modern**: Modern dark theme with blue accents
  - **Light Clean**: Clean light theme with professional styling
  - **Solarized Dark**: Classic Solarized color scheme
  - **Dracula**: Popular Dracula theme with vibrant colors

  The skill specification is ready to use and provides a complete blueprint for implementing sophisticated CLI UX patterns that match the quality of top-tier applications like Git, htop, and pip. It enables Python CLI applications to achieve premium-level interactive themes with advanced color schemes, emoji indicators, subtle animations, and responsive layouts.
outcome: "Dynamic CLI Theme Engine Skill successfully created with all required components: main SKILL.md specification, theme validator script, CLI UX patterns reference, and sample theme configurations."
evaluation: "The skill meets all requirements: advanced theme strategies, cross-platform compatibility, accessibility compliance, comprehensive edge case handling, and premium CLI aesthetics."
---