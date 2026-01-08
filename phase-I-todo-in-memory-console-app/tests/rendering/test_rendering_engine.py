"""
Tests for Rendering & Themes Components
Testing the Rendering & Themes tasks: T080-T088
"""
import unittest
from datetime import datetime
from src.rendering.rendering_engine import (
    BaseRenderer,
    MinimalTheme,
    EmojiTheme,
    HackerTheme,
    ProfessionalTheme,
    ThemeManager,
    ThemeType,
    TaskItem,
    TaskListRenderer,
    MessageFormatter,
    StatusRenderer
)


class TestBaseRendererInterface(unittest.TestCase):
    """Test the base renderer interface (T080)"""

    def test_base_renderer_is_abstract(self):
        """Test that BaseRenderer is abstract (T080)"""
        with self.assertRaises(TypeError):
            BaseRenderer()


class TestMinimalTheme(unittest.TestCase):
    """Test the minimal theme with plain text formatting (T081)"""

    def setUp(self):
        """Set up test fixtures"""
        self.theme = MinimalTheme()
        self.sample_task = TaskItem(id="1", title="Test task", status="PENDING")

    def test_render_single_task(self):
        """Test rendering a single task in minimal format (T081)"""
        result = self.theme.render_single_task(self.sample_task)

        self.assertIn("Task #1:", result)
        self.assertIn("Test task", result)
        self.assertIn("[ ]", result)  # Pending status indicator

    def test_render_task_list(self):
        """Test rendering a list of tasks in minimal format (T081)"""
        tasks = [
            TaskItem(id="1", title="First task", status="PENDING"),
            TaskItem(id="2", title="Second task", status="COMPLETED")
        ]

        result = self.theme.render_task_list(tasks)

        self.assertIn("ID  Title", result)
        self.assertIn("First task", result)
        self.assertIn("Second task", result)
        self.assertIn("[ ]", result)  # Pending
        self.assertIn("[x]", result)  # Completed

    def test_render_success_message(self):
        """Test rendering success message in minimal format (T081)"""
        result = self.theme.render_success_message("Operation successful")

        self.assertIn("[SUCCESS]", result)

    def test_render_error_message(self):
        """Test rendering error message in minimal format (T081)"""
        result = self.theme.render_error_message("An error occurred")

        self.assertIn("[ERROR]", result)

    def test_render_status_indicator_pending(self):
        """Test rendering pending status indicator (T081)"""
        result = self.theme.render_status_indicator("PENDING")

        self.assertEqual(result, "[ ]")

    def test_render_status_indicator_completed(self):
        """Test rendering completed status indicator (T081)"""
        result = self.theme.render_status_indicator("COMPLETED")

        self.assertEqual(result, "[x]")


class TestEmojiTheme(unittest.TestCase):
    """Test the emoji theme with visual indicators (T082)"""

    def setUp(self):
        """Set up test fixtures"""
        self.theme = EmojiTheme()
        self.sample_task = TaskItem(id="1", title="Test task", status="PENDING")

    def test_render_single_task(self):
        """Test rendering a single task in emoji format (T082)"""
        result = self.theme.render_single_task(self.sample_task)

        self.assertIn("📝 Task #1:", result)
        self.assertIn("Test task", result)
        self.assertIn("⏳", result)  # Pending status indicator

    def test_render_status_indicator_pending(self):
        """Test rendering pending status indicator (T082)"""
        result = self.theme.render_status_indicator("PENDING")

        self.assertEqual(result, "⏳")

    def test_render_status_indicator_completed(self):
        """Test rendering completed status indicator (T082)"""
        result = self.theme.render_status_indicator("COMPLETED")

        self.assertEqual(result, "✅")

    def test_render_success_message(self):
        """Test rendering success message in emoji format (T082)"""
        result = self.theme.render_success_message("Operation successful")

        self.assertIn("✅", result)

    def test_render_error_message(self):
        """Test rendering error message in emoji format (T082)"""
        result = self.theme.render_error_message("An error occurred")

        self.assertIn("❌", result)


