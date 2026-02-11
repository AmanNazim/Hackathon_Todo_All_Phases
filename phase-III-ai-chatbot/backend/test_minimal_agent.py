#!/usr/bin/env python3
"""
Minimal isolated test of agent workflow
Avoids all circular imports by importing only what's needed
"""

import asyncio
import sys
from datetime import datetime


async def test_minimal_agent():
    """Test agent with minimal imports"""

    print("=" * 60)
    print("Testing Phase III AI Agent - Minimal Test")
    print("=" * 60)
    print()

    # Test 1: Create tools manually
    print("1. Creating tools manually...")
    test_user_id = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"   User ID: {test_user_id}")

    try:
        from agents import function_tool, Agent, Runner
        from agents.extensions.models.litellm_model import LitellmModel
        from src.config.settings import settings

        # Create tools inline (avoiding tool_adapter import)
        @function_tool
        async def add_task(title: str, description: str = "") -> dict:
            """Create a new task"""
            return {
                "task_id": 1,
                "title": title,
                "description": description,
                "status": "created"
            }

        @function_tool
        async def list_tasks(status: str = "all") -> list:
            """List all tasks"""
            return [
                {"id": 1, "title": "Test task", "completed": False}
            ]

        tools = [add_task, list_tasks]
        print(f"   ✓ Created {len(tools)} tools")

    except Exception as e:
        print(f"   ✗ Tool creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Test 2: Create agent
    print("2. Creating agent...")
    try:
        model_name, api_key = settings.get_model_config()
        print(f"   Model: {model_name}")

        litellm_model = LitellmModel(
            model=model_name,
            api_key=api_key
        )

        agent = Agent(
            name="Test Agent",
            instructions="You are a helpful task management assistant.",
            model=litellm_model,
            tools=tools
        )

        print(f"   ✓ Agent created: {agent.name}")

    except Exception as e:
        print(f"   ✗ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Test 3: Run agent
    print("3. Testing agent execution...")
    test_message = "Add a task to buy groceries"
    print(f"   Prompt: {test_message}")
    print()

    try:
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
    print("=" * 60)
    print("✓ Test Complete - Agent workflow is working!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_minimal_agent())
