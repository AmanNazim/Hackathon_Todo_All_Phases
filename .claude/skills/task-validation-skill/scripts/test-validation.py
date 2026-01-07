#!/usr/bin/env python3
"""
Task Validation Skill - Test Script

This script demonstrates the usage of the task validation system
across different scenarios and contexts.
"""

import sys
import os
from typing import Dict, Any, List

# Add the current directory to the path to import validation tools
sys.path.insert(0, os.path.dirname(__file__))

from validation_tools import (
    validate_task_data,
    validate_title_length,
    validate_task_id,
    validate_task_status,
    ValidationError,
    aggregate_validation_errors,
    has_errors,
    get_error_messages
)

def test_title_validation():
    """Test title validation scenarios"""
    print("Testing Title Validation...")

    # Test valid title
    error = validate_title_length("Valid title")
    assert error is None, f"Valid title should not produce error: {error}"
    print("✓ Valid title passed validation")

    # Test empty title
    error = validate_title_length("")
    assert error is not None and error.code == "TITLE_REQUIRED"
    print("✓ Empty title correctly rejected")

    # Test whitespace-only title
    error = validate_title_length("   ")
    assert error is not None and error.code == "TITLE_WHITESPACE_ONLY"
    print("✓ Whitespace-only title correctly rejected")

    # Test too long title
    long_title = "A" * 201
    error = validate_title_length(long_title)
    assert error is not None and error.code == "TITLE_TOO_LONG"
    print("✓ Too long title correctly rejected")


def test_id_validation():
    """Test ID validation scenarios"""
    print("\nTesting ID Validation...")

    # Test valid ID
    error = validate_task_id(123)
    assert error is None, f"Valid ID should not produce error: {error}"
    print("✓ Valid numeric ID passed validation")

    # Test valid string ID
    error = validate_task_id("task-123")
    assert error is None, f"Valid string ID should not produce error: {error}"
    print("✓ Valid string ID passed validation")

    # Test invalid (negative) ID
    error = validate_task_id(-5)
    assert error is not None and error.code == "TASK_ID_INVALID"
    print("✓ Negative ID correctly rejected")

    # Test invalid (zero) ID
    error = validate_task_id(0)
    assert error is not None and error.code == "TASK_ID_INVALID"
    print("✓ Zero ID correctly rejected")

    # Test null ID
    error = validate_task_id(None)
    assert error is not None and error.code == "TASK_ID_REQUIRED"
    print("✓ Null ID correctly rejected")


def test_status_validation():
    """Test status validation scenarios"""
    print("\nTesting Status Validation...")

    # Test valid status
    error = validate_task_status("pending")
    assert error is None, f"Valid status should not produce error: {error}"
    print("✓ Valid status passed validation")

    # Test invalid status
    error = validate_task_status("invalid_status")
    assert error is not None and error.code == "STATUS_INVALID"
    print("✓ Invalid status correctly rejected")


def test_task_data_validation():
    """Test complete task data validation"""
    print("\nTesting Complete Task Data Validation...")

    # Test valid task data
    task_data = {
        "title": "Valid task title",
        "status": "pending",
        "priority": "high"
    }
    errors = validate_task_data(task_data)
    assert len(errors) == 0, f"Valid task data should not produce errors: {errors}"
    print("✓ Valid task data passed validation")

    # Test task data with missing required field
    task_data = {
        "status": "pending"  # Missing title
    }
    errors = validate_task_data(task_data)
    assert len(errors) > 0, "Task data with missing title should produce errors"
    error_codes = [e.code for e in errors]
    assert "FIELD_REQUIRED" in error_codes
    print("✓ Task data with missing title correctly rejected")

    # Test task data with invalid title
    task_data = {
        "title": "",  # Invalid title
        "status": "pending"
    }
    errors = validate_task_data(task_data)
    assert len(errors) > 0, "Task data with invalid title should produce errors"
    error_codes = [e.code for e in errors]
    assert "TITLE_REQUIRED" in error_codes
    print("✓ Task data with invalid title correctly rejected")


def demonstrate_cli_integration():
    """Demonstrate how validation would be used in a CLI application"""
    print("\nDemonstrating CLI Integration...")

    def create_task_cli(title: str, status: str = None, priority: str = None) -> bool:
        """Simulate a CLI command for creating a task"""
        task_data = {"title": title}
        if status:
            task_data["status"] = status
        if priority:
            task_data["priority"] = priority

        errors = validate_task_data(task_data)

        if has_errors(errors):
            print("Validation failed:")
            for msg in get_error_messages(errors):
                print(f"  - {msg}")
            return False
        else:
            print(f"Task created successfully: {title}")
            return True

    # Test with valid input
    success = create_task_cli("Implement validation system", "pending", "high")
    assert success
    print("✓ Valid CLI input processed successfully")

    # Test with invalid input
    success = create_task_cli("", "invalid_status", "critical")  # Empty title
    assert not success
    print("✓ Invalid CLI input correctly rejected")


def main():
    """Run all validation tests"""
    print("Task Validation Skill - Test Suite\n")

    try:
        test_title_validation()
        test_id_validation()
        test_status_validation()
        test_task_data_validation()
        demonstrate_cli_integration()

        print("\n✓ All validation tests passed successfully!")
        print("\nTask Validation Skill is ready for use across:")
        print("- Python CLI applications")
        print("- Backend FastAPI services")
        print("- Chat-based agent flows")
        print("- Dapr stateful services")
        print("- Kafka event consumers/producers")
        print("- MCP tool specifications")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()