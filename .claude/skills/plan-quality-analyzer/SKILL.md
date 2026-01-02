---
name: plan-quality-analyzer
description: Analyzes plan documents to identify clarity issues, missing acceptance criteria, unaddressed edge cases, and consistency problems. Provides structured quality analysis with concrete improvement recommendations. Use when evaluating plan documents for quality before implementation.
---

# Plan Quality Analyzer Skill

This skill analyzes plan documents to identify quality issues and provide actionable improvement recommendations. The skill operates within a strict Spec-Driven Development workflow and analyzes ONLY plan documents, never acting as a spec or task generator.

## When to Use This Skill

Use this skill when you need to evaluate a plan document for:
- Clarity and precision issues
- Missing or weak acceptance criteria for plan outcomes
- Unaddressed edge cases at the planning level
- Spec alignment and consistency problems
- Planning risk assessment before implementation

## Input Requirements

The skill receives:
- One plan document (Markdown)
- Optional specification document (for alignment checks)
- Optional constitution.md (for rule validation)

If a referenced document is missing:
- Explicitly report the limitation
- Do NOT assume its contents

## Analysis Process

The skill performs five key analyses:

### 1. Plan Clarity Analysis
Detects:
- Vague or abstract steps (e.g., "handle errors", "optimize flow")
- Missing entry/exit criteria for plan steps
- Overloaded steps that mix multiple responsibilities
- Unclear sequencing or dependencies
- Undefined plan terminology

### 2. Acceptance Criteria Analysis (Plan-Level)
For each major plan step:
- Checks whether the success condition is defined
- Detects missing "done" definitions
- Identifies steps that cannot be validated or reviewed
- Suggests how acceptance criteria could be clarified (without writing tests)

### 3. Edge Case Coverage Analysis
Identifies missing planning considerations for:
- Failure paths
- Invalid or partial inputs
- Rollback or recovery logic
- User cancellation or interruption
- Boundary conditions relevant to the plan's scope

### 4. Spec Alignment & Consistency Checks
If a spec is provided:
- Verifies every plan step maps to one or more spec requirements
- Detects orphan plan steps not justified by the spec
- Detects spec requirements not addressed in the plan
- Flags inconsistencies or contradictions

If no spec is provided:
- Clearly states alignment cannot be fully verified

### 5. Planning Risk Assessment
Evaluates the overall risk of proceeding with the plan as written.

## Analysis Rules (Strict)

1. Analyze ONLY what is explicitly written in the plan
2. Do NOT infer requirements not present in the plan or spec
3. Do NOT add tasks, code, or architecture
4. Do NOT redesign the system
5. Do NOT introduce future phases or features
6. Use precise, neutral, technical language
7. Clearly distinguish between:
   - Plan clarity issues
   - Spec gaps (if detected)
   - Plan–spec misalignment

## Recommendation Guidelines

Recommendations:
- Stay strictly at the planning level
- Improve clarity, traceability, or completeness
- Are phrased as suggestions, not directives
- Avoid implementation or coding advice
- Avoid expanding scope
- Reference exact sections or steps from the plan

## Quality Analysis Execution

When analyzing a plan:

1. Read the entire plan document first to understand scope and intent
2. Identify and list all major plan steps
3. Perform clarity analysis on each step and section
4. Check for acceptance criteria for each major plan step
5. Identify potential edge cases for each plan step
6. Verify alignment with spec if provided
7. Generate improvement recommendations based on findings
8. Assess overall planning risk if the plan proceeds unchanged
9. Create structured report following the required format

## Output Format Requirements

The skill MUST produce a structured Markdown report with these EXACT sections:

1. Plan Overview
2. Clarity & Precision Issues
3. Missing or Weak Acceptance Criteria
4. Missing or Unaddressed Edge Cases
5. Spec Alignment & Consistency Checks
6. Improvement Recommendations
7. Planning Risk Assessment

Each issue MUST:
- Reference the exact section or step in the plan
- Explain why the issue exists
- Provide a concrete improvement suggestion at the planning level

## Output Structure Template

The final output MUST follow this exact structure:

```markdown
# Plan Quality Analysis Report

## 1. Plan Overview
- Summary of plan intent and scope
- Overall planning quality assessment (Low / Medium / High)

## 2. Clarity & Precision Issues
- Issue ID
- Plan section or step
- Description of the issue
- Suggested clarification

## 3. Missing or Weak Acceptance Criteria
- Related plan step
- What is missing or unclear
- Suggested acceptance framing (plan-level)

## 4. Missing or Unaddressed Edge Cases
- Scenario description
- Why it matters at the planning level
- Suggested consideration to add

## 5. Spec Alignment & Consistency Checks
- Unmapped plan steps (if any)
- Unaddressed spec requirements (if any)
- Observed inconsistencies

## 6. Improvement Recommendations
- Prioritized list of plan-level improvements

## 7. Planning Risk Assessment
- Risks if the plan proceeds unchanged
- Severity level (Low / Medium / High)
```

## Non-Goals (Absolutely Forbidden)

- No code generation
- No task creation
- No architecture redesign
- No feature invention
- No speculative assumptions
- No modification of the original plan document
- No introduction of implementation details unless already present in the plan

## Helper Tools

The skill includes:
- `scripts/analyze_plan.sh` - Command-line helper for initial pattern detection
- `references/analysis-patterns.md` - Detailed patterns for quality assessment
- `assets/report-template.md` - Template for output structure