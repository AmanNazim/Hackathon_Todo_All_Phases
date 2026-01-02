---
name: spec-quality-analyzer
description: Analyzes specification documents to identify clarity issues, missing acceptance criteria, unaddressed edge cases, and consistency problems. Provides structured quality analysis with concrete improvement recommendations. Use when evaluating spec documents for quality before planning or implementation.
---

# Spec Quality Analyzer Skill

This skill analyzes specification documents to identify quality issues and provide actionable improvement recommendations. The skill operates STRICTLY on provided specification documents and MUST NOT invent requirements, features, phases, or functionality beyond what is explicitly present in the input spec.

## When to Use This Skill

Use this skill when you need to evaluate a specification document for:
- Clarity and ambiguity issues
- Missing or weak acceptance criteria
- Unaddressed edge cases
- Consistency and completeness problems
- Risk assessment before planning/implementation

## Input Requirements

The skill accepts:
- One specification document (Markdown format)
- Optional project constitution.md for rule validation

The input spec may include:
- Requirements
- User stories
- Functional descriptions
- Constraints
- Acceptance criteria (partial or complete)

If a section is missing, the skill should report that absence explicitly.

## Analysis Process

The skill performs four key analyses:

### 1. Clarity Analysis
Detects:
- Vague language (e.g., "should", "fast", "user-friendly")
- Missing constraints (limits, formats, conditions)
- Undefined terms or concepts
- Implicit assumptions
- Mixed responsibilities in single requirements

### 2. Acceptance Criteria Analysis
For each functional requirement:
- Checks if acceptance criteria exist
- Validates measurability and testability
- Detects missing Given/When/Then logic
- Identifies criteria that are too broad or subjective

### 3. Edge Case Analysis
Identifies missing coverage for:
- Invalid input
- Empty states
- Boundary conditions
- Duplicate actions
- Failure scenarios
- User cancellation or interruption
- Conflicting operations

### 4. Consistency Checks
Verifies:
- Terminology consistency
- Requirement numbering consistency
- Alignment with constitution rules (if provided)
- No contradictions within the spec

## Analysis Rules (Strict)

1. Do NOT assume user intent beyond the text provided in the spec
2. Do NOT reference future phases unless explicitly in the spec
3. Do NOT reference implementation details unless the spec explicitly includes them
4. Do NOT rewrite the spec — only analyze
5. Use neutral, professional, technical language
6. If something is ambiguous, clearly explain why it is ambiguous
7. Never hallucinate new features or scope beyond what's in the spec
8. Preserve the original intent of the specification

## Recommendation Guidelines

Recommendations:
- Are phrased as suggestions, not commands
- Remain at the specification level
- Are minimal and precise
- Improve clarity, testability, or completeness
- Avoid implementation or tooling advice
- Reference exact sections or requirements from the spec

## Quality Analysis Execution

When analyzing a specification:

1. Read the entire specification document first to understand scope and intent
2. Identify and list all functional requirements
3. Perform clarity analysis on each requirement and section
4. Check for acceptance criteria for each functional requirement
5. Identify potential edge cases for each requirement
6. Verify consistency throughout the document
7. Generate improvement recommendations based on findings
8. Assess overall risk if the spec proceeds unchanged
9. Create structured report following the required format

## Output Format Requirements

The skill MUST produce a structured Markdown report with these EXACT sections:

1. Spec Overview
2. Clarity Issues
3. Missing or Weak Acceptance Criteria
4. Missing or Unaddressed Edge Cases
5. Consistency & Completeness Checks
6. Improvement Recommendations
7. Risk Assessment Summary

Each issue MUST:
- Reference the exact section or requirement
- Explain why it is problematic
- Provide a concrete suggestion (not an implementation)

## Output Structure Template

The final output MUST follow this exact structure:

```markdown
# Spec Quality Analysis Report

## 1. Spec Overview
- Summary of spec scope and intent
- Overall quality assessment (Low / Medium / High)

## 2. Clarity Issues
- Issue ID
- Location in spec
- Description of ambiguity
- Suggested clarification

## 3. Missing or Weak Acceptance Criteria
- Related requirement
- What is missing or weak
- Suggested acceptance criteria structure

## 4. Missing or Unaddressed Edge Cases
- Scenario description
- Why it matters
- Suggested edge case to document

## 5. Consistency & Completeness Checks
- Observed inconsistencies
- Missing sections (if any)

## 6. Improvement Recommendations
- Prioritized list of spec-level improvements

## 7. Risk Assessment Summary
- Risks if spec proceeds unchanged
- Severity level (Low / Medium / High)
```

## Non-Goals (Absolutely Forbidden)

- No code generation
- No planning or task breakdown
- No speculative behavior beyond what's in the spec
- No modification of the original spec document
- No invention of new features or scope
- No implementation details unless explicitly in the spec

## Helper Tools

The skill includes:
- `scripts/analyze_spec.sh` - Command-line helper for initial pattern detection
- `references/analysis-patterns.md` - Detailed patterns for quality assessment
- `assets/report-template.md` - Template for output structure