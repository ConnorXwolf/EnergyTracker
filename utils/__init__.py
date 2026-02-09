"""
Utility modules package.

Provides configuration constants, date helpers, settings management,
and other utility functions.
"""

from .config import (
    APP_NAME,
    APP_VERSION,
    DATABASE_NAME,
    EXERCISE_CATEGORIES,
    VALID_UNITS,
    UI_COLORS,
    WIDGET_DIMENSIONS,
    DEFAULT_EXERCISES,
    get_category_color,
    get_text_color,
    validate_unit
)

from .date_helpers import (
    get_today,
    format_date_display,
    get_date_range,
    get_week_dates,
    get_month_dates,
    days_between,
    is_today,
    get_yesterday,
    get_tomorrow
)

from .settings_manager import SettingsManager

from .report_generator import ReportGenerator

__all__ = [
    # Config exports
    'APP_NAME',
    'APP_VERSION',
    'DATABASE_NAME',
    'EXERCISE_CATEGORIES',
    'VALID_UNITS',
    'UI_COLORS',
    'WIDGET_DIMENSIONS',
    'DEFAULT_EXERCISES',
    'get_category_color',
    'get_text_color',
    'validate_unit',
    # Date helper exports
    'get_today',
    'format_date_display',
    'get_date_range',
    'get_week_dates',
    'get_month_dates',
    'days_between',
    'is_today',
    'get_yesterday',
    'get_tomorrow',
    # Settings manager
    'SettingsManager',
    # Report generator
    'ReportGenerator'
]