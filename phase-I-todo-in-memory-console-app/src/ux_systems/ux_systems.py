"""
UX Systems for CLI Todo Application
Implements onboarding, help, hints, and session summary as specified in spec section 16
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from enum import Enum
from dataclasses import dataclass
from src.rendering.rendering_engine import BaseRenderer, MessageFormatter
from src.parsers.command_parser import CommandParser
from src.state_machine.cli_state_machine import CLIState


class HelpTopic(Enum):
    """Available help topics"""
    ADD = "add"
    LIST = "list"
    UPDATE = "update"
    DELETE = "delete"
    COMPLETE = "complete"
    HELP = "help"
    UNDO = "undo"
    THEME = "theme"
    SNAPSHOT = "snapshot"
    MACRO = "macro"
    GENERAL = "general"


@dataclass
class UserSessionStats:
    """Track user session statistics"""
    tasks_created: int = 0
    tasks_completed: int = 0
    commands_executed: int = 0
    session_start_time: datetime = None
    session_end_time: datetime = None

    def __post_init__(self):
        if self.session_start_time is None:
            self.session_start_time = datetime.now()


class WelcomeSystem:
    """
    Create welcome message with brief introduction (T090)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer

    def show_welcome_message(self) -> str:
        """
        Display welcome message with brief introduction
        """
        welcome_msg = self.renderer.render_header("Welcome to CLI Todo App")

        intro_text = """
Welcome to the CLI Todo Application!

This is a sophisticated command-line task manager that supports:
• Adding, viewing, updating, and deleting tasks
• Managing task status (pending/completed)
• Multiple interaction modes (menu, natural language, hybrid)
• Various visual themes to customize your experience
• Advanced features like undo, macros, and snapshots

For help, type 'help' or '?' at any time.
"""
        return welcome_msg + intro_text + self.renderer.render_footer()


class QuickStartGuide:
    """
    Implement quick start guide for new users (T091)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer

    def show_quick_start_guide(self) -> str:
        """
        Display quick start guide for new users
        """
        guide_msg = self.renderer.render_header("Quick Start Guide")

        guide_text = """
Getting Started with CLI Todo:

1. Add a new task:
   • Type: add Buy groceries
   • Or: a Buy groceries (shortcut)

2. View all tasks:
   • Type: list
   • Or: l (shortcut)

3. Complete a task:
   • Type: complete 1 (where 1 is the task ID)
   • Or: c 1 (shortcut)

4. Update a task:
   • Type: update 1 Buy organic groceries

5. Delete a task:
   • Type: delete 1
   • Or: d 1 (shortcut)

6. Get help:
   • Type: help
   • Or: ? (shortcut)

Try adding your first task now!
"""
        return guide_msg + guide_text + self.renderer.render_footer()


class HelpSystem:
    """
    Create help system with command examples (T092)
    """

    def __init__(self, renderer: BaseRenderer, command_parser: CommandParser = None):
        self.renderer = renderer
        self.command_parser = command_parser
        self.message_formatter = MessageFormatter(renderer)

        # Define command examples
        self.command_examples = {
            HelpTopic.ADD: [
                "add Buy groceries",
                "add Call mom tomorrow",
                "a Finish report due Monday"
            ],
            HelpTopic.LIST: [
                "list",
                "list completed",
                "list pending",
                "l"
            ],
            HelpTopic.UPDATE: [
                "update 1 Buy organic groceries",
                "edit 2 Call dad instead",
                "update 3 Finish report - urgent"
            ],
            HelpTopic.DELETE: [
                "delete 1",
                "remove 2",
                "del 3",
                "d 4"
            ],
            HelpTopic.COMPLETE: [
                "complete 1",
                "done 2",
                "finish 3",
                "c 4"
            ],
            HelpTopic.UNDO: [
                "undo",
                "revert"
            ],
            HelpTopic.THEME: [
                "theme minimal",
                "theme emoji",
                "theme hacker",
                "theme professional"
            ],
            HelpTopic.SNAPSHOT: [
                "snapshot save",
                "snapshot list",
                "snapshot load"
            ],
            HelpTopic.MACRO: [
                "macro record",
                "macro play my_macro",
                "macro list"
            ],
            HelpTopic.GENERAL: [
                "help",
                "help add",
                "?",
                "? list"
            ]
        }

        self.topic_descriptions = {
            HelpTopic.ADD: "Adding tasks with title and optional description",
            HelpTopic.LIST: "Viewing and filtering task lists",
            HelpTopic.UPDATE: "Updating existing tasks",
            HelpTopic.DELETE: "Removing tasks from the list",
            HelpTopic.COMPLETE: "Marking tasks as completed/incomplete",
            HelpTopic.UNDO: "Reverting the last command",
            HelpTopic.THEME: "Changing the application theme",
            HelpTopic.SNAPSHOT: "Managing application snapshots",
            HelpTopic.MACRO: "Recording and playing command macros",
            HelpTopic.GENERAL: "General help and information"
        }

    def show_general_help(self) -> str:
        """Show general help with all available commands"""
        header = self.renderer.render_header("CLI Todo Help")

        help_text = """