class TestHackerTheme(unittest.TestCase):
    """Test the hacker theme with monochrome styling (T083)"""

    def setUp(self):
        """Set up test fixtures"""
        self.theme = HackerTheme()
        self.sample_task = TaskItem(id="1", title="Test task", status="PENDING")

    def test_render_single_task(self):
        """Test rendering a single task in hacker format (T083)"""
        result = self.theme.render_single_task(self.sample_task)

        self.assertIn("┌─ TASK 0x01", result)
        self.assertIn("│ Title: Test task", result)
        self.assertIn("[○]", result)  # Pending status indicator

    def test_render_status_indicator_pending(self):
        """Test rendering pending status indicator (T083)"""
        result = self.theme.render_status_indicator("PENDING")

        self.assertEqual(result, "[○]")

    def test_render_status_indicator_completed(self):
        """Test rendering completed status indicator (T083)"""
        result = self.theme.render_status_indicator("COMPLETED")

        self.assertEqual(result, "[✓]")

    def test_render_success_message(self):
        """Test rendering success message in hacker format (T083)"""
        result = self.theme.render_success_message("Operation successful")

        self.assertIn("[✓]", result)

    def test_render_error_message(self):
        """Test rendering error message in hacker format (T083)"""
        result = self.theme.render_error_message("An error occurred")

        self.assertIn("[✗]", result)


class TestProfessionalTheme(unittest.TestCase):
    """Test the professional theme with clean appearance (T084)"""

    def setUp(self):
        """Set up test fixtures"""
        self.theme = ProfessionalTheme()
        self.sample_task = TaskItem(id="1", title="Test task", status="PENDING")

    def test_render_single_task(self):
        """Test rendering a single task in professional format (T084)"""
        result = self.theme.render_single_task(self.sample_task)

        self.assertIn("┌─────────────────────────────────────────────────────────┐", result)
        self.assertIn("│ Task ID:", result)
        self.assertIn("│ Title:", result)
        self.assertIn("Pending", result)  # Status indicator

    def test_render_status_indicator_pending(self):
        """Test rendering pending status indicator (T084)"""
        result = self.theme.render_status_indicator("PENDING")

        self.assertEqual(result, "Pending")

    def test_render_status_indicator_completed(self):
        """Test rendering completed status indicator (T084)"""
        result = self.theme.render_status_indicator("COMPLETED")

        self.assertEqual(result, "Completed")

    def test_render_success_message(self):
        """Test rendering success message in professional format (T084)"""
        result = self.theme.render_success_message("Operation successful")

        self.assertIn("✓ Success:", result)

    def test_render_error_message(self):
        """Test rendering error message in professional format (T084)"""
        result = self.theme.render_error_message("An error occurred")

        self.assertIn("✗ Error:", result)


class TestTaskListRenderer(unittest.TestCase):
    """Test the task list renderer (T085)"""

    def setUp(self):
        """Set up test fixtures"""
        self.minimal_renderer = MinimalTheme()
        self.renderer = TaskListRenderer(self.minimal_renderer)

    def test_render_task_list(self):
        """Test rendering a list of tasks (T085)"""
        tasks = [
            TaskItem(id="1", title="First task", status="PENDING"),
            TaskItem(id="2", title="Second task", status="COMPLETED")
        ]

        result = self.renderer.render(tasks)

        self.assertIn("ID  Title", result)
        self.assertIn("First task", result)
        self.assertIn("Second task", result)

    def test_render_empty_list(self):
        """Test rendering an empty task list (T085)"""
        result = self.renderer.render([])

        self.assertIn("No tasks found", result)

    def test_render_limited_list(self):
        """Test rendering a limited task list (T085)"""
        tasks = [TaskItem(id=str(i), title=f"Task {i}", status="PENDING") for i in range(1, 101)]

        result = self.renderer.render(tasks, limit=5)

        # Should only render first 5 tasks
        self.assertIn("Task 1", result)
        self.assertIn("Task 5", result)
        self.assertNotIn("Task 6", result)

    def test_render_paginated(self):
        """Test rendering paginated task list (T085)"""
        tasks = [TaskItem(id=str(i), title=f"Task {i}", status="PENDING") for i in range(1, 11)]

        result = self.renderer.render_paginated(tasks, page_size=3, page=1)

        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 3)
        self.assertEqual(result['total_tasks'], 10)
        self.assertEqual(result['total_pages'], 4)  # ceil(10/3)
        self.assertTrue(result['has_next'])
        self.assertFalse(result['has_prev'])


