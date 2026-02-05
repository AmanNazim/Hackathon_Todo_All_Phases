---
id: 1
title: refactor-command-parser-layer
stage: refactor
date: 2026-01-10
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: developer
command: sp.implement
labels: ["parser", "refactoring", "validation", "ux"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/e/q4-sat-6-to-9/claude-code-development/hackathon-II-todo-all-phases/phase-I-todo-in-memory-console-app/src/cli_todo_app/parsers/command_parser.py
tests: []
---

# Refactor Command Parser Layer

## Overview
Refactored the command parsing layer to make it predictable, robust against edge cases, UX-clear, and future-proof for menu-based flows.

## Changes Made

### 1. Implemented Robust Tokenizer
- Created `tokenize_command` function that handles different quote types (double quotes, single quotes, backticks)
- Added support for angle bracket tags (`<tag>`)
- Properly handles escaped characters and nested quotes

### 2. Enhanced Add Command Parsing
- Require quoted titles (`"Title"`, `'Title'`, or `Title`)
- Support optional descriptions
- Handle multiple tag formats
- Validate that titles are not empty and meet length requirements

### 3. Implemented Identifier Resolution
- Support for task numbers (1, 2, 3...) for delete/update/complete/incomplete commands
- Exact title match resolution (case-insensitive)
- UUID support maintained
- Added `resolve_identifier_to_uuid` method for conversion

### 4. Added Tag Parsing Functionality
- Parse angle bracket tags (`<tag>`)
- Support multiple tags per command
- Validate for empty tags (`<>` is rejected)
- Convert tags to lowercase internally

### 5. Improved Update Command
- Handle partial updates (any combination of title, description, tags)
- Tag replacement only when explicitly provided
- Empty quotes (`""`) mean clear field

### 6. Enhanced Error Messaging
- Actionable help with correct usage examples
- Format: `❌ Invalid add command format` with `💡 Correct usage:` examples
- No stack traces in error messages

### 7. Maintained Backward Compatibility
- Kept legacy parameter names (`task_id`) alongside new ones (`identifier`)
- Parser output maps cleanly to existing function signatures
- Logging remains intact

## Validation
- Commands must be case-insensitive
- Titles must be wrapped in quotes for add command
- Proper validation for all command formats
- Error messages are helpful and instructive

## Success Criteria Met
- No command relies on positional guessing
- No user is required to type UUIDs (task numbers and title matching supported)
- Titles/descriptions are always unambiguous
- Tags are correctly parsed and stored
- Errors are friendly and instructive