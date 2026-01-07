# Error Handling Patterns for CLI Applications

## Common Error Classification Patterns

### Command Recognition Patterns

#### Exact Match First
```pseudocode
FUNCTION findCommand(input: String): Command | null:
    // Check for exact match first
    exactMatch = commandRegistry.get(input)
    IF exactMatch:
        RETURN exactMatch

    // Check for prefix matches
    prefixMatches = commandRegistry.findByPrefix(input)
    IF prefixMatches.length == 1:
        RETURN prefixMatches[0]
    ELSE IF prefixMatches.length > 1:
        THROW AmbiguousCommandError(prefixMatches)

    // Check for fuzzy matches
    fuzzyMatches = findFuzzyMatches(input)
    IF fuzzyMatches.length > 0:
        RETURN suggestFuzzyMatches(fuzzyMatches)

    THROW UnknownCommandError(input)
```

#### Fuzzy Matching with Threshold
```pseudocode
FUNCTION findFuzzyMatches(input: String): List<Command>:
    candidates = []
    FOR each command in commandRegistry.getAll():
        distance = levenshteinDistance(input.toLowerCase(), command.name.toLowerCase())
        similarity = calculateSimilarity(input, command.name)

        // Only include matches above threshold
        IF distance <= 2 OR similarity > 0.7:
            candidates.add({command: command, score: similarity})

    RETURN candidates.sortBy(score, descending=True).take(5)
```

## Suggestion Generation Patterns

### Context-Aware Suggestions
```pseudocode
FUNCTION generateContextualSuggestions(errorType: ErrorType, context: Context): List<String>:
    suggestions = []

    SWITCH errorType:
        CASE UNKNOWN_COMMAND:
            suggestions = generateCommandSuggestions(context.userInput, context)
        CASE MISSING_ARGUMENTS:
            suggestions = generateArgumentSuggestions(context.command, context)
        CASE INVALID_ARGUMENT:
            suggestions = generateValidValueSuggestions(context.expectedType, context)
        DEFAULT:
            suggestions = generateGeneralSuggestions(context)

    RETURN suggestions.limit(5)
```

### Progressive Help Escalation
```pseudocode
FUNCTION getHelpLevel(failureCount: Integer): HelpLevel:
    SWITCH true:
        CASE failureCount == 1:
            RETURN HelpLevel.INLINE
        CASE failureCount == 2:
            RETURN HelpLevel.DETAILED
        CASE failureCount >= 3:
            RETURN HelpLevel.COMPREHENSIVE
        DEFAULT:
            RETURN HelpLevel.INLINE
```

## Intent Detection Strategies

### Multi-Method Intent Detection
```pseudocode
FUNCTION detectUserIntent(input: String): IntentResult:
    methods = [
        checkAbbreviation(input),
        checkCommonMistakes(input),
        checkSimilarCommands(input),
        checkPartialMatches(input)
    ]

    FOR each method in methods:
        IF method.confidence > 0.7:  // High confidence threshold
            RETURN method.result

    RETURN {intent: null, confidence: 0.0}
```

### Common Mistake Patterns
```pseudocode
CONSTANT mistakePatterns = [
    {pattern: "ls", correction: "list"},
    {pattern: "rm", correction: "delete"},
    {pattern: "mk", correction: "add"},
    {pattern: "done", correction: "complete"},
    {pattern: "finish", correction: "complete"}
]

FUNCTION checkCommonMistakes(input: String): IntentResult:
    FOR each pattern in mistakePatterns:
        IF input.equalsIgnoreCase(pattern.pattern):
            command = commandRegistry.get(pattern.correction)
            IF command:
                RETURN {intent: command, confidence: 0.9}

    RETURN {intent: null, confidence: 0.0}
```

## Context Management Patterns

### Stateful Context Tracking
```pseudocode
CLASS ContextManager:
    FIELD recentCommands: Queue<String>
    FIELD errorCount: Map<String, Integer>
    FIELD lastValidCommand: Command

    FUNCTION updateContext(command: String, success: Boolean):
        recentCommands.add(command)
        IF recentCommands.size > 10:  // Keep only last 10
            recentCommands.removeFirst()

        IF NOT success:
            errorCount.increment(command)

    FUNCTION getContext(): Context:
        RETURN {
            recentCommands: recentCommands.toList(),
            currentErrorCount: errorCount.getOrDefault(getCurrentCommand(), 0),
            lastValidCommand: lastValidCommand
        }
```

## Error Message Composition

### Template-Based Message Generation
```pseudocode
CONSTANT errorTemplates = {
    UNKNOWN_COMMAND: {
        message: "I don't recognize the command '{command}'.",
        suggestions: ["Try one of: {similarCommands}", "See 'help' for available commands"]
    },
    MISSING_ARGUMENTS: {
        message: "The '{command}' command needs more information.",
        suggestions: ["{command} {requiredArgs}", "See '{command} --help' for details"]
    },
    INVALID_ARGUMENT: {
        message: "The value '{value}' is not valid for {argument}.",
        suggestions: ["Try: {validExamples}", "See 'help {command}' for valid options"]
    }
}

FUNCTION formatErrorMessage(errorType: ErrorType, data: Map<String, String>): String:
    template = errorTemplates[errorType]
    message = template.message.replacePlaceholders(data)

    suggestions = []
    FOR each suggestionTemplate in template.suggestions:
        suggestions.add(suggestionTemplate.replacePlaceholders(data))

    RETURN {message: message, suggestions: suggestions}
```

