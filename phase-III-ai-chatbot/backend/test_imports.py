#!/usr/bin/env python3
"""Test imports step by step to identify circular import"""

import sys

print("Testing imports step by step...")
print()

try:
    print("1. Importing settings...")
    from src.config.settings import settings
    print("   ✓ Settings imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("2. Importing TaskService...")
    from src.services.task_service import TaskService
    print("   ✓ TaskService imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("3. Importing agents module...")
    from agents import Agent, function_tool
    print("   ✓ Agents module imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

try:
    print("4. Importing tool_adapter directly...")
    import src.agent_sdk.tool_adapter as tool_adapter
    print("   ✓ tool_adapter imported")
    print(f"   Available: {dir(tool_adapter)}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Importing agent_service directly...")
    import src.agent_sdk.agent_service as agent_service
    print("   ✓ agent_service imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("✓ All imports successful!")
