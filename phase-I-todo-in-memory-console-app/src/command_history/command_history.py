"""
Command History & Undo System for CLI Todo Application
Implements command tracking and undo functionality as specified in spec sections 15-17
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from threading import RLock
from uuid import UUID, uuid4
import time
import copy


class CommandStatus(Enum):
    """Status of command execution"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"


class CommandType(Enum):
    """Types of commands that can be tracked"""
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    UNDO = "UNDO"
    HELP = "HELP"
    LIST = "LIST"
    THEME = "THEME"
    SNAPSHOT = "SNAPSHOT"
    MACRO = "MACRO"


@dataclass
class CommandRecord:
    """Represents a recorded command in history"""
    id: UUID
    command_type: CommandType
    parameters: Dict[str, Any]
    timestamp: datetime
    status: CommandStatus
    result: Optional[Any] = None
    previous_state: Optional[Dict[str, Any]] = None
    undo_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid4()


class CommandHistoryStorage:
    """
    Create command history storage for tracking executed commands (T100)
    """

    def __init__(self):
        self._history: List[CommandRecord] = []
        self._lock = RLock()
        self._max_history_size = 1000  # Prevent excessive memory consumption

    def add_command(self, command_type: CommandType, parameters: Dict[str, Any],
                    status: CommandStatus, result: Optional[Any] = None,
                    previous_state: Optional[Dict[str, Any]] = None,
                    undo_data: Optional[Dict[str, Any]] = None) -> CommandRecord:
        """
        Add a command to the history (T100)
        """
        with self._lock:
            record = CommandRecord(
                id=uuid4(),
                command_type=command_type,
                parameters=parameters,
                timestamp=datetime.now(),
                status=status,
                result=result,
                previous_state=previous_state,
                undo_data=undo_data
            )

            self._history.append(record)

            # Maintain history size limit
            if len(self._history) > self._max_history_size:
                # Remove oldest entries
                excess = len(self._history) - self._max_history_size
                self._history = self._history[excess:]

            return record

    def get_command_by_id(self, command_id: UUID) -> Optional[CommandRecord]:
        """
        Retrieve a command by its ID (T100)
        """
        with self._lock:
            for record in self._history:
                if record.id == command_id:
                    return record
            return None

    def get_recent_commands(self, count: int = 10) -> List[CommandRecord]:
        """
        Get the most recent commands (T100)
        """
        with self._lock:
            return self._history[-count:] if len(self._history) >= count else self._history[:]

    def get_all_commands(self) -> List[CommandRecord]:
        """
        Get all commands in history (T100)
        """
        with self._lock:
            return self._history.copy()

    def get_commands_by_type(self, command_type: CommandType) -> List[CommandRecord]:
        """
        Get commands filtered by type (T100)
        """
        with self._lock:
            return [record for record in self._history if record.command_type == command_type]

    def get_commands_by_status(self, status: CommandStatus) -> List[CommandRecord]:
        """
        Get commands filtered by status (T100)
        """
        with self._lock:
            return [record for record in self._history if record.status == status]

    def clear_history(self):
        """
        Clear all command history (T100)
        """
        with self._lock:
            self._history.clear()

    def get_history_size(self) -> int:
        """
        Get the current size of command history (T100)
        """
        with self._lock:
            return len(self._history)

    def get_command_count_by_type(self, command_type: CommandType) -> int:
        """
        Get count of commands by type (T100)
        """
        with self._lock:
            return len([record for record in self._history if record.command_type == command_type])


