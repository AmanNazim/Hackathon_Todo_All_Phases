---
name: cli-parser-skill
description: Defines a universal natural-language-to-action parsing system that acts as the "brainstem" of the system by translating raw user input into structured, machine-readable command intents. Designed to be reusable across CLI, conversational interfaces, and service orchestration layers with deterministic, explainable, rule-driven parsing.
---

# CLI Interaction Parser Skill

This skill defines HOW a universal command parsing engine must be designed, specified, and implemented across multiple interaction surfaces.

This is NOT a feature implementation.
This is a SKILL SPECIFICATION that teaches Claude Code how to build and reuse a parsing engine consistently.

## 1. Skill Overview

The CLI Interaction Parser Skill is a universal natural-language-to-action parsing system.

It acts as the "brainstem" of the system by translating raw user input into structured, machine-readable command intents.

This skill MUST be designed to be reusable across:
- Command-line interfaces (hybrid menu + natural input)
- Conversational interfaces
- Tool routing layers
- Service orchestration layers

The skill must be deterministic, explainable, and rule-driven (not speculative).

## 2. Design Philosophy

### Core Principles
1. **Deterministic parsing**: All parsing must be rule-based with predictable outcomes
2. **No probabilistic guessing**: No guessing without explicit user confirmation
3. **No hallucinated commands**: Only recognized commands can be executed
4. **Explainable outputs**: All parsing results must be transparent and understandable
5. **Ambiguity surfacing**: Uncertainty must be clearly communicated to users
6. **Decoupled logic**: Parsing logic must be separate from execution logic
7. **Implementation-agnostic**: Design must work across different tech stacks

### Safety First Approach
- Never execute ambiguous commands without confirmation
- Always validate required information is present
- Provide clear feedback when input is incomplete or invalid
- Maintain user intent preservation throughout the parsing process

## 3. Input & Output Schema

### Input Contract
The parser accepts:
- `raw_input` (string): Raw user input
- `context` (optional object):
  - `current_mode` (string): Current interaction mode (menu/free-text)
  - `previous_command` (string): Previous command for context
  - `command_vocabulary` (array): List of known commands
  - `active_entities` (object): Currently available entities (e.g., task IDs)

### Output Contract
The parser MUST output a structured parsing result:

```json
{
  "intent_name": "string",
  "intent_confidence": "high|medium|low|none",
  "normalized_command": "string",
  "extracted_entities": {
    "ids": ["string"],
    "titles": ["string"],
    "descriptions": ["string"],
    "flags": ["string"],
    "parameters": {"key": "value"}
  },
  "missing_information": ["string"],
  "ambiguity_flags": ["string"],
  "suggested_clarifications": ["string"],
  "parse_status": "success|partial|ambiguous|invalid",
  "parse_reasoning": "string"
}
```

## 4. Parsing Pipeline Architecture

### Stage 1: Input Normalization
- Trim leading/trailing whitespace
- Normalize casing (optional, configurable)
- Collapse repeated spaces
- Preserve quoted strings as single tokens
- Detect numeric shortcuts (e.g., "1" for menu actions)
- Remove common filler words (optional)

### Stage 2: Tokenization
- Split input into semantic tokens
- Preserve quoted phrases as single tokens
- Separate command verbs from parameters
- Identify numeric identifiers
- Maintain original token positions for error reporting

### Stage 3: Intent Classification (Rule-Based)
- Match token sequences against known command patterns
- Support verb synonyms (e.g., add/create/new)
- Support shorthand commands (e.g., "a milk" → add "milk")
- Support menu index mapping
- Use exact match prioritization over fuzzy matching

### Stage 4: Entity Extraction
- Extract numeric identifiers
- Extract quoted strings as titles/descriptions
- Identify command flags and modifiers
- Parse date/time formats
- Extract positional parameters
- Preserve raw entity text for validation

### Stage 5: Validation & Completeness Check
- Verify required entities exist for the detected intent
- Detect missing required arguments
- Identify conflicting parameters
- Validate entity format and existence
- Check command prerequisites

### Stage 6: Ambiguity Resolution
- Identify when multiple intents match
- Generate specific clarification prompts
- Prioritize most common or most specific matches
- Avoid auto-execution when ambiguous
- Provide disambiguation options

### Stage 7: Final Parse Result Assembly
- Produce final structured output
- Include reasoning metadata
- Calculate parse confidence based on rule matches
- Format error messages for user consumption

## 5. Command Grammar Model

### Grammar Definition Structure
Commands are defined using a declarative grammar model:

```json
{
  "command_name": "add_task",
  "patterns": [
    "add [title]",
    "create [title]",
    "new [title]",
    "a [title]"
  ],
  "required_entities": ["title"],
  "optional_entities": ["description", "due_date"],
  "flags": ["--urgent", "--private"],
  "synonyms": ["create_task", "make_task"]
}
```

### Pattern Matching Rules
- Exact match takes precedence over partial match
- Short forms must map to full forms unambiguously
- Parameter placeholders use square brackets [parameter]
- Optional elements use parentheses (optional)
- Multiple alternatives use pipe syntax (this|that)

