"""
Exercise Manager Window.

Separate window for managing exercises with full checklist interface.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import Qt

from managers import ExerciseManager
from .widgets import ExerciseChecklistWidget


class ExerciseManagerWindow(QDialog):
    """
    Exercise management window.
    
    Provides full exercise checklist interface in a separate window.
    """
    
    def __init__(self, exercise_manager: ExerciseManager, parent=None):
        """
        Initialize exercise manager window.
        
        Args:
            exercise_manager: Manager for exercise operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._exercise_manager = exercise_manager
        
        self.setWindowTitle("Exercise Manager")
        self.setModal(False)
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize window UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add exercise checklist widget
        self.exercise_checklist = ExerciseChecklistWidget(self._exercise_manager)
        layout.addWidget(self.exercise_checklist)
