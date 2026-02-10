"""
Exercise checklist widget with progress bars.

Displays daily exercises with checkboxes, progress bars showing
actual/target ratios, and summary statistics.
"""

from typing import List, Tuple, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QDialog, QLineEdit, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont

from models import Exercise, ExerciseLog
from managers import ExerciseManager
from utils import get_today
from .exercise_progress_bar import ExerciseProgressBar


class ExerciseChecklistWidget(QWidget):
    """
    Main exercise tracking widget with progress visualization.
    
    Displays exercises as list items with checkboxes and progress bars,
    provides summary statistics, and handles user interactions.
    
    Signals:
        exercise_updated: Emitted when exercise progress is updated
    """
    
    exercise_updated = pyqtSignal()
    
    def __init__(self, exercise_manager: ExerciseManager, parent=None):
        """
        Initialize exercise checklist widget.
        
        Args:
            exercise_manager: Manager for exercise operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._exercise_manager = exercise_manager
        self._current_date = get_today()
        
        self._setup_ui()
        self._connect_signals()
        self._load_exercises()
    
    def _setup_ui(self) -> None:
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header section (14pt bold)
        header_layout = QHBoxLayout()
        
        title_label = QLabel("每日運動 (Daily Exercises)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Exercise list
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(8)
        self.list_widget.setMinimumHeight(250)
        
        # Summary footer (increase font size to 12pt)
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #AAAAAA;
                padding: 10px;
                background-color: #2D2D2D;
                border-radius: 3px;
            }
        """)
        
        # Action buttons (larger, like task list)
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Exercise")
        self.add_button.setMinimumWidth(200)
        self.add_button.setMinimumHeight(50)
        add_button_font = QFont()
        add_button_font.setPointSize(12)
        self.add_button.setFont(add_button_font)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMinimumWidth(200)
        self.refresh_button.setMinimumHeight(50)
        refresh_button_font = QFont()
        refresh_button_font.setPointSize(12)
        self.refresh_button.setFont(refresh_button_font)
        
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)
        
        # Assembly
        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.summary_label)
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self.add_button.clicked.connect(self._on_add_exercise)
        self.refresh_button.clicked.connect(self._load_exercises)
        
        # Connect manager signals
        self._exercise_manager.data_changed.connect(self._load_exercises)
    
    def _load_exercises(self) -> None:
        """Load and display exercises for current date."""
        try:
            # Clear existing items
            self.list_widget.clear()
            
            # Get exercises with logs
            exercises_data = self._exercise_manager.get_logs_for_date(self._current_date)
            
            if not exercises_data:
                # Show empty state
                empty_item = QListWidgetItem("No exercises found. Click 'Add Exercise' to get started.")
                self.list_widget.addItem(empty_item)
                self._update_summary([], [])
                return
            
            # Add each exercise as list item
            exercises = []
            logs = []
            
            for exercise, log in exercises_data:
                exercises.append(exercise)
                logs.append(log)
                self._add_exercise_item(exercise, log)
            
            # Update summary
            self._update_summary(exercises, logs)
            
        except Exception as e:
            print(f"Error loading exercises: {e}")
    
    def _add_exercise_item(self, exercise: Exercise, log: ExerciseLog) -> None:
        """
        Add exercise with progress bar to list.
        
        Args:
            exercise: Exercise definition
            log: Current log data
        """
        # Create container widget
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        item_layout.setSpacing(5)
        
        # Row 1: Checkbox + Name + Edit button + Delete button
        top_row = QHBoxLayout()
        
        checkbox = QCheckBox(exercise.name)
        checkbox.setChecked(log.completed)
        # White checkbox styling, 14pt font
        checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid white;
                border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #32CD32;
                border: 2px solid white;
            }
        """)
        
        # Store exercise_id and log in checkbox for later reference
        checkbox.setProperty("exercise_id", exercise.id)
        checkbox.setProperty("log", log)
        
        checkbox.stateChanged.connect(
            lambda state, eid=exercise.id: self._on_checkbox_changed(eid, state)
        )
        
        top_row.addWidget(checkbox)
        top_row.addStretch()
        
        # Edit button (three dots)
        edit_button = QPushButton("⋯")
        edit_button.setMaximumWidth(40)
        edit_button.setMinimumHeight(30)
        edit_button.setStyleSheet("font-size: 20px; font-weight: bold;")
        edit_button.setToolTip("Edit progress")
        edit_button.clicked.connect(
            lambda checked, eid=exercise.id, lg=log: self._on_edit_progress(eid, lg)
        )
        
        # Delete button (trash icon)
        delete_button = QPushButton("🗑")
        delete_button.setMaximumWidth(40)
        delete_button.setMinimumHeight(30)
        delete_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        delete_button.setToolTip("Delete exercise")
        delete_button.clicked.connect(
            lambda checked, eid=exercise.id, name=exercise.name: self._on_delete_exercise(eid, name)
        )
        
        top_row.addWidget(edit_button)
        top_row.addWidget(delete_button)
        
        # Row 2: Progress bar
        progress_bar = ExerciseProgressBar(log, exercise.color)
        
        # Assembly
        item_layout.addLayout(top_row)
        item_layout.addWidget(progress_bar)
        
        # Add to list with fixed height
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 80))
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)
    
    def _on_checkbox_changed(self, exercise_id: int, state: int) -> None:
        """
        Handle checkbox state change.
        
        Args:
            exercise_id: Exercise being toggled
            state: Qt.CheckState value
        """
        is_checked = (state == Qt.CheckState.Checked.value)
        
        if is_checked:
            # Show dialog to input actual value
            self._show_progress_dialog(exercise_id)
        else:
            # Uncheck: set to 0
            self._exercise_manager.update_progress(
                exercise_id=exercise_id,
                date=self._current_date,
                actual_value=0,
                completed=False
            )
            self.exercise_updated.emit()
    
    def _on_edit_progress(self, exercise_id: int, log: ExerciseLog) -> None:
        """
        Handle edit button click.
        
        Args:
            exercise_id: Exercise to edit
            log: Current log data
        """
        self._show_progress_dialog(exercise_id, log.actual_value)
    
    def _show_progress_dialog(
        self,
        exercise_id: int,
        current_value: int = 0
    ) -> None:
        """
        Display dialog for entering exercise progress.
        
        Args:
            exercise_id: Exercise being updated
            current_value: Pre-filled value
        """
        try:
            exercise = self._exercise_manager.get_exercise_by_id(exercise_id)
            if not exercise:
                return
            
            dialog = ProgressInputDialog(exercise, current_value, self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                actual_value = dialog.get_actual_value()
                notes = dialog.get_notes()
                
                # Update progress
                self._exercise_manager.update_progress(
                    exercise_id=exercise_id,
                    date=self._current_date,
                    actual_value=actual_value,
                    completed=(actual_value >= exercise.target_value),
                    notes=notes
                )
                
                self.exercise_updated.emit()
        
        except Exception as e:
            print(f"Error showing progress dialog: {e}")
    
    def _on_add_exercise(self) -> None:
        """Handle add exercise button click."""
        dialog = AddExerciseDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_exercise_data()
            
            try:
                exercise_id = self._exercise_manager.create_exercise(
                    name=data['name'],
                    category=data['category'],
                    target_value=data['target_value'],
                    unit=data['unit']
                )
                
                if exercise_id:
                    QMessageBox.information(
                        self,
                        "Exercise Created",
                        f"Exercise '{data['name']}' has been created successfully."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create exercise:\n{str(e)}"
                )
                print(f"Error creating exercise: {e}")
                import traceback
                traceback.print_exc()
    
    def _on_delete_exercise(self, exercise_id: int, exercise_name: str) -> None:
        """
        Handle delete button click with confirmation.
        
        Args:
            exercise_id: Exercise to delete
            exercise_name: Exercise name for confirmation message
        """
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Permanently delete exercise '{exercise_name}'?\n\n"
            f"This will also delete all associated workout logs.\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Attempt deletion
            success = self._exercise_manager.delete_exercise(exercise_id)
            
            if success:
                # Show success feedback
                QMessageBox.information(
                    self,
                    "Exercise Deleted",
                    f"Exercise '{exercise_name}' has been permanently deleted."
                )
                # Signal will trigger automatic refresh via data_changed connection
            else:
                # Handle failure (should rarely occur)
                QMessageBox.warning(
                    self,
                    "Deletion Failed",
                    f"Failed to delete exercise '{exercise_name}'.\n"
                    f"The exercise may have already been deleted."
                )
        
        except Exception as e:
            # Catch any unexpected errors
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while deleting the exercise:\n{str(e)}"
            )
            print(f"Error deleting exercise {exercise_id}: {e}")
            import traceback
            traceback.print_exc()
            
def _update_summary(
    self,
    exercises: List[Exercise],
    logs: List[ExerciseLog]
) -> None:
    """
    Update summary statistics display.
    
    Args:
        exercises: List of exercises
        logs: List of exercise logs
    """
    if not exercises:
        self.summary_label.setText("No exercises to display")
        self.summary_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #AAAAAA;
                padding: 10px;
                background-color: #2D2D2D;
                border-radius: 3px;
            }
        """)
        return
    
    completed = sum(1 for log in logs if log.completed)
    total = len(exercises)
    completion_pct = (completed / total * 100) if total > 0 else 0
    
    total_actual = sum(log.actual_value for log in logs)
    total_target = sum(log.target_value for log in logs)
    
    summary_text = f"完成率 ({completion_pct:.0f}%)  |  總進度: {total_actual}/{total_target}"
    
    self.summary_label.setText(summary_text)
    self.summary_label.setStyleSheet("""
        QLabel {
            font-size: 14px;
            color: #AAAAAA;
            padding: 10px;
            background-color: #2D2D2D;
            border-radius: 3px;
        }
    """)

    def set_date(self, date: str) -> None:
        """
        Change displayed date.
        
        Args:
            date: Date in ISO format
        """
        self._current_date = date
        self._load_exercises()


