"""
Calendar widget with event integration.

Displays monthly calendar with highlighted dates containing events
and shows event list for selected dates.
"""

from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget,
    QListWidget, QListWidgetItem, QLabel,
    QPushButton, QHBoxLayout, QDialog,
    QLineEdit, QTextEdit, QDialogButtonBox,
    QFormLayout, QDateEdit, QMessageBox  # Added QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize # Added QSize
from PyQt6.QtGui import QTextCharFormat, QColor, QFont

from managers import EventManager
from models import CalendarEvent
from utils import get_today


class CalendarWidget(QWidget):
    """
    Calendar widget with event display.
    
    Shows monthly calendar with date highlighting for events
    and displays event list for selected date.
    """
    
    date_selected = pyqtSignal(str)  # Emits ISO date
    
    def __init__(self, event_manager: EventManager, parent=None):
        """
        Initialize calendar widget.
        """
        super().__init__(parent)
        
        self._event_manager = event_manager
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
        self.calendar.setMinimumSize(500, 350)
        self.calendar.setMaximumWidth(550)
        
        # Right side: Event list section
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        
        list_header = QLabel("Events for selected date:")
        list_header_font = QFont()
        list_header_font.setBold(True)
        list_header.setFont(list_header_font)
        
        self.event_list = QListWidget()
        self.event_list.setMinimumWidth(250)
        self.event_list.setMaximumWidth(300)
        
        # Add event button
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.setMaximumWidth(150)
        
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
    
    def _load_events(self) -> None:
        """Load events for current month and update calendar highlighting."""
        try:
            events = self._event_manager.get_events_for_month(
                self._current_year,
                self._current_month
            )
            self._clear_highlights()
            event_dates = set(event.event_date for event in events)
            for date_str in event_dates:
                self._highlight_date(date_str)
            self._update_event_list()
        except Exception as e:
            print(f"Error loading events: {e}")
    
    def _clear_highlights(self) -> None:
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
    
    def _highlight_date(self, date_str: str) -> None:
        try:
            year, month, day = map(int, date_str.split('-'))
            date = QDate(year, month, day)
            if not date.isValid(): return
            
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor('#4ECDC4'))
            highlight_format.setForeground(QColor('#000000'))
            highlight_format.setFontWeight(QFont.Weight.Bold)
            self.calendar.setDateTextFormat(date, highlight_format)
        except Exception as e:
            print(f"Error highlighting date: {e}")
    
    def _on_date_selected(self) -> None:
        self._update_event_list()
        self.date_selected.emit(self.calendar.selectedDate().toString(Qt.DateFormat.ISODate))
    
    def _on_month_changed(self, year: int, month: int) -> None:
        self._current_year, self._current_month = year, month
        self._load_events()

    # --- UPDATED METHOD ---
    def _update_event_list(self) -> None:
        """Update event list for currently selected date with delete buttons."""
        try:
            selected_date = self.calendar.selectedDate()
            date_str = selected_date.toString(Qt.DateFormat.ISODate)
            
            events = self._event_manager.get_events_for_date(date_str)
            self.event_list.clear()
            
            if not events:
                empty_item = QListWidgetItem("No events for this date")
                self.event_list.addItem(empty_item)
                return
            
            # Add events to list with delete buttons
            for event in events:
                self._add_event_item(event)
            
        except Exception as e:
            print(f"Error updating event list: {e}")
    
    def _on_add_event(self) -> None:
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString(Qt.DateFormat.ISODate)
        dialog = AddEventDialog(date_str, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_event_data()
            self._event_manager.create_event(**data)
    
    def _on_event_created(self, date_str: str) -> None:
        try:
            year, month, _ = map(int, date_str.split('-'))
            if year == self._current_year and month == self._current_month:
                self._load_events()
        except:
            pass

    # --- NEW METHODS ADDED HERE ---
    def _add_event_item(self, event: CalendarEvent) -> None:
        """Add event item with delete button to list."""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        event_text_layout = QVBoxLayout()
        title_label = QLabel(f"• {event.title}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        event_text_layout.addWidget(title_label)
        
        if event.description:
            desc_label = QLabel(f"  {event.description}")
            desc_label.setStyleSheet("color: #AAAAAA; font-size: 10px;")
            desc_label.setWordWrap(True)
            event_text_layout.addWidget(desc_label)
        
        delete_button = QPushButton("🗑")
        delete_button.setFixedSize(35, 35)
        delete_button.setStyleSheet("""
            QPushButton {
                font-size: 16px; background-color: #F44336; color: white;
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


class AddEventDialog(QDialog):
    # (AddTaskDialog logic remains unchanged as provided in calendar_widget.py)
    def __init__(self, default_date: str, parent=None):
        super().__init__(parent)
        self._default_date = default_date
        self.setWindowTitle("Add New Event")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., 明天要交的作業, 回覆訊息")
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
        self.description_input.setMaximumHeight(100)
        form.addRow("Description:", self.description_input)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addLayout(form)
        layout.addWidget(button_box)
    
    def _validate_and_accept(self) -> None:
        if not self.title_input.text().strip(): return
        self.accept()
    
    def get_event_data(self) -> dict:
        return {
            'title': self.title_input.text().strip(),
            'event_date': self.date_input.date().toString(Qt.DateFormat.ISODate),
            'description': self.description_input.toPlainText().strip() or None
        }
