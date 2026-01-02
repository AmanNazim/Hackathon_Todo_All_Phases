---
id: 003
title: "Plan Quality Analyzer Skill Creation"
stage: "general"
date_iso: "2026-01-03"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-plan-quality-analyzer-skill"
labels: ["skill", "plan", "quality", "analysis"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/plan-quality-analyzer/SKILL.md
  - .claude/skills/plan-quality-analyzer/scripts/analyze_plan.sh
  - .claude/skills/plan-quality-analyzer/references/analysis-patterns.md
  - .claude/skills/plan-quality-analyzer/assets/report-template.md
tests_yaml: |
  - "Skill functionality verified with test plan"
  - "Script execution confirmed"
prompt_text: |
  You are a Senior Spec-Driven Software Architect and Software Planning Quality Engineer.

  Your task is to design and implement a reusable internal skill named:

  "Plan Quality Analyzer Skill"

  This skill operates within a strict Spec-Driven Development workflow.
  It evaluates PLAN documents ONLY (e.g., plan.md) and must never act as a spec generator or task generator.

  ────────────────────────────────────────
  PRIMARY OBJECTIVE
  ────────────────────────────────────────
  The Plan Quality Analyzer Skill analyzes a given plan document and produces a structured quality assessment report that validates whether the plan is:
  - Clear
  - Complete
  - Internally consistent
  - Faithful to the governing specification

  The skill must:
  ✔ Detect unclear or vague plan steps
  ✔ Identify missing or implicit acceptance criteria for plan outcomes
  ✔ Detect missing or unaddressed edge cases at the planning level
  ✔ Recommend plan-level improvements (not spec-level, not code-level)

  The skill MUST NOT:
  - Modify the plan
  - Invent features
  - Expand scope
  - Introduce implementation details unless already present in the plan

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill receives:
  - One plan document (Markdown)
  - Optional specification document (for alignment checks)
  - Optional constitution.md (for rule validation)

  If a referenced document is missing:
  - Explicitly report the limitation
  - Do NOT assume its contents

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The skill MUST produce a structured Markdown analysis report with the following sections:

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

  ────────────────────────────────────────
  ANALYSIS RULES (STRICT)
  ────────────────────────────────────────
  1. Analyze ONLY what is explicitly written in the plan.
  2. Do NOT infer requirements not present in the plan or spec.
  3. Do NOT add tasks, code, or architecture.
  4. Do NOT redesign the system.
  5. Do NOT introduce future phases or features.
  6. Use precise, neutral, technical language.
  7. Clearly distinguish between:
     - Plan clarity issues
     - Spec gaps (if detected)
     - Plan–spec misalignment

  ────────────────────────────────────────
  QUALITY CHECKS TO PERFORM
  ────────────────────────────────────────

  ### A. Plan Clarity Analysis
  Detect:
  - Vague or abstract steps (e.g., "handle errors", "optimize flow")
  - Missing entry/exit criteria for plan steps
  - Overloaded steps that mix multiple responsibilities
  - Unclear sequencing or dependencies
  - Undefined plan terminology

  ### B. Acceptance Criteria Analysis (Plan-Level)
  For each major plan step:
  - Check whether the success condition is defined
  - Detect missing "done" definitions
  - Identify steps that cannot be validated or reviewed
  - Suggest how acceptance criteria could be clarified (without writing tests)

  ### C. Edge Case Coverage Analysis
  Identify missing planning considerations for:
  - Failure paths
  - Invalid or partial inputs
  - Rollback or recovery logic
  - User cancellation or interruption
  - Boundary conditions relevant to the plan's scope

  ### D. Spec Alignment & Consistency Checks
  If a spec is provided:
  - Verify every plan step maps to one or more spec requirements
  - Detect orphan plan steps not justified by the spec
  - Detect spec requirements not addressed in the plan
  - Flag inconsistencies or contradictions

  If no spec is provided:
  - Clearly state alignment cannot be fully verified

  ────────────────────────────────────────
  RECOMMENDATION RULES
  ────────────────────────────────────────
  Recommendations must:
  - Stay strictly at the planning level
  - Improve clarity, traceability, or completeness
  - Be phrased as suggestions, not directives
  - Avoid implementation or coding advice
  - Avoid expanding scope

  ────────────────────────────────────────
  OUTPUT FORMAT (MANDATORY)
  ────────────────────────────────────────
  Return ONLY valid Markdown.

  Use the following structure exactly:

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

  ────────────────────────────────────────
  NON-GOALS (ABSOLUTELY FORBIDDEN)
  ────────────────────────────────────────
  ❌ No code generation
  ❌ No task creation
  ❌ No architecture redesign
  ❌ No feature invention
  ❌ No speculative assumptions

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  The output must enable:
  - Cleaner, reviewable plans
  - Stronger spec-to-plan traceability
  - Reduced downstream rework
  - Fewer Claude Code iteration loops
  - Compliance with hackathon evaluation standards

  BEGIN ANALYSIS ONLY AFTER THE PLAN DOCUMENT IS PROVIDED.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Plan Quality Analyzer Skill" with all required components:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/plan-quality-analyzer/SKILL.md` - Contains comprehensive instructions for analyzing plan documents
  - **Helper script**: `.claude/skills/plan-quality-analyzer/scripts/analyze_plan.sh` - Command-line tool for pattern detection in plan documents
  - **Reference guide**: `.claude/skills/plan-quality-analyzer/references/analysis-patterns.md` - Detailed patterns for quality assessment
  - **Template asset**: `.claude/skills/plan-quality-analyzer/assets/report-template.md` - Output structure template

  ### Key Features
  1. **Strict plan-only analysis**: Operates exclusively on plan documents, never acting as a spec or task generator
  2. **Comprehensive analysis**: Covers clarity issues, acceptance criteria, edge cases, and spec alignment
  3. **Structured output**: Follows the exact 7-section format specified in your requirements
  4. **Quality safeguards**: Includes all analysis rules, recommendation guidelines, and non-goals

  ### Analysis Capabilities
  - Detects vague or abstract plan steps
  - Identifies missing acceptance criteria for plan outcomes
  - Finds unaddressed edge cases at the planning level
  - Verifies alignment with governing specifications
  - Provides planning risk assessment with severity levels

  ### Helper Tools
  - The bash script can perform initial pattern detection for common issues in plan documents
  - Reference materials provide detailed analysis patterns for plan quality
  - Template ensures consistent output format

  The skill is ready to use and will help evaluate plan documents for quality issues before implementation, following all the strict rules and requirements specified.
outcome: "Plan Quality Analyzer Skill successfully created with all required components: main SKILL.md, analysis script, reference patterns, and output template."
evaluation: "The skill meets all requirements: strict plan-only analysis, comprehensive quality checks, structured output format, and quality safeguards."
---