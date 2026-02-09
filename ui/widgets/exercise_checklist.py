import traceback
from typing import List, Tuple, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QDialog, QLineEdit, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QTextEdit, QMessageBox  
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont

# 假設這些模組已存在於你的專案中
from models import Exercise, ExerciseLog
from managers import ExerciseManager
from utils import get_today
from .exercise_progress_bar import ExerciseProgressBar


class ExerciseChecklistWidget(QWidget):
    """
    Main exercise tracking widget with progress visualization.
    """
    
    exercise_updated = pyqtSignal()
    
    def __init__(self, exercise_manager: ExerciseManager, parent=None):
        super().__init__(parent)
        self._exercise_manager = exercise_manager
        self._current_date = get_today()
        
        self._setup_ui()
        self._connect_signals()
        self._load_exercises()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header section
        header_layout = QHBoxLayout()
        title_label = QLabel("每日運動 (Daily Exercises)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(8)
        self.list_widget.setMinimumHeight(250)
        
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
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Exercise")
        self.add_button.setMinimumSize(200, 50)
        self.add_button.setFont(QFont("", 12))
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMinimumSize(200, 50)
        self.refresh_button.setFont(QFont("", 12))
        
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.summary_label)
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        self.add_button.clicked.connect(self._on_add_exercise)
        self.refresh_button.clicked.connect(self._load_exercises)
        self._exercise_manager.data_changed.connect(self._load_exercises)
    
    def _load_exercises(self) -> None:
        try:
            self.list_widget.clear()
            exercises_data = self._exercise_manager.get_logs_for_date(self._current_date)
            
            if not exercises_data:
                empty_item = QListWidgetItem("No exercises found.")
                self.list_widget.addItem(empty_item)
                self._update_summary([], [])
                return
            
            exercises = []
            logs = []
            for exercise, log in exercises_data:
                exercises.append(exercise)
                logs.append(log)
                self._add_exercise_item(exercise, log)
            
            self._update_summary(exercises, logs)
        except Exception as e:
            print(f"Error loading exercises: {e}")
    
    def _add_exercise_item(self, exercise: Exercise, log: ExerciseLog) -> None:
        """建立列表中的每一個運動項目卡片 (已修正縮排)"""
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        item_layout.setSpacing(5)
        
        top_row = QHBoxLayout()
        checkbox = QCheckBox(exercise.name)
        checkbox.setChecked(log.completed)
        checkbox.setStyleSheet("""
            QCheckBox { font-size: 14px; font-weight: bold; color: white; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid white; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #32CD32; }
        """)
        
        checkbox.setProperty("exercise_id", exercise.id)
        checkbox.stateChanged.connect(
            lambda state, eid=exercise.id: self._on_checkbox_changed(eid, state)
        )
        
        top_row.addWidget(checkbox)
        top_row.addStretch()
        
        edit_button = QPushButton("⋯")
        edit_button.setFixedSize(40, 30)
        edit_button.setStyleSheet("font-size: 20px;")
        edit_button.clicked.connect(
            lambda _, eid=exercise.id, lg=log: self._on_edit_progress(eid, lg)
        )
        
        delete_button = QPushButton("🗑")
        delete_button.setFixedSize(40, 30)
        delete_button.setStyleSheet("background-color: #F44336; color: white; border-radius: 4px;")
        delete_button.clicked.connect(
            lambda _, eid=exercise.id, name=exercise.name: self._on_delete_exercise(eid, name)
        )
        
        top_row.addWidget(edit_button)
        top_row.addWidget(delete_button)
        
        progress_bar = ExerciseProgressBar(log, exercise.color)
        item_layout.addLayout(top_row)
        item_layout.addWidget(progress_bar)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 85))
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)

    def _on_checkbox_changed(self, exercise_id: int, state: int) -> None:
        # 修正：PyQt6 stateChanged 傳入的是整數，直接比對 CheckState
        is_checked = (state == Qt.CheckState.Checked.value)
        if is_checked:
            self._show_progress_dialog(exercise_id)
        else:
            self._exercise_manager.update_progress(
                exercise_id=exercise_id,
                date=self._current_date,
                actual_value=0,
                completed=False
            )
            self.exercise_updated.emit()

    def _on_edit_progress(self, exercise_id: int, log: ExerciseLog) -> None:
        self._show_progress_dialog(exercise_id, log.actual_value)

    def _show_progress_dialog(self, exercise_id: int, current_value: int = 0) -> None:
        try:
            exercise = self._exercise_manager.get_exercise_by_id(exercise_id)
            if not exercise: return
            
            dialog = ProgressInputDialog(exercise, current_value, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                actual_value = dialog.get_actual_value()
                self._exercise_manager.update_progress(
                    exercise_id=exercise_id,
                    date=self._current_date,
                    actual_value=actual_value,
                    completed=(actual_value >= exercise.target_value),
                    notes=dialog.get_notes()
                )
                self.exercise_updated.emit()
        except Exception as e:
            print(f"Error: {e}")

    def _on_add_exercise(self) -> None:
        dialog = AddExerciseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_exercise_data()
            self._exercise_manager.create_exercise(**data)
            # 如果 manager 沒有自動 emit data_changed，這裡需要手動呼叫：
            # self._load_exercises()

    def _on_delete_exercise(self, exercise_id: int, exercise_name: str) -> None:
        """刪除運動項目並確認 (已修正縮排)"""
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Permanently delete '{exercise_name}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            if self._exercise_manager.delete_exercise(exercise_id):
                QMessageBox.information(self, "Deleted", f"'{exercise_name}' deleted.")
            else:
                QMessageBox.warning(self, "Failed", "Could not delete exercise.")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", str(e))

    def _update_summary(self, exercises: List[Exercise], logs: List[ExerciseLog]) -> None:
        if not exercises:
            self.summary_label.setText("No exercises to display")
            return
        
        completed = sum(1 for log in logs if log.completed)
        total = len(exercises)
        # 計算完成率公式：$$Completion\% = \frac{Completed}{Total} \times 100$$
        pct = (completed / total * 100) if total > 0 else 0
        
        total_actual = sum(log.actual_value for log in logs)
        total_target = sum(log.target_value for log in logs)
        
        self.summary_label.setText(
            f"完成率: {completed}/{total} ({pct:.0f}%) | 總進度: {total_actual}/{total_target}"
        )
        
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

        

        # Form layout

        form = QFormLayout()

        

        # Name input