### Command Registration
- Commands registered declaratively, not hardcoded in logic
- Support for dynamic command loading
- Versioning for command definitions
- Validation of command definition schemas

## 6. Entity Extraction Rules

### Identifier Extraction
- Numeric IDs: \d+ patterns
- Alphanumeric IDs: [a-zA-Z0-9_]+ patterns
- UUID patterns: Standard UUID format detection
- Menu indices: Direct numeric input matching

### Text Extraction
- Quoted strings: Preserve exact content within quotes
- Unquoted strings: Normalize whitespace and casing
- Multi-word titles: Group consecutive non-command tokens
- Escaped characters: Handle escaped quotes and special characters

### Flag Extraction
- Short flags: -f format
- Long flags: --flag-name format
- Flag values: Support for --flag=value syntax
- Boolean flags: Flags without values

### Date/Time Extraction
- Relative dates: "tomorrow", "next week"
- Absolute dates: "2023-12-25", "Dec 25"
- Time formats: "14:30", "2:30 PM"
- Duration patterns: "in 2 hours", "for 30 minutes"

## 7. Ambiguity Resolution Strategy

### Ambiguity Detection
- Multiple pattern matches for same input
- Insufficient information for required entities
- Conflicting parameter combinations
- Unclear references to entities

### Resolution Approaches
1. **Prompt for clarification**: Ask user to specify intent
2. **Provide options**: List possible interpretations
3. **Use context**: Leverage previous commands or current state
4. **Default to safe**: Choose least destructive interpretation
5. **Ask for confirmation**: Verify user intent before execution

### Confidence Scoring
- **High**: Exact pattern match with all required entities
- **Medium**: Pattern match with some ambiguity or missing optional entities
- **Low**: Partial match requiring significant assumptions
- **None**: No matching patterns found

## 8. Edge Case Handling Matrix

| Edge Case | Detection | Response | Safety Measure |
|-----------|-----------|----------|----------------|
| Empty input | Length check | Return menu or help | Prevent silent failures |
| Unknown commands | No pattern matches | Suggest similar commands | Guide user to valid options |
| Partial commands | Missing required entities | Request missing information | Preserve user intent |
| Repeated commands | Same command multiple times | Confirm before executing | Prevent accidental duplication |
| Conflicting args | Validation failure | Explain conflict, suggest resolution | Maintain data integrity |
| Invalid IDs | ID format validation | Explain valid format | Prevent invalid operations |
| Destructive commands | Delete/trash patterns | Require confirmation | Prevent accidental data loss |
| Mixed input | Numeric + text patterns | Prioritize based on context | Maintain predictable behavior |
| Quoted text | Quote detection | Preserve exact content | Maintain user's intended text |
| User corrections | "no, I meant..." patterns | Parse correction intent | Handle user feedback gracefully |

## 9. Error & Feedback Guidelines

### Error Handling Principles
- Never crash on invalid input
- Never silently discard user input
- Always explain why parsing failed
- Always suggest valid alternatives
- Preserve user's original intent when possible

### Feedback Characteristics
- **Contextual**: Error messages relate to current state
- **Minimal**: Only provide necessary information
- **Actionable**: Include clear next steps
- **Non-judgmental**: Avoid blaming user for input errors

### Error Message Format
- Clear description of what went wrong
- Specific example of correct format
- Suggestion for alternative approaches
- Reference to available commands or help

## 10. Extensibility Strategy

### Adding New Commands
1. Define command in declarative grammar format
2. Register command with parser
3. Implement corresponding handler function
4. Add to command vocabulary

### Synonym Registration
- Define synonyms in command grammar
- Map to canonical command name
- Maintain backward compatibility
- Support for user-defined aliases

### Grammar Extension
- Modular grammar components
- Support for domain-specific commands
- Validation of extended grammars
- Conflict detection for overlapping patterns

### Integration with Routers
- Standardized parse result format
- Consistent error handling
- Context propagation
- Asynchronous command handling support

### Non-CLI Environment Reuse
- Platform-agnostic parsing logic
- Configurable input/output formats
- Support for different interaction patterns
- Adaptable to different user interfaces

## 11. Non-Goals & Explicit Limitations

### What This Skill Does NOT Do
- Execute commands (parsing only)
- Render UI elements
- Store or manage data
- Implement business logic
- Perform fuzzy matching without user confirmation
- Generate AI responses beyond parsing
- Handle application-specific workflows

### Explicit Limitations
- Cannot handle completely novel command structures without registration
- Requires predefined command vocabulary
- Does not perform semantic analysis beyond entity extraction
- Does not handle complex nested command structures
- Limited to rule-based pattern matching (no ML/AI guessing)

## Helper Tools

The skill includes:
- `scripts/parse_tester.sh` - Command-line helper for testing parse scenarios
- `references/parsing-rules.md` - Detailed parsing rules and examples
- `assets/parser-schema.json` - JSON schema for parse results