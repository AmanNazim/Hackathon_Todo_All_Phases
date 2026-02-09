"""OpenAI Agent runner for executing conversations with tools"""

from typing import List, Dict
from openai import OpenAI
from src.config.settings import settings
from src.mcp.server import get_mcp_schemas, get_tool_by_name
from src.agent.config import SYSTEM_PROMPT
import json

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


async def run_agent(user_id: str, messages: List[Dict]) -> str:
    """
    Run OpenAI agent with conversation history and MCP tools.

    Args:
        user_id: User identifier (passed to tools)
        messages: Conversation history in OpenAI format

    Returns:
        AI response text
    """
    # Get MCP tool schemas
    tool_schemas = get_mcp_schemas()

    # Convert MCP schemas to OpenAI function format
    functions = [
        {
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["parameters"]
            }
        }
        for schema in tool_schemas
    ]

    # Build messages with system prompt
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + messages

    # Call OpenAI API
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=full_messages,
        tools=functions,
        tool_choice="auto"
    )

    # Get the assistant's response
    assistant_message = response.choices[0].message

    # Check if there are tool calls
    if assistant_message.tool_calls:
        # Execute tool calls
        tool_results = []

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Add user_id to tool arguments
            tool_args["user_id"] = user_id

            # Get and execute the tool
            tool_function = get_tool_by_name(tool_name)
            if tool_function:
                try:
                    result = await tool_function(**tool_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(result)
                    })
                except Exception as e:
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps({"error": str(e)})
                    })

        # If we have tool results, make another call to get final response
        if tool_results:
            # Add assistant message with tool calls
            full_messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Add tool results
            full_messages.extend(tool_results)

            # Make final call to get response
            final_response = client.chat.completions.create(
                model=settings.openai_model,
                messages=full_messages
            )

            return final_response.choices[0].message.content

    # Return direct response if no tool calls
    return assistant_message.content or "I'm here to help with your tasks!"
