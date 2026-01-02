---
id: 006
title: "Tasks Quality Improver Skill Creation"
stage: "general"
date_iso: "2026-01-03"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "create-tasks-quality-improver-skill"
labels: ["skill", "tasks", "quality", "improvement"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .claude/skills/tasks-quality-improver/SKILL.md
  - .claude/skills/tasks-quality-improver/scripts/improve_tasks.sh
  - .claude/skills/tasks-quality-improver/references/improvement-patterns.md
  - .claude/skills/tasks-quality-improver/assets/improvement-template.md
tests_yaml: |
  - "Skill functionality verified with test tasks and analysis report"
  - "Script execution confirmed"
prompt_text: |
  You are a Senior Spec-Driven Software Architect and Task Decomposition Specialist.

  Your task is to design and implement a reusable internal skill named:

  "Tasks Quality Improver Skill"

  This skill operates STRICTLY within a Spec-Driven Development workflow and MUST be used ONLY AFTER a Tasks Quality Analyzer Skill has produced its analysis report.

  ────────────────────────────────────────
  PRIMARY OBJECTIVE
  ────────────────────────────────────────
  The Tasks Quality Improver Skill takes:
  1) A tasks.md file
  2) The output report of the Tasks Quality Analyzer Skill
  3) (Optional) The related spec.md and constitution.md

  Its purpose is to produce an IMPROVED version of the tasks.md file by addressing the identified quality issues, while strictly preserving original scope and intent.

  The skill must:
  ✔ Improve unclear or ambiguous tasks
  ✔ Add missing tasks that are strictly implied by the spec
  ✔ Refine vague or oversized tasks into atomic, implementable units
  ✔ Add or improve edge-case tasks
  ✔ Incorporate and refine recommended improvements
  ✔ Elevate tasks.md to an ADVANCED, implementation-ready level

  ────────────────────────────────────────
  STRICT NON-HALLUCINATION RULES
  ────────────────────────────────────────
  1. Do NOT invent new features.
  2. Do NOT expand scope beyond the provided spec.
  3. Do NOT add tasks for phases not explicitly defined.
  4. Do NOT introduce technologies, tools, or architectures not mentioned.
  5. Every added or modified task MUST be traceable to:
     - the spec.md
     - the analyzer report
     - or an explicit gap in task coverage.

  If justification cannot be found, DO NOT add the task.

  ────────────────────────────────────────
  INPUT CONTRACT
  ────────────────────────────────────────
  The skill receives:
  - tasks.md (original)
  - Tasks Quality Analyzer Report
  - Optional spec.md
  - Optional constitution.md

  If analyzer output is missing or incomplete:
  → The skill must refuse to proceed and explain why.

  ────────────────────────────────────────
  OUTPUT CONTRACT
  ────────────────────────────────────────
  The skill MUST output:
  - A fully rewritten and improved tasks.md
  - Clearly structured
  - Implementation-ready
  - Atomic and testable tasks
  - Proper ordering and dependencies

  The output MUST be valid Markdown ONLY.

  ────────────────────────────────────────
  TASK IMPROVEMENT RESPONSIBILITIES
  ────────────────────────────────────────

  ### A. Improve Unclear or Ambiguous Tasks
  - Rewrite vague task descriptions into precise, objective statements
  - Remove subjective language (e.g., "properly", "nicely", "handle well")
  - Clarify inputs, outputs, and expected behavior
  - Ensure each task has a single responsibility

  ### B. Add Missing Tasks
  Add tasks ONLY when:
  - Analyzer explicitly flagged missing coverage
  - Spec logically requires preparatory or supporting tasks
  - Edge-case handling is required but missing

  Each added task MUST:
  - Reference the originating requirement
  - Be minimal and justified
  - Fit naturally into the task sequence

  ### C. Improve Task Granularity
  - Split oversized tasks into atomic units
  - Ensure tasks are small enough to be implemented in a single Claude Code run
  - Avoid multi-concern tasks
  - Avoid implementation details beyond task scope

  ### D. Improve Edge Case Coverage
  Add or refine tasks to handle:
  - Invalid inputs
  - Empty states
  - Boundary conditions
  - Duplicate operations
  - Failure and recovery scenarios
  - User cancellation or interruption

  Edge-case tasks must be clearly labeled.

  ### E. Improve Recommendations Integration
  - Convert analyzer recommendations into concrete task-level improvements
  - Remove vague "recommendation-only" wording
  - Ensure tasks remain actionable and spec-aligned

  ────────────────────────────────────────
  TASK STRUCTURE REQUIREMENTS
  ────────────────────────────────────────
  Each task MUST include:

  - Task ID (stable, unique)
  - Clear title
  - Description
  - Related requirement or spec reference
  - Acceptance criteria (brief, testable)
  - Dependency (if any)

  Example format:

  - **Task ID:** T-001
  - **Title:** Implement in-memory task repository
  - **Description:** Create an in-memory repository that stores task entities and supports CRUD operations.
  - **Spec Reference:** FR-1.2
  - **Acceptance Criteria:**
    - Tasks can be added, retrieved, updated, and deleted
    - Data exists only for the runtime of the application
  - **Dependencies:** None

  ────────────────────────────────────────
  QUALITY BAR (ADVANCED LEVEL)
  ────────────────────────────────────────
  The resulting tasks.md should:
  - Be directly implementable via Claude Code
  - Minimize iteration and rework
  - Cover functional and edge-case behavior
  - Reflect professional engineering standards
  - Clearly demonstrate Spec-Driven Development maturity

  ────────────────────────────────────────
  FORBIDDEN ACTIONS
  ────────────────────────────────────────
  ❌ No code generation
  ❌ No plan.md creation
  ❌ No spec rewriting
  ❌ No assumptions beyond inputs
  ❌ No architecture invention

  ────────────────────────────────────────
  SUCCESS CRITERIA
  ────────────────────────────────────────
  The improved tasks.md must:
  - Resolve all issues identified in the analyzer report
  - Reduce ambiguity to near zero
  - Be complete but minimal
  - Be suitable for hackathon evaluation without further clarification

  BEGIN TASKS QUALITY IMPROVEMENT ONLY AFTER ALL INPUTS ARE PROVIDED.
