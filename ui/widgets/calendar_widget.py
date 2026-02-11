"""
Calendar widget with event and task integration.

Displays monthly calendar with highlighted dates containing events and tasks,
and shows unified event/task list for selected dates.
"""

from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget,
    QListWidget, QListWidgetItem, QLabel,
    QPushButton, QHBoxLayout, QDialog,
    QLineEdit, QTextEdit, QDialogButtonBox,
    QFormLayout, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt6.QtGui import QTextCharFormat, QColor, QFont

from managers import EventManager, TaskManager
from models import CalendarEvent, Task
from utils import get_today


class CalendarWidget(QWidget):
    """
    Calendar widget with event and task display.
    
    Shows monthly calendar with date highlighting for events and tasks,
    and displays unified list for selected date.
    """
    
    date_selected = pyqtSignal(str)  # Emits ISO date
    
    def __init__(self, event_manager: EventManager, task_manager: TaskManager, parent=None):
        """
        Initialize calendar widget with event and task integration.
        
        Args:
            event_manager: Manager for calendar events
            task_manager: Manager for task operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._event_manager = event_manager
        self._task_manager = task_manager
        self._current_year = QDate.currentDate().year()
        self._current_month = QDate.currentDate().month()
        
        self._setup_ui()
        self._connect_signals()
        self._load_events()
    
    def _setup_ui(self) -> None:
        """Initialize UI components and layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Left side: Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumSize(700, 350)
        self.calendar.setMaximumWidth(750)
        
        # Right side: Event list section
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        
        list_header = QLabel("Event & Task")
        list_header_font = QFont()
        list_header_font.setBold(True)
        list_header_font.setPointSize(16)
        list_header.setFont(list_header_font)

        self.event_list = QListWidget()
        self.event_list.setMinimumWidth(550)
        self.event_list.setMaximumWidth(700)
        self.event_list.setMinimumHeight(400)
        
        # Add event button
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.setMaximumWidth(300)
        
        # Assemble right side
        right_layout.addWidget(list_header)
        right_layout.addWidget(self.event_list)
        right_layout.addWidget(self.add_event_button)
        right_layout.addStretch()
        
        main_layout.addWidget(self.calendar)
        main_layout.addStretch()
        main_layout.addLayout(right_layout)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self.calendar.selectionChanged.connect(self._on_date_selected)
        self.calendar.currentPageChanged.connect(self._on_month_changed)
        self.add_event_button.clicked.connect(self._on_add_event)
        
        self._event_manager.data_changed.connect(self._load_events)
        self._event_manager.event_created.connect(self._on_event_created)
        
        # Connect task manager signals
        self._task_manager.data_changed.connect(self._load_events)
    
    def _load_events(self) -> None:
        """
        Load events AND tasks for current month and update calendar highlighting.
        
        FIXED: Now considers both task.date and task.due_date fields.
        """
        try:
            print(f"\n=== Loading calendar for {self._current_year}-{self._current_month:02d} ===")
            
            # Fetch events
            events = self._event_manager.get_events_for_month(
                self._current_year,
                self._current_month
            )
            print(f"Events found: {len(events)}")
            for event in events:
                print(f"  Event: {event.title} on {event.event_date}")
            
            # ==================== FIXED: TASK RETRIEVAL ====================
            # Get ALL tasks and filter by EITHER date field or due_date field
            all_tasks = self._task_manager.get_all_tasks()
            
            tasks_this_month = []
            for task in all_tasks:
                matched = False
                
                # Check due_date first (higher priority)
                if task.due_date:
                    try:
                        y, m, _ = map(int, task.due_date.split('-'))
                        if y == self._current_year and m == self._current_month:
                            tasks_this_month.append(task)
                            matched = True
                            print(f"  Task (due_date): {task.title} on {task.due_date}")
                    except Exception as e:
                        print(f"  Error parsing task due_date: {e}")
                
                # Fallback to date field if not already matched
                if not matched and task.date:
                    try:
                        y, m, _ = map(int, task.date.split('-'))
                        if y == self._current_year and m == self._current_month:
                            tasks_this_month.append(task)
                            print(f"  Task (date): {task.title} on {task.date}")
                    except Exception as e:
                        print(f"  Error parsing task date: {e}")
            
            print(f"Tasks in this month: {len(tasks_this_month)}")
            # ================================================================
            
            # Clear existing highlights
            self._clear_highlights()
            
            # Get unique event dates
            event_dates = set(event.event_date for event in events)
            
            # ==================== FIXED: TASK DATE EXTRACTION ====================
            # Get unique task display dates (prioritize due_date over date)
            task_dates = set()
            for task in tasks_this_month:
                display_date = task.due_date if task.due_date else task.date
                if display_date:
                    task_dates.add(display_date)
            # =====================================================================
            
            print(f"Unique event dates: {event_dates}")
            print(f"Unique task dates: {task_dates}")
            
            # Highlight dates based on content type
            dates_with_both = event_dates & task_dates
            dates_with_only_events = event_dates - task_dates
            dates_with_only_tasks = task_dates - event_dates
            
            print(f"Dates with events only: {dates_with_only_events}")
            print(f"Dates with tasks only: {dates_with_only_tasks}")
            print(f"Dates with both: {dates_with_both}")
            
            # Apply highlighting with visual distinction
            for date_str in dates_with_only_events:
                self._highlight_date(date_str, highlight_type='event')
            
            for date_str in dates_with_only_tasks:
                self._highlight_date(date_str, highlight_type='task')
            
            for date_str in dates_with_both:
                self._highlight_date(date_str, highlight_type='both')
            
            # Refresh event list for currently selected date
            self._update_event_list()
            
            print("=== Calendar loading complete ===\n")
            
        except Exception as e:
            print(f"ERROR loading events and tasks: {e}")
            import traceback
            traceback.print_exc()
    
    def _clear_highlights(self) -> None:
        """Clear all calendar date highlights."""
        default_format = QTextCharFormat()
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        for day in range(1, 32):
            try:
                date = QDate(year, month, day)
                if date.isValid():
                    self.calendar.setDateTextFormat(date, default_format)
            except:
                break
    
    def _highlight_date(self, date_str: str, highlight_type: str = 'event') -> None:
        """
        Highlight calendar date with type-specific styling.
        
        Args:
            date_str: Date in ISO format (YYYY-MM-DD)
            highlight_type: Type of highlight ('event', 'task', 'both')
        """
        try:
            year, month, day = map(int, date_str.split('-'))
            date = QDate(year, month, day)
            if not date.isValid():
                return
            
            highlight_format = QTextCharFormat()
            
            # Color coding by type
            if highlight_type == 'event':
                # Cyan background for events only
                highlight_format.setBackground(QColor('#4ECDC4'))
                highlight_format.setForeground(QColor('#000000'))
            elif highlight_type == 'task':
                # Orange background for tasks only
                highlight_format.setBackground(QColor("#FFB700"))
                highlight_format.setForeground(QColor('#000000'))
            elif highlight_type == 'both':
                # Purple background for mixed dates
                highlight_format.setBackground(QColor('#9B59B6'))
                highlight_format.setForeground(QColor('#FFFFFF'))
            
            highlight_format.setFontWeight(QFont.Weight.Bold)
            self.calendar.setDateTextFormat(date, highlight_format)
            
            print(f"Highlighted {date_str} as {highlight_type}")
            
        except Exception as e:
            print(f"ERROR highlighting date {date_str}: {e}")
    
    def _on_date_selected(self) -> None:
        """Handle calendar date selection."""
        self._update_event_list()
        self.date_selected.emit(self.calendar.selectedDate().toString(Qt.DateFormat.ISODate))
    
    def _on_month_changed(self, year: int, month: int) -> None:
        """Handle calendar month change."""
        self._current_year, self._current_month = year, month
        self._load_events()
    
    def _update_event_list(self) -> None:
        """
        Update event list for currently selected date with tasks and events.
        
        FIXED: Now matches tasks by EITHER date or due_date field.
        """
        try:
            selected_date = self.calendar.selectedDate()
            date_str = selected_date.toString(Qt.DateFormat.ISODate)
            
            print(f"\n=== Updating event list for {date_str} ===")
            
            # Fetch events
            events = self._event_manager.get_events_for_date(date_str)
            print(f"Events found: {len(events)}")
            for event in events:
                print(f"  Event: {event.title}")
            
            # ==================== FIXED: TASK MATCHING ====================
            # Get ALL tasks and filter by EITHER date or due_date
            all_tasks = self._task_manager.get_all_tasks()
            print(f"Total tasks in database: {len(all_tasks)}")
            
            tasks_for_date = []
            for task in all_tasks:
                matched = False
                match_reason = ""
                
                # Priority 1: Match by due_date
                if task.due_date == date_str:
                    tasks_for_date.append(task)
                    matched = True
                    match_reason = "due_date"
                
                # Priority 2: Match by date field (only if due_date didn't match)
                elif not matched and task.date == date_str:
                    tasks_for_date.append(task)
                    matched = True
                    match_reason = "date"
                
                if matched:
                    print(f"  Task '{task.title}': matched by {match_reason} = {date_str}")
            
            print(f"Tasks for {date_str}: {len(tasks_for_date)}")
            # ==============================================================
            
            self.event_list.clear()
            
            # Check if there's any content to display
            if not events and not tasks_for_date:
                empty_item = QListWidgetItem("No events or tasks for this date")
                self.event_list.addItem(empty_item)
                print("No events or tasks to display")
                return
            
            # Display events first
            for event in events:
                print(f"Adding event to list: {event.title}")
                self._add_event_item(event)
            
            # Display tasks
            if tasks_for_date:
                # Sort by priority (high to low) then alphabetically
                sorted_tasks = sorted(
                    tasks_for_date,
                    key=lambda t: (-t.priority, t.title)
                )
                
                for task in sorted_tasks:
                    print(f"Adding task to list: {task.title}")
                    self._add_task_item(task)
            
            print("=== Event list update complete ===\n")
            
        except Exception as e:
            print(f"ERROR updating event list: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_event_item(self, event: CalendarEvent) -> None:
        """Add event item with delete button to list."""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        event_text_layout = QVBoxLayout()
        title_label = QLabel(f"📅 {event.title}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        event_text_layout.addWidget(title_label)
        
        if event.description:
            desc_label = QLabel(f"  {event.description}")
            desc_label.setStyleSheet("color: #AAAAAA; font-size: 16px;")
            desc_label.setWordWrap(True)
            event_text_layout.addWidget(desc_label)
        
        delete_button = QPushButton("X")
        delete_button.setFixedSize(35, 35)
        delete_button.setStyleSheet("""
            QPushButton {
                font-size: 18px; background-color: #F44336; color: white;
                border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        delete_button.clicked.connect(lambda: self._on_delete_event(event.id, event.title))
        
        item_layout.addLayout(event_text_layout)
        item_layout.addStretch()
        item_layout.addWidget(delete_button)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 60))
        self.event_list.addItem(list_item)
        self.event_list.setItemWidget(list_item, item_widget)
    
    def _add_task_item(self, task: Task) -> None:
        """
        Add task item to event list with visual distinction.
        
        Args:
            task: Task model to display
        """
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # Task icon and text layout
        task_text_layout = QVBoxLayout()
        
        # Task title with completion indicator and priority badge
        completion_icon = "✓" if task.is_completed else "○"
        priority_badge = ""
        if task.priority == 2:
            priority_badge = "🔴 "  # High priority
        elif task.priority == 1:
            priority_badge = "🟡 "  # Medium priority
        
        # Format: 任務名稱(類別) or just 任務名稱 if no category
        if task.category:
            display_text = f"{completion_icon} {priority_badge}{task.title}({task.category})"
        else:
            display_text = f"{completion_icon} {priority_badge}{task.title}"
        
        title_label = QLabel(display_text)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        
        # Strikethrough if completed
        if task.is_completed:
            title_label.setStyleSheet("color: #888888; text-decoration: line-through;")
        else:
            title_label.setStyleSheet("color: #FFE153;")  # Orange for pending tasks
        
        task_text_layout.addWidget(title_label)
        
        # Delete button for tasks
        delete_button = QPushButton("X")
        delete_button.setFixedSize(35, 35)
        delete_button.setStyleSheet("""
            QPushButton {
                font-size: 18px; background-color: #F44336; color: white;
                border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        delete_button.clicked.connect(
            lambda: self._on_delete_task(task.id, task.title)
        )
        
        item_layout.addLayout(task_text_layout)
        item_layout.addStretch()
        item_layout.addWidget(delete_button)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 60))
        self.event_list.addItem(list_item)
        self.event_list.setItemWidget(list_item, item_widget)
    
    def _on_add_event(self) -> None:
        """Handle add event button click."""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString(Qt.DateFormat.ISODate)
        dialog = AddEventDialog(date_str, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_event_data()
            self._event_manager.create_event(**data)
    
    def _on_event_created(self, date_str: str) -> None:
        """Handle event creation signal."""
        try:
            year, month, _ = map(int, date_str.split('-'))
            if year == self._current_year and month == self._current_month:
                self._load_events()
        except:
            pass
    
    def _on_delete_event(self, event_id: int, event_title: str) -> None:
        """Handle event deletion with confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Permanently delete event:\n'{event_title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            if self._event_manager.delete_event(event_id):
                QMessageBox.information(self, "Event Deleted", f"Event '{event_title}' deleted.")
            else:
                QMessageBox.warning(self, "Deletion Failed", "The event may have already been deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            import traceback
            traceback.print_exc()
    
    def _on_delete_task(self, task_id: int, task_title: str) -> None:
        """
        Handle task deletion with confirmation.
        
        Args:
            task_id: Task identifier
            task_title: Task title for confirmation message
        """
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Permanently delete task:\n'{task_title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            if self._task_manager.delete_task(task_id):
                QMessageBox.information(self, "Task Deleted", f"Task '{task_title}' deleted.")
                # Refresh calendar to update highlighting
                self._load_events()
            else:
                QMessageBox.warning(self, "Deletion Failed", "The task may have already been deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            import traceback
            traceback.print_exc()


class AddEventDialog(QDialog):
    """Dialog for adding new calendar events."""
    
    def __init__(self, default_date: str, parent=None):
        """
        Initialize add event dialog.
        
        Args:
            default_date: Default date for new event
            parent: Parent widget
        """
        super().__init__(parent)
        self._default_date = default_date
        self.setWindowTitle("Add New Event")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize dialog UI."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-size: 20px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus {
                border: 1px solid #4ECDC4;
            }
            QDateEdit::drop-down {
                border: none;
                background-color: #4ECDC4;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
                margin-right: 5px;
            }
            QPushButton {
                background-color: #4ECDC4;
                color: #000000;
                border: none;
                padding: 8px 18px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6FE4DB;
            }
        """)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Clinic, Reply Emails")
        form.addRow("Event Title:", self.title_input)
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        try:
            y, m, d = map(int, self._default_date.split('-'))
            self.date_input.setDate(QDate(y, m, d))
        except:
            self.date_input.setDate(QDate.currentDate())
        form.addRow("Event Date:", self.date_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(200)
        form.addRow("Description:", self.description_input)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(button_box)
    
    def _validate_and_accept(self) -> None:
        """Validate input and accept dialog."""
        if not self.title_input.text().strip():
            return
        self.accept()
    
    def get_event_data(self) -> dict:
        """
        Get entered event data.
        
        Returns:
            Dictionary with title, event_date, description
        """
        return {
            'title': self.title_input.text().strip(),
            'event_date': self.date_input.date().toString(Qt.DateFormat.ISODate),
            'description': self.description_input.toPlainText().strip() or None
        }
