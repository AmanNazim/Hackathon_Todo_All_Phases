---
name: help-error-reasoner-skill
description: A professional-grade Help and Error-Reasoning system for command-line applications that transforms low-quality CLI errors into structured, contextual, actionable feedback. Teaches how to implement error classification, intent detection, context-aware help generation, and progressive error resolution following best practices of top-level CLI apps.
---

# Help & Error-Reasoner Skill

## 1. Purpose & Scope

### What the skill teaches
The Help & Error-Reasoner Skill teaches how to implement a professional-grade error handling and help system for command-line applications. It transforms low-quality CLI errors (e.g., "invalid command") into structured, contextual, actionable feedback that explains why the input failed, suggests valid alternatives, and guides the user toward success.

### Why this skill is required
Most CLI applications provide generic, unhelpful error messages that frustrate users and impede productivity. Professional CLI tools like Git, Docker, and AWS CLI implement sophisticated error reasoning systems that understand user intent and provide actionable guidance. This skill teaches how to implement similar systems that enhance user experience and reduce support burden.

## 2. Core Responsibilities

### What this skill enforces
- **Command failure classification**: Systematically categorize different types of command failures
- **Intent detection**: Determine user intent from malformed input when possible
- **Context-aware messaging**: Generate help messages appropriate to the current context
- **Suggestion generation**: Provide valid alternatives based on known commands
- **Help escalation**: Implement progressive help levels from inline to comprehensive
- **Edge case handling**: Consistently handle unusual input patterns
- **Integration patterns**: Define how the system integrates with command parsing

### What it explicitly does NOT do
- **Command parsing**: Does not handle parsing user input into commands
- **Business logic execution**: Does not execute commands or modify application state
- **Command implementation**: Does not implement specific command functionality
- **Persistence operations**: Does not handle data storage or retrieval
- **Authentication**: Does not handle user permissions or access control

## 3. Error Classification Model

### Core Error Categories

#### Unknown Command
- **Detection**: Input doesn't match any known command
- **Explanation**: "The command 'xyz' is not recognized"
- **Suggestions**: List similar commands using edit distance or prefix matching
- **Example**: User types "ad" instead of "add"

#### Partial or Ambiguous Command
- **Detection**: Input matches prefix of multiple commands
- **Explanation**: "The command 'del' is ambiguous"
- **Suggestions**: List all matching commands explicitly
- **Example**: User types "del" when both "delete" and "details" exist

#### Missing Required Arguments
- **Detection**: Command recognized but required arguments missing
- **Explanation**: "The 'add' command requires a task description"
- **Suggestions**: Show proper syntax with required arguments
- **Example**: User types "add" without providing a task

#### Invalid Argument Type or Format
- **Detection**: Command recognized but argument doesn't match expected format
- **Explanation**: "Task ID must be a number, got 'abc'"
- **Suggestions**: Show valid format examples
- **Example**: User types "complete abc" instead of "complete 123"

#### Out-of-Range Values
- **Detection**: Argument format is correct but value is invalid
- **Explanation**: "Task ID 999 doesn't exist"
- **Suggestions**: Show valid range or list available options
- **Example**: User references a task that doesn't exist

#### Conflicting Arguments
- **Detection**: Multiple arguments that contradict each other
- **Explanation**: "Cannot use --all and --id together"
- **Suggestions**: Show valid combinations
- **Example**: User specifies both --all and --id flags

#### Command Not Allowed in Current State
- **Detection**: Command is valid but not applicable in current context
- **Explanation**: "No tasks available to delete"
- **Suggestions**: Show available actions or required prerequisites
- **Example**: User tries to delete when no tasks exist

#### No-op Commands
- **Detection**: Command is valid but has no effect
- **Explanation**: "Task 1 is already completed"
- **Suggestions**: Show current state or alternative actions
- **Example**: User marks an already-completed task as complete

#### Internal Parsing Failure
- **Detection**: System error during command processing
- **Explanation**: "Internal error processing your command"
- **Suggestions**: Report error and suggest retrying
- **Example**: Unexpected exception during parsing

## 4. Intent & Suggestion Strategy

### Command Matching Algorithm
```pseudocode
FUNCTION findSimilarCommands(userInput, knownCommands):
    candidates = []

    FOR each command in knownCommands:
        // Prefix matching
        IF command.startsWith(userInput):
            candidates.add(command, score=0.9)

        // Edit distance (Levenshtein)
        distance = calculateEditDistance(userInput, command)
        IF distance <= 2:
            score = 1.0 - (distance * 0.1)
            candidates.add(command, score=score)

    RETURN candidates.sortedBy(score, descending=True).take(5)
```

