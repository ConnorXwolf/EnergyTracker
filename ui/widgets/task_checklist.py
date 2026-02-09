"""
Task checklist widget with grouped task display.

Displays tasks organized by category with completion checkboxes
and summary statistics.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QDialog, QLineEdit, QDialogButtonBox,
    QFormLayout, QComboBox, QDateEdit, QMenu, QMessageBox  # Added QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QSize, pyqtSignal, QPoint  # Added QPoint
from PyQt6.QtGui import QFont

from managers import TaskManager
from models import Task, TaskGroup


class TaskChecklistWidget(QWidget):
    """
    Task checklist widget with grouping support.
    
    Displays tasks organized by category with checkboxes,
    provides summary statistics, and handles task interactions.
    """
    
    task_updated = pyqtSignal()
    
    def __init__(self, task_manager: TaskManager, parent=None):
        """
        Initialize task checklist widget.
        """
        super().__init__(parent)
        
        self._task_manager = task_manager
        self._current_date = None  # Will be set by parent
        
        self._setup_ui()
        self._connect_signals()
        self._load_tasks()
    
    def set_current_date(self, date_str: str) -> None:
        """Set the current date being viewed/edited."""
        self._current_date = date_str
        self._load_tasks()
    
    def _setup_ui(self) -> None:
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header section
        header_layout = QHBoxLayout()
        title_label = QLabel("任務清單 (Task Checklist)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # --- Task list section (MODIFIED) ---
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(5)
        # Enable context menu
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # Connect signal
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        
        list_font = QFont()
        list_font.setPointSize(14)
        self.list_widget.setFont(list_font)
        
        # Style for white checkboxes
        self.list_widget.setStyleSheet("""
            QCheckBox { color: white; }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid white; border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #4ECDC4; border: 2px solid white;
            }
        """)
        
        # Summary footer
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            QLabel {
                font-size: 13px; color: #AAAAAA; padding: 8px;
                background-color: #2D2D2D; border-radius: 3px;
            }
        """)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.add_button.setMinimumSize(200, 50)
        self.add_button.setFont(QFont("", 12))
        
        self.clear_button = QPushButton("Clear Completed")
        self.clear_button.setMinimumSize(200, 50)
        self.clear_button.setFont(QFont("", 12))
        
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        
        # Assembly
        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.summary_label)
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self.add_button.clicked.connect(self._on_add_task)
        self.clear_button.clicked.connect(self._on_clear_completed)
        self._task_manager.data_changed.connect(self._load_tasks)

    # --- Context Menu Methods (NEWLY ADDED) ---
    def _show_context_menu(self, position: QPoint) -> None:
        """
        Display context menu for task item.
        """
        # Get the item at the clicked position
        item = self.list_widget.itemAt(position)
        if item is None:
            return
        
        # Get the widget associated with this item
        widget = self.list_widget.itemWidget(item)
        if widget is None or not isinstance(widget, QCheckBox):
            return
        
        # Retrieve task_id from widget property
        task_id = widget.property("task_id")
        if task_id is None:
            return
        
        # Get task title for confirmation message
        task_title = widget.text()
        
        # Create context menu
        menu = QMenu(self)
        delete_action = menu.addAction("🗑 Delete Task")
        
        # Show menu and get selected action
        action = menu.exec(self.list_widget.mapToGlobal(position))
        
        if action == delete_action:
            self._on_delete_task(task_id, task_title)

    def _on_delete_task(self, task_id: int, task_title: str) -> None:
        """
        Handle task deletion with confirmation.
        """
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Permanently delete task:\n'{task_title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Attempt deletion
            success = self._task_manager.delete_task(task_id)
            
            if success:
                QMessageBox.information(
                    self, "Task Deleted",
                    f"Task '{task_title}' has been permanently deleted."
                )
            else:
                QMessageBox.warning(
                    self, "Deletion Failed",
                    f"Failed to delete task '{task_title}'.\nThe task may have already been deleted."
                )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
            import traceback
            traceback.print_exc()

    # --- Other Logic Methods ---
    def _load_tasks(self) -> None:
        """Load and display tasks organized by groups."""
        try:
            self.list_widget.clear()
            groups = self._task_manager.get_task_groups()
            
            if not groups:
                empty_item = QListWidgetItem("No tasks. Click 'Add Task' to create one.")
                self.list_widget.addItem(empty_item)
                self._update_summary(0, 0)
                return
            
            total_tasks = 0
            completed_tasks = 0
            for group in groups:
                self._add_group_header(group)
                for task in group.tasks:
                    self._add_task_item(task)
                    total_tasks += 1
                    if task.is_completed:
                        completed_tasks += 1
            
            self._update_summary(completed_tasks, total_tasks)
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def _add_group_header(self, group: TaskGroup) -> None:
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 15, 5, 15)
        
        name_label = QLabel(f"📋 {group.category}")
        name_label.setFont(QFont("", 15, QFont.Weight.Bold))
        
        progress_label = QLabel(group.format_progress())
        progress_label.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(progress_label)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        list_item.setFlags(Qt.ItemFlag.NoItemFlags)
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, header_widget)
    
    def _add_task_item(self, task: Task) -> None:
        checkbox = QCheckBox(task.title)
        checkbox.setChecked(task.is_completed)
        checkbox.setStyleSheet("""
            QCheckBox { padding-left: 20px; font-size: 14px; color: white; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid white; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #4ECDC4; }
        """)
        checkbox.setProperty("task_id", task.id)
        checkbox.stateChanged.connect(
            lambda state, tid=task.id: self._on_task_toggled(tid, state)
        )
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 50))
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, checkbox)
    
    def _on_task_toggled(self, task_id: int, state: int) -> None:
        is_checked = (state == Qt.CheckState.Checked.value)
        self._task_manager.update_task(task_id=task_id, is_completed=is_checked)
        self.task_updated.emit()
    
    def _on_add_task(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            from utils import get_today
            task_date = self._current_date if self._current_date else get_today()
            self._task_manager.create_task(
                title=data['title'], date=task_date,
                due_date=data.get('due_date'), priority=data.get('priority', 0),
                category=data.get('category')
            )
    
    def _on_clear_completed(self) -> None:
        count = self._task_manager.clear_completed_tasks()
        print(f"Cleared {count} completed tasks")
    
    def _update_summary(self, completed: int, total: int) -> None:
        if total == 0:
            self.summary_label.setText("No tasks to display")
            return
        percentage = (completed / total * 100) if total > 0 else 0
        self.summary_label.setText(f"Completed: {completed}/{total} ({percentage:.0f}%)")


class AddTaskDialog(QDialog):
    # (此類別保持不變，程式碼已包含在檔案末尾)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        self.setModal(True)
        self.setMinimumWidth(350)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., work, reading, learning")
        form.addRow("Task Title:", self.title_input)
        self.category_input = QLineEdit()
        self.category_input.setText("unspecific")
        form.addRow("Category:", self.category_input)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("Due Date:", self.date_input)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['Low', 'Medium', 'High'])
        form.addRow("Priority:", self.priority_combo)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addLayout(form)
        layout.addWidget(button_box)
    
    def _validate_and_accept(self) -> None:
        if not self.title_input.text().strip(): return
        self.accept()
    
    def get_task_data(self) -> dict:
        priority_map = {'Low': 0, 'Medium': 1, 'High': 2}
        due_date = None
        if self.date_input.date() != QDate.currentDate():
            due_date = self.date_input.date().toString(Qt.DateFormat.ISODate)
        return {
            'title': self.title_input.text().strip(),
            'category': self.category_input.text().strip() or None,
            'due_date': due_date,
            'priority': priority_map[self.priority_combo.currentText()]
        }