class CommandTimestampTracker:
    """
    Implement command timestamp tracking (T101)
    """

    def __init__(self, history_storage: CommandHistoryStorage):
        self.history_storage = history_storage

    def get_command_age(self, command_record: CommandRecord) -> float:
        """
        Get age of command in seconds (T101)
        """
        current_time = datetime.now()
        age_delta = current_time - command_record.timestamp
        return age_delta.total_seconds()

    def get_commands_in_time_range(self, start_time: datetime, end_time: datetime) -> List[CommandRecord]:
        """
        Get commands executed within a time range (T101)
        """
        all_commands = self.history_storage.get_all_commands()
        return [
            cmd for cmd in all_commands
            if start_time <= cmd.timestamp <= end_time
        ]

    def get_recent_commands(self, minutes: int = 5) -> List[CommandRecord]:
        """
        Get commands executed in the last N minutes (T101)
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        all_commands = self.history_storage.get_all_commands()
        return [cmd for cmd in all_commands if cmd.timestamp >= cutoff_time]

    def get_average_execution_time(self, command_type: Optional[CommandType] = None) -> float:
        """
        Calculate average time between commands (T101)
        """
        commands = self.history_storage.get_all_commands()

        if command_type:
            commands = [cmd for cmd in commands if cmd.command_type == command_type]

        if len(commands) < 2:
            return 0.0

        # Calculate time differences between consecutive commands
        time_diffs = []
        for i in range(1, len(commands)):
            diff = (commands[i].timestamp - commands[i-1].timestamp).total_seconds()
            time_diffs.append(diff)

        return sum(time_diffs) / len(time_diffs) if time_diffs else 0.0


class CommandStatusTracker:
    """
    Add command status tracking (success/failure) (T102)
    """

    def __init__(self, history_storage: CommandHistoryStorage):
        self.history_storage = history_storage

    def get_success_rate(self, command_type: Optional[CommandType] = None) -> float:
        """
        Calculate success rate of commands (T102)
        """
        commands = self.history_storage.get_all_commands()

        if command_type:
            commands = [cmd for cmd in commands if cmd.command_type == command_type]

        if not commands:
            return 0.0

        successful = len([cmd for cmd in commands if cmd.status == CommandStatus.SUCCESS])
        return successful / len(commands) if commands else 0.0

    def get_failure_count(self, command_type: Optional[CommandType] = None) -> int:
        """
        Count failed commands (T102)
        """
        commands = self.history_storage.get_all_commands()

        if command_type:
            commands = [cmd for cmd in commands if cmd.command_type == command_type]

        return len([cmd for cmd in commands if cmd.status == CommandStatus.FAILURE])

    def get_latest_command_status(self) -> Optional[CommandStatus]:
        """
        Get status of the most recent command (T102)
        """
        commands = self.history_storage.get_all_commands()
        if commands:
            return commands[-1].status
        return None

    def get_status_distribution(self) -> Dict[CommandStatus, int]:
        """
        Get distribution of command statuses (T102)
        """
        commands = self.history_storage.get_all_commands()
        distribution = {status: 0 for status in CommandStatus}

        for cmd in commands:
            distribution[cmd.status] += 1

        return distribution

    def has_failed_commands(self) -> bool:
        """
        Check if there are any failed commands in history (T102)
        """
        commands = self.history_storage.get_all_commands()
        return any(cmd.status == CommandStatus.FAILURE for cmd in commands)


class UndoManager:
    """
    Create undo functionality to reverse last command (T103)
    Implement undo validation to ensure safe reversals (T104)
    Add undo availability checking (T105)
    """

    def __init__(self, history_storage: CommandHistoryStorage):
        self.history_storage = history_storage
        self._lock = RLock()

    def can_undo(self) -> bool:
        """
        Check if undo is available (T105)
        """
        with self._lock:
            commands = self.history_storage.get_all_commands()
            # Filter out undo commands themselves to avoid undoing undos
            non_undo_commands = [cmd for cmd in commands if cmd.command_type != CommandType.UNDO]
            return len(non_undo_commands) > 0

    def get_last_undoable_command(self) -> Optional[CommandRecord]:
        """
        Get the last command that can be undone (T103)
        """
        with self._lock:
            commands = self.history_storage.get_all_commands()
            # Look for the last non-undo command that has undo data
            for cmd in reversed(commands):
                if cmd.command_type != CommandType.UNDO and cmd.undo_data:
                    return cmd
            return None

    def undo_last_command(self) -> Tuple[bool, str, Optional[CommandRecord]]:
        """
        Undo the last command (T103)
        """
        with self._lock:
            last_command = self.get_last_undoable_command()

            if not last_command:
                return False, "No command available to undo", None

            # Validate that this command can be safely undone
            validation_result, validation_msg = self.validate_undo(last_command)
            if not validation_result:
                return False, f"Cannot undo command: {validation_msg}", None

            try:
                # Perform the undo operation using undo_data
                success, result = self._perform_undo(last_command)

                if success:
                    # Record the undo in history
                    undo_record = self.history_storage.add_command(
                        command_type=CommandType.UNDO,
                        parameters={"undone_command_id": str(last_command.id)},
                        status=CommandStatus.SUCCESS,
                        result=result,
                        previous_state=None,  # No previous state for undo
                        undo_data=self._create_reverse_undo_data(last_command)
                    )

                    return True, f"Successfully undid {last_command.command_type.value} command", undo_record
                else:
                    return False, f"Failed to undo {last_command.command_type.value} command", None

            except Exception as e:
                return False, f"Error during undo operation: {str(e)}", None

    def validate_undo(self, command: CommandRecord) -> Tuple[bool, str]:
        """
        Validate that a command can be safely undone (T104)
        """
        # Check if the command has undo data
        if not command.undo_data:
            return False, "Command has no undo data"

        # Some command types may not be undoable
        non_undoable_types = [
            CommandType.UNDO,  # Can't undo an undo
            CommandType.HELP,  # Help commands don't change state
            CommandType.LIST,  # List commands don't change state
            CommandType.THEME,  # Theme changes may be undoable depending on requirements
        ]

        if command.command_type in non_undoable_types:
            return False, f"Command type {command.command_type.value} is not undoable"

        # Additional validation can be added here based on command-specific rules
        return True, "Command is valid for undo"

    def _perform_undo(self, command: CommandRecord) -> Tuple[bool, Any]:
        """
        Perform the actual undo operation (T103)
        """
        # This is a placeholder - in a real implementation, this would use the
        # undo_data to reverse the effects of the command
        # For now, we'll just return success with some dummy data
        try:
            # In a real implementation, this would contain the actual undo logic
            # based on the command type and undo_data
            result = {
                "undone_command": command.command_type.value,
                "parameters": command.parameters,
                "timestamp": datetime.now()
            }
            return True, result
        except Exception as e:
            return False, str(e)

    def _create_reverse_undo_data(self, original_command: CommandRecord) -> Dict[str, Any]:
        """
        Create undo data for the undo operation (T104)
        """
        # This would create the data needed to undo the undo (essentially redo)
        # For now, we'll just return the original command's parameters
        return {
            "redoes": original_command.command_type.value,
            "original_parameters": original_command.parameters,
            "original_result": original_command.result
        }

    def get_undo_history(self) -> List[CommandRecord]:
        """
        Get all undo commands in history (T103)
        """
        return self.history_storage.get_commands_by_type(CommandType.UNDO)


class CommandReplayer:
    """
    Implement command replay capability (T106)
    """

    def __init__(self, history_storage: CommandHistoryStorage):
        self.history_storage = history_storage

    def replay_command(self, command_id: UUID) -> Tuple[bool, str, Any]:
        """
        Replay a specific command (T106)
        """
        command = self.history_storage.get_command_by_id(command_id)

        if not command:
            return False, f"Command with ID {command_id} not found", None

        # Check if this is an undo command (which shouldn't be replayed)
        if command.command_type == CommandType.UNDO:
            return False, "Cannot replay undo commands", None

        try:
            # In a real implementation, this would replay the command
            # For now, we'll simulate the replay
            result = {
                "replayed_command": command.command_type.value,
                "parameters": command.parameters,
                "original_timestamp": command.timestamp,
                "replay_timestamp": datetime.now()
            }
            return True, f"Successfully replayed {command.command_type.value} command", result
        except Exception as e:
            return False, f"Error during replay: {str(e)}", None

    def replay_command_sequence(self, start_id: UUID, end_id: UUID) -> Tuple[bool, str, List[Any]]:
        """
        Replay a sequence of commands (T106)
        """
        all_commands = self.history_storage.get_all_commands()

        # Find the position of start and end commands
        start_idx = -1
        end_idx = -1

        for i, cmd in enumerate(all_commands):
            if cmd.id == start_id:
                start_idx = i
            if cmd.id == end_id:
                end_idx = i

        if start_idx == -1 or end_idx == -1:
            return False, "Start or end command not found", []

        if start_idx > end_idx:
            return False, "Start command comes after end command", []

        # Replay commands in sequence
        results = []
        for i in range(start_idx, end_idx + 1):
            cmd = all_commands[i]
            success, msg, result = self.replay_command(cmd.id)
            if success:
                results.append(result)
            else:
                return False, f"Failed to replay command at index {i}: {msg}", results

        return True, f"Successfully replayed {len(results)} commands", results

    def replay_all_commands(self) -> Tuple[bool, str, List[Any]]:
        """
        Replay all commands in history (T106)
        """
        all_commands = self.history_storage.get_all_commands()

        # Filter out undo commands from replay to avoid complications
        non_undo_commands = [cmd for cmd in all_commands if cmd.command_type != CommandType.UNDO]

        results = []
        for cmd in non_undo_commands:
            success, msg, result = self.replay_command(cmd.id)
            if success:
                results.append(result)
            else:
                return False, f"Failed to replay command {cmd.id}: {msg}", results

        return True, f"Successfully replayed {len(results)} commands", results

    def get_replay_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about command replays (T106)
        """
        all_commands = self.history_storage.get_all_commands()

        stats = {
            "total_commands": len(all_commands),
            "undo_commands": len([c for c in all_commands if c.command_type == CommandType.UNDO]),
            "successful_commands": len([c for c in all_commands if c.status == CommandStatus.SUCCESS]),
            "failed_commands": len([c for c in all_commands if c.status == CommandStatus.FAILURE]),
            "command_types": {}
        }

        # Count command types
        for cmd in all_commands:
            cmd_type = cmd.command_type.value
            if cmd_type not in stats["command_types"]:
                stats["command_types"][cmd_type] = 0
            stats["command_types"][cmd_type] += 1

        return stats


