# Plan Quality Analysis Patterns

This reference contains detailed patterns and heuristics for identifying quality issues in plan documents.

## Plan Clarity Issue Patterns

### Vague Step Detection
Look for these terms that indicate unclear plan steps:
- Action terms: "handle", "manage", "deal with", "take care of", "work on", "implement", "create"
- Quality terms: "optimize", "improve", "enhance", "refactor", "tune", "adjust", "fix later"
- Abstract terms: "the system", "it", "that", "this" without clear referents
- Incomplete actions: "setup", "configure", "integrate" without context

### Missing Entry/Exit Criteria
Check for missing:
- Prerequisites for starting a step
- Success conditions for completing a step
- Failure conditions that would stop a step
- Validation requirements after completion
- Dependencies on other steps

### Overloaded Steps
Flag steps that combine multiple responsibilities:
- Steps that mention multiple components or systems
- Steps that include both development and testing activities
- Steps that combine design and implementation
- Steps that mix different phases of work

### Undefined Terms
Terms that may need clarification in planning context:
- Technical jargon specific to the domain
- Acronyms without explanation
- Process-specific terminology
- Tool or system names without context

## Acceptance Criteria Analysis Patterns

### Plan-Level Quality Indicators
Good plan steps should include:
- Clear success/failure indicators
- Review or validation checkpoints
- Measurable outcomes
- Observable results
- Verification methods

### Missing Elements
Look for missing:
- How to verify completion of each step
- What constitutes acceptable completion
- How to validate intermediate results
- Review criteria for plan steps
- Quality gates between steps

### Structure Patterns
Valid plan acceptance formats include:
- "Step is complete when [specific condition]"
- "Validate that [measurable outcome] has been achieved"
- "Review and approve [specific deliverable]"

## Edge Case Categories for Planning

### Failure Path Planning
- What happens when a step fails
- Rollback procedures
- Recovery strategies
- Escalation procedures
- Alternative approaches when primary method fails

### Boundary Conditions
- Resource limits during execution
- Timeline constraints
- Dependency delays
- Team availability issues
- Environment constraints

### Input/Output Issues
- Invalid inputs to plan steps
- Missing dependencies
- Partial completion scenarios
- Interrupted execution
- Concurrent execution conflicts

### Validation Scenarios
- How to handle unexpected results
- What to do if validation fails
- Procedures for rework
- Communication protocols for issues
- Documentation requirements for changes

## Spec Alignment Patterns

### Mapping Indicators
Good plan-to-spec alignment includes:
- Clear reference to specific spec requirements
- Traceability from plan steps to spec items
- Coverage of all major spec requirements
- Explicit handling of non-functional requirements

### Misalignment Signs
Watch for:
- Plan steps without spec justification
- Spec requirements not addressed in plan
- Scope creep beyond spec requirements
- Missing coverage of critical spec elements
- Contradictions between plan and spec

## Risk Assessment Categories

### High Risk Indicators
- Multiple vague or abstract steps
- No validation or review checkpoints
- Critical requirements without plan coverage
- Missing failure handling strategies
- Undefined dependencies or prerequisites

### Medium Risk Indicators
- Some unclear step descriptions
- Limited acceptance criteria
- Partial spec coverage
- Few validation checkpoints
- Missing edge case considerations

### Low Risk Indicators
- Clear, specific step descriptions
- Well-defined acceptance criteria
- Complete spec coverage
- Comprehensive validation approach
- Good failure handling planning

## Plan Quality Heuristics

### Completeness Check
- Does every major spec requirement have corresponding plan steps?
- Are all major risks addressed in the plan?
- Are validation and review points included?
- Are rollback/recovery procedures planned?

### Clarity Check
- Can each step be executed without further clarification?
- Are success/failure conditions clearly defined?
- Are dependencies and prerequisites explicit?
- Is the sequence logical and complete?

### Feasibility Check
- Are the required resources available?
- Are timelines realistic?
- Are dependencies properly sequenced?
- Are potential obstacles addressed?