"""
Renderer Middleware for CLI Todo Application
T055: Create RendererMiddleware for formatting output
"""
from typing import Dict, Any, Callable
from .pipeline import MiddlewareResult, MiddlewareResultStatus


class BaseRenderer:
    """Base renderer class defining the interface"""

    def format_success(self, message: str) -> str:
        raise NotImplementedError

    def format_error(self, message: str) -> str:
        raise NotImplementedError

    def format_warning(self, message: str) -> str:
        raise NotImplementedError

    def format_info(self, message: str) -> str:
        raise NotImplementedError

    def format_help(self, content: str) -> str:
        raise NotImplementedError

    def render_task_list(self, tasks) -> str:
        raise NotImplementedError

    def format_snapshot_list(self, snapshots) -> str:
        raise NotImplementedError

    def format_macro_list(self, macros) -> str:
        raise NotImplementedError


class MinimalRenderer(BaseRenderer):
    """Minimal renderer implementation"""
    def format_success(self, message: str) -> str:
        return f"✓ {message}"

    def format_error(self, message: str) -> str:
        return f"✗ {message}"

    def format_warning(self, message: str) -> str:
        return f"⚠ {message}"

    def format_info(self, message: str) -> str:
        return f"ℹ {message}"

    def format_help(self, content: str) -> str:
        return content

    def render_task_list(self, tasks) -> str:
        if not tasks:
            return self.format_info("No tasks found.")

        output = "ID\tTitle\t\t\tStatus\n"
        output += "-" * 50 + "\n"
        for task in tasks:
            # Assuming task has id, title and status attributes
            status = "COMPLETED" if hasattr(task, 'status') and str(task.status).upper().endswith('COMPLETED') else "PENDING"
            title = getattr(task, 'title', 'No Title')
            task_id = getattr(task, 'id', 'No ID')
            output += f"{task_id[:8]}\t{title[:20]}\t\t{status}\n"
        return output

    def format_snapshot_list(self, snapshots) -> str:
        return f"Snapshots: {len(snapshots)} found"

    def format_macro_list(self, macros) -> str:
        return f"Macros: {len(macros)} found"


class EmojiRenderer(MinimalRenderer):
    """Emoji renderer implementation"""
    def format_success(self, message: str) -> str:
        return f"✅ {message}"

    def format_error(self, message: str) -> str:
        return f"❌ {message}"

    def format_warning(self, message: str) -> str:
        return f"⚠️  {message}"

    def format_info(self, message: str) -> str:
        return f"ℹ️  {message}"


class HackerRenderer(MinimalRenderer):
    """Hacker renderer implementation"""
    def format_success(self, message: str) -> str:
        return f"[OK] {message}"

    def format_error(self, message: str) -> str:
        return f"[ERROR] {message}"

    def format_warning(self, message: str) -> str:
        return f"[WARN] {message}"

    def format_info(self, message: str) -> str:
        return f"[INFO] {message}"


class ProfessionalRenderer(MinimalRenderer):
    """Professional renderer implementation"""
    def format_success(self, message: str) -> str:
        return f"✓ {message.upper()}"

    def format_error(self, message: str) -> str:
        return f"✗ {message.upper()}"

    def format_warning(self, message: str) -> str:
        return f"⚠ {message.upper()}"

    def format_info(self, message: str) -> str:
        return f"ℹ {message.upper()}"


class ThemeManager:
    """Simple theme manager for handling themes"""

    def __init__(self):
        self.available_themes = ['minimal', 'emoji', 'hacker', 'professional']
        self.current_theme = 'minimal'


