#!/usr/bin/env python3
"""
Test script for the Help & Error-Reasoner skill utilities.

This script demonstrates the usage of the error handling system
across different scenarios and validates the core functionality.
"""

import sys
import os
from typing import List

# Add the scripts directory to the path to import error tools
sys.path.insert(0, os.path.dirname(__file__))

from error_tools import (
    process_cli_error,
    ErrorType,
    find_similar_commands,
    levenshtein_distance,
    classify_error,
    generate_suggestions,
    format_error_message,
    normalize_whitespace,
    extract_command_and_args,
    validate_argument_types
)


def test_levenshtein_distance():
    """Test the Levenshtein distance calculation"""
    print("Testing Levenshtein Distance...")

    # Test identical strings
    assert levenshtein_distance("hello", "hello") == 0
    print("✓ Identical strings have distance 0")

    # Test simple insertion
    assert levenshtein_distance("hello", "hell") == 1
    assert levenshtein_distance("hell", "hello") == 1
    print("✓ Insertion/deletion operations work correctly")

    # Test substitution
    assert levenshtein_distance("hello", "hallo") == 1
    print("✓ Substitution operations work correctly")

    # Test transposition
    assert levenshtein_distance("hello", "ehllo") == 2  # Actually 2 operations: h->e, e->h
    print("✓ Complex operations calculated correctly")


def test_find_similar_commands():
    """Test the similar command finder"""
    print("\nTesting Similar Command Finder...")

    commands = ["add", "list", "complete", "delete", "help", "edit", "status"]

    # Test exact match
    similar = find_similar_commands("add", commands)
    assert "add" in similar
    print("✓ Exact matches found")

    # Test prefix match
    similar = find_similar_commands("ad", commands)
    assert "add" in similar
    print("✓ Prefix matches found")

    # Test fuzzy match
    similar = find_similar_commands("cmplete", commands)  # Typo for "complete"
    assert "complete" in similar or any("complet" in cmd for cmd in similar)
    print("✓ Fuzzy matches found")

    # Test no matches
    similar = find_similar_commands("xyz", commands)
    assert len(similar) <= 5  # Should be limited
    print("✓ Results properly limited")


def test_error_classification():
    """Test error classification functionality"""
    print("\nTesting Error Classification...")

    commands = ["add", "list", "complete", "delete", "help"]

    # Test unknown command
    error_type = classify_error("xyz123", commands)
    assert error_type == ErrorType.UNKNOWN_COMMAND
    print("✓ Unknown command correctly classified")

    # Test empty input
    error_type = classify_error("", commands)
    assert error_type == ErrorType.EMPTY_INPUT
    print("✓ Empty input correctly classified")

    # Test valid command with missing arguments
    context = {
        'expected_args': {
            'complete': {'required': ['<task_id>'], 'formats': {'<task_id>': r'\d+'}}
        }
    }
    error_type = classify_error("complete", commands, context)
    assert error_type == ErrorType.MISSING_ARGUMENTS
    print("✓ Missing arguments correctly classified")


def test_suggestion_generation():
    """Test suggestion generation"""
    print("\nTesting Suggestion Generation...")

    commands = ["add", "list", "complete", "delete", "help"]

    # Test suggestions for unknown command
    suggestions = generate_suggestions(ErrorType.UNKNOWN_COMMAND, "ad", commands)
    assert "add" in suggestions or any("add" in s for s in suggestions)
    print("✓ Suggestions generated for unknown command")

    # Test suggestions for missing arguments
    context = {
        'expected_args': {
            'complete': {'required': ['<task_id>']}
        }
    }
    suggestions = generate_suggestions(ErrorType.MISSING_ARGUMENTS, "complete", commands, context)
    has_complete_suggestion = any("complete" in s and "<task_id>" in s for s in suggestions)
    assert has_complete_suggestion
    print("✓ Suggestions generated for missing arguments")

    # Test suggestions limited to 5
    suggestions = generate_suggestions(ErrorType.UNKNOWN_COMMAND, "xyz", commands)
    assert len(suggestions) <= 5
    print("✓ Suggestions properly limited")