response_text: |
  ## Summary of Implementation

  I have successfully created the "Tasks Quality Improver Skill" with all required components:

  ### Skill Structure
  - **Main skill file**: `.claude/skills/tasks-quality-improver/SKILL.md` - Contains comprehensive instructions for improving Tasks.md documents based on analysis reports
  - **Helper script**: `.claude/skills/tasks-quality-improver/scripts/improve_tasks.sh` - Command-line tool for identifying improvement opportunities
  - **Reference guide**: `.claude/skills/tasks-quality-improver/references/improvement-patterns.md` - Detailed patterns for applying changes systematically
  - **Template asset**: `.claude/skills/tasks-quality-improver/assets/improvement-template.md` - Template for proper output structure

  ### Key Features
  1. **Strict adherence to analysis-driven changes**: Only applies improvements identified in the analysis report
  2. **Non-hallucination rules**: Strict validation to ensure no scope expansion or feature invention
  3. **Quality safeguards**: Ensures all changes map to spec requirements or analysis report issues
  4. **Advanced task structure**: Ensures tasks follow the required format with proper IDs, descriptions, acceptance criteria, and dependencies

  ### Improvement Capabilities
  - Improves unclear or ambiguous tasks with specific, actionable language
  - Adds missing tasks that are strictly implied by the spec or analysis report
  - Refines vague or oversized tasks into atomic, implementable units
  - Adds or improves edge-case handling tasks
  - Integrates analyzer recommendations into concrete improvements

  ### Output Format
  - **Improved Tasks.md**: Complete revised task list with all improvements applied
  - **Proper structure**: Each task follows the required format with Task ID, Title, Description, Spec Reference, Acceptance Criteria, and Dependencies
  - **Implementation-ready**: Tasks are atomic and suitable for direct implementation

  ### Quality Validation
  - All changes traceable to specific issues in the analysis report
  - Original intent and scope strictly preserved
  - Constitution rules compliance maintained
  - No unauthorized feature additions or scope expansion

  The skill is designed to work as a perfect complement to the Tasks Quality Analyzer Skill, taking the analysis report as input and producing an improved task list that addresses all identified issues while maintaining strict adherence to the original requirements and constraints. The resulting tasks are advanced, implementation-ready, and suitable for hackathon evaluation without further clarification.
outcome: "Tasks Quality Improver Skill successfully created with all required components: main SKILL.md, improvement script, reference patterns, and output template."
evaluation: "The skill meets all requirements: strict adherence to analysis-driven changes, non-hallucination rules, advanced task structure, and quality validation."
---