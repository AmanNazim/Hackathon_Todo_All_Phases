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

A specification is acceptable ONLY if it contains clear acceptance criteria, comprehensive scope definition, explicit constraints, and verifiable requirements. Plans MUST be rejected if they exceed Phase I scope boundaries, violate architectural principles, or introduce unauthorized technologies. Tasks are considered incomplete if they lack clear dependencies, measurable acceptance criteria, or proper test definitions. Claude Code MUST self-correct outputs that violate architectural constraints, introduce unauthorized features, or fail to meet quality standards. Hallucinated features, unauthorized capabilities, or scope creep MUST be immediately identified and corrected as violations. Code quality MUST meet Python best practices including proper error handling, input validation, and maintainable structure.

## Required Deliverables

The constitution MUST enforce generation of the following deliverables:

- `constitution.md` (this file)
- `/specs/phase-1/specification.md` containing the Phase I specification
- `/specs/phase-1/plan.md` containing the Phase I implementation plan
- `/specs/phase-1/tasks.md` containing the Phase I tasks
- `/specs/history/` containing all spec iterations
- `/src/` Python source directory
- `README.md` (setup + usage)
- `CLAUDE.md` (Claude Code instructions)

All deliverables MUST comply with the specifications, plans, and tasks defined in this constitution.

## Future Compatibility Guarantees

The system architecture MUST maintain forward compatibility with future phases through proper abstraction layers and clean interfaces. Future compatibility is a design guarantee, not an implemented feature. The codebase MUST be structured to accommodate persistence, web interfaces, and advanced features in future phases without requiring fundamental architectural changes to the core domain model. Extension points MUST be planned with appropriate abstractions but remain unimplemented until required by future phases. The system MUST follow industry-standard patterns that enable seamless migration to Phase II+ architectures while maintaining current functionality. Dependency management using UV MUST support gradual evolution without breaking changes to core domain logic. Package structure and module organization MUST facilitate future expansion while maintaining current requirements.