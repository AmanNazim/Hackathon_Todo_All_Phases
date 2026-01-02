# Plan Improvement Patterns

This reference contains detailed patterns for applying improvements based on analysis reports.

## Clarity Improvement Patterns

### Vague Language Replacement
Replace vague plan steps with specific, actionable language:

**Before:** "Handle user authentication flow"
**After:** "Implement user authentication flow with username/password validation and session management"

**Before:** "Optimize the database queries"
**After:** "Optimize database queries by adding appropriate indexes and reviewing query execution plans"

### Entry/Exit Condition Addition
Add missing conditions for plan steps:

**Before:** "Test the feature"
**After:** "Test the feature when development is complete, then validate all acceptance criteria are met"

### Responsibility Clarification
Add clarity to ambiguous responsibilities:

**Before:** "The system handles errors"
**After:** "The application logs errors to the error log and displays user-friendly messages"

## Acceptance Criteria Improvement Patterns

### Plan-Level Acceptance Criteria
Add measurable outcomes at the plan level:

**Before:** "Implement login feature"
**After:** "Implement login feature when users can successfully authenticate with valid credentials and receive appropriate error messages for invalid credentials"

### Validation Point Addition
Add review and validation checkpoints:

**Before:** "Create the database schema"
**After:** "Create the database schema, then review with database team and validate against requirements"

## Edge Case Addition Patterns

### Failure Path Planning
Add failure handling to plan steps:

**Analysis flags:** Missing failure handling
**Addition:** "Plan rollback procedures for each major implementation step"

### Dependency Management
Add dependency considerations:

**Analysis flags:** Missing dependency validation
**Addition:** "Validate all external dependencies are available before starting implementation"

### Recovery Planning
Add recovery strategies:

**Analysis flags:** Missing recovery procedures
**Addition:** "Plan for recovery steps if integration testing fails"

## Consistency Improvement Patterns

### Terminology Standardization
Normalize inconsistent terminology:

**Before:** "User, Customer, Client used interchangeably"
**After:** "User used consistently throughout plan"

### Structure Normalization
Standardize plan formatting:

**Before:** Mixed heading levels and styles
**After:** Consistent heading hierarchy (##, ###, etc.) and step formatting

## Traceability Mapping

### Issue-to-Change Mapping
Each change must map back to a specific issue:

**Issue ID:** PQ-01 (Plan Quality Issue #1)
**Original:** "Handle errors appropriately"
**Improved:** "Log errors to error log and display user-friendly messages"
**Section:** Implementation Phase/Step 3
**Type:** Clarity Improvement

## Quality Checks

### Scope Validation
Before making any change, verify:
- Does this address an issue in the analysis report? ✓
- Does this preserve original plan intent? ✓
- Does this stay within original scope? ✓
- Does this violate any constitution rules? ✗

### Intent Preservation
- Maintain the same overall plan flow
- Keep the same major milestones
- Preserve business requirements
- Retain original constraints

## Improvement Prioritization

### High Priority Improvements
- Missing acceptance criteria for major milestones
- Vague plan steps that cannot be executed
- Missing failure handling for critical steps
- Inconsistent terminology that causes confusion

### Medium Priority Improvements
- Minor clarity issues
- Missing validation points
- Incomplete edge case coverage
- Minor formatting inconsistencies

### Low Priority Improvements
- Stylistic improvements
- Minor terminology adjustments
- Additional clarifications that don't affect execution