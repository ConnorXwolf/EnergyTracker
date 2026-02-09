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
    QFormLayout, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
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
        
        Args:
            event_manager: Manager for event operations
            parent: Parent widget
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
        # Main horizontal layout (calendar + spacer + event list)
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
        
        # Assemble main layout (calendar + stretch + event list on far right)
        main_layout.addWidget(self.calendar)
        main_layout.addStretch()  # Push event list to the right
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
            # Get events for current month
            events = self._event_manager.get_events_for_month(
                self._current_year,
                self._current_month
            )
            
            # Clear existing highlights
            self._clear_highlights()
            
            # Highlight dates with events
            event_dates = set(event.event_date for event in events)
            for date_str in event_dates:
                self._highlight_date(date_str)
            
            # Refresh event list for selected date
            self._update_event_list()
            
        except Exception as e:
            print(f"Error loading events: {e}")
    
    def _clear_highlights(self) -> None:
        """Remove all date highlights from calendar."""
        # Reset all dates to default format
        default_format = QTextCharFormat()
        
        # Get first and last day of visible month
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        
        # Clear all days in month
        for day in range(1, 32):
            try:
                date = QDate(year, month, day)
                if date.isValid():
                    self.calendar.setDateTextFormat(date, default_format)
            except:
                break
    
    def _highlight_date(self, date_str: str) -> None:
        """
        Highlight specific date in calendar.
        
        Args:
            date_str: Date in ISO format to highlight
        """
        try:
            # Parse ISO date
            year, month, day = map(int, date_str.split('-'))
            date = QDate(year, month, day)
            
            if not date.isValid():
                return
            
            # Create highlight format
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor('#4ECDC4'))
            highlight_format.setForeground(QColor('#000000'))
            highlight_format.setFontWeight(QFont.Weight.Bold)
            
            self.calendar.setDateTextFormat(date, highlight_format)
            
        except Exception as e:
            print(f"Error highlighting date {date_str}: {e}")
    
    def _on_date_selected(self) -> None:
        """Handle calendar date selection change."""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString(Qt.DateFormat.ISODate)
        
        self._update_event_list()
        self.date_selected.emit(date_str)
    
    def _on_month_changed(self, year: int, month: int) -> None:
        """
        Handle calendar month change.
        
        Args:
            year: New year
            month: New month
        """
        self._current_year = year
        self._current_month = month
        self._load_events()
    
    def _update_event_list(self) -> None:
        """Update event list for currently selected date."""
        try:
            selected_date = self.calendar.selectedDate()
            date_str = selected_date.toString(Qt.DateFormat.ISODate)
            
            # Get events for date
            events = self._event_manager.get_events_for_date(date_str)
            
            # Clear list
            self.event_list.clear()
            
            if not events:
                empty_item = QListWidgetItem("No events for this date")
                self.event_list.addItem(empty_item)
                return
            
            # Add events to list
            for event in events:
                item_text = f"• {event.title}"
                if event.description:
                    item_text += f"\n  {event.description}"
                
                item = QListWidgetItem(item_text)
                self.event_list.addItem(item)
            
        except Exception as e:
            print(f"Error updating event list: {e}")
    
    def _on_add_event(self) -> None:
        """Handle add event button click."""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString(Qt.DateFormat.ISODate)
        
        dialog = AddEventDialog(date_str, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_event_data()
            
            self._event_manager.create_event(
                title=data['title'],
                event_date=data['event_date'],
                description=data.get('description')
            )
    
    def _on_event_created(self, date_str: str) -> None:
        """
        Handle event creation signal.
        
        Args:
            date_str: Date of created event
        """
        # If event was created for currently visible month, reload
        try:
            year, month, _ = map(int, date_str.split('-'))
            if year == self._current_year and month == self._current_month:
                self._load_events()
        except:
            pass


class AddEventDialog(QDialog):
    """
    Dialog for creating new calendar events.
    
    Allows user to specify event title, date, and description.
    """
    
    def __init__(self, default_date: str, parent=None):
        """
        Initialize add event dialog.
        
        Args:
            default_date: Pre-filled date in ISO format
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._default_date = default_date
        
        self.setWindowTitle("Add New Event")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., 明天要交的作業, 回覆訊息")
        form.addRow("Event Title:", self.title_input)
        
        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        
        # Parse default date
        try:
            year, month, day = map(int, self._default_date.split('-'))
            self.date_input.setDate(QDate(year, month, day))
        except:
            self.date_input.setDate(QDate.currentDate())
        
        form.addRow("Event Date:", self.date_input)
        
        # Description input
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Optional description...")
        form.addRow("Description:", self.description_input)
        
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
