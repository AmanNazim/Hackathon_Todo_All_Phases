# CLI Parsing Rules and Examples

This reference contains detailed parsing rules and examples for the CLI Interaction Parser Skill.

## Input Normalization Rules

### Whitespace Handling
- Leading/trailing spaces: Removed
- Multiple internal spaces: Collapsed to single space
- Tabs: Converted to spaces
- Newlines: Treated as sentence separators

### Case Normalization
- Commands: Lowercase by default
- User content: Preserve original case
- Flags: Lowercase for standardization

### Quoted String Handling
- Single quotes: 'text' preserved as single token
- Double quotes: "text" preserved as single token
- Escaped quotes: \" and \' handled within strings
- Nested quotes: Invalid, treated as separate tokens

## Tokenization Patterns

### Command Token Recognition
- Verbs: First meaningful word after normalization
- Parameters: Words following verb (except flags)
- Flags: Starting with - or --
- Numbers: Standalone numeric tokens
- Identifiers: Alphanumeric with underscores/hyphens

### Semantic Unit Preservation
- Quoted phrases: Treated as single tokens
- File paths: Preserved with separators
- URLs: Treated as single tokens
- Email addresses: Treated as single tokens

## Intent Classification Patterns

### Common Verb Synonyms
```
Add: add, create, make, new, insert, generate
Delete: delete, remove, del, rm, destroy, trash
Update: update, modify, edit, change, set, alter
List: list, show, view, display, get, retrieve
Help: help, ?, --help, -h, info, manual
```

### Shorthand Commands
```
"a title" → add "title"
"l" → list
"d 1" → delete task 1
"v 2" → view task 2
```

### Menu Index Recognition
- Standalone numbers: "1", "2", "15" → menu selections
- Numbered commands: "1 add task" → execute command 1
- Range notation: "1-5" → multiple selections

## Entity Extraction Patterns

### Identifier Extraction
- Numeric IDs: \b\d+\b (standalone numbers)
- Alphanumeric IDs: \b[a-zA-Z][a-zA-Z0-9_-]*\b
- UUIDs: [0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}

### Title/Description Extraction
- Quoted content: "text in quotes" or 'text in quotes'
- Unquoted content: After command verb
- Multi-word: Consecutive non-command tokens

### Flag Extraction
- Short flags: -[a-z] pattern
- Long flags: --[a-z][a-z0-9-]* pattern
- Flag values: --flag=value or --flag value patterns

### Date/Time Extraction
- Relative: today, tomorrow, next week, in 2 hours
- Absolute: YYYY-MM-DD, DD/MM/YYYY, Month DD, YYYY
- Time: HH:MM, HH:MM AM/PM, h o'clock

## Validation Rules

### Required Entity Validation
- Commands must have required parameters present
- Missing required entities → return to user for clarification
- Validate entity format before processing

### Conflicting Parameter Detection
- Mutually exclusive flags: --force vs --dry-run
- Contradictory values: --start --stop simultaneously
- Incompatible combinations: --all --id=123

### Entity Existence Validation
- Validate referenced IDs exist in system
- Check cross-references are valid
- Verify dependencies are met

## Ambiguity Resolution Examples

### Multiple Intent Matches
Input: "a meeting"
- Could match: add meeting, attend meeting, agenda meeting
Resolution: "Did you mean to add a meeting or view meeting agenda?"

### Partial Command Resolution
Input: "rem"
- Could match: remove, remember, remote
Resolution: "Command 'rem' is ambiguous. Did you mean: remove, remember?"

### Missing Information
Input: "delete"
- Missing: what to delete
Resolution: "What would you like to delete? Please specify."

### Context-Based Disambiguation
Input: "1" in task list context
- Context: currently viewing task list
- Resolution: select task #1 from current list

## Error Handling Examples

### Empty Input
Input: ""
Response: "Please enter a command. Type 'help' for available commands."

### Unknown Command
Input: "flibbertigibbet"
Response: "Unknown command 'flibbertigibbet'. Type 'help' for available commands."

### Invalid Format
Input: "add -- --title My Task"
Response: "Invalid command format. Did you mean: add 'My Task'?"

### Invalid ID
Input: "view 999" (non-existent ID)
Response: "Task 999 not found. Use 'list' to see available tasks."

## Confidence Scoring Examples

### High Confidence
- Exact command match
- All required entities present
- No ambiguity detected
Example: "add 'Buy milk'" → 95% confidence

### Medium Confidence
- Synonym match
- Optional entities missing
- Minor ambiguity resolved by context
Example: "a 'Buy milk'" → 75% confidence

### Low Confidence
- Partial match
- Multiple interpretations
- Missing required information
Example: "rem" → 30% confidence

### No Confidence
- No pattern matches
- Complete garbage input
- Invalid format
Example: "xyz123!@#" → 0% confidence