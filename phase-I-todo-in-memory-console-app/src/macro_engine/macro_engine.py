"""
Macro Engine Implementation for CLI Todo Application
Implements T110-T115: Macro Engine functionality
"""
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
import queue


class MacroStatus(Enum):
    """Status of a macro"""
    RECORDING = "recording"
    STOPPED = "stopped"
    PLAYING = "playing"


@dataclass
class Macro:
    """Represents a stored macro with its recorded commands"""
    id: UUID
    name: str
    commands: List[Dict[str, Any]]  # Store command representations
    created_at: datetime
    status: MacroStatus = MacroStatus.STOPPED
    last_played_at: Optional[datetime] = None


class MacroStorage:
    """In-memory storage for macros"""

    def __init__(self):
        self._macros: Dict[str, Macro] = {}
        self._lock = threading.RLock()

    def save_macro(self, macro: Macro) -> None:
        """Save a macro to storage"""
        with self._lock:
            self._macros[macro.name] = macro

    def get_macro(self, name: str) -> Optional[Macro]:
        """Retrieve a macro by name"""
        with self._lock:
            return self._macros.get(name)

    def list_macros(self) -> List[Macro]:
        """List all stored macros"""
        with self._lock:
            return list(self._macros.values())

    def delete_macro(self, name: str) -> bool:
        """Delete a macro by name"""
        with self._lock:
            if name in self._macros:
                del self._macros[name]
                return True
            return False

    def clear_all(self) -> None:
        """Clear all macros from storage"""
        with self._lock:
            self._macros.clear()


class MacroRecorder:
    """Records command sequences for macro functionality"""

    def __init__(self, storage: MacroStorage):
        self._storage = storage
        self._recording_macro: Optional[Macro] = None
        self._recording_commands: List[Dict[str, Any]] = []
        self._is_recording = False
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        """Check if currently recording a macro"""
        with self._lock:
            return self._is_recording

    def start_recording(self, name: str) -> Tuple[bool, str]:
        """Start recording a new macro with the given name"""
        with self._lock:
            if self._is_recording:
                return False, "Already recording a macro. Please stop current recording first."

            if not name.strip():
                return False, "Macro name cannot be empty."

            # Check if macro with this name already exists
            if self._storage.get_macro(name):
                return False, f"Macro '{name}' already exists. Choose a different name."

            self._recording_commands = []
            self._recording_macro = Macro(
                id=uuid4(),
                name=name,
                commands=[],
                created_at=datetime.now(),
                status=MacroStatus.RECORDING
            )
            self._is_recording = True
            return True, f"Started recording macro '{name}'. All commands will be captured until you stop recording."

    def record_command(self, command_data: Dict[str, Any]) -> None:
        """Record a command during macro recording"""
        with self._lock:
            if not self._is_recording or not self._recording_macro:
                return

            # Store command data for later replay
            self._recording_commands.append(command_data.copy())

    def stop_recording(self) -> Tuple[bool, str, Optional[str]]:
        """Stop the current macro recording and save it"""
        with self._lock:
            if not self._is_recording or not self._recording_macro:
                return False, "Not currently recording a macro.", None

            # Finalize the macro
            self._recording_macro.commands = self._recording_commands.copy()
            self._recording_macro.status = MacroStatus.STOPPED

            # Save to storage
            self._storage.save_macro(self._recording_macro)

            # Store the name before resetting
            macro_name = self._recording_macro.name

            # Reset recording state
            self._recording_macro = None
            self._recording_commands = []
            self._is_recording = False

            return True, f"Stopped recording macro '{macro_name}'.", macro_name

    def cancel_recording(self) -> Tuple[bool, str]:
        """Cancel the current macro recording without saving"""
        with self._lock:
            if not self._is_recording:
                return False, "Not currently recording a macro."

            self._recording_macro = None
            self._recording_commands = []
            self._is_recording = False
            return True, "Cancelled current macro recording."


