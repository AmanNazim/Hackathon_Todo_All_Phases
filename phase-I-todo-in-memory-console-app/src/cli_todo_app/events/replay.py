"""
Event replay mechanism for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from typing import List, Dict, Type
from datetime import datetime
from ..domain.entities import Task
from ..domain.events import (
    TaskEvent, EventType, TaskCreatedEvent, TaskUpdatedEvent,
    TaskDeletedEvent, TaskCompletedEvent, TaskReopenedEvent
)
from .event_store import EventStore


class EventReplayService:
    """
    Event replay mechanism to rebuild state from events (T033)
    Implements state reconstruction from event sequence
    """

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def rebuild_state(self) -> Dict[str, Task]:
        """
        Rebuild the current state from all events in chronological order
        Returns a dictionary mapping task IDs to Task objects
        """
        events = self.event_store.get_events()
        tasks: Dict[str, Task] = {}

        for event in events:
            tasks = self._apply_event(tasks, event)

        return tasks

    def rebuild_state_for_aggregate(self, aggregate_id: str) -> Task:
        """
        Rebuild the state for a specific task (aggregate) from its events
        Returns the reconstructed Task object
        """
        events = self.event_store.get_events_by_aggregate(aggregate_id)
        task = None

        for event in events:
            task = self._apply_event_to_single_task(task, event)

        return task

    def _apply_event(self, tasks: Dict[str, Task], event: TaskEvent) -> Dict[str, Task]:
        """
        Apply a single event to the current state
        """
        if event.type == EventType.TASK_CREATED:
            if isinstance(event, TaskCreatedEvent):
                # For TaskCreatedEvent, we need to reconstruct the task from the event data
                # Since we can't easily recreate a Task with a specific ID, we'll need to use reflection
                # or a different approach. Let's construct the task manually.

                # Create a new task with the data from the event
                from ..domain.entities import Task
                from ..domain.status import TaskStatus

                # Create the task object directly, bypassing the factory method to set the ID
                # Get the TaskStatus enum value based on the string from the event
                status_value = event.data['status']
                if status_value == 'PENDING':
                    status_enum = TaskStatus.PENDING
                elif status_value == 'COMPLETED':
                    status_enum = TaskStatus.COMPLETED
                else:
                    status_enum = TaskStatus.PENDING  # default fallback

                task = Task(
                    id=event.aggregate_id,
                    title=event.data['title'],
                    description=event.data.get('description'),
                    status=status_enum,
                    tags=event.data.get('tags', []),
                    created_at=event.data.get('created_at', datetime.now().isoformat())
                )
                # Update updated_at to current time since it's being recreated
                task.updated_at = datetime.now().isoformat()

                tasks[event.aggregate_id] = task
        elif event.type == EventType.TASK_UPDATED:
            if isinstance(event, TaskUpdatedEvent) and event.aggregate_id in tasks:
                task = tasks[event.aggregate_id]
                # Apply the updates from the event data
                if 'new_values' in event.data:
                    new_values = event.data['new_values']
                    update_kwargs = {}

                    if 'title' in new_values and new_values['title'] is not None:
                        update_kwargs['title'] = new_values['title']
                    if 'description' in new_values and new_values['description'] is not None:
                        update_kwargs['description'] = new_values['description']
                    if 'tags' in new_values and new_values['tags'] is not None:
                        update_kwargs['tags'] = new_values['tags']

                    if update_kwargs:
                        task.update(**update_kwargs)
        elif event.type == EventType.TASK_DELETED:
            if isinstance(event, TaskDeletedEvent):
                # Remove the task from the state
                tasks.pop(event.aggregate_id, None)
        elif event.type == EventType.TASK_COMPLETED:
            if isinstance(event, TaskCompletedEvent) and event.aggregate_id in tasks:
                tasks[event.aggregate_id].mark_completed()
        elif event.type == EventType.TASK_REOPENED:
            if isinstance(event, TaskReopenedEvent) and event.aggregate_id in tasks:
                tasks[event.aggregate_id].mark_pending()

        return tasks

    def _apply_event_to_single_task(self, task: Task, event: TaskEvent) -> Task:
        """
        Apply a single event to a specific task
        """
        if event.type == EventType.TASK_CREATED:
            if isinstance(event, TaskCreatedEvent):
                # For TaskCreatedEvent, create a new task from the event data
                from ..domain.entities import Task as TaskEntity
                from ..domain.status import TaskStatus

                # Get the TaskStatus enum value based on the string from the event
                status_value = event.data['status']
                if status_value == 'PENDING':
                    status_enum = TaskStatus.PENDING
                elif status_value == 'COMPLETED':
                    status_enum = TaskStatus.COMPLETED
                else:
                    status_enum = TaskStatus.PENDING  # default fallback

                new_task = TaskEntity(
                    id=event.aggregate_id,
                    title=event.data['title'],
                    description=event.data.get('description'),
                    status=status_enum,
                    tags=event.data.get('tags', []),
                    created_at=event.data.get('created_at', datetime.now().isoformat())
                )
                # Update updated_at to current time since it's being recreated
                new_task.updated_at = datetime.now().isoformat()
                return new_task
        elif event.type == EventType.TASK_UPDATED:
            if isinstance(event, TaskUpdatedEvent) and task:
                # Apply the updates from the event data
                update_kwargs = {}
                if 'new_values' in event.data:
                    new_values = event.data['new_values']
                    if 'title' in new_values and new_values['title'] is not None:
                        update_kwargs['title'] = new_values['title']
                    if 'description' in new_values and new_values['description'] is not None:
                        update_kwargs['description'] = new_values['description']
                    if 'tags' in new_values and new_values['tags'] is not None:
                        update_kwargs['tags'] = new_values['tags']

                    if update_kwargs:
                        task.update(**update_kwargs)
        elif event.type == EventType.TASK_DELETED:
            if isinstance(event, TaskDeletedEvent):
                # Return None to indicate the task was deleted
                return None
        elif event.type == EventType.TASK_COMPLETED:
            if isinstance(event, TaskCompletedEvent) and task:
                task.mark_completed()
        elif event.type == EventType.TASK_REOPENED:
            if isinstance(event, TaskReopenedEvent) and task:
                task.mark_pending()

        return task

    def get_state_at_timestamp(self, timestamp: str) -> Dict[str, Task]:
        """
        Get the state of the system at a specific point in time
        """
        events = self.event_store.get_events_since(timestamp)
        tasks: Dict[str, Task] = {}

        # Need to get all events up to the timestamp and replay them
        all_events = self.event_store.get_events()
        filtered_events = [event for event in all_events if event.timestamp <= timestamp]

        for event in filtered_events:
            tasks = self._apply_event(tasks, event)

        return tasks

    def validate_replay_integrity(self) -> bool:
        """
        Validate that the replay mechanism produces consistent results
        """
        # Rebuild state twice and compare
        state1 = self.rebuild_state()
        state2 = self.rebuild_state()

        # Compare the states
        if len(state1) != len(state2):
            return False

        for task_id, task1 in state1.items():
            if task_id not in state2:
                return False
            task2 = state2[task_id]

            # Compare key attributes
            if (task1.title != task2.title or
                task1.description != task2.description or
                task1.status != task2.status or
                task1.tags != task2.tags):
                return False

        return True

    def get_task_lifecycle(self, task_id: str) -> List[TaskEvent]:
        """
        Get the complete lifecycle of a task from creation to current state
        """
        return self.event_store.get_events_by_aggregate(task_id)


class EventReplayValidator:
    """
    Validator for event replay mechanism integrity
    """

    @staticmethod
    def validate_replay_consistency(original_state: Dict[str, Task], replayed_state: Dict[str, Task]) -> bool:
        """
        Validate that the original state matches the replayed state
        """
        if len(original_state) != len(replayed_state):
            return False

        for task_id, original_task in original_state.items():
            if task_id not in replayed_state:
                return False

            replayed_task = replayed_state[task_id]

            if (original_task.id != replayed_task.id or
                original_task.title != replayed_task.title or
                original_task.description != replayed_task.description or
                original_task.status != replayed_task.status or
                original_task.created_at != replayed_task.created_at or
                original_task.updated_at != replayed_task.updated_at or
                original_task.tags != replayed_task.tags):
                return False

        return True

    @staticmethod
    def validate_event_sequence(events: List[TaskEvent]) -> bool:
        """
        Validate that events are in chronological order
        """
        for i in range(1, len(events)):
            if events[i-1].timestamp > events[i].timestamp:
                return False
        return True