Available Commands:
==================

Task Management:
  add <title> [description]     - Add a new task
  a <title> [description]       - Shortcut for add
  list [filter]                 - List all tasks (completed/pending/all)
  l                             - Shortcut for list
  update <id> <new_title> [desc] - Update task details
  edit <id> <new_title> [desc]  - Shortcut for update
  delete <id>                   - Delete a task
  remove <id>                   - Shortcut for delete
  del <id>                      - Shortcut for delete
  d <id>                        - Shortcut for delete
  complete <id>                 - Mark task as complete
  done <id>                     - Shortcut for complete
  finish <id>                   - Shortcut for complete
  c <id>                        - Shortcut for complete
  incomplete <id>               - Mark task as incomplete
  reopen <id>                   - Shortcut for incomplete
  open <id>                     - Shortcut for incomplete
  i <id>                        - Shortcut for incomplete

System Commands:
  help [topic]                  - Show help (this page)
  h [topic]                     - Shortcut for help
  ? [topic]                     - Shortcut for help
  --help [topic]                - Shortcut for help
  theme <name>                  - Change display theme
  undo                          - Undo last command
  revert                        - Shortcut for undo
  snapshot [action]             - Manage snapshots
  macro [action] [name]         - Record/play command macros

Theme Options:
  minimal, emoji, hacker, professional

Filter Options:
  completed, pending, all
