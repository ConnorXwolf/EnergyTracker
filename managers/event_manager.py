"""
Calendar event business logic manager.

Handles event CRUD operations and provides date-based queries
for calendar widget integration.
"""

from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from database import DatabaseManager
from models import CalendarEvent, EventSummary
from utils import get_today


class EventManager(QObject):
    """
    Business logic manager for calendar events.
    
    Manages event definitions, date-based queries, and provides
    statistics for calendar visualization.
    
    Signals:
        data_changed: Emitted when event data is modified
        event_created: Emitted with date when new event is created
    """
    
    data_changed = pyqtSignal()
    event_created = pyqtSignal(str)  # Emits event date
    
    def __init__(self):
        """Initialize manager with database connection."""
        super().__init__()
        self._db = DatabaseManager()
    
    # ==================== Event CRUD Operations ====================
    
    def create_event(
        self,
        title: str,
        event_date: str,
        description: Optional[str] = None
    ) -> Optional[int]:
        """
        Create new calendar event.
        
        Args:
            title: Event title
            event_date: Date in ISO format (YYYY-MM-DD)
            description: Optional detailed description
            
        Returns:
            Event ID if created, None if failed
        """
        try:
            event = CalendarEvent(
                title=title,
                event_date=event_date,
                description=description
            )
            
            event_id = self._db.create_event(event)
            
            self.data_changed.emit()
            self.event_created.emit(event_date)
            
            return event_id
            
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def get_events_for_date(self, date: str) -> List[CalendarEvent]:
        """
        Retrieve events for specific date.
        
        Args:
            date: Date in ISO format
            
        Returns:
            List of CalendarEvent models for the date
        """
        try:
            return self._db.get_events_by_date(date)
        except Exception as e:
            print(f"Error retrieving events for {date}: {e}")
            return []
    
    def get_events_for_month(self, year: int, month: int) -> List[CalendarEvent]:
        """
        Retrieve all events in a month.
        
        Args:
            year: Year (e.g., 2026)
            month: Month (1-12)
            
        Returns:
            List of CalendarEvent models in the month
        """
        try:
            return self._db.get_events_by_month(year, month)
        except Exception as e:
            print(f"Error retrieving events for {year}-{month:02d}: {e}")
            return []
    
    def get_today_events(self) -> List[CalendarEvent]:
        """
        Retrieve events for today.
        
        Returns:
            List of CalendarEvent models for current date
        """
        return self.get_events_for_date(get_today())
    
    def update_event(
        self,
        event_id: int,
        title: Optional[str] = None,
        event_date: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Update existing event with partial updates.
        
        Args:
            event_id: Event to update
            title: New title (if provided)
            event_date: New date (if provided)
            description: New description (if provided)
            
        Returns:
            True if updated successfully
        """
        try:
            # Retrieve existing event
            existing_event = None
            all_events = self._db.get_events_by_date("")  # Get all events hack
            
            # Find event by iterating through months (inefficient but works)
            from datetime import datetime
            current_date = datetime.now()
            for month_offset in range(-12, 13):
                year = current_date.year
                month = current_date.month + month_offset
                
                # Adjust year and month
                while month > 12:
                    month -= 12
                    year += 1
                while month < 1:
                    month += 12
                    year -= 1
                
                events = self._db.get_events_by_month(year, month)
                for event in events:
                    if event.id == event_id:
                        existing_event = event
                        break
                
                if existing_event:
                    break
            
            if not existing_event:
                return False
            
            # Apply updates
            updated_event = CalendarEvent(
                id=event_id,
                title=title if title is not None else existing_event.title,
                event_date=event_date if event_date is not None else existing_event.event_date,
                description=description if description is not None else existing_event.description
            )
            
            success = self._db.update_event(updated_event)
            
            if success:
                self.data_changed.emit()
            
            return success
            
        except Exception as e:
            print(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: int) -> bool:
        """
        Delete event by ID.
        
        Args:
            event_id: Event to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            success = self._db.delete_event(event_id)
            
            if success:
                self.data_changed.emit()
            
            return success
            
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    # ==================== Statistics & Queries ====================
    
    def get_dates_with_events(self, year: int, month: int) -> List[str]:
        """
        Get list of dates that have events in a month.
        
        Useful for highlighting dates in calendar widget.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            List of ISO date strings that have events
        """
        try:
            events = self._db.get_events_by_month(year, month)
            # Get unique dates
            dates = list(set(event.event_date for event in events))
            return sorted(dates)
        except Exception as e:
            print(f"Error getting event dates: {e}")
            return []
    
    def get_event_count_for_date(self, date: str) -> int:
        """
        Count events on specific date.
        
        Args:
            date: Date in ISO format
            
        Returns:
            Number of events on the date
        """
        try:
            events = self._db.get_events_by_date(date)
            return len(events)
        except Exception as e:
            print(f"Error counting events: {e}")
            return 0
    
    def get_upcoming_events(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """
        Retrieve events in the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming CalendarEvent models
        """
        try:
            from datetime import datetime, timedelta
            
            today = get_today()
            events = []
            
            # Get events for next N days
            for i in range(days_ahead):
                date = (datetime.fromisoformat(today) + timedelta(days=i)).date().isoformat()
                day_events = self._db.get_events_by_date(date)
                events.extend(day_events)
            
            return events
            
        except Exception as e:
            print(f"Error retrieving upcoming events: {e}")
            return []
    
    def get_past_events(self, days_back: int = 7) -> List[CalendarEvent]:
        """
        Retrieve events from the past N days.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of past CalendarEvent models
        """
        try:
            from datetime import datetime, timedelta
            
            today = get_today()
            events = []
            
            # Get events for past N days (excluding today)
            for i in range(1, days_back + 1):
                date = (datetime.fromisoformat(today) - timedelta(days=i)).date().isoformat()
                day_events = self._db.get_events_by_date(date)
                events.extend(day_events)
            
            return events
            
        except Exception as e:
            print(f"Error retrieving past events: {e}")
            return []
    
    def get_month_summary(self, year: int, month: int) -> EventSummary:
        """
        Calculate summary statistics for a month.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            EventSummary with aggregated metrics
        """
        try:
            from datetime import date
            
            events = self._db.get_events_by_month(year, month)
            today = get_today()
            
            total = len(events)
            past = sum(1 for e in events if e.is_past_event(today))
            today_count = sum(1 for e in events if e.is_today(today))
            upcoming = sum(1 for e in events if e.is_upcoming(today))
            
            # Calculate date range for the month
            first_day = date(year, month, 1).isoformat()
            if month == 12:
                last_day = date(year, 12, 31).isoformat()
            else:
                last_day = (date(year, month + 1, 1) - timedelta(days=1)).isoformat()
            
            return EventSummary(
                total_events=total,
                past_events=past,
                today_events=today_count,
                upcoming_events=upcoming,
                date_range_start=first_day,
                date_range_end=last_day
            )
            
        except Exception as e:
            print(f"Error calculating month summary: {e}")
            from datetime import timedelta, date
            first_day = date(year, month, 1).isoformat()
            return EventSummary(
                total_events=0,
                past_events=0,
                today_events=0,
                upcoming_events=0,
                date_range_start=first_day,
                date_range_end=first_day
            )
    
    def search_events(self, keyword: str) -> List[CalendarEvent]:
        """
        Search events by title keyword.
        
        Args:
            keyword: Search term
            
        Returns:
            List of CalendarEvent models matching keyword
        """
        try:
            # Simple implementation: get events from current year
            from datetime import datetime
            current_year = datetime.now().year
            
            all_events = []
            for month in range(1, 13):
                events = self._db.get_events_by_month(current_year, month)
                all_events.extend(events)
            
            # Filter by keyword (case-insensitive)
            keyword_lower = keyword.lower()
            matching = [
                event for event in all_events
                if keyword_lower in event.title.lower() or
                   (event.description and keyword_lower in event.description.lower())
            ]
            
            return matching
            
        except Exception as e:
            print(f"Error searching events: {e}")
            return []
