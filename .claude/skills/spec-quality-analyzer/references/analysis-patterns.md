# Spec Quality Analysis Patterns

This reference contains detailed patterns and heuristics for identifying quality issues in specification documents.

## Clarity Issue Patterns

### Vague Language Detection
Look for these terms that indicate unclear requirements:
- Performance terms: "fast", "quick", "efficient", "responsive", "high-performance"
- Quality descriptors: "user-friendly", "intuitive", "good", "great", "easy", "simple"
- Comparative terms: "better", "best", "improved", "enhanced"
- Temporal terms: "immediate", "soon", "timely", "promptly", "as soon as possible"
- Quantitative terms without values: "many", "few", "several", "a lot", "some", "etc."
- Unclear pronouns: "it", "they", "this", "that" without clear referents

### Missing Constraints
Check for missing:
- Numeric limits: maximum/minimum values, thresholds
- Time constraints: timeouts, deadlines, intervals
- Format specifications: data formats, validation rules
- Environmental constraints: platform, browser, device compatibility
- Resource constraints: memory, storage, bandwidth limits
- Permission constraints: access levels, security requirements

### Undefined Terms
Flag terms that are used without definition:
- Domain-specific jargon
- Technical acronyms on first use
- Business concepts unique to the organization
- Interface or system names without explanation

## Acceptance Criteria Patterns

### Quality Indicators
Good acceptance criteria should include:
- Specific, measurable conditions
- Clear pass/fail criteria
- Given/When/Then structure
- Testable scenarios
- Edge case considerations

### Missing Elements
Look for missing:
- Input validation criteria
- Expected output specifications
- Error handling requirements
- Performance benchmarks
- User interaction sequences
- Data state transitions

### Structure Patterns
Valid formats include:
- "Given [context], when [action], then [result]"
- "As a [user type], I can [action] so that [benefit]"
- "The system shall [behavior] when [conditions]"

## Edge Case Categories

### Input Validation
- Empty or null values
- Maximum/minimum boundary values
- Invalid format values
- Special characters
- Unicode characters
- Very large inputs
- Very small inputs

### State Transitions
- Initial state handling
- Invalid state transitions
- Concurrent operations
- Interrupted operations
- Failed operations
- Timeout conditions

### User Interactions
- Cancel operations
- Undo actions
- Multiple rapid clicks
- Browser back/forward
- Tab switching
- Session expiration
- Network interruptions

### Data Conditions
- Missing dependencies
- Corrupted data
- Duplicate entries
- Concurrent modifications
- Race conditions
- Cache invalidation

## Consistency Checks

### Terminology
- Same concept with different names
- Different concepts with same name
- Acronym usage consistency
- Technical term usage

### Format Consistency
- Requirement numbering
- Header structure
- List formatting
- Table formatting
- Code block formatting

### Logical Consistency
- Contradictory requirements
- Circular dependencies
- Impossible conditions
- Missing logical connections

## Risk Assessment Categories

### High Risk Indicators
- Multiple ambiguous requirements
- No acceptance criteria
- Critical functionality without edge cases
- Contradictory requirements
- Missing error handling
- Undefined performance requirements

### Medium Risk Indicators
- Some vague language
- Partial acceptance criteria
- Limited edge case coverage
- Minor inconsistencies

### Low Risk Indicators
- Clear, specific requirements
- Well-defined acceptance criteria
- Comprehensive edge case coverage
- Consistent terminology
- Complete specification sections