class ProgressInputDialog(QDialog):
    """
    Dialog for entering exercise progress values.
    
    Allows user to input actual value achieved and optional notes.
    """
    
    def __init__(self, exercise: Exercise, current_value: int = 0, parent=None):
        """
        Initialize progress input dialog.
        
        Args:
            exercise: Exercise being updated
            current_value: Pre-filled value
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._exercise = exercise
        
        self.setWindowTitle("Update Exercise Progress")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        self._setup_ui(current_value)
    
    def _setup_ui(self, current_value: int) -> None:
        """
        Initialize dialog UI.
        
        Args:
            current_value: Pre-filled value
        """
        layout = QVBoxLayout(self)
        
        # Apply dialog-specific styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit, QSpinBox, QTextEdit {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border: 1px solid #4ECDC4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4ECDC4;
                border: none;
                width: 16px;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #FFFFFF;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #FFFFFF;
            }
            QPushButton {
                background-color: #4ECDC4;
                color: #000000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6FE4DB;
            }
        """)
        
        # Form layout
        form = QFormLayout()
        
        # Exercise info (read-only)
        exercise_label = QLabel(f"<b>{self._exercise.name}</b>")
        target_label = QLabel(f"Target: {self._exercise.target_value} {self._exercise.unit}")
        
        form.addRow("Exercise:", exercise_label)
        form.addRow("", target_label)
        
        # Actual value input
        self.value_input = QSpinBox()
        self.value_input.setMinimum(0)
        self.value_input.setMaximum(9999)
        self.value_input.setValue(current_value)
        self.value_input.setSuffix(f" {self._exercise.unit}")
        
        form.addRow("Actual Value:", self.value_input)
        
        # Notes input
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Optional notes about your workout...")
        
        form.addRow("Notes:", self.notes_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Assembly
        layout.addLayout(form)
        layout.addWidget(button_box)
    
    def get_actual_value(self) -> int:
        """Get entered actual value."""
        return self.value_input.value()
    
    def get_notes(self) -> str:
        """Get entered notes."""
        return self.notes_input.toPlainText().strip()


class AddExerciseDialog(QDialog):
    """
    Dialog for creating new exercise definitions.
    
    Allows user to specify exercise name, category, target, and unit.
    """
    
    def __init__(self, parent=None):
        """Initialize add exercise dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Add New Exercise")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        
        # Apply dialog-specific styling to fix visibility issues
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #4ECDC4;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #4ECDC4;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
                margin-right: 5px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4ECDC4;
                border: none;
                width: 16px;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #FFFFFF;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #FFFFFF;
            }
            QPushButton {
                background-color: #4ECDC4;
                color: #000000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6FE4DB;
            }
        """)
        
        # Form layout
        form = QFormLayout()
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Push-ups, Running")
        form.addRow("Exercise Name:", self.name_input)
        
        # Category selection
        self.category_combo = QComboBox()
        self.category_combo.addItems(['cardio', 'muscle', 'stretch'])
        form.addRow("Category:", self.category_combo)
        
        # Target value
        self.target_input = QSpinBox()
        self.target_input.setMinimum(1)
        self.target_input.setMaximum(9999)
        self.target_input.setValue(30)
        form.addRow("Target Value:", self.target_input)
        
        # Unit selection
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['reps', 'sets', 'minutes', 'km', 'hours'])
        form.addRow("Unit:", self.unit_combo)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Assembly
        layout.addLayout(form)
        layout.addWidget(button_box)
    
    def _validate_and_accept(self) -> None:
        """Validate inputs before accepting."""
        if not self.name_input.text().strip():
            # Could show error message here
            return
        
        self.accept()
    
    def get_exercise_data(self) -> dict:
        """
        Get entered exercise data.
        
        Returns:
            Dictionary with name, category, target_value, unit
        """
        return {
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText(),
            'target_value': self.target_input.value(),
            'unit': self.unit_combo.currentText()
        }
