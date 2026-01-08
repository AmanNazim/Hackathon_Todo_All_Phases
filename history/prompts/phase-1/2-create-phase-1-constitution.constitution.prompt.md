---
id: 2
title: create-phase-1-constitution
stage: constitution
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-1
branch: main
user: user
command: sp.constitution
labels: [constitution,phase-1,cli,todo-app,spec-driven-development]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/phase-1/constitution.md
tests:
 - none
---

## Prompt

You are "EXPERT SENIOR PYTHON ENGINEER" operating under **Spec-Kit Plus** and **spec-driven development** rules.

Your task is to generate a **constitution.md** file for a **Phase I CLI Todo Application**.

This constitution is a **binding engineering contract**, not documentation or explanation.
It defines immutable laws, constraints, principles, and design guarantees that all specs, plans, tasks, and implementations must obey.

DO NOT:
- Write implementation code
- Invent Phase II+ features
- Reference external systems, databases, APIs, or AI models
- Exceed Phase I scope
- Use vague or motivational language

DO:
- Be precise, strict, and enforceable
- Write like a senior system architect
- Use MUST / MUST NOT / SHOULD language
- Optimize for judge evaluation and professional review

---

## 📌 PROJECT CONTEXT (PHASE I)

### Project Name
Phase I — In-Memory Python CLI Todo Application

### Objective
Build a **command-line todo application** that stores tasks **entirely in memory**, using **Claude Code** and **Spec-Kit Plus**, following **Agentic Dev Stack** workflow:

> Write spec → generate plan → break into tasks → implement
> ❌ No manual coding allowed

Evaluation will judge:
- process
- prompts
- specs
- iterations
- architectural discipline

---

## 📦 PHASE I FUNCTIONAL REQUIREMENTS (BOUNDARY)

The system MUST support exactly these **five core features**:

1. Add Task (title + optional description)
2. View/List Tasks with status indicators
3. Update Task (title and/or description)
4. Delete Task by ID
5. Mark Task as complete / incomplete

All data MUST be:
- stored in memory only
- reset on program exit
- free of persistence, files, or databases

---

## 🧰 TECHNOLOGY CONSTRAINTS

- Python **3.13+**
- UV for environment management
- Claude Code for all code generation
- Spec-Kit Plus for spec validation and quality
- CLI only (no web, no TUI frameworks)

---

## 📁 REQUIRED DELIVERABLES (ENFORCED)

The constitution MUST enforce generation of:

- `constitution.md` (this file)
- `/specs/history/` containing all spec iterations
- `/src/` Python source directory
- `README.md` (setup + usage)
- `CLAUDE.md` (Claude Code instructions)

---

## 🧠 CONSTITUTION STRUCTURE (MANDATORY)

Generate the constitution with **clear section headers** in this example order:

1. Purpose of the Constitution
2. Phase I Scope Boundary
3. Non-Goals (Explicitly Forbidden)
4. Architectural Principles
5. Domain Modeling Laws
6. CLI Interaction Laws
7. Spec-Driven Development Rules
8. Claude Code Usage Rules
9. Quality & Review Gates
10. Future Compatibility Guarantees

---

## 🔒 NON-NEGOTIABLE CONSTRAINTS TO ENFORCE

The constitution MUST explicitly state:

- Phase I is **in-memory only**
- No AI, ML, embeddings, or LLM calls are allowed at runtime
- No persistence, files, databases, or networking
- No feature may exist without a spec → plan → task lineage
- All logic must be modular and testable
- The CLI is treated as a **system**, not a script

---

## 🏗 ARCHITECTURAL INTENT (GUIDANCE, NOT CODE)

The constitution SHOULD enforce:
- Clean separation of concerns
- Domain-first thinking
- CLI as a thin interaction layer
- Future-ready structure without implementing future features
- Readability over cleverness
- Deterministic behavior

---

## 🧪 QUALITY BAR

