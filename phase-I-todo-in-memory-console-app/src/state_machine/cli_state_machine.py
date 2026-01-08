"""
CLI State Machine for Todo Application
Implements state management for CLI interaction as specified in spec section 12
"""
from enum import Enum
from typing import Dict, Any, Callable, Optional
import threading
from dataclasses import dataclass
import time
from threading import RLock


class CLIState(Enum):
    """
    Define CLI state enumeration with MAIN_MENU, ADDING_TASK, UPDATING_TASK, etc. (T060)
    """
    MAIN_MENU = "MAIN_MENU"
    ADDING_TASK = "ADDING_TASK"
    UPDATING_TASK = "UPDATING_TASK"
    DELETING_TASK = "DELETING_TASK"
    CONFIRMATION_DIALOG = "CONFIRMATION_DIALOG"
    EXITING = "EXITING"

    def __hash__(self):
        """Make enum hashable for use in dictionaries"""
        return hash(self.value)


@dataclass
class StateTransition:
    """Represents a state transition with validation"""
    from_state: CLIState
    to_state: CLIState
    reason: str = ""
    allowed: bool = True


class CLIStateMachine:
    """
    Create state machine class to manage CLI states and transitions (T061)
    """

    def __init__(self):
        self._current_state: CLIState = CLIState.MAIN_MENU
        self._previous_state: Optional[CLIState] = None
        self._state_data: Dict[str, Any] = {}
        self._lock = RLock()  # Thread-safe operations
        self._transition_history: list = []

        # Define allowed state transitions according to specification
        self._allowed_transitions = {
            CLIState.MAIN_MENU: [
                CLIState.ADDING_TASK,
                CLIState.UPDATING_TASK,
                CLIState.DELETING_TASK,
                CLIState.EXITING,
                CLIState.CONFIRMATION_DIALOG
            ],
            CLIState.ADDING_TASK: [
                CLIState.MAIN_MENU
            ],
            CLIState.UPDATING_TASK: [
                CLIState.MAIN_MENU
            ],
            CLIState.DELETING_TASK: [
                CLIState.MAIN_MENU
            ],
            CLIState.CONFIRMATION_DIALOG: [
                CLIState.MAIN_MENU,  # Return to previous state after confirmation
                CLIState.EXITING
            ],
            CLIState.EXITING: [
                CLIState.EXITING  # Stay in exiting state until complete
            ]
        }

    @property
    def current_state(self) -> CLIState:
        """Get the current state"""
        with self._lock:
            return self._current_state

    @property
    def previous_state(self) -> Optional[CLIState]:
        """Get the previous state"""
        with self._lock:
            return self._previous_state

    def is_transition_allowed(self, from_state: CLIState, to_state: CLIState) -> bool:
        """
        Add state validation to prevent invalid transitions (T064)
        Implements validation as per specification section 12
        """
        with self._lock:
            allowed_destinations = self._allowed_transitions.get(from_state, [])
            is_allowed = to_state in allowed_destinations

            return is_allowed

    def validate_state_for_operation(self, operation: str) -> tuple[bool, str]:
        """
        Additional state validation for specific operations
        """
        with self._lock:
            current = self._current_state

            # Validate that we're in an appropriate state for the operation
            if operation == "add_task":
                # Can add task from main menu or adding task state
                if current in [CLIState.MAIN_MENU, CLIState.ADDING_TASK]:
                    return True, "Valid state for adding task"
                else:
                    return False, f"Cannot add task from {current.value} state"

            elif operation == "list_tasks":
                # Can list tasks from main menu or other states
                if current in [CLIState.MAIN_MENU, CLIState.ADDING_TASK, CLIState.UPDATING_TASK,
                              CLIState.DELETING_TASK, CLIState.CONFIRMATION_DIALOG]:
                    return True, "Valid state for listing tasks"
                else:
                    return False, f"Cannot list tasks from {current.value} state"

            elif operation == "update_task":
                # Can update task from main menu or updating task state
                if current in [CLIState.MAIN_MENU, CLIState.UPDATING_TASK]:
                    return True, "Valid state for updating task"
                else:
                    return False, f"Cannot update task from {current.value} state"

            elif operation == "delete_task":
                # Can delete task from main menu or deleting task state
                if current in [CLIState.MAIN_MENU, CLIState.DELETING_TASK]:
                    return True, "Valid state for deleting task"
                else:
                    return False, f"Cannot delete task from {current.value} state"

            elif operation == "complete_task":
                # Can complete task from main menu
                if current == CLIState.MAIN_MENU:
                    return True, "Valid state for completing task"
                else:
                    return False, f"Cannot complete task from {current.value} state"

            elif operation == "exit":
                # Can exit from any state
                return True, "Valid state for exiting"

            else:
                return False, f"Unknown operation: {operation}"

    def transition_to(self, new_state: CLIState, data: Optional[Dict[str, Any]] = None, reason: str = "") -> bool:
        """
        Attempt to transition to a new state (T062)
        Implements state transition rules as defined in specification section 12
        """
        with self._lock:
            current = self._current_state

            # Validate transition according to specification rules
            if not self.is_transition_allowed(current, new_state):
                # Log invalid transition attempt per specification
                self._transition_history.append({
                    'from': current,
                    'to': new_state,
                    'valid': False,
                    'timestamp': time.time(),
                    'reason': reason or 'Invalid transition per specification rules'
                })
                return False

            # Additional business logic for specific transitions
            transition_result = self._validate_business_rules(current, new_state, data)
            if not transition_result['valid']:
                self._transition_history.append({
                    'from': current,
                    'to': new_state,
                    'valid': False,
                    'timestamp': time.time(),
                    'reason': transition_result['reason']
                })
                return False

            # Store previous state as per specification requirement
            self._previous_state = current

            # Update current state
            self._current_state = new_state

            # Store transition data if provided for persistence across operations
            if data:
                self._state_data.update(data)

            # Log successful transition per specification
            self._transition_history.append({
                'from': current,
                'to': new_state,
                'valid': True,
                'timestamp': time.time(),
                'reason': reason or 'Valid transition per specification rules'
            })

            return True

    def _validate_business_rules(self, from_state: CLIState, to_state: CLIState, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate business rules for state transitions
        """
        # According to spec section 12, certain transitions have specific requirements
        if from_state == CLIState.CONFIRMATION_DIALOG and to_state == CLIState.MAIN_MENU:
            # When returning from confirmation dialog, we should have confirmation result
            if data and data.get('confirmed') is False:
                # If user didn't confirm, we might want to stay in previous state
                # For now, we'll allow the transition back to main menu as per spec
                pass

        # All validations passed
        return {'valid': True, 'reason': 'Business rules satisfied'}

    def get_state_data(self, key: str = None) -> Any:
        """
        Retrieve state data (T065)
        Implements state persistence across operations as per specification
        """
        with self._lock:
            if key is None:
                return self._state_data.copy()
            return self._state_data.get(key)

    def set_state_data(self, key: str, value: Any) -> None:
        """
        Set state data (T065)
        Implements state persistence across operations as per specification
        """
        with self._lock:
            self._state_data[key] = value

    def update_state_data(self, data_dict: Dict[str, Any]) -> None:
        """
        Update state data with multiple key-value pairs (T065)
        """
        with self._lock:
            self._state_data.update(data_dict)

    def clear_state_data(self, keys: list = None) -> None:
        """
        Clear state data - optionally specific keys or all (T065)
        """
        with self._lock:
            if keys is None:
                # Clear all state data
                self._state_data.clear()
            else:
                # Clear specific keys only
                for key in keys:
                    if key in self._state_data:
                        del self._state_data[key]

    def persist_state_snapshot(self) -> Dict[str, Any]:
        """
        Create a snapshot of the current state for persistence (T065)
        """
        with self._lock:
            return {
                'current_state': self._current_state,
                'previous_state': self._previous_state,
                'state_data': self._state_data.copy(),
                'transition_history': self._transition_history.copy()
            }

    def restore_from_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        Restore state from a snapshot (T065)
        """
        with self._lock:
            try:
                self._current_state = snapshot.get('current_state', CLIState.MAIN_MENU)
                self._previous_state = snapshot.get('previous_state')
                self._state_data = snapshot.get('state_data', {})
                self._transition_history = snapshot.get('transition_history', [])
                return True
            except Exception:
                return False

    def get_persistent_data_keys(self) -> list:
        """
        Get keys that should persist across operations (T065)
        """
        with self._lock:
            return list(self._state_data.keys())

    def reset_to_main_menu(self) -> bool:
        """
        Reset to main menu state
        """
        return self.transition_to(CLIState.MAIN_MENU)

    def can_exit(self) -> bool:
        """
        Check if the state machine is ready to exit
        """
        with self._lock:
            return self._current_state == CLIState.EXITING

    def get_transition_history(self) -> list:
        """
        Get the history of state transitions for debugging and analysis
        """
        with self._lock:
            return self._transition_history.copy()


class StateHandler:
    """
    Create state handlers for each CLI state (T063)
    Implements state handlers according to specification section 12
    """

    def __init__(self, state_machine: CLIStateMachine):
        self.state_machine = state_machine
        self.handlers: Dict[CLIState, Callable] = {
            CLIState.MAIN_MENU: self.handle_main_menu,
            CLIState.ADDING_TASK: self.handle_adding_task,
            CLIState.UPDATING_TASK: self.handle_updating_task,
            CLIState.DELETING_TASK: self.handle_deleting_task,
            CLIState.CONFIRMATION_DIALOG: self.handle_confirmation_dialog,
            CLIState.EXITING: self.handle_exiting,
        }

    def handle_current_state(self, *args, **kwargs):
        """
        Handle the current state based on state machine
        """
        current_state = self.state_machine.current_state
        handler = self.handlers.get(current_state)

        if handler:
            return handler(*args, **kwargs)
        else:
            # Default handler for unknown states
            return self.handle_unknown_state(current_state, *args, **kwargs)

    def handle_main_menu(self, *args, **kwargs):
        """
        Handle main menu state as per specification
        """
        # In the main menu, the application typically shows options to the user
        # Following the specification's menu mode (section 10)
        return {
            'state': self.state_machine.current_state.value,
            'action': 'show_main_menu',
            'data': self.state_machine.get_state_data(),
            'menu_options': [
                {'option': '1', 'command': 'add', 'description': 'Add Task'},
                {'option': '2', 'command': 'list', 'description': 'View Tasks'},
                {'option': '3', 'command': 'update', 'description': 'Update Task'},
                {'option': '4', 'command': 'delete', 'description': 'Delete Task'},
                {'option': '5', 'command': 'complete', 'description': 'Mark Complete'},
                {'option': '6', 'command': 'help', 'description': 'Help'},
                {'option': '7', 'command': 'exit', 'description': 'Exit'}
            ]
        }

    def handle_adding_task(self, *args, **kwargs):
        """
        Handle adding task state as per specification
        """
        # In this state, the application is collecting task details
        # This corresponds to when user selects add option (transitions from MAIN_MENU)
        return {
            'state': self.state_machine.current_state.value,
            'action': 'collect_task_details',
            'data': self.state_machine.get_state_data(),
            'prompt': 'Enter task title and optional description:',
            'expected_input': 'task_title [task_description]'
        }

    def handle_updating_task(self, *args, **kwargs):
        """
        Handle updating task state as per specification
        """
        # In this state, the application is collecting update details
        # This corresponds to when user selects update option (transitions from MAIN_MENU)
        return {
            'state': self.state_machine.current_state.value,
            'action': 'collect_update_details',
            'data': self.state_machine.get_state_data(),
            'prompt': 'Enter task ID and new title with optional description:',
            'expected_input': 'task_id new_title [new_description]'
        }

    def handle_deleting_task(self, *args, **kwargs):
        """
        Handle deleting task state as per specification
        """
        # In this state, the application is confirming deletion
        # This corresponds to when user selects delete option (transitions from MAIN_MENU)
        return {
            'state': self.state_machine.current_state.value,
            'action': 'confirm_deletion',
            'data': self.state_machine.get_state_data(),
            'prompt': 'Enter task ID to delete:',
            'expected_input': 'task_id'
        }

    def handle_confirmation_dialog(self, *args, **kwargs):
        """
        Handle confirmation dialog state as per specification
        """
        # In this state, the application is waiting for user confirmation
        # Critical operations require confirmation as per spec section 10
        return {
            'state': self.state_machine.current_state.value,
            'action': 'await_confirmation',
            'data': self.state_machine.get_state_data(),
            'prompt': kwargs.get('confirmation_prompt', 'Confirm operation? (y/N):'),
            'expected_input': 'y/N'
        }

    def handle_exiting(self, *args, **kwargs):
        """
        Handle exiting state as per specification
        """
        # In this state, the application is performing cleanup and exit
        # Following spec section 12, this is where cleanup happens
        return {
            'state': self.state_machine.current_state.value,
            'action': 'perform_cleanup_and_exit',
            'data': self.state_machine.get_state_data(),
            'cleanup_actions': ['save_session_stats', 'clear_temp_data', 'display_exit_summary']
        }

    def handle_unknown_state(self, state: CLIState, *args, **kwargs):
        """
        Handle unknown state according to error handling rules
        """
        return {
            'state': state.value,
            'action': 'unknown_state_error',
            'data': self.state_machine.get_state_data(),
            'error': f'Unknown state: {state}',
            'recovery_action': 'reset_to_main_menu'
        }


# Additional utility functions for state management

def create_state_context_manager(state_machine: CLIStateMachine, target_state: CLIState):
    """
    Context manager for temporarily changing state and restoring previous state
    """
    class StateContextManager:
        def __init__(self, sm: CLIStateMachine, ts: CLIState):
            self.sm = sm
            self.ts = ts
            self.original_state = None

        def __enter__(self):
            self.original_state = self.sm.current_state
            self.sm.transition_to(self.ts)
            return self.sm

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Restore original state
            self.sm.transition_to(self.original_state)

    return StateContextManager(state_machine, target_state)