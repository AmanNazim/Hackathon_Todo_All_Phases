# Spec Improvement Patterns

This reference contains detailed patterns for applying improvements based on analysis reports.

## Clarity Improvement Patterns

### Vague Language Replacement
Replace vague terms with specific, measurable alternatives:

**Before:** "The system should be fast"
**After:** "The system should respond within 2 seconds for 95% of requests"

**Before:** "The interface should be user-friendly"
**After:** "The interface should allow users to complete the task in 3 clicks or fewer"

### Constraint Addition
Add missing constraints identified in analysis:

**Before:** "Users can upload files"
**After:** "Users can upload files up to 10MB in size, supporting PDF, DOC, and TXT formats"

### Undefined Term Definition
Add definitions for terms flagged as undefined:

**Before:** "The processor handles requests"
**After:** "The processor (the system component responsible for request handling) handles requests"

## Acceptance Criteria Improvement Patterns

### Given/When/Then Structure
Convert loose criteria to structured format:

**Before:** "Feature works when user clicks"
**After:** "Given a user on the dashboard, when they click the submit button, then the form data is saved"

### Measurable Criteria
Replace subjective criteria with measurable ones:

**Before:** "The system performs well"
**After:** "The system processes requests with 99.9% uptime and response time under 2 seconds"

### Edge Case Coverage
Add criteria for failure paths:

**Before:** "User logs in successfully"
**After:** "Given valid credentials, when user submits login form, then they access the dashboard.
Given invalid credentials, when user submits login form, then they receive an error message."

## Edge Case Addition Patterns

### Input Validation Cases
Add cases for invalid inputs:

**Analysis flags:** Missing validation for empty inputs
**Addition:** "When user submits empty form, then system shows validation errors"

### Boundary Conditions
Add cases for limits:

**Analysis flags:** Missing boundary checks
**Addition:** "When user enters value at maximum limit, then system accepts it.
When user enters value above maximum limit, then system shows error."

### Error Scenarios
Add failure handling:

**Analysis flags:** Missing error handling
**Addition:** "When network is unavailable, then system shows offline message and queues requests."

## Structural Improvement Patterns

### Consistency Fixes
Normalize inconsistent terminology:

**Before:** "User, Customer, Client used interchangeably"
**After:** "User used consistently throughout document"

### Formatting Improvements
Standardize formatting as recommended:

**Before:** Mixed heading levels and styles
**After:** Consistent heading hierarchy (##, ###, etc.)

## Traceability Mapping

### Issue-to-Change Mapping
Each change must map back to a specific issue:

**Issue ID:** QI-01 (Clarity Issue #1)
**Original:** "System should be fast"
**Improved:** "System responds within 2 seconds"
**Section:** Requirements/Performance
**Type:** Clarity Improvement

## Quality Checks

### Scope Validation
Before making any change, verify:
- Does this address an issue in the analysis report? ✓
- Does this preserve original intent? ✓
- Does this stay within original scope? ✓
- Does this violate any constitution rules? ✗

### Intent Preservation
- Maintain the same functional behavior
- Keep the same user goals
- Preserve business requirements
- Retain original constraints