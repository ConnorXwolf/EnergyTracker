"""
Task Manager Window.

Separate window for managing tasks with full checklist interface.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import Qt

from managers import TaskManager
from .widgets import TaskChecklistWidget


class TaskManagerWindow(QDialog):
    """
    Task management window.
    
    Provides full task checklist interface in a separate window.
    """
    
    def __init__(self, task_manager: TaskManager, parent=None):
        """
        Initialize task manager window.
        
        Args:
            task_manager: Manager for task operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._task_manager = task_manager
        
        self.setWindowTitle("Task Manager")
        self.setModal(False)
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize window UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add task checklist widget
        self.task_checklist = TaskChecklistWidget(self._task_manager)
        layout.addWidget(self.task_checklist)
