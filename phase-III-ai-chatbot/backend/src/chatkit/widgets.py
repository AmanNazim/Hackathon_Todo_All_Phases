"""
ChatKit Widget Builders

Functions to create ChatKit widgets for task management UI.
"""

from typing import List, Dict, Any, Optional


def build_task_list_widget(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a ChatKit widget displaying a list of tasks.

    Args:
        tasks: List of task dictionaries with id, title, description, status

    Returns:
        ChatKit Card widget with ListView of tasks
    """
    task_items = []

    for task in tasks:
        task_items.append({
            "type": "ListViewItem",
            "title": task.get("title", "Untitled Task"),
            "description": task.get("description", ""),
            "badge": {
                "label": task.get("status", "pending"),
                "color": "primary" if task.get("status") == "pending" else "success"
            },
            "actions": [
                {
                    "type": "Button",
                    "label": "Complete",
                    "style": "primary",
                    "size": "sm",
                    "onClickAction": {
                        "type": "complete_task",
                        "payload": {"task_id": task.get("id")},
                        "handler": "server"
                    }
                },
                {
                    "type": "Button",
                    "label": "Delete",
                    "style": "secondary",
                    "size": "sm",
                    "onClickAction": {
                        "type": "delete_task",
                        "payload": {"task_id": task.get("id")},
                        "handler": "server"
                    }
                }
            ]
        })

    return {
        "type": "Card",
        "children": [
            {
                "type": "Title",
                "value": "Your Tasks"
            },
            {
                "type": "ListView",
                "items": task_items
            }
        ]
    }


def build_task_card(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a ChatKit widget for a single task.

    Args:
        task: Task dictionary with id, title, description, status

    Returns:
        ChatKit Card widget for single task
    """
    return {
        "type": "Card",
        "size": "md",
        "children": [
            {
                "type": "Title",
                "value": task.get("title", "Untitled Task")
            },
            {
                "type": "Text",
                "value": task.get("description", "No description")
            },
            {
                "type": "Badge",
                "label": task.get("status", "pending"),
                "color": "primary" if task.get("status") == "pending" else "success"
            },
            {
                "type": "Row",
                "children": [
                    {
                        "type": "Button",
                        "label": "Complete",
                        "style": "primary",
                        "onClickAction": {
                            "type": "complete_task",
                            "payload": {"task_id": task.get("id")},
                            "handler": "server"
                        }
                    },
                    {
                        "type": "Button",
                        "label": "Edit",
                        "style": "secondary",
                        "onClickAction": {
                            "type": "edit_task",
                            "payload": {"task_id": task.get("id")},
                            "handler": "server"
                        }
                    },
                    {
                        "type": "Button",
                        "label": "Delete",
                        "style": "secondary",
                        "onClickAction": {
                            "type": "delete_task",
                            "payload": {"task_id": task.get("id")},
                            "handler": "server"
                        }
                    }
                ]
            }
        ]
    }


def build_task_form(task: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build a ChatKit form widget for creating or editing a task.

    Args:
        task: Optional task dictionary for editing (None for creation)

    Returns:
        ChatKit Form widget
    """
    is_edit = task is not None
    action_type = "update_task" if is_edit else "create_task"
    title = "Edit Task" if is_edit else "Create New Task"
    button_label = "Update" if is_edit else "Create"

    form_children = [
        {
            "type": "Title",
            "value": title
        },
        {
            "type": "Text",
            "value": "Title",
            "color": "secondary",
            "size": "sm"
        },
        {
            "type": "Text",
            "value": task.get("title", "") if task else "",
            "editable": {
                "name": "title",
                "required": True,
                "placeholder": "Enter task title"
            }
        },
        {
            "type": "Text",
            "value": "Description",
            "color": "secondary",
            "size": "sm"
        },
        {
            "type": "Text",
            "value": task.get("description", "") if task else "",
            "editable": {
                "name": "description",
                "placeholder": "Enter task description (optional)"
            }
        },
        {
            "type": "Button",
            "label": button_label,
            "submit": True,
            "style": "primary"
        }
    ]

    payload = {"task_id": task.get("id")} if task else {}

    return {
        "type": "Form",
        "onSubmitAction": {
            "type": action_type,
            "payload": payload,
            "handler": "server"
        },
        "children": form_children
    }


def build_starter_prompts() -> List[Dict[str, Any]]:
    """
    Build starter prompt buttons for the welcome screen.

    Returns:
        List of starter prompt configurations
    """
    return [
        {
            "text": "Add a task to buy groceries",
            "icon": "plus"
        },
        {
            "text": "Show me all my tasks",
            "icon": "list"
        },
        {
            "text": "What tasks are pending?",
            "icon": "clock"
        },
        {
            "text": "Mark my first task as complete",
            "icon": "check"
        }
    ]