"""

        footer = "\nFor specific help, type: help <command>\n"
        return header + help_text + footer + self.renderer.render_footer()

    def show_topic_help(self, topic: HelpTopic) -> str:
        """Show help for a specific topic"""
        header = self.renderer.render_header(f"Help: {topic.value}")

        description = self.topic_descriptions.get(topic, "No description available")
        examples = self.command_examples.get(topic, [])

        help_text = f"\nDescription:\n  {description}\n\nExamples:\n"
        for example in examples:
            help_text += f"  • {example}\n"

        return header + help_text + self.renderer.render_footer()

    def show_help(self, topic_str: str = None) -> str:
        """Main help function that shows general help or specific topic help"""
        if topic_str is None:
            return self.show_general_help()

        # Map topic string to enum
        topic_map = {t.value: t for t in HelpTopic}
        topic = topic_map.get(topic_str.lower())

        if topic:
            return self.show_topic_help(topic)
        else:
            # Try to find closest match
            for t in HelpTopic:
                if topic_str.lower() in t.value:
                    return self.show_topic_help(t)

            # If no match, show general help
            error_msg = self.message_formatter.format_error(f"No help available for topic: {topic_str}")
            general_help = self.show_general_help()
            return error_msg + "\n\n" + general_help


class HintSystem:
    """
    Implement contextual hints based on user patterns (T093)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer
        self.message_formatter = MessageFormatter(renderer)
        self.user_patterns = {}
        self.session_start_time = time.time()

    def register_user_action(self, action: str, details: Dict[str, Any] = None):
        """Register a user action to track patterns"""
        if action not in self.user_patterns:
            self.user_patterns[action] = []
        self.user_patterns[action].append({
            'timestamp': time.time(),
            'details': details
        })

    def get_contextual_hint(self, current_state: str, command: str = None) -> Optional[str]:
        """Generate contextual hint based on user patterns and current context"""
        # Calculate session duration
        session_duration = time.time() - self.session_start_time

        # Provide hints based on session duration and user behavior
        if session_duration < 60:  # Less than 1 minute
            # New user hints
            if current_state == "MAIN_MENU":
                return self.message_formatter.format_warning(
                    "Tip: Type 'add' to create your first task, or 'help' for command examples"
                )
            elif command and "list" in command.lower():
                return self.message_formatter.format_warning(
                    "Tip: You can filter tasks with 'list completed' or 'list pending'"
                )
        elif session_duration > 300:  # More than 5 minutes
            # Experienced user hints
            if current_state == "ADDING_TASK":
                return self.message_formatter.format_warning(
                    "Pro tip: You can add multiple tasks in a row without returning to main menu"
                )

        # Check for repeated actions that might indicate confusion
        if command:
            command_count = len([act for act in self.user_patterns.get(command, [])])
            if command_count > 3:
                return self.message_formatter.format_warning(
                    f"It seems you're using '{command}' frequently. Did you know you can use shortcuts like 'a' for add, 'l' for list?"
                )

        return None

    def get_common_usage_hint(self) -> Optional[str]:
        """Provide common usage hints based on typical user behavior"""
        # If user has created several tasks but never completed any
        created_count = len(self.user_patterns.get("add", []))
        completed_count = len(self.user_patterns.get("complete", []))

        if created_count > 3 and completed_count == 0:
            return self.message_formatter.format_warning(
                "You've added several tasks! Remember to mark completed tasks with 'complete <id>'"
            )

        # If user is frequently listing tasks
        list_count = len(self.user_patterns.get("list", []))
        if list_count > 5:
            return self.message_formatter.format_warning(
                "You seem to be checking your task list often. Consider using 'list completed' or 'list pending' to filter"
            )

        return None


class TipSystem:
    """
    Add non-blocking tip display system (T094)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer
        self.message_formatter = MessageFormatter(renderer)
        self.tips = [
            "💡 Pro tip: Use shortcuts like 'a', 'l', 'c', 'd' for faster task management",
            "💡 You can change themes with 'theme <name>' to suit your preference",
            "💡 Use 'undo' to reverse your last command if you make a mistake",
            "💡 Tasks can have descriptions: 'add Buy groceries Get milk, eggs, bread'",
            "💡 Use 'list completed' to see finished tasks or 'list pending' for active ones",
            "💡 The CLI supports both menu mode and natural language mode",
            "💡 Press Ctrl+C to exit the application at any time",
            "💡 Use 'help <command>' to get specific help for any command",
            "💡 You can use 'snapshot save' to save your current state",
            "💡 Macros let you record and replay sequences of commands"
        ]
        self.tip_interval = 300  # Show tip every 5 minutes of activity
        self.last_tip_time = 0
        self.current_tip_index = 0

    def should_show_tip(self) -> bool:
        """Check if enough time has passed to show another tip"""
        current_time = time.time()
        return (current_time - self.last_tip_time) > self.tip_interval

    def get_random_tip(self) -> str:
        """Get a random tip"""
        if not self.tips:
            return ""

        tip = self.tips[self.current_tip_index % len(self.tips)]
        self.current_tip_index += 1
        self.last_tip_time = time.time()
        return tip

    def get_contextual_tip(self, context: str = None) -> str:
        """Get a contextual tip based on the current context"""
        if context == "add":
            return "💡 Pro tip: You can add multiple tasks with descriptions: 'add Buy groceries Get milk, eggs, bread'"
        elif context == "list":
            return "💡 Pro tip: Filter your list with 'list completed', 'list pending', or 'list all'"
        elif context == "theme":
            return "💡 Pro tip: Try different themes: minimal, emoji, hacker, professional"
        elif context == "help":
            return "💡 Pro tip: Use 'help <command>' to get specific help for any command"

        # Otherwise return a random tip if appropriate
        if self.should_show_tip():
            return self.get_random_tip()

        return ""


class ExitSessionSummary:
    """
    Create exit session summary with statistics (T095)
    """

    def __init__(self, renderer: BaseRenderer):
        self.renderer = renderer
        self.message_formatter = MessageFormatter(renderer)

    def generate_session_summary(self, stats: UserSessionStats) -> str:
        """Generate exit session summary with statistics"""
        header = self.renderer.render_header("Session Summary")

        # Calculate session duration
        if stats.session_end_time:
            duration = stats.session_end_time - stats.session_start_time
            duration_minutes = int(duration.total_seconds() / 60)
        else:
            duration_minutes = int((datetime.now() - stats.session_start_time).total_seconds() / 60)

        summary_text = f"""