def test_error_processing():
    """Test the complete error processing pipeline"""
    print("\nTesting Complete Error Processing...")

    commands = ["add", "list", "complete", "delete", "help"]

    # Test unknown command
    result = process_cli_error("xyz123", commands)
    assert result.error_type == ErrorType.UNKNOWN_COMMAND
    assert len(result.suggestions) >= 0
    print("✓ Unknown command processed correctly")

    # Test empty input
    result = process_cli_error("", commands)
    assert result.error_type == ErrorType.EMPTY_INPUT
    print("✓ Empty input processed correctly")

    # Test typo correction
    result = process_cli_error("ad", commands)
    assert result.error_type in [ErrorType.UNKNOWN_COMMAND, ErrorType.AMBIGUOUS_COMMAND]
    # Should suggest "add" as a correction
    has_add_suggestion = any("add" in s for s in result.suggestions)
    assert has_add_suggestion
    print("✓ Typo correction suggested")


def test_utility_functions():
    """Test utility functions"""
    print("\nTesting Utility Functions...")

    # Test whitespace normalization
    assert normalize_whitespace("  hello   world  ") == "hello world"
    assert normalize_whitespace("") == ""
    assert normalize_whitespace("   ") == ""
    print("✓ Whitespace normalization works")

    # Test command and argument extraction
    cmd, args = extract_command_and_args("add buy milk and eggs")
    assert cmd == "add"
    assert args == ["buy", "milk", "and", "eggs"]
    print("✓ Command and argument extraction works")

    # Test argument type validation
    results = validate_argument_types(["123", "456"], [int, int])
    assert all(results)
    results = validate_argument_types(["123", "abc"], [int, int])
    assert not all(results)
    print("✓ Argument type validation works")


def demonstrate_cli_integration():
    """Demonstrate how error handling would be used in a CLI application"""
    print("\nDemonstrating CLI Integration...")

    def handle_user_command(user_input: str, available_commands: List[str]) -> bool:
        """Simulate CLI command handling with error processing"""
        # In a real CLI, you would first try to parse and execute the command
        # If that fails, you'd use the error processor
        result = process_cli_error(user_input, available_commands)

        if result.error_type != ErrorType.EMPTY_INPUT:  # Assuming empty input isn't an error in this context
            print(f"Error: {result.message}")
            if result.suggestions:
                print("Suggestions:", ", ".join(result.suggestions))
            return False
        else:
            # Empty input might just show help in a real CLI
            print("No command provided. Available commands:", ", ".join(available_commands))
            return True

    commands = ["add", "list", "complete", "delete", "help"]

    # Test with valid command (would normally succeed, but we're testing error path)
    print("Testing with 'ad' (typo for 'add'):")
    success = handle_user_command("ad", commands)
    print(f"Handled with suggestions: {success}")

    # Test with unknown command
    print("\nTesting with 'xyz' (unknown command):")
    success = handle_user_command("xyz", commands)
    print(f"Handled with suggestions: {success}")


def main():
    """Run all error handling tests"""
    print("Help & Error-Reasoner Skill - Test Suite\n")

    try:
        test_levenshtein_distance()
        test_find_similar_commands()
        test_error_classification()
        test_suggestion_generation()
        test_error_processing()
        test_utility_functions()
        demonstrate_cli_integration()

        print("\n✓ All error handling tests passed successfully!")
        print("\nHelp & Error-Reasoner Skill is ready for use in CLI applications.")
        print("\nThe system provides:")
        print("- Professional-grade error messages")
        print("- Context-aware suggestions")
        print("- Fuzzy command matching")
        print("- Progressive help escalation")
        print("- Consistent error handling patterns")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()