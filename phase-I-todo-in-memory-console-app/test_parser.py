#!/usr/bin/env python3
"""
Test script for the refactored command parser
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'phase-I-todo-in-memory-console-app', 'src'))

from cli_todo_app.parsers.command_parser import CommandParser, tokenize_command


def test_tokenizer():
    """Test the new tokenizer functionality"""
    print("Testing tokenizer...")

    # Test different quote types
    test_cases = [
        ('add "Title with spaces" "Description with spaces"', ['add', 'Title with spaces', 'Description with spaces']),
        ("add 'Single quoted title' 'Single quoted desc'", ['add', 'Single quoted title', 'Single quoted desc']),
        ("add `Backtick quoted title` `Backtick quoted desc`", ['add', 'Backtick quoted title', 'Backtick quoted desc']),
        ('add "Title" <tag1> <tag2>', ['add', 'Title', '<tag1>', '<tag2>']),
        ("add 'Title' <tag1> 'Description'", ['add', 'Title', '<tag1>', 'Description']),
        ('add "Buy milk" "From the dairy" <groceries> <urgent>', ['add', 'Buy milk', 'From the dairy', '<groceries>', '<urgent>']),
    ]

    for i, (input_str, expected) in enumerate(test_cases, 1):
        result = tokenize_command(input_str)
        if result == expected:
            print(f"  ✓ Test {i}: PASSED - {input_str} -> {result}")
        else:
            print(f"  ✗ Test {i}: FAILED - {input_str}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {result}")

    print()


def test_parser():
    """Test the command parser functionality"""
    print("Testing command parser...")

    parser = CommandParser()

    # Test add command with different formats
    test_cases = [
        'add "Buy groceries"',
        'add "Buy groceries" "Buy organic items"',
        "add 'Buy groceries'",
        "add 'Buy groceries' 'Buy organic items'",
        "add `Buy groceries`",
        "add `Buy groceries` `Buy organic items`",
        'add "Buy milk" <groceries>',
        'add "Buy milk" "From dairy" <groceries> <urgent>',
    ]

    for i, command in enumerate(test_cases, 1):
        result = parser.parse(command)
        if result.is_valid:
            print(f"  ✓ Test {i}: PASSED - {command}")
            print(f"    Parsed: {result.parameters}")
        else:
            print(f"  ✗ Test {i}: FAILED - {command}")
            print(f"    Error: {result.error_message}")

    # Test invalid add commands
    invalid_cases = [
        'add',  # No title
        'add Buy milk',  # No quotes around title
        'add Buy milk Buy groceries',  # No quotes around title or description
    ]

    print("\nTesting invalid add commands (should fail)...")
    for i, command in enumerate(invalid_cases, 1):
        result = parser.parse(command)
        if not result.is_valid:
            print(f"  ✓ Test {i}: CORRECTLY REJECTED - {command}")
        else:
            print(f"  ✗ Test {i}: SHOULD HAVE FAILED - {command}")

    # Test other commands
    print("\nTesting other commands...")
    other_cases = [
        'list',
        'list all',
        'delete 1',
        'complete 2',
        'incomplete 3',
        'update 1 "New title"',
        'update 1 "New title" "New description"',
    ]

    for i, command in enumerate(other_cases, 1):
        result = parser.parse(command)
        if result.is_valid:
            print(f"  ✓ Test {i}: PASSED - {command}")
        else:
            print(f"  ✗ Test {i}: FAILED - {command}")
            print(f"    Error: {result.error_message}")

    print()


def main():
    print("Testing refactored command parser...\n")

    test_tokenizer()
    test_parser()

    print("Parser testing completed!")


if __name__ == "__main__":
    main()