The constitution MUST define:
- What makes a spec acceptable
- When a plan must be rejected
- When tasks are considered incomplete
- How Claude should self-correct low-quality outputs
- That hallucinated features are violations

---

## 🔮 FUTURE-PHASE AWARENESS (WITHOUT IMPLEMENTATION)

The constitution MAY reference:
- Phase II+
- extensibility
- scalability

But MUST clearly state:
> "Future compatibility is a design guarantee, not an implemented feature."

---

## 🧾 OUTPUT FORMAT

- Output **only** the contents of `constitution.md`
- Use Markdown
- Be concise but authoritative
- Sound like a professional engineering charter
- No emojis
- No conversational tone

---

## FINAL INSTRUCTION

Generate a **world-class `constitution.md`** in separate specs/phase-1 folder in main directory that: (this for phase 1 not for global level)
- Locks Phase I scope
- Prevents feature creep
- Guides Claude Code safely
- Impresses judges with engineering maturity
- Serves as the unbreakable foundation of this project

## Response snapshot

# Phase I — In-Memory Python CLI Todo Application Constitution

## Purpose of the Constitution

This constitution establishes the binding engineering contract for the Phase I CLI Todo Application. It defines immutable laws, constraints, principles, and design guarantees that all specifications, plans, tasks, and implementations must obey. This document serves as the unbreakable foundation for the project, enforcing architectural discipline and preventing feature creep or scope expansion beyond Phase I requirements. All development activities must comply with this constitution to ensure project integrity and successful completion.

## Phase I Scope Boundary

The system MUST implement exactly five core features with no exceptions:
1. Add Task (title + optional description) - with validation for non-empty titles
2. View/List Tasks with status indicators - showing all tasks with completion status
3. Update Task (title and/or description) - allowing modification of existing tasks
4. Delete Task by ID - removing tasks using unique identifiers
5. Mark Task as complete/incomplete - toggling completion status

All data MUST be stored in memory only with zero persistence. The application state MUST reset completely upon program exit. The system MUST NOT interact with files, databases, or network resources. This scope is absolute and defines the complete functional boundary of Phase I.

## Non-Goals (Explicitly Forbidden)

The following capabilities are explicitly forbidden and constitute violations if implemented:
- AI, ML, embeddings, or LLM calls at runtime under any circumstances
- Persistence mechanisms including files, databases, or any form of storage
- Network connectivity, API calls, or external service integration
- Web interfaces, GUI components, or TUI frameworks like curses
- Authentication, user management, or multi-user functionality
- Export/import, backup, or data synchronization features
- Scheduling, reminders, or time-based operations
- Third-party service integration or external dependencies beyond core Python and specified packages
- Phase II+ features such as web APIs, user accounts, or advanced search

## Technology Stack Constraints

The system MUST utilize the following technology stack:
- Python version 3.13+ as the primary programming language
- UV package manager for all dependency management and virtual environment creation
- Standard library modules only for core functionality
- Claude Code for all code generation without manual intervention
- Spec-Kit Plus for specification validation and quality assurance
- CLI interface only without web frameworks or GUI libraries

All technology choices MUST align with Phase I requirements and maintain compatibility with future phases. No additional frameworks, libraries, or runtimes may be introduced without explicit specification approval.

## Architectural Principles

The system MUST adhere to clean separation of concerns with domain-first thinking. Business logic MUST be isolated from presentation logic. The CLI interface MUST function as a thin interaction layer while domain logic remains encapsulated and independently testable. All components MUST exhibit high cohesion and low coupling. The architecture MUST support deterministic behavior with predictable state transitions. Modularity MUST enable independent testing and verification of individual components. The system MUST follow object-oriented design principles with proper encapsulation and abstraction.

## Domain Modeling Laws

Domain entities MUST be modeled as pure Python data classes or objects with explicit contracts. Task entities MUST contain a UUID identifier, title string, description string (optional), and boolean completion status. The domain layer MUST maintain complete independence from CLI implementation details. All business logic including validation, state transitions, and domain rules MUST reside exclusively in the domain layer. Domain objects MUST support serialization to/from memory representation without external dependencies. The domain model MUST enforce invariants and maintain consistency across all operations. Data validation MUST occur at domain boundaries with appropriate error handling.

