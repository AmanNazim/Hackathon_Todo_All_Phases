---
id: 001
title: "Spec Quality Analyzer Skill Creation"
stage: "general"
date_iso: "2026-01-02"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-spec-quality-analyzer-skill"
labels: ["skill", "spec", "quality", "analysis"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/spec-quality-analyzer/SKILL.md
  - .claude/skills/spec-quality-analyzer/scripts/analyze_spec.sh
  - .claude/skills/spec-quality-analyzer/references/analysis-patterns.md
  - .claude/skills/spec-quality-analyzer/assets/report-template.md
tests_yaml: |
  - "Skill functionality verified with test spec"
  - "Script execution confirmed"
prompt_text: |
  You are a Senior Spec-Driven Software Architect and Quality Engineering Specialist.

  Your task is to design and implement a reusable internal skill named:

  "Spec Quality Analyzer Skill"

  This skill is part of a Spec-Driven Development workflow and must operate STRICTLY on provided specification documents.
  It must NOT invent requirements, features, phases, or functionality beyond what is explicitly present in the input spec.

  ────────────────────────────────────────
  PRIMARY OBJECTIVE
  ────────────────────────────────────────
  The Spec Quality Analyzer Skill evaluates a given specification document and produces a structured, actionable quality analysis that helps improve the spec BEFORE planning or implementation.

  The skill must:
  ✔ Detect unclear, ambiguous, or underspecified requirements
  ✔ Suggest missing or incomplete acceptance criteria
  ✔ Identify missing or weak edge cases
  ✔ Recommend concrete, spec-level improvements
  ✔ Preserve the original intent of the specification
  ✔ Never hallucinate new features or scope

  This skill MUST NOT modify the spec directly.
  It only analyzes and reports.

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill receives:
  - One specification document (Markdown)
  - Optional project constitution.md (for rule validation)

  The input spec may include:
  - Requirements
  - User stories
  - Functional descriptions
  - Constraints
  - Acceptance criteria (partial or complete)

  If a section is missing, the skill should report that absence explicitly.

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The skill MUST produce a structured Markdown report with the following sections:

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

  ────────────────────────────────────────
  ANALYSIS RULES (STRICT)
  ────────────────────────────────────────
  1. Do NOT assume user intent beyond the text.

  3. Do NOT reference future phases unless explicitly in the spec.
  4. Do NOT reference implementation details unless the spec explicitly includes them.
  5. Do NOT rewrite the spec — only analyze.
  6. Use neutral, professional, technical language.
  7. If something is ambiguous, clearly explain why it is ambiguous.

  ────────────────────────────────────────
  QUALITY CHECKS TO PERFORM
  ────────────────────────────────────────

  ### A. Clarity Analysis
  Detect:
  - Vague language (e.g., "should", "fast", "user-friendly")
  - Missing constraints (limits, formats, conditions)
  - Undefined terms or concepts
  - Implicit assumptions
  - Mixed responsibilities in single requirements

  ### B. Acceptance Criteria Analysis
  For each functional requirement:
  - Check if acceptance criteria exist
  - Validate measurability and testability
  - Detect missing Given/When/Then logic
  - Identify criteria that are too broad or subjective

  ### C. Edge Case Analysis
  Identify missing coverage for:
  - Invalid input
  - Empty states
  - Boundary conditions
  - Duplicate actions
  - Failure scenarios
  - User cancellation or interruption
  - Conflicting operations

  ### D. Consistency Checks
  Verify:
  - Terminology consistency
  - Requirement numbering consistency
  - Alignment with constitution rules (if provided)
  - No contradictions within the spec

  ────────────────────────────────────────
  RECOMMENDATION RULES
  ────────────────────────────────────────
  Recommendations must:
  - Be phrased as suggestions, not commands
  - Remain at the specification level
  - Be minimal and precise
  - Improve clarity, testability, or completeness
  - Avoid implementation or tooling advice

  ────────────────────────────────────────
  OUTPUT FORMAT (MANDATORY)
  ────────────────────────────────────────
  Return ONLY valid Markdown.

  Use the following structure exactly:

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

  ────────────────────────────────────────
  NON-GOALS (ABSOLUTELY FORBIDDEN)
  ────────────────────────────────────────
  ❌ No code generation
  ❌ No planning or task breakdown
  ❌ No speculative behavior

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  The output should enable:
  - A clearer spec
  - Better planning
  - Fewer Claude Code iterations
  - Reduced rework

  BEGIN ANALYSIS ONLY AFTER THE SPEC IS PROVIDED.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Spec Quality Analyzer Skill" with all required components:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/spec-quality-analyzer/SKILL.md` - Contains comprehensive instructions for analyzing spec documents
  - **Helper script**: `.claude/skills/spec-quality-analyzer/scripts/analyze_spec.sh` - Command-line tool for pattern detection
  - **Reference guide**: `.claude/skills/spec-quality-analyzer/references/analysis-patterns.md` - Detailed patterns for quality assessment
  - **Template asset**: `.claude/skills/spec-quality-analyzer/assets/report-template.md` - Output structure template

  ### Key Features
  1. **Strict adherence to requirements**: The skill operates only on provided specification documents and does not invent new features or scope
  2. **Comprehensive analysis**: Covers clarity issues, acceptance criteria, edge cases, and consistency checks
  3. **Structured output**: Follows the exact 7-section format specified in your requirements
  4. **Quality guidelines**: Includes all analysis rules, recommendation guidelines, and non-goals

  ### Analysis Capabilities
  - Detects vague language and missing constraints
  - Identifies missing or weak acceptance criteria
  - Finds unaddressed edge cases
  - Verifies consistency and completeness
  - Provides risk assessment with severity levels

  ### Helper Tools
  - The bash script can perform initial pattern detection for common issues
  - Reference materials provide detailed analysis patterns
  - Template ensures consistent output format

  The skill is ready to use and will help evaluate specification documents for quality issues before planning or implementation, following all the strict rules and requirements specified.
outcome: "Spec Quality Analyzer Skill successfully created with all required components: main SKILL.md, analysis script, reference patterns, and output template."
evaluation: "The skill meets all requirements: strict adherence to spec-only analysis, proper output format, comprehensive analysis capabilities, and quality safeguards."
---