Session Statistics:
=================
• Tasks Created:     {stats.tasks_created}
• Tasks Completed:   {stats.tasks_completed}
• Commands Executed: {stats.commands_executed}
• Session Duration:  ~{duration_minutes} minutes

Achievement Summary:
• Completion Rate:   {self._calculate_completion_rate(stats):.1f}% of created tasks
• Activity Level:    {self._determine_activity_level(stats)}
"""

        if stats.tasks_completed > 0:
            summary_text += f"• Productivity Score:  {self._calculate_productivity_score(stats)}\n"

        footer = f"""
Thank you for using CLI Todo App!
Come back anytime to manage your tasks efficiently.
"""

        return header + summary_text + footer + self.renderer.render_footer()

    def _calculate_completion_rate(self, stats: UserSessionStats) -> float:
        """Calculate task completion rate percentage"""
        if stats.tasks_created == 0:
            return 0.0
        return (stats.tasks_completed / stats.tasks_created) * 100

    def _determine_activity_level(self, stats: UserSessionStats) -> str:
        """Determine activity level based on commands executed"""
        if stats.commands_executed < 5:
            return "Casual User"
        elif stats.commands_executed < 15:
            return "Regular User"
        elif stats.commands_executed < 30:
            return "Active User"
        else:
            return "Power User"

    def _calculate_productivity_score(self, stats: UserSessionStats) -> str:
        """Calculate a simple productivity score"""
        if stats.tasks_completed == 0:
            return "Just Getting Started"

        ratio = stats.tasks_completed / max(stats.tasks_created, 1)
        if ratio >= 0.8:
            return "High Achiever 🌟"
        elif ratio >= 0.6:
            return "Productive 🚀"
        elif ratio >= 0.4:
            return "Making Progress 📈"
        else:
            return "Building Momentum 💪"


class AdaptiveHelpSystem:
    """
    Implement adaptive help behavior (T096)
    """

    def __init__(self, renderer: BaseRenderer, help_system: HelpSystem):
        self.renderer = renderer
        self.help_system = help_system
        self.user_experience_level = "new"  # new, intermediate, experienced
        self.command_usage_counts = {}
        self.session_start_time = time.time()

    def update_user_profile(self, command: str):
        """Update user profile based on command usage"""
        if command not in self.command_usage_counts:
            self.command_usage_counts[command] = 0
        self.command_usage_counts[command] += 1

        # Recalculate experience level
        total_commands = sum(self.command_usage_counts.values())
        unique_commands = len(self.command_usage_counts)

        if total_commands < 5:
            self.user_experience_level = "new"
        elif total_commands < 20 or unique_commands < 5:
            self.user_experience_level = "intermediate"
        else:
            self.user_experience_level = "experienced"

    def get_adaptive_help(self, topic: str = None) -> str:
        """Get help content adapted to user experience level"""
        if self.user_experience_level == "new":
            return self._get_beginner_help(topic)
        elif self.user_experience_level == "intermediate":
            return self._get_intermediate_help(topic)
        else:
            return self._get_advanced_help(topic)

    def _get_beginner_help(self, topic: str = None) -> str:
        """Get simplified help for beginners"""
        if topic:
            basic_help = self.help_system.show_help(topic)
            # Add beginner-friendly explanations
            beginner_addition = "\n\nAs a new user, remember:\n• Start with simple commands like 'add' and 'list'\n• Use 'help' anytime for assistance\n• Shortcuts like 'a', 'l', 'c', 'd' make tasks faster"
            return basic_help + beginner_addition
        else:
            return self.help_system.show_general_help()

    def _get_intermediate_help(self, topic: str = None) -> str:
        """Get moderately detailed help for intermediate users"""
        if topic:
            return self.help_system.show_help(topic)
        else:
            # Add some advanced tips to general help
            general_help = self.help_system.show_general_help()
            intermediate_tips = "\n\nAdvanced Tips:\n• Use filters with list command\n• Try different themes for better visibility\n• Use undo to reverse mistakes\n• Check command shortcuts to save time"
            return general_help + intermediate_tips

    def _get_advanced_help(self, topic: str = None) -> str:
        """Get detailed help for advanced users"""
        if topic:
            # For advanced users, provide more technical details
            basic_help = self.help_system.show_help(topic)
            # Add advanced usage patterns
            if topic == "add":
                advanced_section = "\n\nAdvanced Usage:\n• Add multiple tasks in batch mode\n• Use tags to categorize tasks\n• Combine with macros for automation"
                return basic_help + advanced_section
            elif topic == "list":
                advanced_section = "\n\nAdvanced Usage:\n• Chain filters: list completed pending\n• Export lists to different formats\n• Use with custom themes"
                return basic_help + advanced_section
            else:
                return basic_help
        else:
            # Advanced users get the standard help with power-user additions
            return self.help_system.show_general_help()


class UXController:
    """
    Main controller for all UX systems
    """

    def __init__(self,
                 renderer: BaseRenderer,
                 command_parser: CommandParser = None):
        self.welcome_system = WelcomeSystem(renderer)
        self.quick_start_guide = QuickStartGuide(renderer)
        self.help_system = HelpSystem(renderer, command_parser)
        self.hint_system = HintSystem(renderer)
        self.tip_system = TipSystem(renderer)
        self.exit_summary = ExitSessionSummary(renderer)
        self.adaptive_help_system = AdaptiveHelpSystem(renderer, self.help_system)

        # Initialize session stats
        self.session_stats = UserSessionStats()

    def show_welcome(self) -> str:
        """Show welcome message"""
        return self.welcome_system.show_welcome_message()

    def show_quick_start(self) -> str:
        """Show quick start guide"""
        return self.quick_start_guide.show_quick_start_guide()

    def show_help(self, topic: str = None) -> str:
        """Show help (adaptive based on user experience)"""
        return self.adaptive_help_system.get_adaptive_help(topic)

    def get_contextual_hint(self, current_state: str, command: str = None) -> Optional[str]:
        """Get contextual hint"""
        hint = self.hint_system.get_contextual_hint(current_state, command)
        if not hint:
            hint = self.hint_system.get_common_usage_hint()
        return hint

    def get_tip(self, context: str = None) -> str:
        """Get a tip"""
        return self.tip_system.get_contextual_tip(context)

    def register_user_action(self, action: str, details: Dict[str, Any] = None):
        """Register user action for pattern analysis"""
        self.hint_system.register_user_action(action, details)
        self.adaptive_help_system.update_user_profile(action)

    def generate_exit_summary(self) -> str:
        """Generate exit session summary"""
        self.session_stats.session_end_time = datetime.now()
        return self.exit_summary.generate_session_summary(self.session_stats)

    def update_session_stats(self, stat_type: str):
        """Update session statistics"""
        if stat_type == "task_created":
            self.session_stats.tasks_created += 1
        elif stat_type == "task_completed":
            self.session_stats.tasks_completed += 1
        elif stat_type == "command_executed":
            self.session_stats.commands_executed += 1