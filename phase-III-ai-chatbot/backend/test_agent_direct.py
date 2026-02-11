#!/usr/bin/env python3
"""
Direct test of the agent workflow without FastAPI server.
Tests: Agent → LiteLLM → Tools → TaskService → Database
"""

import asyncio
import sys
from datetime import datetime


async def test_agent_workflow():
    """Test the complete agent workflow directly"""

    print("=" * 60)
    print("Testing Phase III AI Agent - Direct Workflow")
    print("=" * 60)
    print()

    # Test 1: Import all modules
    print("1. Testing module imports...")
    try:
        import src.agent_sdk.agent_service as agent_service
        import src.agent_sdk.tool_adapter as tool_adapter
        from src.services.task_service import TaskService

        create_task_agent = agent_service.create_task_agent
        create_function_tools = tool_adapter.create_function_tools

        print("   ✓ All modules imported successfully")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return

    print()

    # Test 2: Create agent with tools
    print("2. Creating agent with tools...")
    test_user_id = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"   User ID: {test_user_id}")

    try:
        tools = create_function_tools(test_user_id)
        print(f"   ✓ Created {len(tools)} tools")

        agent = create_task_agent(tools)
        print(f"   ✓ Agent created: {agent.name}")
    except Exception as e:
        print(f"   ✗ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Test 3: Test agent with task creation
    print("3. Testing agent task creation...")
    test_message = "Add a task to buy groceries for dinner tonight"
    print(f"   Prompt: {test_message}")
    print()

    try:
        from agents import Runner

        print("   Sending request to agent...")
        result = await Runner.run(agent, test_message)

        print("   ✓ Agent responded successfully")
        print()
        print("   Agent Response:")
        print(f"   {result.final_output}")
        print()

    except Exception as e:
        print(f"   ✗ Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Test 4: Verify task was created
    print("4. Verifying task in database...")
    try:
        tasks = await TaskService.list_tasks(test_user_id, "all")
        print(f"   ✓ Found {len(tasks)} task(s)")

        if tasks:
            for task in tasks:
                print(f"   - Task {task['id']}: {task['title']}")

    except Exception as e:
        print(f"   ✗ Database verification failed: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent_workflow())