class MacroPlayer:
    """Plays back recorded macros"""

    def __init__(self, storage: MacroStorage):
        self._storage = storage
        self._currently_playing_macro: Optional[Macro] = None
        self._interrupt_event = threading.Event()
        self._lock = threading.Lock()

    @property
    def is_playing(self) -> bool:
        """Check if currently playing a macro"""
        with self._lock:
            return self._currently_playing_macro is not None

    def play_macro(self, name: str, command_executor_callback) -> Tuple[bool, str]:
        """Play a macro by name using the provided command executor callback"""
        with self._lock:
            if self._currently_playing_macro:
                return False, f"Already playing macro '{self._currently_playing_macro.name}'. Please wait or interrupt first."

        macro = self._storage.get_macro(name)
        if not macro:
            return False, f"Macro '{name}' not found."

        # Update macro status
        macro.status = MacroStatus.PLAYING
        macro.last_played_at = datetime.now()
        self._storage.save_macro(macro)

        with self._lock:
            self._currently_playing_macro = macro

        # Play the macro commands
        success, message = self._execute_macro_commands(macro, command_executor_callback)

        # Reset playing state
        with self._lock:
            self._currently_playing_macro = None

        # Update macro status back to stopped
        macro.status = MacroStatus.STOPPED
        self._storage.save_macro(macro)

        return success, message

    def _execute_macro_commands(self, macro: Macro, command_executor_callback) -> Tuple[bool, str]:
        """Execute all commands in a macro"""
        for i, command_data in enumerate(macro.commands):
            # Check if interruption was requested
            if self._interrupt_event.is_set():
                self._interrupt_event.clear()
                return False, f"Macro '{macro.name}' playback interrupted after {i} commands."

            # Execute the command using the callback
            try:
                success, result_message = command_executor_callback(command_data)
                if not success:
                    return False, f"Macro '{macro.name}' failed at command {i+1}: {result_message}"
            except Exception as e:
                return False, f"Macro '{macro.name}' failed at command {i+1} with error: {str(e)}"

        return True, f"Successfully played macro '{macro.name}' with {len(macro.commands)} commands."

    def interrupt_current_playback(self) -> Tuple[bool, str]:
        """Interrupt the current macro playback"""
        with self._lock:
            if not self._currently_playing_macro:
                return False, "No macro is currently playing."

        # Set the interrupt event
        self._interrupt_event.set()
        macro_name = self._currently_playing_macro.name
        return True, f"Requested interruption of macro '{macro_name}'."

    def get_currently_playing_macro(self) -> Optional[Macro]:
        """Get the currently playing macro"""
        with self._lock:
            return self._currently_playing_macro


class MacroEngine:
    """Main macro engine coordinating recording and playback"""

    def __init__(self):
        self._storage = MacroStorage()
        self._recorder = MacroRecorder(self._storage)
        self._player = MacroPlayer(self._storage)
        self._lock = threading.RLock()

    @property
    def recorder(self) -> MacroRecorder:
        """Access to the macro recorder"""
        return self._recorder

    @property
    def player(self) -> MacroPlayer:
        """Access to the macro player"""
        return self._player

    def get_macro(self, name: str) -> Optional[Macro]:
        """Get a macro by name"""
        return self._storage.get_macro(name)

    def list_macros(self) -> List[Macro]:
        """List all available macros"""
        return self._storage.list_macros()

    def delete_macro(self, name: str) -> bool:
        """Delete a macro by name"""
        return self._storage.delete_macro(name)

    def clear_all_macros(self) -> None:
        """Clear all macros from storage"""
        self._storage.clear_all()

    def is_recording(self) -> bool:
        """Check if currently recording a macro"""
        return self._recorder.is_recording

    def is_playing(self) -> bool:
        """Check if currently playing a macro"""
        return self._player.is_playing

    def interrupt_current_playback(self) -> Tuple[bool, str]:
        """Interrupt the current macro playback"""
        return self._player.interrupt_current_playback()

    def get_currently_playing_macro(self) -> Optional[Macro]:
        """Get the currently playing macro"""
        return self._player.get_currently_playing_macro()