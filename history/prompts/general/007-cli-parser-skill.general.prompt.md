---
id: 007
title: "CLI Parser Skill Creation"
stage: "general"
date_iso: "2026-01-03"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-cli-parser-skill"
labels: ["skill", "cli", "parsing", "specification"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/cli-parser-skill/SKILL.md
  - .claude/skills/cli-parser-skill/scripts/parse_tester.sh
  - .claude/skills/cli-parser-skill/references/parsing-rules.md
  - .claude/skills/cli-parser-skill/assets/parser-schema.json
tests_yaml: |
  - "Skill specification verified for completeness"
  - "Script execution confirmed"
prompt_text: |
  You are a Senior Language Systems Engineer and Spec-Driven Architect.

  Your task is to design a reusable internal skill named:

  "CLI Interaction Parser Skill"

  This skill defines HOW a universal command parsing engine must be designed, specified, and implemented across multiple interaction surfaces.

  This is NOT a feature implementation.
  This is a SKILL SPECIFICATION that teaches Claude Code how to build and reuse a parsing engine consistently.

  ────────────────────────────────────────
  SKILL PURPOSE
  ────────────────────────────────────────
  The CLI Interaction Parser Skill is a universal natural-language-to-action parsing system.

  It acts as the "brainstem" of the system by translating raw user input into structured, machine-readable command intents.

  This skill MUST be designed to be reusable across:
  - Command-line interfaces (hybrid menu + natural input)
  - Conversational interfaces
  - Tool routing layers
  - Service orchestration layers

  The skill must be deterministic, explainable, and rule-driven (not speculative).

  ────────────────────────────────────────
  NON-NEGOTIABLE DESIGN PRINCIPLES
  ────────────────────────────────────────
  1. Parsing must be deterministic and rule-based.
  2. No probabilistic guessing without user confirmation.
  3. No hallucinated commands or actions.
  4. All parsing outputs must be explainable.
  5. Ambiguity must be surfaced, not hidden.
  6. Parsing logic must be decoupled from execution logic.
  7. Skill must remain implementation-agnostic but technically precise.

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The parser accepts:
  - Raw user input (string)
  - Optional interaction context:
    - current mode (menu / free-text)
    - previous command
    - known command vocabulary
    - active entities (e.g., task IDs)

  The skill must assume inputs can be:
  - incomplete
  - abbreviated
  - grammatically incorrect
  - mixed-mode (menu numbers + text)
  - partially structured

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The parser MUST output a structured parsing result with:

  - intent_name
  - intent_confidence (rule-based, not probabilistic)
  - normalized_command
  - extracted_entities
  - missing_information (if any)
  - ambiguity_flags
  - suggested_clarifications (if required)
  - parse_status (success | partial | ambiguous | invalid)

  All outputs must be serializable and human-readable.

  ────────────────────────────────────────
  MANDATORY PARSING PIPELINE
  ────────────────────────────────────────
  The skill MUST define a multi-stage parsing pipeline:

  ### Stage 1: Input Normalization
  - Trim whitespace
  - Normalize casing
  - Collapse repeated spaces
  - Preserve quoted strings
  - Detect numeric shortcuts (e.g., "1" for menu actions)

  ### Stage 2: Tokenization
  - Split input into tokens
  - Preserve semantic units (quoted phrases, IDs)
  - Detect command verbs vs parameters

  ### Stage 3: Intent Classification (Rule-Based)
  - Match tokens against known command grammar
  - Support verb synonyms (e.g., add/create/new)
  - Support shorthand commands (e.g., "a milk")
  - Support menu index mapping

  ### Stage 4: Entity Extraction
  - Extract identifiers (IDs, indices)
  - Extract titles and descriptions
  - Detect flags and modifiers
  - Preserve raw entity text

  ### Stage 5: Validation & Completeness Check
  - Verify required entities exist
  - Detect missing arguments
  - Detect conflicting parameters
  - Detect invalid entity references

  ### Stage 6: Ambiguity Resolution
  - Identify multiple possible intents
  - Generate clarification prompts
  - Avoid auto-execution when ambiguous

  ### Stage 7: Final Parse Result Assembly
  - Produce final structured output
  - Include reasoning metadata
  - Include parse confidence explanation

  ────────────────────────────────────────
  EDGE CASES (MANDATORY)
  ────────────────────────────────────────
  The skill MUST explicitly define handling for:

  - Empty input
  - Unknown commands
  - Partial commands
  - Repeated commands
  - Conflicting arguments
  - Invalid identifiers
  - Accidental destructive commands
  - Mixed numeric + text input
  - Quoted vs unquoted text
  - User corrections (e.g., "no, I meant…")

  Each edge case must:
  - Be detected
  - Be classified
  - Produce a safe response
  - Never cause silent failure

  ────────────────────────────────────────
  ERROR & FEEDBACK STRATEGY
  ────────────────────────────────────────
  The parser MUST:
  - Never crash on invalid input
  - Never silently discard input
  - Always explain why parsing failed
  - Suggest valid alternatives
  - Preserve user intent when possible

  Error feedback must be:
  - Contextual
  - Minimal
  - Actionable
  - Non-judgmental

  ────────────────────────────────────────
  EXTENSIBILITY REQUIREMENTS
  ────────────────────────────────────────
  The skill MUST define:
  - How new commands are added
  - How synonyms are registered
  - How grammar rules are extended
  - How the parser integrates with routers
  - How the same parser logic can be reused in non-CLI environments

  No hard-coding of commands inside logic.
  Command definitions must be declarative.

  ────────────────────────────────────────
  DOCUMENTATION OUTPUT (MANDATORY)
  ────────────────────────────────────────
  Claude MUST generate a Markdown skill document containing:

  1. Skill Overview
  2. Design Philosophy
  3. Input & Output Schema
  4. Parsing Pipeline Architecture
  5. Command Grammar Model
  6. Entity Extraction Rules
  7. Ambiguity Resolution Strategy
  8. Edge Case Handling Matrix
  9. Error & Feedback Guidelines
  10. Extensibility Strategy
  11. Non-Goals & Explicit Limitations

  ────────────────────────────────────────
  FORBIDDEN BEHAVIOR
  ────────────────────────────────────────
  ❌ No AI guessing
  ❌ No fuzzy execution without confirmation
  ❌ No implementation shortcuts
  ❌ No phase-specific assumptions
  ❌ No hard-coded application logic
  ❌ No UI rendering logic

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  This skill is successful if:
  - It can drive a CLI without coupling to business logic
  - It can be reused across interaction layers
  - It produces predictable, inspectable results
  - It reduces downstream error handling complexity
  - It aligns with Spec-Driven Development discipline

  BEGIN GENERATING THE CLI Interaction Parser Skill DOCUMENTATION NOW.
response_text: |
  ## Summary of Implementation

  I have successfully created the "CLI Interaction Parser Skill" specification as requested. Here's what has been implemented:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/cli-parser-skill/SKILL.md` - Contains comprehensive specification for the CLI Interaction Parser Skill
  - **Helper script**: `.claude/skills/cli-parser-skill/scripts/parse_tester.sh` - Command-line tool for demonstrating parsing pipeline stages
  - **Reference guide**: `.claude/skills/cli-parser-skill/references/parsing-rules.md` - Detailed parsing rules and examples
  - **Template asset**: `.claude/skills/cli-parser-skill/assets/parser-schema.json` - JSON schema for parse result structure

  ### Key Features
  1. **Universal parsing engine**: Designed to work across CLI, conversational interfaces, and service orchestration layers
  2. **Deterministic and rule-based**: No probabilistic guessing without user confirmation
  3. **Extensible architecture**: Supports declarative command definitions and grammar extensions
  4. **Comprehensive edge case handling**: Covers all specified edge cases with safe responses
  5. **Clear output schema**: Well-defined structure for parse results with confidence levels

  ### Core Components
  - **7-stage parsing pipeline**: Input normalization, tokenization, intent classification, entity extraction, validation, ambiguity resolution, and result assembly
  - **Command grammar model**: Declarative format for defining commands, synonyms, and patterns
  - **Entity extraction rules**: Comprehensive handling of IDs, titles, flags, dates, and other entities
  - **Ambiguity resolution strategy**: Clear approach to handling uncertain inputs safely
  - **Error and feedback guidelines**: Contextual, minimal, actionable, non-judgmental feedback

  ### Output Format
  - **Structured parse results**: Complete with intent, confidence, entities, and status
  - **JSON schema**: Formal definition of the expected output format
  - **Reasoning metadata**: Explanation of parsing decisions for transparency

  The skill specification is ready to use and provides a complete blueprint for implementing a universal CLI parsing engine that can be reused across multiple interaction surfaces while maintaining deterministic, explainable, and safe parsing behavior.

  ### Answer to Implementation Question
  Yes, it's definitely possible to create a CLI parser based on the logic defined in the specification without using external tools or APIs. The CLI parser can be implemented using just the core programming language's built-in string manipulation, pattern matching, and data structures. All the parsing stages can be implemented with basic programming constructs.
outcome: "CLI Interaction Parser Skill successfully created with all required components: main SKILL.md specification, parser tester script, parsing rules reference, and JSON schema."
evaluation: "The skill meets all requirements: comprehensive specification with 7-stage parsing pipeline, deterministic rule-based approach, extensibility model, and clear output schema."
---