class RendererMiddleware:
    """
    Middleware to format output according to current theme and display requirements
    Implements T055: Create RendererMiddleware for formatting output
    """

    def __init__(self, theme_manager=None):
        self.name = "RendererMiddleware"
        self.theme_manager = theme_manager or ThemeManager()

        # Initialize available renderers
        self.renderers = {
            'minimal': MinimalRenderer(),
            'emoji': EmojiRenderer(),
            'hacker': HackerRenderer(),
            'professional': ProfessionalRenderer()
        }

        # Set default theme
        self.current_theme = 'minimal'

    def process(self, data: Dict[str, Any], next_middleware: Callable) -> MiddlewareResult:
        """
        Process the input data by formatting output according to the current theme
        """
        # Get the intent and results from previous middleware
        intent = data.get('intent', 'unknown')
        results = data.get('results', {})  # Results from command execution

        # Determine what needs to be rendered based on the intent
        formatted_output = self._format_output(intent, results, data)

        # Add the formatted output to the data
        data['formatted_output'] = formatted_output
        data['render_context'] = {
            'theme': self.current_theme,
            'output_format': 'cli',
            'timestamp': data.get('analytics', {}).get('timestamp', None)
        }

        # Pass to the next middleware in the chain
        return next_middleware(data)

    def _format_output(self, intent: str, results: Dict[str, Any], full_data: Dict[str, Any]) -> str:
        """
        Format the output based on intent and results
        """
        # Get the current renderer based on theme
        current_renderer = self.renderers.get(self.current_theme, self.renderers['minimal'])

        try:
            if intent == 'add':
                return self._format_add_result(results, current_renderer)
            elif intent == 'list':
                return self._format_list_result(results, current_renderer)
            elif intent in ['update', 'delete', 'complete', 'incomplete']:
                return self._format_operation_result(intent, results, current_renderer)
            elif intent == 'help':
                return self._format_help_result(results, current_renderer)
            elif intent == 'theme':
                return self._format_theme_result(results, current_renderer)
            elif intent == 'undo':
                return self._format_undo_result(results, current_renderer)
            elif intent == 'snapshot':
                return self._format_snapshot_result(results, current_renderer)
            elif intent == 'macro':
                return self._format_macro_result(results, current_renderer)
            else:
                # For unknown intents or error cases
                if 'error' in results:
                    return self._format_error_result(results, current_renderer)
                else:
                    return self._format_default_result(results, current_renderer)

        except Exception as e:
            # If formatting fails, return a simple error message
            return current_renderer.format_error(f"Error formatting output: {str(e)}")

    def _format_add_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of an add command
        """
        if results.get('success', False):
            task_id = results.get('task_id', 'unknown')
            title = results.get('title', 'untitled')
            return renderer.format_success(f"Task added with ID: {task_id}")
        else:
            error_msg = results.get('error', 'Unknown error')
            return renderer.format_error(f"Failed to add task: {error_msg}")

    def _format_list_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of a list command
        """
        tasks = results.get('tasks', [])
        if not tasks:
            return renderer.format_info("No tasks found.")

        # Format the task list using the renderer
        return renderer.render_task_list(tasks)

    def _format_operation_result(self, operation: str, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of update/delete/complete/incomplete operations
        """
        success = results.get('success', False)
        task_id = results.get('task_id', 'unknown')

        if success:
            if operation == 'update':
                return renderer.format_success(f"Task {task_id} updated successfully")
            elif operation == 'delete':
                return renderer.format_success(f"Task {task_id} deleted successfully")
            elif operation == 'complete':
                return renderer.format_success(f"Task {task_id} marked as complete")
            elif operation == 'incomplete':
                return renderer.format_success(f"Task {task_id} marked as incomplete")
        else:
            error_msg = results.get('error', 'Operation failed')
            return renderer.format_error(f"Failed to {operation} task {task_id}: {error_msg}")

    def _format_help_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of a help command
        """
        help_content = results.get('help_content', 'No help content available')
        return renderer.format_help(help_content)

    def _format_theme_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of a theme command
        """
        success = results.get('success', False)
        theme_name = results.get('theme_name', 'unknown')

        if success:
            return renderer.format_success(f"Theme changed to: {theme_name}")
        else:
            error_msg = results.get('error', 'Failed to change theme')
            return renderer.format_error(error_msg)

    def _format_undo_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of an undo command
        """
        success = results.get('success', False)

        if success:
            undone_command = results.get('undone_command', 'unknown')
            return renderer.format_success(f"Undid: {undone_command}")
        else:
            error_msg = results.get('error', 'Undo failed')
            return renderer.format_error(error_msg)

    def _format_snapshot_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of a snapshot command
        """
        success = results.get('success', False)
        action = results.get('action', 'unknown')

        if success:
            if action == 'list':
                snapshots = results.get('snapshots', [])
                return renderer.format_snapshot_list(snapshots)
            else:
                return renderer.format_success(f"Snapshot {action} completed successfully")
        else:
            error_msg = results.get('error', 'Snapshot operation failed')
            return renderer.format_error(error_msg)

    def _format_macro_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format the result of a macro command
        """
        success = results.get('success', False)
        action = results.get('action', 'unknown')

        if success:
            if action == 'list':
                macros = results.get('macros', [])
                return renderer.format_macro_list(macros)
            else:
                return renderer.format_success(f"Macro {action} completed successfully")
        else:
            error_msg = results.get('error', 'Macro operation failed')
            return renderer.format_error(error_msg)

    def _format_error_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format an error result
        """
        error_msg = results.get('error', 'An error occurred')
        suggestions = results.get('suggestions', [])

        error_output = renderer.format_error(error_msg)

        if suggestions:
            error_output += "\nSuggestions: " + "; ".join(suggestions)

        return error_output

    def _format_default_result(self, results: Dict[str, Any], renderer) -> str:
        """
        Format a default result when intent is unknown
        """
        if results:
            return renderer.format_info(str(results))
        else:
            return renderer.format_info("Command processed")

    def set_theme(self, theme_name: str) -> bool:
        """
        Change the current theme for output formatting
        """
        if theme_name in self.renderers:
            self.current_theme = theme_name
            return True
        return False

    def get_available_themes(self) -> list:
        """
        Get list of available themes
        """
        return list(self.renderers.keys())

    def format_raw_output(self, content: Any, output_type: str = 'info') -> str:
        """
        Format raw content using the current renderer
        """
        current_renderer = self.renderers.get(self.current_theme, self.renderers['minimal'])

        if output_type == 'success':
            return current_renderer.format_success(str(content))
        elif output_type == 'error':
            return current_renderer.format_error(str(content))
        elif output_type == 'warning':
            return current_renderer.format_warning(str(content))
        else:
            return current_renderer.format_info(str(content))