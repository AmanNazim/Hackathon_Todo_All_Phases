"""Unit tests for Agent SDK components"""

import pytest
from src.agent_sdk.agent_service import create_task_agent, get_agent_config
from src.agent_sdk.session_service import get_or_create_session
from src.agent_sdk.tool_adapter import create_function_tools, get_tool_names
from src.agent_sdk.guardrails import (
    input_validation_guardrail,
    output_quality_guardrail
)
from uuid import uuid4


class TestAgentService:
    """Test cases for agent service"""

    def test_create_task_agent(self):
        """Test agent creation"""
        tools = []
        agent = create_task_agent(tools)

        assert agent is not None
        assert agent.name == "Task Management Agent"
        assert agent.model == "gpt-4o-mini"
        assert agent.max_iterations == 10

    def test_get_agent_config(self):
        """Test agent configuration retrieval"""
        config = get_agent_config()

        assert "model" in config
        assert "temperature" in config
        assert "max_iterations" in config
        assert config["temperature"] == 0.7
        assert config["max_iterations"] == 10


class TestSessionService:
    """Test cases for session service"""

    def test_create_new_session(self):
        """Test creating a new session"""
        session, conv_id = get_or_create_session(None)

        assert session is not None
        assert conv_id is not None
        assert str(conv_id) == session.session_id

    def test_get_existing_session(self):
        """Test retrieving an existing session"""
        existing_id = uuid4()
        session, conv_id = get_or_create_session(existing_id)

        assert session is not None
        assert conv_id == existing_id
        assert str(conv_id) == session.session_id


class TestToolAdapter:
    """Test cases for tool adapter"""

    def test_create_function_tools(self):
        """Test creating function tools"""
        user_id = "test_user_123"
        tools = create_function_tools(user_id)

        assert len(tools) == 5
        assert all(callable(tool) for tool in tools)

    def test_get_tool_names(self):
        """Test getting tool names"""
        names = get_tool_names()

        assert len(names) == 5
        assert "add_task_tool" in names
        assert "list_tasks_tool" in names
        assert "complete_task_tool" in names
        assert "delete_task_tool" in names
        assert "update_task_tool" in names


@pytest.mark.asyncio
class TestGuardrails:
    """Test cases for guardrails"""

    async def test_input_validation_empty_message(self):
        """Test input guardrail rejects empty messages"""
        result = await input_validation_guardrail(None, None, "")

        assert result.tripwire_triggered is True
        assert "error" in result.output_info

    async def test_input_validation_long_message(self):
        """Test input guardrail rejects messages over 1000 chars"""
        long_message = "x" * 1001
        result = await input_validation_guardrail(None, None, long_message)

        assert result.tripwire_triggered is True
        assert "error" in result.output_info

    async def test_input_validation_valid_message(self):
        """Test input guardrail accepts valid messages"""
        result = await input_validation_guardrail(None, None, "Hello, add a task")

        assert result.tripwire_triggered is False
        assert result.output_info["valid"] is True

    async def test_output_quality_empty_response(self):
        """Test output guardrail rejects empty responses"""
        result = await output_quality_guardrail(None, None, "input", "")

        assert result.tripwire_triggered is True
        assert "error" in result.output_info

    async def test_output_quality_short_response(self):
        """Test output guardrail rejects very short responses"""
        result = await output_quality_guardrail(None, None, "input", "Hi")

        assert result.tripwire_triggered is True

    async def test_output_quality_valid_response(self):
        """Test output guardrail accepts valid responses"""
        result = await output_quality_guardrail(
            None, None, "input", "I've added the task to your list."
        )

        assert result.tripwire_triggered is False
        assert result.output_info["quality"] == "good"
