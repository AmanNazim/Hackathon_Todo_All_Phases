#!/usr/bin/env python3
"""
Test script to verify the complete agent workflow:
1. Agent receives natural language prompt
2. Agent uses add_task tool
3. Task is created in database
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_agent_add_task():
    """Test the complete workflow of adding a task through the agent"""

    base_url = "http://localhost:8001"

    print("=" * 60)
    print("Testing Phase III AI Chatbot - Complete Workflow")
    print("=" * 60)
    print()

    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("   ✓ Health check passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"   ✗ Health check failed: {response.status_code}")
                return
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        print("   Make sure the server is running: uvicorn main:app --reload")
        return

    print()

    # Test 2: Add task through agent
    print("2. Testing agent task creation...")
    test_user_id = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    chat_request = {
        "message": "Add a task to buy groceries for dinner tonight"
    }

    # Authentication header (placeholder auth accepts any token)
    headers = {
        "Authorization": "Bearer test-token-for-development"
    }

    print(f"   User ID: {test_user_id}")
    print(f"   Prompt: {chat_request['message']}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("   Sending request to agent...")
            response = await client.post(
                f"{base_url}/api/chat",
                json=chat_request,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print("   ✓ Agent responded successfully")
                print()
                print("   Agent Response:")
                print(f"   {result.get('response', 'No response')}")
                print()

                # Check if conversation_id is present
                if result.get('conversation_id'):
                    print(f"   Conversation ID: {result['conversation_id']}")

                # Check if usage info is present
                if result.get('usage'):
                    usage = result['usage']
                    print(f"   Token Usage: {usage}")

            else:
                print(f"   ✗ Agent request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return

    except httpx.TimeoutException:
        print("   ✗ Request timed out (agent may be processing)")
        print("   This could mean:")
        print("     - Mistral API is slow to respond")
        print("     - LLM_API_KEY is invalid")
        print("     - Network connectivity issues")
        return
    except Exception as e:
        print(f"   ✗ Agent request failed: {e}")
        return

    print()

    # Test 3: Verify task was created
    print("3. Verifying task creation in database...")
    try:
        async with httpx.AsyncClient() as client:
            # List tasks for the test user
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "message": "Show me all my tasks"
                },
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print("   ✓ Task list retrieved")
                print()
                print("   Agent Response:")
                print(f"   {result.get('response', 'No response')}")
            else:
                print(f"   ✗ Failed to retrieve tasks: {response.status_code}")

    except Exception as e:
        print(f"   ✗ Failed to verify task: {e}")

    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Check the agent responses above")
    print("2. Verify tasks were created correctly")
    print("3. Test with different prompts:")
    print("   - 'Add a task to call mom'")
    print("   - 'Mark task 1 as complete'")
    print("   - 'Delete the groceries task'")
    print()


if __name__ == "__main__":
    asyncio.run(test_agent_add_task())
