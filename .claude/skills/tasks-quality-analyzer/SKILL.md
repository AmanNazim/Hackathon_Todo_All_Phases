---
name: tasks-quality-analyzer
description: Analyzes Tasks.md documents to identify clarity issues, missing tasks, vague or overly broad tasks, edge case gaps, and dependency problems. Provides structured quality analysis with concrete improvement recommendations. Use when evaluating task documents for quality before implementation.
---

# Tasks Quality Analyzer Skill

This skill analyzes Tasks.md documents to identify quality issues and provide actionable improvement recommendations. The skill operates exclusively on Tasks.md documents generated as part of a Spec-Driven Development workflow.

## When to Use This Skill

Use this skill when you need to evaluate a Tasks.md document for:
- Clarity and ambiguity issues
- Missing or incomplete tasks
- Vague or overly broad tasks
- Edge case coverage gaps
- Task dependency and ordering problems
- Task readiness before implementation

## Input Requirements

The skill receives:
- One Tasks.md document (Markdown)
- Optional references to:
  - spec.md
  - plan.md
  - constitution.md

If reference documents are provided, they may ONLY be used for alignment checks.
They MUST NOT be used to invent new scope.

## Analysis Process

The skill performs six key analyses:

### 1. Task Clarity Analysis
Detects tasks that:
- Use vague verbs (e.g., "handle", "support", "manage")
- Lack clear inputs, outputs, or success conditions
- Combine multiple responsibilities
- Depend on undefined behavior
- Cannot be validated or verified

### 2. Task Completeness Analysis
Evaluates whether tasks cover:
- All functional requirements from the spec (if provided)
- All architectural components from the plan (if provided)
- All necessary setup, glue, and orchestration steps
- Required validation, error handling, and cleanup tasks

Identifies missing tasks ONLY when they are clearly required by the provided documents.

### 3. Task Granularity Analysis
Detects:
- Tasks that are too large to implement in one iteration
- Tasks that are too small or redundant
- Tasks that mix design, implementation, and validation

Recommends appropriate granularity adjustments WITHOUT rewriting tasks.

### 4. Edge Case Coverage Analysis
Identifies missing tasks related to:
- Invalid input handling
- Empty or initial state handling
- Boundary conditions
- Error propagation
- User cancellation or interruption
- Conflicting or repeated operations

### 5. Dependency & Ordering Analysis
Checks for:
- Implicit dependencies between tasks
- Missing prerequisite tasks
- Incorrect task ordering assumptions
- Cyclic dependencies

### 6. Task Readiness Assessment
Evaluates overall readiness for execution.

## Strict Analysis Rules

1. Do NOT hallucinate missing features
2. Do NOT assume implementation details
3. Do NOT merge tasks or rewrite them
4. Do NOT generate new code-level tasks
5. Do NOT infer future phases or enhancements
6. If uncertainty exists, explain it explicitly
7. Use neutral, technical, professional language
8. Preserve the original scope and intent of the project
9. NEVER invent features or expand scope beyond the source documents

## Recommendation Guidelines

All recommendations:
- Must be task-level (not code-level)
- Must be phrased as suggestions
- Must reference exact task IDs or descriptions
- Must explain WHY the improvement is needed
- Must avoid implementation or tooling advice

## Quality Analysis Execution

When analyzing tasks:

1. Read the entire Tasks.md document first to understand scope and intent
2. Identify and list all tasks
3. Perform clarity analysis on each task
4. Check for completeness against spec and plan if provided
5. Evaluate task granularity and sizing
6. Identify potential edge cases for each task
7. Verify dependencies and ordering
8. Generate improvement recommendations based on findings
9. Assess overall risk if tasks proceed unchanged
10. Create structured report following the required format

## Output Format Requirements

The skill MUST produce a structured Markdown report with these EXACT sections:

1. Task Set Overview
2. Unclear or Ambiguous Tasks
3. Missing or Incomplete Tasks
4. Vague or Overly Broad Tasks
5. Missing Edge Case Tasks
6. Task Dependency & Ordering Issues
7. Improvement Recommendations
8. Risk Assessment Summary

Each issue MUST:
- Reference the exact task or section
- Explain why the issue exists
- Provide a concrete improvement suggestion at the task level

## Output Structure Template

The final output MUST follow this exact structure:

```markdown
# Tasks Quality Analysis Report

## 1. Task Set Overview
- Summary of task scope
- Overall task readiness rating (Low / Medium / High)

## 2. Unclear or Ambiguous Tasks
- Task reference
- Description of ambiguity
- Suggested clarification direction

## 3. Missing or Incomplete Tasks
- Related requirement or plan section
- What task appears missing
- Why it is required

## 4. Vague or Overly Broad Tasks
- Task reference
- Issue description
- Suggested refinement approach

## 5. Missing Edge Case Tasks
- Edge case scenario
- Why it matters
- Suggested task to add (description only)

## 6. Task Dependency & Ordering Issues
- Identified dependency
- Risk description

## 7. Improvement Recommendations
- Prioritized list of task-level improvements

## 8. Risk Assessment Summary
- Risks if tasks are executed as-is
- Severity level (Low / Medium / High)
```

## Non-Goals (Absolutely Forbidden)

- No code generation
- No implementation details
- No plan or spec rewriting
- No feature expansion
- No scope creep
- No hallucinated tasks unrelated to inputs
- No modification of the original tasks document
- No assumption of implementation details beyond what's in the inputs

## Helper Tools

The skill includes:
- `scripts/analyze_tasks.sh` - Command-line helper for initial pattern detection
- `references/analysis-patterns.md` - Detailed patterns for quality assessment
- `assets/report-template.md` - Template for output structure