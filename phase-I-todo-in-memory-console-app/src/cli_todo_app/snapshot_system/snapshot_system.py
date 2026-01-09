"""
Snapshot System Implementation for CLI Todo Application
Implements T120-T125: Snapshot System functionality
"""
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from uuid import UUID, uuid4
from copy import deepcopy


@dataclass
class Snapshot:
    """Represents a stored snapshot of the application state"""
    id: UUID
    name: str
    created_at: datetime
    state_data: Dict[str, Any]  # Complete application state
    task_count: int
    event_count: int


class SnapshotStorage:
    """In-memory storage for snapshots"""

    def __init__(self, max_snapshots: int = 100):
        self._snapshots: Dict[str, Snapshot] = {}
        self._max_snapshots = max_snapshots
        self._lock = threading.RLock()

    def save_snapshot(self, snapshot: Snapshot) -> bool:
        """Save a snapshot to storage, respecting max limit"""
        with self._lock:
            # Check if we've reached the max limit
            if len(self._snapshots) >= self._max_snapshots:
                # Remove the oldest snapshot to make room
                oldest_name = min(self._snapshots.keys(),
                                key=lambda k: self._snapshots[k].created_at)
                del self._snapshots[oldest_name]

            self._snapshots[snapshot.name] = snapshot
            return True

    def get_snapshot(self, name: str) -> Optional[Snapshot]:
        """Retrieve a snapshot by name"""
        with self._lock:
            return self._snapshots.get(name)

    def list_snapshots(self) -> List[Snapshot]:
        """List all stored snapshots ordered by creation time"""
        with self._lock:
            return sorted(list(self._snapshots.values()), key=lambda s: s.created_at, reverse=True)

    def delete_snapshot(self, name: str) -> bool:
        """Delete a snapshot by name"""
        with self._lock:
            if name in self._snapshots:
                del self._snapshots[name]
                return True
            return False

    def clear_all(self) -> None:
        """Clear all snapshots from storage"""
        with self._lock:
            self._snapshots.clear()

    def get_snapshot_count(self) -> int:
        """Get the number of stored snapshots"""
        with self._lock:
            return len(self._snapshots)


class SnapshotSystem:
    """Main snapshot system for capturing and restoring application state"""

    def __init__(self, max_snapshots: int = 100):
        self._storage = SnapshotStorage(max_snapshots)
        self._lock = threading.RLock()

    def create_snapshot(self, name: Optional[str] = None,
                      capture_callback=None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a snapshot of the current application state.

        Args:
            name: Optional name for the snapshot, will use timestamp if None
            capture_callback: Callback function to capture application state data

        Returns:
            Tuple of (success, message, snapshot_name)
        """
        with self._lock:
            if capture_callback is None:
                return False, "Capture callback is required", None

            # Generate name if not provided
            if name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"snapshot_{timestamp}"

            # Validate name
            if not name.strip():
                return False, "Snapshot name cannot be empty", None

            # Check if snapshot with this name already exists
            if self._storage.get_snapshot(name):
                return False, f"Snapshot '{name}' already exists. Choose a different name.", None

            try:
                # Capture the current application state
                state_data = capture_callback()

                # Create snapshot object
                snapshot = Snapshot(
                    id=uuid4(),
                    name=name,
                    created_at=datetime.now(),
                    state_data=deepcopy(state_data),  # Deep copy to prevent reference issues
                    task_count=state_data.get('task_count', 0),
                    event_count=state_data.get('event_count', 0)
                )

                # Save to storage
                success = self._storage.save_snapshot(snapshot)
                if success:
                    return True, f"Snapshot '{name}' created successfully with {snapshot.task_count} tasks and {snapshot.event_count} events.", name
                else:
                    return False, f"Failed to save snapshot '{name}'.", None

            except Exception as e:
                return False, f"Error creating snapshot: {str(e)}", None

    def restore_snapshot(self, name: str, restore_callback=None) -> Tuple[bool, str]:
        """
        Restore application state from a snapshot.

        Args:
            name: Name of the snapshot to restore
            restore_callback: Callback function to restore application state from snapshot data

        Returns:
            Tuple of (success, message)
        """
        with self._lock:
            if restore_callback is None:
                return False, "Restore callback is required"

            snapshot = self._storage.get_snapshot(name)
            if not snapshot:
                return False, f"Snapshot '{name}' not found."

            try:
                # Restore the application state using the callback
                success = restore_callback(snapshot.state_data)
                if success:
                    return True, f"Successfully restored from snapshot '{name}' with {snapshot.task_count} tasks and {snapshot.event_count} events."
                else:
                    return False, f"Failed to restore from snapshot '{name}'."

            except Exception as e:
                return False, f"Error restoring snapshot: {str(e)}"

    def get_snapshot(self, name: str) -> Optional[Snapshot]:
        """Get a snapshot by name"""
        return self._storage.get_snapshot(name)

    def list_snapshots(self) -> List[Snapshot]:
        """List all available snapshots"""
        return self._storage.list_snapshots()

    def delete_snapshot(self, name: str) -> bool:
        """Delete a snapshot by name"""
        return self._storage.delete_snapshot(name)

    def clear_all_snapshots(self) -> None:
        """Clear all snapshots from storage"""
        self._storage.clear_all()

    def get_snapshot_count(self) -> int:
        """Get the number of stored snapshots"""
        return self._storage.get_snapshot_count()

    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about snapshot storage"""
        snapshots = self._storage.list_snapshots()
        total_tasks = sum(s.task_count for s in snapshots)
        total_events = sum(s.event_count for s in snapshots)

        return {
            'snapshot_count': len(snapshots),
            'total_tasks': total_tasks,
            'total_events': total_events,
            'max_snapshots': self._storage._max_snapshots
        }