---
id: 005
title: "Tasks Quality Analyzer Skill Creation"
stage: "general"
date_iso: "2026-01-03"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-tasks-quality-analyzer-skill"
labels: ["skill", "tasks", "quality", "analysis"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/tasks-quality-analyzer/SKILL.md
  - .claude/skills/tasks-quality-analyzer/scripts/analyze_tasks.sh
  - .claude/skills/tasks-quality-analyzer/references/analysis-patterns.md
  - .claude/skills/tasks-quality-analyzer/assets/report-template.md
tests_yaml: |
  - "Skill functionality verified with test tasks"
  - "Script execution confirmed"
prompt_text: |
  You are a Senior Spec-Driven Software Architect and Delivery Quality Engineer specializing in task decomposition, execution readiness, and engineering rigor.

  Your task is to design and implement a reusable internal skill named:

  "Tasks Quality Analyzer Skill"

  This skill operates exclusively on Tasks.md documents generated as part of a Spec-Driven Development workflow.

  ────────────────────────────────────────
  PRIMARY OBJECTIVE
  ────────────────────────────────────────
  The Tasks Quality Analyzer Skill evaluates a Tasks.md document to determine whether it is:
  - Clear
  - Complete
  - Executable
  - Properly scoped
  - Aligned with upstream specs and plans

  The skill must:
  ✔ Detect unclear, ambiguous, or underspecified tasks
  ✔ Identify missing tasks required for completeness
  ✔ Detect overly vague, overly broad, or non-actionable tasks
  ✔ Identify missing edge-case-related tasks
  ✔ Recommend concrete task-level improvements
  ✔ Preserve the original scope and intent of the project
  ✔ NEVER invent features or expand scope beyond the source documents

  This skill analyzes tasks ONLY.
  It does NOT generate code, plans, or specs.

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill receives:
  - One Tasks.md document (Markdown)
  - Optional references to:
    - spec.md
    - plan.md
    - constitution.md

  If reference documents are provided, they may ONLY be used for alignment checks.
  They MUST NOT be used to invent new scope.

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The skill MUST produce a structured Markdown report that evaluates the quality and readiness of the task list.

  The output MUST NOT modify the original tasks.
  It MUST only analyze and recommend.

  ────────────────────────────────────────
  STRICT ANALYSIS RULES
  ────────────────────────────────────────
  1. Do NOT hallucinate missing features.
  2. Do NOT assume implementation details.
  3. Do NOT merge tasks or rewrite them.
  4. Do NOT generate new code-level tasks.
  5. Do NOT infer future phases or enhancements.
  6. If uncertainty exists, explain it explicitly.
  7. Use neutral, technical, professional language.

  ────────────────────────────────────────
  ANALYSIS DIMENSIONS (MANDATORY)
  ────────────────────────────────────────

  ### A. Task Clarity Analysis
  Detect tasks that:
  - Use vague verbs (e.g., "handle", "support", "manage")
  - Lack clear inputs, outputs, or success conditions
  - Combine multiple responsibilities
  - Depend on undefined behavior
  - Cannot be validated or verified

  ### B. Task Completeness Analysis
  Evaluate whether tasks cover:
  - All functional requirements from the spec (if provided)
  - All architectural components from the plan (if provided)
  - All necessary setup, glue, and orchestration steps
  - Required validation, error handling, and cleanup tasks

  Identify missing tasks ONLY when they are clearly required by the provided documents.

  ### C. Task Granularity Analysis
  Detect:
  - Tasks that are too large to implement in one iteration
  - Tasks that are too small or redundant
  - Tasks that mix design, implementation, and validation

  Recommend appropriate granularity adjustments WITHOUT rewriting tasks.

  ### D. Edge Case Coverage Analysis
  Identify missing tasks related to:
  - Invalid input handling
  - Empty or initial state handling
  - Boundary conditions
  - Error propagation
  - User cancellation or interruption
  - Conflicting or repeated operations

  ### E. Dependency & Ordering Analysis
  Check for:
  - Implicit dependencies between tasks
  - Missing prerequisite tasks
  - Incorrect task ordering assumptions
  - Cyclic dependencies

  ────────────────────────────────────────
  RECOMMENDATION RULES
  ────────────────────────────────────────
  All recommendations MUST:
  - Be task-level (not code-level)
  - Be phrased as suggestions
  - Reference exact task IDs or descriptions
  - Explain WHY the improvement is needed
  - Avoid implementation or tooling advice

  ────────────────────────────────────────
  OUTPUT FORMAT (MANDATORY)
  ────────────────────────────────────────
  Return ONLY valid Markdown using the structure below:

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

  ────────────────────────────────────────
  NON-GOALS (ABSOLUTE PROHIBITIONS)
  ────────────────────────────────────────
  ❌ No code generation
  ❌ No implementation details
  ❌ No plan or spec rewriting
  ❌ No feature expansion
  ❌ No scope creep
  ❌ No hallucinated tasks unrelated to inputs

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  The output should enable:
  - Cleaner task breakdowns
  - Fewer Claude Code execution failures
  - Reduced rework
  - Better phase isolation
  - Stronger alignment with hackathon judging criteria

  BEGIN ANALYSIS ONLY AFTER Tasks.md IS PROVIDED.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Tasks Quality Analyzer Skill" with all required components:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/tasks-quality-analyzer/SKILL.md` - Contains comprehensive instructions for analyzing Tasks.md documents
  - **Helper script**: `.claude/skills/tasks-quality-analyzer/scripts/analyze_tasks.sh` - Command-line tool for pattern detection in task documents
  - **Reference guide**: `.claude/skills/tasks-quality-analyzer/references/analysis-patterns.md` - Detailed patterns for quality assessment
  - **Template asset**: `.claude/skills/tasks-quality-analyzer/assets/report-template.md` - Output structure template

  ### Key Features
  1. **Strict task-only analysis**: Operates exclusively on Tasks.md documents, never generating code, plans, or specs
  2. **Comprehensive analysis**: Covers clarity issues, completeness, granularity, edge cases, and dependencies
  3. **Structured output**: Follows the exact 8-section format specified in your requirements
  4. **Quality safeguards**: Includes all analysis rules, recommendation guidelines, and non-goals

  ### Analysis Capabilities
  - Detects unclear, ambiguous, or underspecified tasks
  - Identifies missing tasks required for completeness
  - Detects overly vague, overly broad, or non-actionable tasks
  - Identifies missing edge-case-related tasks
  - Analyzes task dependencies and ordering
  - Provides risk assessment with severity levels

  ### Helper Tools
  - The bash script can perform initial pattern detection for common issues in task documents
  - Reference materials provide detailed analysis patterns for task quality
  - Template ensures consistent output format

  The skill is ready to use and will help evaluate Tasks.md documents for quality issues before implementation, following all the strict rules and requirements specified.
outcome: "Tasks Quality Analyzer Skill successfully created with all required components: main SKILL.md, analysis script, reference patterns, and output template."
evaluation: "The skill meets all requirements: strict task-only analysis, comprehensive quality checks, structured output format, and quality safeguards."
---