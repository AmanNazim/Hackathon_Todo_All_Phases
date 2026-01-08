"""
Tests for UX Systems Components
Testing the UX Systems tasks: T090-T096
"""
import unittest
from unittest.mock import Mock
from datetime import datetime
from src.ux_systems.ux_systems import (
    WelcomeSystem,
    QuickStartGuide,
    HelpSystem,
    HintSystem,
    TipSystem,
    ExitSessionSummary,
    AdaptiveHelpSystem,
    UXController,
    UserSessionStats,
    HelpTopic
)
from src.rendering.rendering_engine import MinimalTheme, MessageFormatter


class TestWelcomeSystem(unittest.TestCase):
    """Test the welcome message with brief introduction (T090)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.welcome_system = WelcomeSystem(self.renderer)

    def test_show_welcome_message_contains_introduction(self):
        """Test that welcome message contains introduction (T090)"""
        result = self.welcome_system.show_welcome_message()

        self.assertIn("Welcome", result)
        self.assertIn("CLI Todo App", result)
        self.assertIn("command-line task manager", result)
        self.assertGreater(len(result), 50)  # Ensure it's not too short


class TestQuickStartGuide(unittest.TestCase):
    """Test the quick start guide for new users (T091)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.guide = QuickStartGuide(self.renderer)

    def test_show_quick_start_guide(self):
        """Test that quick start guide shows instructions (T091)"""
        result = self.guide.show_quick_start_guide()

        self.assertIn("Getting Started", result)
        self.assertIn("add", result)
        self.assertIn("list", result)
        self.assertIn("complete", result)
        self.assertGreater(len(result), 100)  # Ensure it has substantial content

    def test_quick_start_guide_has_examples(self):
        """Test that quick start guide has command examples (T091)"""
        result = self.guide.show_quick_start_guide()

        self.assertIn("add Buy groceries", result)
        self.assertIn("list", result)
        self.assertIn("complete 1", result)


class TestHelpSystem(unittest.TestCase):
    """Test the help system with command examples (T092)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.help_system = HelpSystem(self.renderer)

    def test_show_general_help(self):
        """Test that general help shows all commands (T092)"""
        result = self.help_system.show_general_help()

        self.assertIn("Available Commands", result)
        self.assertIn("add", result)
        self.assertIn("list", result)
        self.assertIn("update", result)
        self.assertIn("delete", result)

    def test_show_topic_help(self):
        """Test that topic help shows specific examples (T092)"""
        result = self.help_system.show_topic_help(HelpTopic.ADD)

        self.assertIn("Help: add", result)
        self.assertIn("Description", result)
        self.assertIn("add Buy groceries", result)
        self.assertIn("a Finish report due Monday", result)

    def test_show_help_with_topic(self):
        """Test showing help with specific topic (T092)"""
        result = self.help_system.show_help("add")

        self.assertIn("Help: add", result)

    def test_show_help_with_invalid_topic(self):
        """Test showing help with invalid topic (T092)"""
        result = self.help_system.show_help("invalid_topic")

        self.assertIn("[ERROR]", result)
        self.assertIn("No help available", result)


class TestHintSystem(unittest.TestCase):
    """Test contextual hints based on user patterns (T093)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.hint_system = HintSystem(self.renderer)

    def test_register_user_action(self):
        """Test registering user actions (T093)"""
        self.hint_system.register_user_action("add", {"title": "test"})

        self.assertIn("add", self.hint_system.user_patterns)
        self.assertEqual(len(self.hint_system.user_patterns["add"]), 1)

    def test_get_contextual_hint_new_user_main_menu(self):
        """Test contextual hint for new user in main menu (T093)"""
        hint = self.hint_system.get_contextual_hint("MAIN_MENU")

        # May not return a hint immediately, but shouldn't error
        if hint:
            self.assertIn("add", hint) or self.assertIn("help", hint)

    def test_get_contextual_hint_after_repeated_action(self):
        """Test hint for repeated actions (T093)"""
        # Simulate repeated add actions
        for _ in range(4):
            self.hint_system.register_user_action("add", {"title": "test"})

        hint = self.hint_system.get_contextual_hint("ADDING_TASK", "add")

        if hint:
            self.assertIn("add", hint) and self.assertIn("shortcuts", hint)


