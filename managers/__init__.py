"""
Business logic managers package.

Provides manager classes for exercise tracking, task management,
and calendar events with Qt signal integration.
"""

from .exercise_manager import ExerciseManager
from .task_manager import TaskManager
from .event_manager import EventManager

__all__ = [
    'ExerciseManager',
    'TaskManager',
    'EventManager'
]