class TestThemeManager(unittest.TestCase):
    """Test the theme switching functionality (T088)"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ThemeManager()

    def test_initial_theme_is_minimal(self):
        """Test that initial theme is minimal (T088)"""
        self.assertEqual(self.manager.get_current_theme(), ThemeType.MINIMAL)

    def test_set_theme(self):
        """Test switching themes (T088)"""
        result = self.manager.set_theme(ThemeType.EMOJI)

        self.assertTrue(result)
        self.assertEqual(self.manager.get_current_theme(), ThemeType.EMOJI)

    def test_get_available_themes(self):
        """Test getting available themes (T088)"""
        themes = self.manager.get_available_themes()

        self.assertIn(ThemeType.MINIMAL, themes)
        self.assertIn(ThemeType.EMOJI, themes)
        self.assertIn(ThemeType.HACKER, themes)
        self.assertIn(ThemeType.PROFESSIONAL, themes)

    def test_render_with_different_theme(self):
        """Test rendering with different theme temporarily (T088)"""
        tasks = [TaskItem(id="1", title="Test task", status="PENDING")]

        original_theme = self.manager.get_current_theme()
        result = self.manager.render_with_theme(ThemeType.EMOJI, tasks)

        # Should contain emoji characters
        self.assertIn("📋", result)  # Header emoji
        self.assertIn("⏳", result)  # Status indicator emoji

        # Theme should not have changed permanently
        self.assertEqual(self.manager.get_current_theme(), original_theme)


class TestMessageFormatter(unittest.TestCase):
    """Test the success/failure message formatting (T087)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.formatter = MessageFormatter(self.renderer)

    def test_format_success(self):
        """Test formatting success messages (T087)"""
        result = self.formatter.format_success("Task added successfully")

        self.assertIn("[SUCCESS]", result)

    def test_format_error(self):
        """Test formatting error messages (T087)"""
        result = self.formatter.format_error("Failed to add task")

        self.assertIn("[ERROR]", result)

    def test_format_success_with_details(self):
        """Test formatting success messages with details (T087)"""
        result = self.formatter.format_success("Task added", "Task ID: 123")

        self.assertIn("[SUCCESS]", result)
        self.assertIn("Task ID: 123", result)

    def test_format_error_with_details(self):
        """Test formatting error messages with details (T087)"""
        result = self.formatter.format_error("Failed to add task", "Invalid title")

        self.assertIn("[ERROR]", result)
        self.assertIn("Invalid title", result)

    def test_format_warning(self):
        """Test formatting warning messages (T087)"""
        result = self.formatter.format_warning("This is a warning")

        self.assertIn("⚠ Warning:", result)


class TestStatusRenderer(unittest.TestCase):
    """Test the status indicator rendering (T086)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.status_renderer = StatusRenderer(self.renderer)

    def test_render_pending_status(self):
        """Test rendering pending status (T086)"""
        result = self.status_renderer.render_status("PENDING")

        self.assertEqual(result, "[ ]")

    def test_render_completed_status(self):
        """Test rendering completed status (T086)"""
        result = self.status_renderer.render_status("COMPLETED")

        self.assertEqual(result, "[x]")

    def test_render_status_block(self):
        """Test rendering status block with label (T086)"""
        result = self.status_renderer.render_status_block("COMPLETED", "Status")

        self.assertIn("Status:", result)
        self.assertIn("[x]", result)


class TestTaskItem(unittest.TestCase):
    """Test the TaskItem dataclass"""

    def test_task_item_creation(self):
        """Test creating a TaskItem"""
        task = TaskItem(id="1", title="Test task", status="PENDING")

        self.assertEqual(task.id, "1")
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.status, "PENDING")

    def test_task_item_defaults(self):
        """Test TaskItem default values"""
        task = TaskItem(id="1", title="Test task")

        self.assertEqual(task.status, "PENDING")
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
        self.assertEqual(task.tags, [])


if __name__ == '__main__':
    unittest.main()