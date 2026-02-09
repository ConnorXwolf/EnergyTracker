import logging
import traceback
from typing import List, Tuple, Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QDialog, QLineEdit, QDialogButtonBox,
    QFormLayout, QSpinBox, QComboBox, QTextEdit, QMessageBox  
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont

# 模組化導入
try:
    from models import Exercise, ExerciseLog
    from managers import ExerciseManager
    from utils import get_today
    from .exercise_progress_bar import ExerciseProgressBar
except ImportError:
    pass

# 設定系統日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExerciseChecklistWidget(QWidget):
    """
    主運動追蹤組件。
    """
    
    exercise_updated = pyqtSignal()
    
    def __init__(self, exercise_manager: 'ExerciseManager', parent=None):
        super().__init__(parent)
        self._exercise_manager = exercise_manager
        self._current_date = get_today()
        
        self._setup_ui()
        self._connect_signals()
        self._load_exercises()
    
    def _setup_ui(self) -> None:
        """初始化主介面佈局。"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("每日運動追蹤 (Daily Track)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(8)
        self.list_widget.setStyleSheet("QListWidget { background-color: transparent; border: none; }")
        
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
        self.add_button = QPushButton("＋ Add Exercise")
        self.add_button.setMinimumHeight(45)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: #000000;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #6FE4DB; }
        """)
        
        button_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.summary_label)
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        self.add_button.clicked.connect(self._on_add_exercise)
        self._exercise_manager.data_changed.connect(self._load_exercises)
    
    def _load_exercises(self) -> None:
        try:
            self.list_widget.clear()
            exercises_data = self._exercise_manager.get_logs_for_date(self._current_date)
            
            if not exercises_data:
                self.summary_label.setText("No exercises set for today.")
                return
            
            for exercise, log in exercises_data:
                self._add_exercise_item(exercise, log)
            
            self._update_summary([e for e, l in exercises_data], [l for e, l in exercises_data])
        except Exception as e:
            logger.error(f"Failed to load exercises: {e}")
    
    def _add_exercise_item(self, exercise: 'Exercise', log: 'ExerciseLog') -> None:
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        
        top_row = QHBoxLayout()
        checkbox = QCheckBox(exercise.name)
        checkbox.setChecked(log.completed)
        checkbox.stateChanged.connect(lambda s: self._on_checkbox_changed(exercise.id, s))
        
        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda: self._show_progress_dialog(exercise.id, log.actual_value))
        
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(30, 30)
        del_btn.setStyleSheet("color: #FF6B6B;")
        del_btn.clicked.connect(lambda: self._on_delete_exercise(exercise.id, exercise.name))
        
        top_row.addWidget(checkbox)
        top_row.addStretch()
        top_row.addWidget(edit_btn)
        top_row.addWidget(del_btn)
        
        progress_bar = ExerciseProgressBar(log, exercise.color)
        
        item_layout.addLayout(top_row)
        item_layout.addWidget(progress_bar)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 90))
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)

    def _on_checkbox_changed(self, exercise_id: int, state: int) -> None:
        completed = (state == Qt.CheckState.Checked.value)
        try:
            if completed:
                self._show_progress_dialog(exercise_id)
            else:
                self._exercise_manager.update_progress(exercise_id, self._current_date, 0, False)
        except Exception as e:
            logger.error(f"Update failed: {e}")

    def _on_delete_exercise(self, exercise_id: int, name: str) -> None:
        if QMessageBox.warning(self, "Confirm", f"Delete '{name}'?", 
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self._exercise_manager.delete_exercise(exercise_id)

    def _show_progress_dialog(self, exercise_id: int, current: int = 0) -> None:
        exercise = self._exercise_manager.get_exercise_by_id(exercise_id)
        if not exercise: return
        
        dialog = ProgressInputDialog(exercise, current, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            val = dialog.get_actual_value()
            self._exercise_manager.update_progress(
                exercise_id, self._current_date, val, 
                val >= exercise.target_value, dialog.get_notes()
            )

    def _on_add_exercise(self) -> None:
        """Handle add exercise button click."""
        dialog = AddExerciseDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_exercise_data()
            
            self._exercise_manager.create_exercise(
                name=data['name'],
                category=data['category'],
                target_value=data['target_value'],
                unit=data['unit']
            )

    def _update_summary(self, exercises, logs) -> None:
        done = sum(1 for l in logs if l.completed)
        self.summary_label.setText(f"Today's Progress: {done}/{len(exercises)} completed")


class ProgressInputDialog(QDialog):
    def __init__(self, exercise, current=0, parent=None):
        super().__init__(parent)
        self.exercise = exercise
        self.setWindowTitle("Log Progress")
        self._setup_ui(current)

    def _setup_ui(self, current):
        self.setStyleSheet("QDialog { background-color: #2D2D2D; color: white; }")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.val_input = QSpinBox()
        self.val_input.setRange(0, 10000)
        self.val_input.setValue(current)
        self.val_input.setSuffix(f" {self.exercise.unit}")
        
        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(60)
        
        form.addRow(f"{self.exercise.name} Amount:", self.val_input)
        form.addRow("Notes:", self.note_input)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(btns)

    def get_actual_value(self) -> int: return self.val_input.value()
    def get_notes(self) -> str: return self.note_input.toPlainText()


class AddExerciseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Exercise")
        self.setModal(True)
        self.setMinimumWidth(350)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QDialog { background-color: #2D2D2D; }
            QLabel { color: #FFFFFF; font-size: 12px; }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #3D3D3D; color: #FFFFFF;
                border: 1px solid #555555; border-radius: 3px;
                padding: 5px; font-size: 12px;
            }
            QPushButton {
                background-color: #4ECDC4; color: #000000;
                border: none; padding: 8px 16px;
                border-radius: 4px; font-weight: bold;
            }
        """)
        
        form = QFormLayout()
        self.name_input = QLineEdit()
        form.addRow("Exercise Name:", self.name_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(['physical', 'mental', 'sleepiness'])
        form.addRow("Category:", self.category_combo)
        
        self.target_input = QSpinBox()
        self.target_input.setMinimum(1)
        self.target_input.setMaximum(9999)
        self.target_input.setValue(30)
        form.addRow("Target Value:", self.target_input)
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['reps', 'sets', 'minutes', 'km', 'hours'])
        form.addRow("Unit:", self.unit_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(button_box)

    def _validate_and_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Input Error", "Please enter an exercise name.")
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