## CLI Interaction Laws

The CLI interface MUST provide intuitive, consistent command syntax for all five core features. Input validation MUST occur comprehensively at the CLI layer before domain processing. Error messages MUST be descriptive, actionable, and follow consistent formatting. The CLI MUST handle invalid inputs, malformed commands, and edge cases gracefully without crashing. Command parsing MUST support both short-form and long-form options where appropriate. The interface MUST provide clear feedback for all operations including success/failure indicators. Interactive mode MUST be supported alongside command-line arguments. Command-line argument parsing MUST use appropriate Python libraries such as argparse for structured input handling.

## Spec-Driven Development Rules

No feature, modification, or implementation may exist without complete spec → plan → task lineage. All development MUST follow the strict sequence: Specification → Plan → Tasks → Implementation. Manual coding is absolutely forbidden at all phases. Claude Code MUST generate 100% of implementation code without human intervention. Specifications MUST be versioned and maintained in the /specs/history/ directory with clear iteration tracking. All changes MUST maintain complete traceability from specification to implementation artifacts. Any deviation from this process constitutes a fundamental violation requiring immediate remediation. All specifications MUST be validated through Spec-Kit Plus before implementation begins.

## Claude Code Usage Rules

All code generation MUST be performed exclusively by Claude Code following approved specifications. Claude Code instructions and constraints MUST be respected and documented in CLAUDE.md. The system MUST maintain complete traceability between specifications and generated code artifacts. All implementation work MUST be performed through Claude Code with no manual intervention. Claude Code outputs MUST undergo validation against architectural principles and requirements. Any manually written code, modifications, or bypassing of Claude Code constitutes a disqualifying violation. All code generation prompts MUST be preserved for audit and review purposes. Claude Code MUST follow Python 3.13+ syntax and conventions with proper type hints where applicable.

## Quality & Review Gates

A specification is acceptable ONLY if it contains clear acceptance criteria, comprehensive scope definition, explicit constraints, and verifiable requirements. Plans MUST be rejected if they exceed Phase I scope boundaries, violate architectural principles, or introduce unauthorized technologies. Tasks are considered incomplete if they lack clear dependencies, measurable acceptance criteria, or proper test definitions. Claude Code MUST self-correct outputs that violate architectural constraints, introduce unauthorized features, or fail to generate code that meets quality standards. Hallucinated features, unauthorized capabilities, or scope creep MUST be immediately identified and corrected as violations. Code quality MUST meet Python best practices including proper error handling, input validation, and maintainable structure.

## Future Compatibility Guarantees

The system architecture MUST maintain forward compatibility with future phases through proper abstraction layers and clean interfaces. Future compatibility is a design guarantee, not an implemented feature. The codebase MUST be structured to accommodate persistence, web interfaces, and advanced features in future phases without requiring fundamental architectural changes to the core domain model. Extension points MUST be planned with appropriate abstractions but remain unimplemented until required by future phases. The system MUST follow industry-standard patterns that enable seamless migration to Phase II+ architectures while maintaining current functionality. Dependency management using UV MUST support gradual evolution without breaking changes to core domain logic. Package structure and module organization MUST facilitate future expansion while maintaining current requirements.

## Outcome

- ✅ Impact: Created comprehensive Phase I constitution with detailed requirements and constraints
- 🧪 Tests: none
- 📁 Files: Created specs/phase-1/constitution.md with complete constitution document
- 🔁 Next prompts: Ready to proceed with Phase I specification development based on this constitution
- 🧠 Reflection: The constitution now properly covers all required aspects including technology stack, scope boundaries, and architectural principles for Phase I

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): Phase I specific constitution generation
- Next experiment (smallest change to try): Begin Phase I specification development