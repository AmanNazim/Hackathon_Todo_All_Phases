"""
Reusable error handling utilities for CLI applications.

This module provides common error handling and suggestion generation functions
that can be used across different CLI applications.
"""

from typing import List, Dict, Any, Optional, NamedTuple
from enum import Enum
import difflib
import re
from datetime import datetime


class ErrorType(Enum):
    """Enumeration of different error types"""
    UNKNOWN_COMMAND = "unknown_command"
    AMBIGUOUS_COMMAND = "ambiguous_command"
    MISSING_ARGUMENTS = "missing_arguments"
    INVALID_ARGUMENT_FORMAT = "invalid_argument_format"
    OUT_OF_RANGE_VALUE = "out_of_range_value"
    CONFLICTING_ARGUMENTS = "conflicting_arguments"
    INVALID_STATE = "invalid_state"
    NO_OP_COMMAND = "no_op_command"
    INTERNAL_ERROR = "internal_error"
    EMPTY_INPUT = "empty_input"


class ErrorResult(NamedTuple):
    """Structured result for error handling"""
    error_type: ErrorType
    message: str
    suggestions: List[str]
    context: Dict[str, Any]
    timestamp: datetime = datetime.now()


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def find_similar_commands(user_input: str, available_commands: List[str], max_suggestions: int = 5) -> List[str]:
    """Find commands similar to user input using fuzzy matching"""
    if not user_input or not available_commands:
        return []

    # First check for prefix matches (higher priority)
    prefix_matches = [cmd for cmd in available_commands if cmd.startswith(user_input.lower())]

    # Then check for close matches using difflib
    close_matches = difflib.get_close_matches(
        user_input.lower(),
        [cmd.lower() for cmd in available_commands],
        n=max_suggestions,
        cutoff=0.6
    )

    # Combine results, prioritizing prefix matches
    all_matches = list(dict.fromkeys(prefix_matches + close_matches))  # Remove duplicates while preserving order

    return all_matches[:max_suggestions]


def classify_error(user_input: str, available_commands: List[str], context: Dict[str, Any] = None) -> ErrorType:
    """Classify the type of error based on user input and context"""
    if context is None:
        context = {}

    # Normalize input
    normalized_input = user_input.strip().lower() if user_input else ""

    # Check for empty input
    if not normalized_input:
        return ErrorType.EMPTY_INPUT

    # Extract command part (first word)
    input_parts = normalized_input.split()
    if not input_parts:
        return ErrorType.EMPTY_INPUT

    command_part = input_parts[0]

    # Check if command exists
    command_exists = any(cmd.lower() == command_part for cmd in available_commands)

    if not command_exists:
        # Check for ambiguous commands (partial matches)
        partial_matches = [cmd for cmd in available_commands if cmd.lower().startswith(command_part)]
        if len(partial_matches) > 1:
            return ErrorType.AMBIGUOUS_COMMAND
        elif len(partial_matches) == 1:
            # This is a valid command that's just abbreviated
            return ErrorType.MISSING_ARGUMENTS
        else:
            return ErrorType.UNKNOWN_COMMAND

    # Command exists, check for arguments
    expected_args = context.get('expected_args', {})
    if command_part in expected_args:
        required_args = expected_args[command_part].get('required', [])
        provided_args = input_parts[1:]  # Exclude command part

        if len(provided_args) < len(required_args):
            return ErrorType.MISSING_ARGUMENTS

        # Check argument format if specified
        arg_formats = expected_args[command_part].get('formats', {})
        for i, arg in enumerate(provided_args):
            if i < len(required_args):
                arg_name = required_args[i]
                if arg_name in arg_formats:
                    pattern = arg_formats[arg_name]
                    if not re.match(pattern, arg):
                        return ErrorType.INVALID_ARGUMENT_FORMAT

    return ErrorType.UNKNOWN_COMMAND  # Default fallback


def generate_suggestions(error_type: ErrorType, user_input: str, available_commands: List[str], context: Dict[str, Any] = None) -> List[str]:
    """Generate appropriate suggestions based on error type"""
    if context is None:
        context = {}

    suggestions = []

    if error_type == ErrorType.UNKNOWN_COMMAND:
        # Find similar commands
        similar = find_similar_commands(user_input.split()[0] if user_input.split() else "", available_commands)
        suggestions.extend(similar[:3])

        # Add general help if no close matches
        if not similar and 'help' in available_commands:
            suggestions.append('help')

    elif error_type == ErrorType.AMBIGUOUS_COMMAND:
        # List all possible matches
        input_cmd = user_input.split()[0] if user_input.split() else ""
        ambiguous_matches = [cmd for cmd in available_commands if cmd.lower().startswith(input_cmd.lower())]
        suggestions.extend(ambiguous_matches[:5])

    elif error_type == ErrorType.MISSING_ARGUMENTS:
        # Show proper syntax for the command
        cmd = user_input.split()[0] if user_input.split() else ""
        if cmd in available_commands:
            # Provide example with required arguments
            expected_args = context.get('expected_args', {}).get(cmd, {})
            required = expected_args.get('required', ['<args>'])
            if required:
                example_args = ' '.join(required)
                suggestions.append(f"{cmd} {example_args}")

            # Add help for the command
            if 'help' in available_commands:
                suggestions.append(f"help {cmd}")

    elif error_type == ErrorType.EMPTY_INPUT:
        # Suggest common commands
        common_commands = ['list', 'add', 'help']
        for cmd in common_commands:
            if cmd in available_commands:
                suggestions.append(cmd)

    # Add general help if suggestions are limited
    if len(suggestions) < 3 and 'help' in available_commands:
        if 'help' not in suggestions:
            suggestions.append('help')

    return suggestions[:5]  # Limit to 5 suggestions