## Edge Case Handling Patterns

### Repetitive Failure Detection
```pseudocode
CLASS FailureDetector:
    FIELD failureWindow: TimeWindow
    FIELD failureThreshold: Integer = 3
    FIELD timeLimit: Duration = Duration.ofMinutes(5)

    FUNCTION isRepetitiveFailure(userInput: String): Boolean:
        recentFailures = failureWindow.getFailuresWithin(timeLimit)
        sameCommandFailures = recentFailures.filter(cmd => cmd == userInput)

        RETURN sameCommandFailures.length >= failureThreshold
```

### Whitespace and Empty Input Handling
```pseudocode
FUNCTION normalizeInput(input: String): String:
    IF input == null:
        RETURN ""

    normalized = input.trim()

    // Replace multiple spaces with single space
    normalized = normalized.replaceAll("\\s+", " ")

    RETURN normalized

FUNCTION isMeaningfulInput(input: String): Boolean:
    normalized = normalizeInput(input)
    RETURN normalized.length > 0
```

## Integration Patterns

### Middleware Error Handling
```pseudocode
CLASS ErrorHandlingMiddleware:
    FIELD errorReasoner: ErrorReasoner
    FIELD nextHandler: CommandHandler

    FUNCTION handle(input: String): Result:
        TRY:
            RETURN nextHandler.handle(input)
        CATCH CommandError e:
            errorResult = errorReasoner.processError(input, getCurrentContext())
            RETURN Result.error(errorResult.message, errorResult.suggestions)
```

### Decorator Pattern for Error Handling
```pseudocode
FUNCTION createErrorHandlingDecorator(baseCommand: Command, errorReasoner: ErrorReasoner): Command:
    RETURN CLASS extends Command:
        FUNCTION execute(context: Context): Result:
            TRY:
                RETURN baseCommand.execute(context)
            CATCH Error e:
                errorResult = errorReasoner.processError(context.input, context)
                RETURN Result.error(errorResult.message, errorResult.suggestions)
```

## Performance Considerations

### Caching Strategies
```pseudocode
CLASS CachedSuggestionEngine:
    FIELD cache: Map<String, List<Suggestion>> = new LRUCache(100)
    FIELD fallbackEngine: SuggestionEngine

    FUNCTION getSuggestions(input: String, context: Context): List<Suggestion>:
        cacheKey = generateCacheKey(input, context)
        cached = cache.get(cacheKey)

        IF cached != null:
            RETURN cached

        suggestions = fallbackEngine.generate(input, context)
        cache.put(cacheKey, suggestions)
        RETURN suggestions
```

### Early Exit Strategies
```pseudocode
FUNCTION classifyErrorEfficiently(userInput: String, context: Context): ErrorType:
    // Quick checks first
    IF isMeaningfulInput(userInput) == false:
        RETURN ErrorType.EMPTY_INPUT

    commandPart = extractCommandPart(userInput)
    IF commandRegistry.hasCommand(commandPart) == false:
        RETURN ErrorType.UNKNOWN_COMMAND

    // More expensive checks later
    parsedCommand = parseCommand(userInput)
    validationErrors = validateArguments(parsedCommand, context)
    IF validationErrors.length > 0:
        RETURN ErrorType.INVALID_ARGUMENT

    RETURN ErrorType.VALID_COMMAND
```

## Testing Patterns

### Error Scenario Testing
```pseudocode
TEST_SUITE ErrorReasonerTest:
    TEST unknownCommandScenario():
        userInput = "xyz123"
        context = createContextWithCommands(["add", "list", "complete"])
        result = errorReasoner.processError(userInput, context)

        ASSERT result.type == ErrorType.UNKNOWN_COMMAND
        ASSERT result.suggestions.contains("add")  // Similar to 'x' prefix?

    TEST typoCorrectionScenario():
        userInput = "complte 1"  // Missing 'e'
        context = createContextWithCommands(["complete", "add", "list"])
        result = errorReasoner.processError(userInput, context)

        ASSERT result.suggestions.contains("complete 1")

    TEST missingArgumentsScenario():
        userInput = "add"
        result = errorReasoner.processError(userInput, context)

        ASSERT result.message.contains("needs more information")
        ASSERT result.suggestions.any(s -> s.contains("add"))
```

## Best Practices

### Consistency Guidelines
1. Always provide 3-5 suggestions maximum
2. Sort suggestions by relevance/probability
3. Use consistent formatting across all error types
4. Include actual command syntax in suggestions
5. Never suggest commands that don't exist

### User Experience Principles
1. Errors should inform, not intimidate
2. Help should be progressive, not overwhelming
3. Suggestions should be actionable
4. Messages should acknowledge user intent when clear
5. Feedback should guide toward success, not just away from failure