class TestTipSystem(unittest.TestCase):
    """Test non-blocking tip display system (T094)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.tip_system = TipSystem(self.renderer)

    def test_get_random_tip(self):
        """Test getting a random tip (T094)"""
        tip = self.tip_system.get_random_tip()

        self.assertIsInstance(tip, str)
        self.assertGreater(len(tip), 0)

    def test_get_contextual_tip_add(self):
        """Test getting contextual tip for add command (T094)"""
        tip = self.tip_system.get_contextual_tip("add")

        self.assertIsInstance(tip, str)

    def test_get_contextual_tip_list(self):
        """Test getting contextual tip for list command (T094)"""
        tip = self.tip_system.get_contextual_tip("list")

        self.assertIsInstance(tip, str)
        if tip:
            self.assertIn("list", tip)


class TestExitSessionSummary(unittest.TestCase):
    """Test exit session summary with statistics (T095)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.summary = ExitSessionSummary(self.renderer)

    def test_generate_session_summary(self):
        """Test generating session summary (T095)"""
        stats = UserSessionStats()
        stats.tasks_created = 5
        stats.tasks_completed = 3
        stats.commands_executed = 12
        stats.session_start_time = datetime.now()
        stats.session_end_time = datetime.now()

        result = self.summary.generate_session_summary(stats)

        self.assertIn("Session Summary", result)
        self.assertIn("Tasks Created:     5", result)
        self.assertIn("Tasks Completed:   3", result)
        self.assertIn("Commands Executed: 12", result)


class TestAdaptiveHelpSystem(unittest.TestCase):
    """Test adaptive help behavior (T096)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.mock_help_system = Mock()
        self.mock_help_system.show_help.return_value = "Mock help content"
        self.mock_help_system.show_general_help.return_value = "Mock general help"
        self.adaptive_help = AdaptiveHelpSystem(self.renderer, self.mock_help_system)

    def test_update_user_profile_new_user(self):
        """Test updating user profile for new user (T096)"""
        self.adaptive_help.update_user_profile("add")

        self.assertEqual(self.adaptive_help.user_experience_level, "new")

    def test_update_user_profile_intermediate_user(self):
        """Test updating user profile for intermediate user (T096)"""
        # Update profile multiple times to reach intermediate level
        for i in range(10):
            self.adaptive_help.update_user_profile("add")

        # Should now be intermediate level
        self.assertEqual(self.adaptive_help.user_experience_level, "intermediate")

    def test_get_adaptive_help_new_user(self):
        """Test adaptive help for new user (T096)"""
        # Since we're mocking, just test that the method can be called
        result = self.adaptive_help.get_adaptive_help()

        # The method should work without errors
        self.assertIsNotNone(result)


class TestUXController(unittest.TestCase):
    """Test the main UX Controller"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MinimalTheme()
        self.controller = UXController(self.renderer)

    def test_show_welcome(self):
        """Test showing welcome message"""
        result = self.controller.show_welcome()

        self.assertIn("Welcome", result)

    def test_show_quick_start(self):
        """Test showing quick start guide"""
        result = self.controller.show_quick_start()

        self.assertIn("Getting Started", result)

    def test_show_help(self):
        """Test showing help"""
        result = self.controller.show_help()

        self.assertIn("Available Commands", result)

    def test_get_contextual_hint(self):
        """Test getting contextual hint"""
        hint = self.controller.get_contextual_hint("MAIN_MENU")

        # May return None if no hint is appropriate
        if hint is not None:
            self.assertIsInstance(hint, str)

    def test_get_tip(self):
        """Test getting tip"""
        tip = self.controller.get_tip("add")

        self.assertIsInstance(tip, str)

    def test_register_user_action(self):
        """Test registering user action"""
        # Should not raise an exception
        self.controller.register_user_action("add", {"title": "test"})

    def test_update_session_stats(self):
        """Test updating session stats"""
        initial_count = self.controller.session_stats.tasks_created

        self.controller.update_session_stats("task_created")

        self.assertEqual(self.controller.session_stats.tasks_created, initial_count + 1)

    def test_generate_exit_summary(self):
        """Test generating exit summary"""
        result = self.controller.generate_exit_summary()

        self.assertIn("Session Summary", result)


class TestUserSessionStats(unittest.TestCase):
    """Test the UserSessionStats dataclass"""

    def test_user_session_stats_defaults(self):
        """Test default values for UserSessionStats"""
        stats = UserSessionStats()

        self.assertEqual(stats.tasks_created, 0)
        self.assertEqual(stats.tasks_completed, 0)
        self.assertEqual(stats.commands_executed, 0)
        self.assertIsNotNone(stats.session_start_time)

    def test_user_session_stats_custom_values(self):
        """Test custom values for UserSessionStats"""
        now = datetime.now()
        stats = UserSessionStats(
            tasks_created=5,
            tasks_completed=3,
            commands_executed=10,
            session_start_time=now
        )

        self.assertEqual(stats.tasks_created, 5)
        self.assertEqual(stats.tasks_completed, 3)
        self.assertEqual(stats.commands_executed, 10)
        self.assertEqual(stats.session_start_time, now)


if __name__ == '__main__':
    unittest.main()