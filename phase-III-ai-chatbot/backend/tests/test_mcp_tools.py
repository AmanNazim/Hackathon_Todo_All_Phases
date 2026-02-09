"""Unit tests for MCP tools"""

import pytest
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.delete_task import delete_task
from src.mcp.tools.update_task import update_task


@pytest.mark.asyncio
class TestMCPTools:
    """Test cases for MCP tools"""

    async def test_add_task(self):
        """Test adding a task"""
        result = await add_task("user123", "Buy milk")

        assert result is not None
        assert "task_id" in result
        assert result["status"] == "created"
        assert result["title"] == "Buy milk"

    async def test_add_task_with_description(self):
        """Test adding a task with description"""
        result = await add_task(
            "user123",
            "Buy groceries",
            "Milk, eggs, bread"
        )

        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"

    async def test_list_tasks_all(self):
        """Test listing all tasks"""
        tasks = await list_tasks("user123", "all")

        assert isinstance(tasks, list)

    async def test_list_tasks_pending(self):
        """Test listing pending tasks"""
        tasks = await list_tasks("user123", "pending")

        assert isinstance(tasks, list)

    async def test_complete_task(self):
        """Test completing a task"""
        result = await complete_task("user123", "task-id-123")

        assert result["status"] == "completed"
        assert "task_id" in result

    async def test_delete_task(self):
        """Test deleting a task"""
        result = await delete_task("user123", "task-id-123")

        assert result["status"] == "deleted"
        assert "task_id" in result

    async def test_update_task_title(self):
        """Test updating task title"""
        result = await update_task(
            "user123",
            "task-id-123",
            title="New title"
        )

        assert result["status"] == "updated"
        assert result["title"] == "New title"

    async def test_update_task_description(self):
        """Test updating task description"""
        result = await update_task(
            "user123",
            "task-id-123",
            description="New description"
        )

        assert result["status"] == "updated"