### Intent Detection Logic
- **Fuzzy matching**: Compare input against known commands using edit distance
- **Pattern recognition**: Identify common typos or abbreviations
- **Context awareness**: Consider recent user actions when determining intent
- **Confidence scoring**: Only suggest when confidence exceeds threshold

### Suggestion Ranking
1. **Exact prefix matches**: Highest priority
2. **Low edit distance**: High priority
3. **Semantic similarity**: Medium priority
4. **Frequently used commands**: Low priority tiebreaker

### Suggestion Format
```
❌ I couldn't understand your input.
💡 Try:
   • add "Buy milk"
   • delete 2
   • complete 3
   • help commands
```

## 5. Help Generation Architecture

### ErrorReasoner Component
Central orchestrator that analyzes failures and generates appropriate responses.

### Error Classifier
Categorizes errors into the defined error types using pattern matching and context analysis.

### Suggestion Generator
Creates relevant suggestions based on error type and available commands.

### Help Renderer
Formats help messages with consistent styling and appropriate detail level.

### Context Manager
Maintains state about current application context to provide relevant help.

## 6. Help Generation Strategy

### Multi-Level Help System

#### Level 1: Inline Error Help
- **Trigger**: Command failure
- **Content**: Brief explanation + 3-5 suggestions
- **Format**: Concise, actionable
- **Example**: "Unknown command. Did you mean: add, list, complete?"

#### Level 2: Command-Specific Help
- **Trigger**: "help <command>" or failed command
- **Content**: Syntax, arguments, examples
- **Format**: Structured with usage patterns
- **Example**: "add <task> - Add a new task to the list"

#### Level 3: Context-Aware Help
- **Trigger**: Current state + failed action
- **Content**: Relevant to current context
- **Format**: Adaptive based on available data
- **Example**: "Available tasks: 1, 2, 3 - use complete <id>"

#### Level 4: Global Help Overview
- **Trigger**: "help" or "help all"
- **Content**: Complete command reference
- **Format**: Comprehensive but organized
- **Example**: Full command list with brief descriptions

#### Level 5: Progressive Help Escalation
- **Trigger**: Repeated failures or "help more"
- **Content**: Detailed examples and tutorials
- **Format**: Extended documentation
- **Example**: Step-by-step usage guide

### Help Content Guidelines
- **Conciseness**: Keep messages under 5 lines when possible
- **Actionability**: Every message should guide toward next action
- **Consistency**: Use same terminology and formatting
- **Relevance**: Only show applicable commands and options

## 7. Error Modeling & Reporting

### Error Object Structure
```pseudocode
CLASS ErrorResult:
    type: ErrorType
    message: String
    suggestions: List<String>
    context: Map<String, Object>
    timestamp: DateTime
    confidence: Float
```

### Error Type Enum
- UNKNOWN_COMMAND
- AMBIGUOUS_COMMAND
- MISSING_ARGUMENTS
- INVALID_ARGUMENT_FORMAT
- OUT_OF_RANGE_VALUE
- CONFLICTING_ARGUMENTS
- INVALID_STATE
- NO_OP_COMMAND
- INTERNAL_ERROR

### Context Information
- **Current command**: The command that failed
- **Available commands**: List of valid commands in context
- **Recent actions**: Previous user actions
- **Application state**: Relevant state information
- **Valid values**: Available options for current context

## 8. Reusability Across Systems

### CLI Application Integration
The ErrorReasoner integrates as middleware between the command parser and command execution, processing failures before they reach the user.

### Configuration-Driven Behavior
- Command definitions loaded from configuration
- Error message templates customizable per application
- Suggestion algorithms configurable for different domains

### Extensibility Points
- **Custom error types**: Applications can define domain-specific error categories
- **Custom suggestion logic**: Specialized suggestion algorithms for specific use cases
- **Custom help renderers**: Different output formats for various interfaces

### Cross-Platform Considerations
- **Terminal capabilities**: Adapt help formatting based on terminal support
- **Input methods**: Handle different input sources (stdin, args, etc.)
- **Output formatting**: Consistent styling across platforms

## 9. Edge Case Handling

### Empty Input
- **Detection**: Input string is empty or whitespace only
- **Response**: Show general help or most common commands
- **Message**: "No command provided. Try: add, list, help"

### Whitespace-Only Input
- **Detection**: Input contains only spaces, tabs, newlines
- **Response**: Same as empty input with additional guidance
- **Message**: "Input contains only whitespace. Try: add 'task name'"

### Repeated Invalid Commands
- **Detection**: Same invalid command entered multiple times
- **Response**: Escalate to more detailed help
- **Message**: After 2 failures: "See 'help commands' for all options"

