"""
Date and time utility functions.

Provides helper functions for date calculations, formatting, and
calendar-related operations used throughout the application.
"""

from datetime import datetime, date, timedelta
from typing import List, Tuple


def get_today() -> str:
    """
    Get current date in ISO format.
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    return date.today().isoformat()


def format_date_display(date_str: str) -> str:
    """
    Convert ISO date to human-readable format.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        Formatted date string (e.g., "February 09, 2026")
        
    Raises:
        ValueError: If date string is malformed
    """
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%B %d, %Y")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}") from e


def get_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Generate list of dates between start and end (inclusive).
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of ISO date strings
        
    Raises:
        ValueError: If date strings are malformed or end < start
    """
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        if end < start:
            raise ValueError("End date must be after start date")
        
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.isoformat())
            current += timedelta(days=1)
        
        return date_list
    except ValueError as e:
        raise ValueError(f"Invalid date range: {start_date} to {end_date}") from e


def get_week_dates(reference_date: str) -> List[str]:
    """
    Get all dates in the week containing reference date.
    
    Args:
        reference_date: Any date in YYYY-MM-DD format
        
    Returns:
        List of 7 ISO date strings (Monday to Sunday)
        
    Raises:
        ValueError: If date string is malformed
    """
    try:
        ref = datetime.fromisoformat(reference_date).date()
        # Calculate Monday of the week (0 = Monday, 6 = Sunday)
        monday = ref - timedelta(days=ref.weekday())
        
        return [
            (monday + timedelta(days=i)).isoformat()
            for i in range(7)
        ]
    except ValueError as e:
        raise ValueError(f"Invalid reference date: {reference_date}") from e


def get_month_dates(year: int, month: int) -> List[Tuple[str, bool]]:
    """
    Get all dates in a month with indication of current month membership.
    
    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
        
    Returns:
        List of tuples (date_string, is_in_current_month)
        Includes padding days from previous/next months for calendar grid
        
    Raises:
        ValueError: If month is invalid
    """
    if not 1 <= month <= 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12")
    
    try:
        # First day of the month
        first_day = date(year, month, 1)
        
        # Last day of the month
        if month == 12:
            last_day = date(year, 12, 31)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        dates = []
        
        # Add padding days from previous month
        start_weekday = first_day.weekday()  # 0 = Monday
        if start_weekday > 0:
            for i in range(start_weekday, 0, -1):
                padding_date = first_day - timedelta(days=i)
                dates.append((padding_date.isoformat(), False))
        
        # Add days of current month
        current = first_day
        while current <= last_day:
            dates.append((current.isoformat(), True))
            current += timedelta(days=1)
        
        # Add padding days from next month
        end_weekday = last_day.weekday()  # 0 = Monday
        if end_weekday < 6:
            for i in range(1, 7 - end_weekday):
                padding_date = last_day + timedelta(days=i)
                dates.append((padding_date.isoformat(), False))
        
        return dates
    except ValueError as e:
        raise ValueError(f"Invalid year/month combination: {year}-{month}") from e


def days_between(date1: str, date2: str) -> int:
    """
    Calculate number of days between two dates.
    
    Args:
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format
        
    Returns:
        Absolute number of days between dates
        
    Raises:
        ValueError: If date strings are malformed
    """
    try:
        d1 = datetime.fromisoformat(date1).date()
        d2 = datetime.fromisoformat(date2).date()
        return abs((d2 - d1).days)
    except ValueError as e:
        raise ValueError(f"Invalid date format in comparison") from e


def is_today(date_str: str) -> bool:
    """
    Check if date is today.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        True if date is today, False otherwise
    """
    try:
        return date_str == get_today()
    except Exception:
        return False


def get_yesterday() -> str:
    """
    Get yesterday's date in ISO format.
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    yesterday = date.today() - timedelta(days=1)
    return yesterday.isoformat()


def get_tomorrow() -> str:
    """
    Get tomorrow's date in ISO format.
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    tomorrow = date.today() + timedelta(days=1)
    return tomorrow.isoformat()