def format_error_message(error_type: ErrorType, user_input: str, suggestions: List[str]) -> str:
    """Format a user-friendly error message based on error type"""

    base_messages = {
        ErrorType.UNKNOWN_COMMAND: f"❌ I couldn't understand '{user_input.split()[0] if user_input.split() else ''}'.",
        ErrorType.AMBIGUOUS_COMMAND: f"❓ The command '{user_input.split()[0] if user_input.split() else ''}' is ambiguous.",
        ErrorType.MISSING_ARGUMENTS: f"📋 The command needs more information.",
        ErrorType.INVALID_ARGUMENT_FORMAT: f"📝 That input format isn't quite right.",
        ErrorType.OUT_OF_RANGE_VALUE: f"📊 That value is outside the valid range.",
        ErrorType.CONFLICTING_ARGUMENTS: f"⚠️  Those options conflict with each other.",
        ErrorType.INVALID_STATE: f"🚫 That command isn't available right now.",
        ErrorType.NO_OP_COMMAND: f"✅ That task is already done!",
        ErrorType.INTERNAL_ERROR: f"⚙️  Something went wrong internally.",
        ErrorType.EMPTY_INPUT: f"🤔 No command received."
    }

    base_msg = base_messages.get(error_type, "An error occurred.")

    if suggestions:
        base_msg += "\n💡 Try:"
        for suggestion in suggestions[:3]:  # Show up to 3 suggestions in the message
            base_msg += f"\n   • {suggestion}"

    return base_msg


def process_cli_error(user_input: str, available_commands: List[str], context: Dict[str, Any] = None) -> ErrorResult:
    """
    Main function to process CLI errors and return structured results.

    Args:
        user_input: The raw user input that caused the error
        available_commands: List of valid commands for the application
        context: Additional context information (optional)

    Returns:
        ErrorResult: Structured error information with suggestions
    """
    if context is None:
        context = {}

    # Classify the error
    error_type = classify_error(user_input, available_commands, context)

    # Generate suggestions
    suggestions = generate_suggestions(error_type, user_input, available_commands, context)

    # Format the error message
    message = format_error_message(error_type, user_input, suggestions)

    # Create context for the result
    result_context = {
        'original_input': user_input,
        'available_commands_count': len(available_commands),
        'suggestions_provided': len(suggestions),
        'error_type': error_type.value
    }
    result_context.update(context)

    return ErrorResult(
        error_type=error_type,
        message=message,
        suggestions=suggestions,
        context=result_context
    )


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in input text"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


def is_valid_command_structure(user_input: str, command_pattern: str) -> bool:
    """
    Check if user input matches a command pattern.

    Args:
        user_input: The user's input
        command_pattern: Regex pattern for valid command structure

    Returns:
        bool: True if input matches pattern
    """
    return bool(re.match(command_pattern, user_input.strip()))


def extract_command_and_args(user_input: str) -> tuple:
    """
    Extract command and arguments from user input.

    Args:
        user_input: Raw user input

    Returns:
        tuple: (command, list of arguments)
    """
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def validate_argument_types(args: List[str], expected_types: List[type]) -> List[bool]:
    """
    Validate that arguments match expected types.

    Args:
        args: List of argument strings
        expected_types: List of expected types

    Returns:
        List[bool]: Validation results for each argument
    """
    results = []
    for i, arg in enumerate(args):
        if i >= len(expected_types):
            # No type expectation for this argument
            results.append(True)
        else:
            expected_type = expected_types[i]
            try:
                if expected_type == int:
                    int(arg)
                    results.append(True)
                elif expected_type == float:
                    float(arg)
                    results.append(True)
                elif expected_type == str:
                    results.append(True)  # Any string is valid
                else:
                    results.append(True)  # Default to True for other types
            except ValueError:
                results.append(False)
    return results


# Example usage function
def demonstrate_error_handling():
    """Demonstrate the error handling utilities"""
    available_commands = ["add", "list", "complete", "delete", "help", "edit"]

    test_cases = [
        "ad",  # Unknown command (similar to add)
        "complete",  # Missing arguments
        "xyz123",  # Completely unknown
        "",  # Empty input
        "list all items"  # Valid command with extra args
    ]

    context = {
        'expected_args': {
            'add': {'required': ['<task_description>']},
            'complete': {'required': ['<task_id>'], 'formats': {'<task_id>': r'\d+'}},
            'delete': {'required': ['<task_id>'], 'formats': {'<task_id>': r'\d+'}}
        }
    }

    print("Error Handling Demonstration:")
    print("=" * 40)

    for test_input in test_cases:
        print(f"\nInput: '{test_input}'")
        result = process_cli_error(test_input, available_commands, context)
        print(f"Error Type: {result.error_type.value}")
        print(f"Message: {result.message}")
        print(f"Suggestions: {result.suggestions}")


if __name__ == "__main__":
    demonstrate_error_handling()