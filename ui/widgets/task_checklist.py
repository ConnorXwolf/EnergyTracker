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
    QFormLayout, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, QSize, pyqtSignal
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
        
        Args:
            task_manager: Manager for task operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._task_manager = task_manager
        self._current_date = None  # Will be set by parent
        
        self._setup_ui()
        self._connect_signals()
        self._load_tasks()
    
    def set_current_date(self, date_str: str) -> None:
        """
        Set the current date being viewed/edited.
        
        Args:
            date_str: Date in ISO format (YYYY-MM-DD)
        """
        self._current_date = date_str
        self._load_tasks()
    
    def _setup_ui(self) -> None:
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header section (14pt bold)
        header_layout = QHBoxLayout()
        
        title_label = QLabel("任務清單 (Task Checklist)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Task list (14pt font, white checkboxes)
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(5)
        list_font = QFont()
        list_font.setPointSize(14)  # 14pt for content
        self.list_widget.setFont(list_font)
        
        # Style for white checkboxes
        self.list_widget.setStyleSheet("""
            QCheckBox {
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
                background-color: #4ECDC4;
                border: 2px solid white;
            }
        """)
        
        # Summary footer
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #AAAAAA;
                padding: 8px;
                background-color: #2D2D2D;
                border-radius: 3px;
            }
        """)
        
        # Action buttons (larger, like task list)
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Task")
        self.add_button.setMinimumWidth(200)  # Larger button
        self.add_button.setMinimumHeight(50)  # Larger button
        add_button_font = QFont()
        add_button_font.setPointSize(12)
        self.add_button.setFont(add_button_font)
        
        self.clear_button = QPushButton("Clear Completed")
        self.clear_button.setMinimumWidth(200)  # Larger button
        self.clear_button.setMinimumHeight(50)  # Larger button
        clear_button_font = QFont()
        clear_button_font.setPointSize(12)
        self.clear_button.setFont(clear_button_font)
        
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()  # Push buttons to edges
        button_layout.addWidget(self.clear_button)
        
        # Assembly
        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)  # Main area will auto expand
        layout.addWidget(self.summary_label)
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self.add_button.clicked.connect(self._on_add_task)
        self.clear_button.clicked.connect(self._on_clear_completed)
        
        self._task_manager.data_changed.connect(self._load_tasks)
    
    def _load_tasks(self) -> None:
        """Load and display tasks organized by groups."""
        try:
            self.list_widget.clear()
            
            # Get task groups
            groups = self._task_manager.get_task_groups()
            
            if not groups:
                empty_item = QListWidgetItem("No tasks. Click 'Add Task' to create one.")
                self.list_widget.addItem(empty_item)
                self._update_summary(0, 0)
                return
            
            # Display each group
            total_tasks = 0
            completed_tasks = 0
            
            for group in groups:
                # Add group header
                self._add_group_header(group)
                
                # Add tasks in group
                for task in group.tasks:
                    self._add_task_item(task)
                    total_tasks += 1
                    if task.is_completed:
                        completed_tasks += 1
            
            self._update_summary(completed_tasks, total_tasks)
            
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def _add_group_header(self, group: TaskGroup) -> None:
        """
        Add group header with progress summary.
        
        Args:
            group: TaskGroup to display
        """
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 15, 5, 15)  # Increased vertical padding
        
        # Group name
        name_label = QLabel(f"📋 {group.category}")
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(15)  # Increased font size
        name_label.setFont(name_font)
        
        # Progress text
        progress_text = group.format_progress()
        progress_label = QLabel(progress_text)
        progress_label.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(progress_label)
        
        # Add to list with increased height
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))  # Increased height to 70px
        list_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Not selectable
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, header_widget)
    
    def _add_task_item(self, task: Task) -> None:
        """
        Add task checkbox to list.
        
        Args:
            task: Task to display
        """
        # Create checkbox with white styling
        checkbox = QCheckBox(task.title)
        checkbox.setChecked(task.is_completed)
        checkbox.setStyleSheet("""
            QCheckBox {
                padding-left: 20px;
                font-size: 14px;
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
                background-color: #4ECDC4;
                border: 2px solid white;
            }
        """)
        
        # Store task_id for later reference
        checkbox.setProperty("task_id", task.id)
        
        # Connect signal
        checkbox.stateChanged.connect(
            lambda state, tid=task.id: self._on_task_toggled(tid, state)
        )
        
        # Add to list with increased height
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 50))  # Set height to 50px
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, checkbox)
    
    def _on_task_toggled(self, task_id: int, state: int) -> None:
        """
        Handle task checkbox toggle.
        
        Args:
            task_id: Task being toggled
            state: Qt.CheckState value
        """
        is_checked = (state == Qt.CheckState.Checked.value)
        
        self._task_manager.update_task(
            task_id=task_id,
            is_completed=is_checked
        )
        
        self.task_updated.emit()
    
    def _on_add_task(self) -> None:
        """Handle add task button click."""
        dialog = AddTaskDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            
            # Use current date or get today as fallback
            from utils import get_today
            task_date = self._current_date if self._current_date else get_today()
            
            self._task_manager.create_task(
                title=data['title'],
                date=task_date,  # Add date parameter
                due_date=data.get('due_date'),
                priority=data.get('priority', 0),
                category=data.get('category')
            )
    
    def _on_clear_completed(self) -> None:
        """Handle clear completed button click."""
        count = self._task_manager.clear_completed_tasks()
        print(f"Cleared {count} completed tasks")
    
    def _update_summary(self, completed: int, total: int) -> None:
        """
        Update summary statistics display.
        
        Args:
            completed: Number of completed tasks
            total: Total number of tasks
        """
        if total == 0:
            self.summary_label.setText("No tasks to display")
            return
        
        percentage = (completed / total * 100) if total > 0 else 0
        summary_text = f"Completed: {completed}/{total} ({percentage:.0f}%)"
        
        self.summary_label.setText(summary_text)


class AddTaskDialog(QDialog):
    """
    Dialog for creating new tasks.
    
    Allows user to specify task title, category, due date, and priority.
    """
    
    def __init__(self, parent=None):
        """Initialize add task dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Add New Task")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., work, reading, learning")
        form.addRow("Task Title:", self.title_input)
        
        # Category input
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., unspecific")
        self.category_input.setText("unspecific")
        form.addRow("Category:", self.category_input)
        
        # Due date (optional)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setSpecialValueText("No due date")
        form.addRow("Due Date:", self.date_input)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['Low', 'Medium', 'High'])
        form.addRow("Priority:", self.priority_combo)
        
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
        if not self.title_input.text().strip():
            return
        
        self.accept()
    
    def get_task_data(self) -> dict:
        """
        Get entered task data.
        
        Returns:
            Dictionary with task properties
        """
        # Convert priority
        priority_map = {'Low': 0, 'Medium': 1, 'High': 2}
        priority = priority_map[self.priority_combo.currentText()]
        
        # Get due date (None if special value)
        due_date = None
        if self.date_input.date() != QDate.currentDate():
            due_date = self.date_input.date().toString(Qt.DateFormat.ISODate)
        
        # Get category (None if empty)
        category = self.category_input.text().strip() or None
        
        return {
            'title': self.title_input.text().strip(),
            'category': category,
            'due_date': due_date,
            'priority': priority
        }