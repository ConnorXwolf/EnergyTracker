"""
Calendar event data model.

Defines the Pydantic model for calendar events with date validation
and display formatting.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CalendarEvent(BaseModel):
    """
    Calendar event model.
    
    Represents a single event in the calendar system with date,
    title, and optional description.
    
    Attributes:
        id: Unique identifier (0 for unsaved events)
        title: Event title/summary
        event_date: Event date in ISO format (YYYY-MM-DD)
        description: Optional detailed description
    """
    id: int = Field(default=0, ge=0)
    title: str = Field(min_length=1, max_length=200)
    event_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    description: Optional[str] = Field(default=None, max_length=1000)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        """
        Ensure event title is not just whitespace.
        
        Args:
            value: Event title to validate
            
        Returns:
            Trimmed event title
            
        Raises:
            ValueError: If title is empty after trimming
        """
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Event title cannot be empty or whitespace")
        return trimmed
    
    @field_validator('event_date')
    @classmethod
    def validate_event_date(cls, value: str) -> str:
        """
        Validate event date format.
        
        Args:
            value: Date string to validate
            
        Returns:
            Validated date string
            
        Raises:
            ValueError: If date format is invalid
        """
        from datetime import datetime
        try:
            datetime.fromisoformat(value)
            return value
        except ValueError as e:
            raise ValueError(
                f"Invalid event date format: {value}. Expected YYYY-MM-DD"
            ) from e
    
    def format_display_date(self) -> str:
        """
        Format event date for display.
        
        Returns:
            Human-readable date string (e.g., "February 09, 2026")
        """
        from datetime import datetime
        try:
            date_obj = datetime.fromisoformat(self.event_date)
            return date_obj.strftime("%B %d, %Y")
        except ValueError:
            return self.event_date
    
    def is_past_event(self, current_date: str) -> bool:
        """
        Check if event is in the past.
        
        Args:
            current_date: Current date in ISO format
            
        Returns:
            True if event date is before current date
        """
        from datetime import datetime
        try:
            event = datetime.fromisoformat(self.event_date).date()
            current = datetime.fromisoformat(current_date).date()
            return event < current
        except ValueError:
            return False
    
    def is_today(self, current_date: str) -> bool:
        """
        Check if event is today.
        
        Args:
            current_date: Current date in ISO format
            
        Returns:
            True if event date matches current date
        """
        return self.event_date == current_date
    
    def is_upcoming(self, current_date: str, days_ahead: int = 7) -> bool:
        """
        Check if event is upcoming within specified days.
        
        Args:
            current_date: Current date in ISO format
            days_ahead: Number of days to look ahead
            
        Returns:
            True if event is within the specified future window
        """
        from datetime import datetime, timedelta
        try:
            event = datetime.fromisoformat(self.event_date).date()
            current = datetime.fromisoformat(current_date).date()
            future_limit = current + timedelta(days=days_ahead)
            return current <= event <= future_limit
        except ValueError:
            return False


class EventSummary(BaseModel):
    """
    Aggregated event statistics for a date range.
    
    Attributes:
        total_events: Total number of events in range
        past_events: Number of past events
        today_events: Number of events today
        upcoming_events: Number of upcoming events
        date_range_start: Range start date
        date_range_end: Range end date
    """
    total_events: int = Field(ge=0)
    past_events: int = Field(ge=0)
    today_events: int = Field(ge=0)
    upcoming_events: int = Field(ge=0)
    date_range_start: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    date_range_end: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    
    @field_validator('date_range_start', 'date_range_end')
    @classmethod
    def validate_date_range(cls, value: str) -> str:
        """Validate date format for range boundaries."""
        from datetime import datetime
        try:
            datetime.fromisoformat(value)
            return value
        except ValueError as e:
            raise ValueError(f"Invalid date format: {value}") from e
