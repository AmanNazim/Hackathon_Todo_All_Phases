---
name: task-normalization
description: Converts arbitrary natural-language task phrases into clean, structured task objects with title, description, priority, tags, and null placeholders for temporal fields. Performs normalization without hallucination or interpretation beyond the text.
---

# Task Normalization Skill

This skill converts arbitrary natural-language task phrases into clean, structured task objects with title, description, priority, tags, and null placeholders for temporal fields. Performs normalization without hallucination or interpretation beyond the text.

## 1. Skill Overview

The Task Normalization Skill converts arbitrary natural-language task phrases into a clean, structured canonical task object.

Example:

Input:
"remind me to pay bills before Sunday morning"

Normalized Output:
```json
{
  "title": "Pay bills",
  "description": "Before Sunday morning",
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

IMPORTANT:
- This skill performs NORMALIZATION, not interpretation beyond the text.
- It must NOT invent dates, priorities, tags, or meanings not explicitly present.
- Fields such as due_date and recurrence MUST remain null in current phases.
- Future upgrades must be clearly marked but NOT implemented.

## 2. Purpose & Non-Goals

### Purpose
- Normalize free-form user input into structured task representations
- Extract meaningful task components from natural language
- Maintain consistency across task inputs
- Preserve user intent while standardizing format

### Non-Goals
- Interpret meaning beyond explicit text
- Convert temporal references to actual dates
- Split multiple tasks into separate objects
- Perform AI inference beyond defined rules
- Generate code or execute tasks

## 3. Input / Output Schema

### Input Contract
- `input_text` (string): A single free-form string representing a user's task intent

The input may include:
- Polite language ("please", "remind me")
- Temporal hints ("tomorrow", "before Sunday")
- Redundant phrasing
- Ambiguous wording
- Multiple clauses
- Noise words

### Output Contract
The output MUST be a structured task object with the following fixed schema:

```json
{
  "title": "string (mandatory)",
  "description": "string | null",
  "priority": "one of [\"low\", \"normal\", \"high\"]",
  "tags": "list of strings",
  "due_date": "null (reserved for future phase)",
  "recurrence": "null (reserved for future phase)"
}
```

## 4. Normalization Rules

### 1. Title Extraction
- The title must be:
  - Action-oriented
  - Short (ideally 2–6 words)
  - Free of filler words
- Remove:
  - Polite prefixes ("remind me", "please")
  - Temporal qualifiers
  - Redundant verbs
- Capitalize appropriately.

### 2. Description Extraction
- Description should capture:
  - Temporal hints
  - Contextual clauses
  - Additional clarifying phrases
- If no meaningful description exists, set to null.

### 3. Priority Assignment
- Default priority is "normal".
- Priority may ONLY change if explicit indicators exist:
  - "urgent", "asap" → high
  - "whenever", "optional" → low
- No inferred urgency allowed.

### 4. Tags Extraction
- Tags must be:
  - Explicitly mentioned topics or nouns
  - Lowercase
  - Singular
- Do NOT infer tags.
- If none exist, return an empty list.

### 5. Temporal Handling
- Temporal phrases must:
  - Be moved into description
  - NOT converted into actual dates
- due_date must remain null.

### 6. Ambiguity Handling
- If input is vague:
  - Still produce a best-effort normalized task
  - Add ambiguity notes into description if needed
- Do NOT reject input.

## 5. Priority Resolution Rules

### Priority Indicators
- **High Priority**: "urgent", "asap", "immediately", "emergency", "critical", "important"
- **Low Priority**: "whenever", "optional", "maybe", "if possible", "low priority"
- **Normal Priority**: Default for all other inputs

### Priority Resolution Process
1. Scan input for explicit priority indicators
2. If found, assign appropriate priority level
3. If none found, assign "normal"
4. Do not infer priority from context

## 6. Edge Case Matrix

| Edge Case | Input | Expected Output | Handling Strategy |
|-----------|-------|-----------------|-------------------|
| Empty Input | "" | Minimal task with empty title | Set title to "Empty task", description to null |
| Only Verb | "call" | Action-oriented title | Set title to "Call", description to null |
| Only Noun | "groceries" | Interpret as action | Set title to "Get groceries", description to null |
| Long Input | Very long sentence | Extract core task | Focus on primary action, move rest to description |
| Multiple Tasks | "do X and Y" | Single normalized task | Normalize first task, add second to description |
| Contradictory | "urgent optional" | Resolve conflict | Prioritize explicit indicators, document conflict |
| Repeated Words | "call call the doctor" | Remove redundancy | Normalize to "Call the doctor" |
| Non-actionable | "hello world" | Interpret as best possible | Set to "Say hello", description: "to world" |
| With Emojis | "buy 🛒 milk" | Extract text meaning | Set title to "Buy milk", tags: ["shopping"] |
| With Numbers | "buy 3 apples" | Extract quantities | Set title to "Buy apples", description: "3 apples" |

## 7. Examples

### Example 1: Basic Task
Input: "buy milk"
Output:
```json
{
  "title": "Buy milk",
  "description": null,
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 2: With Temporal Hint
Input: "remind me to pay bills before Sunday morning"
Output:
```json
{
  "title": "Pay bills",
  "description": "Before Sunday morning",
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 3: High Priority
Input: "urgent: fix the bug"
Output:
```json
{
  "title": "Fix the bug",
  "description": null,
  "priority": "high",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 4: With Polite Language
Input: "please remind me to call mom"
Output:
```json
{
  "title": "Call mom",
  "description": null,
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 5: With Description
Input: "buy groceries for dinner party"
Output:
```json
{
  "title": "Buy groceries",
  "description": "For dinner party",
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 6: With Tags
Input: "buy groceries (shopping)"
Output:
```json
{
  "title": "Buy groceries",
  "description": null,
  "priority": "normal",
  "tags": ["shopping"],
  "due_date": null,
  "recurrence": null
}
```

### Example 7: Ambiguous Input
Input: "maybe call the doctor"
Output:
```json
{
  "title": "Call the doctor",
  "description": "Maybe",
  "priority": "low",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 8: Multiple Clauses
Input: "buy milk and bread"
Output:
```json
{
  "title": "Buy milk",
  "description": "And bread",
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 9: Only Noun
Input: "milk"
Output:
```json
{
  "title": "Get milk",
  "description": null,
  "priority": "normal",
  "tags": [],
  "due_date": null,
  "recurrence": null
}
```

### Example 10: With Emoji
Input: "buy 🛒 groceries"
Output:
```json
{
  "title": "Buy groceries",
  "description": null,
  "priority": "normal",
  "tags": ["shopping"],
  "due_date": null,
  "recurrence": null
}
```

## 8. Determinism Guarantees

- The same input must always produce the same output
- No randomness is allowed
- No probabilistic behavior is allowed
- The system must be rule-based and explainable
- All processing follows deterministic algorithms
- Results are reproducible across all executions

## 9. Phase Compatibility Notes

- Temporal fields (due_date, recurrence) are placeholders only
- No external services or models are allowed
- Works entirely in-memory
- Must comply with hackathon rules
- No AI hallucination or implicit assumption is allowed

## 10. Integration Guidance

### Integration Points
- Input validation layer for task creation
- Pre-processing for task storage systems
- Standardization layer in task management workflows
- Consistency enforcement in user interfaces

### Usage Recommendations
- Apply before task validation
- Use as a standardization step in task ingestion
- Integrate as a normalization primitive in task processing pipelines
- Use to ensure consistent task format across the system

### Implementation Notes
- All rules must be implemented as deterministic functions
- No external dependencies should be required
- Processing should be fast and efficient
- Error handling should be minimal but robust

## Helper Tools

The skill includes:
- `scripts/normalize_task.sh` - Command-line helper for testing normalization
- `references/normalization-rules.md` - Detailed normalization rules and examples
- `assets/task-schema.json` - JSON schema for normalized task objects