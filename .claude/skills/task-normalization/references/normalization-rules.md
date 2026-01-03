# Task Normalization Rules and Examples

This reference contains detailed normalization rules and examples for the Task Normalization Skill.

## Title Extraction Rules

### Action-Oriented Titles
- Convert nouns to actions when appropriate:
  - "groceries" → "Get groceries" or "Buy groceries"
  - "milk" → "Get milk" or "Buy milk"
  - "doctor" → "Call the doctor" or "Visit the doctor"

### Remove Filler Words
- Remove polite prefixes:
  - "please" → removed
  - "remind me to" → removed
  - "help me to" → removed
  - "can you" → removed

### Capitalization Rules
- Title case for the first letter of the main action
- Preserve proper nouns as they appear
- Keep other words in lowercase unless they're proper nouns

## Description Extraction Rules

### Temporal Hints
Move these to the description:
- "before Sunday morning"
- "after 5 PM"
- "on Tuesday"
- "by Friday"
- "until next week"
- "during the weekend"

### Contextual Clauses
Move these to the description:
- "for the meeting"
- "with John"
- "at the store"
- "in the kitchen"

## Priority Assignment Rules

### High Priority Indicators
- "urgent"
- "asap"
- "immediately"
- "emergency"
- "critical"
- "important"
- "high priority"

### Low Priority Indicators
- "whenever"
- "optional"
- "maybe"
- "if possible"
- "low priority"
- "when you have time"

### Normal Priority
- Default for all inputs without explicit indicators
- No special processing needed

## Tags Extraction Rules

### Parenthetical Tags
- "(work)" → ["work"]
- "(personal, urgent)" → ["personal", "urgent"]
- "(shopping, groceries)" → ["shopping", "groceries"]

### Emoji to Tags
- "🛒" → ["shopping"]
- "📞" → ["call"]
- "📧" → ["email"]
- "📅" → ["meeting"]
- "🏠" → ["home"]

### Explicit Category Words
- "work task" → ["work"]
- "personal errand" → ["personal"]
- "shopping list" → ["shopping"]

## Temporal Handling Rules

### Temporal Phrases to Description
- "before Sunday" → moved to description
- "after the meeting" → moved to description
- "on Tuesday" → moved to description
- "by end of week" → moved to description

### Temporal Words to Remove from Title
- "tomorrow" → moved to description
- "next week" → moved to description
- "this weekend" → moved to description

## Ambiguity Resolution

### Vague Inputs
- "something" → "Do something"
- "stuff" → "Handle stuff"
- "it" → Clarify based on context

### Multiple Meanings
- "call" → "Make a call" (default)
- "buy" → Keep as "Buy" (action-oriented)

## Edge Case Handling

### Empty Input
Input: ""
Output: { "title": "Empty task", "description": null, ... }

### Single Word Input
Input: "call"
Output: { "title": "Call", "description": null, ... }

Input: "milk"
Output: { "title": "Get milk", "description": null, ... }

### Long Input
Input: "please remind me to call the doctor for the appointment before 3 PM on Friday"
Output: {
  "title": "Call the doctor",
  "description": "For the appointment before 3 PM on Friday",
  ...
}

### Multiple Tasks
Input: "buy milk and bread"
Output: {
  "title": "Buy milk",
  "description": "And bread",
  ...
}

### Contradictory Input
Input: "urgent optional task"
Output: {
  "title": "Do task",
  "description": "Optional but urgent",
  "priority": "high",
  ...
}

## Example Normalizations

### Example 1: Basic Normalization
Input: "buy milk"
Title: "Buy milk"
Description: null
Priority: "normal"
Tags: []

### Example 2: With Temporal
Input: "remind me to pay bills before Sunday"
Title: "Pay bills"
Description: "Before Sunday"
Priority: "normal"
Tags: []

### Example 3: High Priority
Input: "urgent: fix the bug"
Title: "Fix the bug"
Description: null
Priority: "high"
Tags: []

### Example 4: With Tags
Input: "buy groceries (shopping, weekly)"
Title: "Buy groceries"
Description: null
Priority: "normal"
Tags: ["shopping", "weekly"]

### Example 5: Complex Input
Input: "please remind me to call mom tomorrow afternoon for the birthday party"
Title: "Call mom"
Description: "Tomorrow afternoon for the birthday party"
Priority: "normal"
Tags: []

### Example 6: Emoji Input
Input: "buy 🛒 groceries"
Title: "Buy groceries"
Description: null
Priority: "normal"
Tags: ["shopping"]

### Example 7: Low Priority
Input: "maybe call the doctor when you have time"
Title: "Call the doctor"
Description: "Maybe when you have time"
Priority: "low"
Tags: []

### Example 8: Multiple Actions
Input: "buy milk and bread for the party"
Title: "Buy milk"
Description: "And bread for the party"
Priority: "normal"
Tags: []

## Deterministic Processing

### Consistency Rules
- Same input always produces same output
- Processing order: remove prefixes → extract title → determine priority → extract tags → set description
- No random or probabilistic elements
- All rules applied in fixed order

### Validation Checks
- Ensure all required fields are present
- Verify priority is one of: "low", "normal", "high"
- Ensure due_date and recurrence remain null
- Confirm tags are in array format