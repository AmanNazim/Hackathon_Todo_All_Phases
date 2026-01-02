# Tasks Quality Analysis Patterns

This reference contains detailed patterns and heuristics for identifying quality issues in Tasks.md documents.

## Task Clarity Issue Patterns

### Vague Verb Detection
Look for these terms that indicate unclear tasks:
- Action terms: "handle", "manage", "deal with", "take care of", "work on", "implement", "create"
- Quality terms: "optimize", "improve", "enhance", "refactor", "tune", "adjust", "fix later"
- Support terms: "support", "enable", "facilitate", "allow", "provide"
- Abstract terms: "the system", "it", "that", "this" without clear referents

### Missing Success Conditions
Check for tasks missing:
- Clear completion criteria
- Verification steps
- Validation requirements
- Acceptance tests
- Expected outcomes

### Mixed Responsibilities
Flag tasks that combine multiple types of work:
- Design and implementation in one task
- Development and testing in one task
- Multiple components in one task
- Different phases in one task

### Undefined Dependencies
Tasks that reference undefined elements:
- Unknown systems or components
- Undefined data formats
- Unspecified interfaces
- Undefined user roles or permissions

## Task Completeness Analysis Patterns

### Coverage Indicators
Good task coverage includes:
- All major functional requirements from spec
- All architectural components from plan
- Setup and configuration tasks
- Validation and verification tasks
- Error handling tasks
- Cleanup and maintenance tasks

### Missing Element Patterns
Look for missing:
- Data validation tasks
- Error handling tasks
- Input sanitization tasks
- Output formatting tasks
- User interface tasks (if required)
- Integration tasks
- Testing tasks
- Documentation tasks

## Task Granularity Patterns

### Overly Large Tasks
Indicators of oversized tasks:
- Tasks that span multiple components
- Tasks that require multiple days/weeks
- Tasks that mix design and implementation
- Tasks with multiple success criteria
- Tasks with many sub-components

### Appropriate Sizing Indicators
Well-sized tasks:
- Can be completed in 1-3 days
- Focus on a single component or functionality
- Have clear, measurable outcomes
- Can be validated independently
- Are self-contained

## Edge Case Coverage Patterns

### Common Missing Edge Cases
Tasks often miss planning for:
- Invalid input validation
- Empty state handling
- Boundary conditions (min/max values)
- Error propagation scenarios
- User cancellation or interruption
- Concurrent operations
- Duplicate operations
- Network failures
- Data corruption
- Permission failures

### Edge Case Indicators
Good tasks address:
- What happens with invalid inputs
- What happens at system boundaries
- What happens during failures
- What happens with concurrent access
- What happens during interruption

## Dependency Analysis Patterns

### Dependency Indicators
Look for these dependency patterns:
- "After task X is complete" - sequential dependency
- "Requires Y to be set up" - prerequisite dependency
- "Must be done before Z" - ordering constraint
- "Depends on interface A" - interface dependency
- "Uses service B" - service dependency

### Dependency Issues
Common problems:
- Circular dependencies
- Missing prerequisite tasks
- Assumed but unstated dependencies
- Ordering violations
- Unmet interface requirements

## Task Quality Heuristics

### Completeness Check
- Do tasks cover all functional requirements?
- Are all major components addressed?
- Are validation steps included?
- Are error scenarios planned?
- Are integration points covered?

### Clarity Check
- Can each task be executed without further clarification?
- Are inputs and outputs clearly defined?
- Are success conditions explicit?
- Are dependencies and prerequisites clear?
- Is the scope well-defined?

### Feasibility Check
- Are the required resources available?
- Are the time estimates realistic?
- Are dependencies properly sequenced?
- Are potential obstacles addressed?
- Are validation approaches clear?