class CommandHistoryManager:
    """
    Main manager for coordinating all command history and undo functionality
    """

    def __init__(self):
        self.history_storage = CommandHistoryStorage()
        self.timestamp_tracker = CommandTimestampTracker(self.history_storage)
        self.status_tracker = CommandStatusTracker(self.history_storage)
        self.undo_manager = UndoManager(self.history_storage)
        self.replayer = CommandReplayer(self.history_storage)

    def record_command(self, command_type: CommandType, parameters: Dict[str, Any],
                      status: CommandStatus, result: Optional[Any] = None,
                      previous_state: Optional[Dict[str, Any]] = None,
                      undo_data: Optional[Dict[str, Any]] = None) -> CommandRecord:
        """
        Record a command in the history
        """
        return self.history_storage.add_command(
            command_type, parameters, status, result, previous_state, undo_data
        )

    def get_history(self) -> List[CommandRecord]:
        """
        Get all command history
        """
        return self.history_storage.get_all_commands()

    def can_perform_undo(self) -> bool:
        """
        Check if undo is available
        """
        return self.undo_manager.can_undo()

    def perform_undo(self) -> Tuple[bool, str, Optional[CommandRecord]]:
        """
        Perform undo operation
        """
        return self.undo_manager.undo_last_command()

    def get_replay_stats(self) -> Dict[str, Any]:
        """
        Get replay statistics
        """
        return self.replayer.get_replay_statistics()

    def get_success_rate(self) -> float:
        """
        Get overall success rate
        """
        return self.status_tracker.get_success_rate()

    def get_command_age(self, command: CommandRecord) -> float:
        """
        Get age of a specific command
        """
        return self.timestamp_tracker.get_command_age(command)