### Rapid Consecutive Failures
- **Detection**: Multiple failures in quick succession
- **Response**: Suggest getting help or starting over
- **Message**: "Multiple errors detected. See 'help' or 'help quickstart'"

### Commands with Extra Unused Arguments
- **Detection**: Valid command with unexpected extra arguments
- **Response**: Process valid parts, warn about extras
- **Message**: "Command processed, ignoring extra arguments: [list of extras]"

### Commands with No Available Data
- **Detection**: Command requires data that doesn't exist
- **Response**: Explain the issue and suggest creating data first
- **Message**: "No tasks available. Try: add 'new task'"

### User Cancellation or Interruption
- **Detection**: SIGINT, SIGTERM, or similar interruption
- **Response**: Graceful exit with optional save confirmation
- **Message**: "Operation cancelled. Changes not saved."

### Help Requested During Error State
- **Detection**: Help command after error state
- **Response**: Show error-specific help or reset to clean state
- **Message**: "Current error context: [error]. Type 'clear' to reset."

## 10. Implementation Architecture

### Integration Points in CLI Pipeline
```
Input → Parser → ErrorReasoner → Command Executor
                ↓
           Success? → No → Generate Help Message
```

### Decoupled Design Pattern
- **Separation of concerns**: Error reasoning separate from command execution
- **Dependency injection**: ErrorReasoner injected into command handler
- **Interface abstraction**: Clean interfaces between components
- **Testability**: Each component testable in isolation

### Error Reasoning Flow
```pseudocode
FUNCTION processCommandError(userInput, context):
    errorType = classifyError(userInput, context)
    suggestions = generateSuggestions(userInput, errorType, context)
    message = formatErrorMessage(errorType, suggestions)

    RETURN ErrorResult(
        type=errorType,
        message=message,
        suggestions=suggestions,
        context=extractRelevantContext(context)
    )
```

### Suggestion Generation Process
```pseudocode
FUNCTION generateSuggestions(userInput, errorType, context):
    suggestions = []

    SWITCH errorType:
        CASE UNKNOWN_COMMAND:
            suggestions = findSimilarCommands(userInput, context.availableCommands)
        CASE MISSING_ARGUMENTS:
            suggestions = showCommandSyntax(userInput, context.commandMetadata)
        CASE OUT_OF_RANGE_VALUE:
            suggestions = listValidValues(context.validOptions)
        DEFAULT:
            suggestions = getDefaultSuggestions(context.availableCommands)

    RETURN suggestions.limit(5)
```

## 11. Non-Goals & Constraints

### Explicitly Forbidden Behaviors
- **Command hallucination**: Never suggest commands that don't exist
- **Data modification**: Error reasoning must not change application state
- **External dependencies**: Keep system self-contained
- **Complex algorithms**: Use simple, reliable methods over sophisticated ones
- **Assumption making**: Only suggest what can be reasonably inferred

### What this skill intentionally avoids
- **Command implementation**: Focuses on error handling, not command logic
- **Persistence logic**: No data storage concerns in error system
- **Authentication**: Error reasoning independent of access control
- **Complex state management**: Keep error context simple and focused
- **External service calls**: All data comes from local context

## Implementation Examples

### Basic Error Reasoner Class
```pseudocode
CLASS ErrorReasoner:
    FIELD commandRegistry: CommandRegistry
    FIELD suggestionEngine: SuggestionEngine
    FIELD helpRenderer: HelpRenderer

    FUNCTION processError(userInput: String, context: Context): ErrorResult:
        errorType = classifyInput(userInput, context)
        suggestions = suggestionEngine.generate(userInput, errorType, context)
        message = helpRenderer.format(errorType, suggestions)

        RETURN ErrorResult(
            type=errorType,
            message=message,
            suggestions=suggestions
        )

    FUNCTION classifyInput(userInput: String, context: Context): ErrorType:
        // Implementation of error classification logic
        IF !commandRegistry.isValidCommand(userInput.split(" ")[0]):
            RETURN ErrorType.UNKNOWN_COMMAND
        // Additional classification logic...
```

### Integration with Command Handler
```pseudocode
CLASS CommandHandler:
    FIELD errorReasoner: ErrorReasoner
    FIELD commandParser: CommandParser

    FUNCTION handleInput(userInput: String): Result:
        TRY:
            command = commandParser.parse(userInput)
            RETURN command.execute()
        CATCH ParseError e:
            errorResult = errorReasoner.processError(userInput, getCurrentContext())
            RETURN Result.error(errorResult.message, errorResult.suggestions)
```

For detailed implementation examples and reference materials, see:
- `references/error-patterns.md` - Common error handling patterns
- `scripts/error-tools.py` - Reusable error handling utilities
- `assets/error-config.json` - Configuration templates