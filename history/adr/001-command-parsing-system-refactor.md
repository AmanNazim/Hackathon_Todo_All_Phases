---
id: 1
title: Command Parsing System Refactor
status: Accepted
date: 2026-01-10
---

# Command Parsing System Refactor

## Context

The CLI Todo Application's command parsing system needed significant refactoring to improve robustness, predictability, and user experience. The original implementation used basic string splitting which was prone to errors and didn't handle complex command formats properly. The system needed to support various quoting styles, tag parsing, and identifier resolution while maintaining backward compatibility.

## Decision

We decided to implement a comprehensive command parsing refactor with the following components:

- **Robust Tokenizer**: A new tokenizer function that handles different quote types (double quotes, single quotes, backticks) and angle bracket tags, similar to shlex but extended for specific requirements
- **Identifier Resolution**: Support for task numbers, exact title matches, and UUIDs for commands like delete/update/complete/incomplete
- **Enhanced Validation**: Strict validation that requires quoted titles for add commands and proper format validation
- **Tag Parsing**: Support for angle bracket tags (`<tag>`) with validation for empty tags
- **Improved Error Messaging**: Actionable error messages with correct usage examples using the format `❌ Invalid command` and `💡 Correct usage:`

## Alternatives Considered

1. **Minimal Changes Approach**: Only fix the most critical parsing issues without major refactoring
   - Pros: Lower risk, faster implementation
   - Cons: Would leave underlying architecture problematic, limited improvement in UX

2. **Complete Parser Rewrite**: Replace the entire parsing system with a formal grammar parser (like ANTLR)
   - Pros: Most robust solution, better for complex future requirements
   - Cons: Higher complexity, potential breaking changes, longer development time

3. **Incremental Refactoring**: Gradually improve the parser over multiple releases
   - Pros: Lower risk, allows for gradual testing
   - Cons: Would leave the system inconsistent during transition period

## Consequences

### Positive
- More predictable and robust command parsing
- Better user experience with clear error messages and suggestions
- Support for advanced features like tags and flexible identifier resolution
- Maintained backward compatibility with existing functionality
- Improved code maintainability and extensibility

### Negative
- Increased complexity in the parsing logic
- Potential for subtle behavioral differences that might affect existing users
- More complex testing requirements

## References

- plan.md: Command Parsing subsystem section
- command_parser.py: Implementation of the refactored parser
- test_parser.py: Test suite for the new parser functionality