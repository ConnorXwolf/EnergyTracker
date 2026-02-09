"""
Application-wide configuration constants and color schemes.

This module defines exercise categories, color palettes, and system-wide
constants used throughout the Energy Tracker application.
"""

from typing import Dict, List, Any

# Application metadata
APP_NAME: str = "Energy Tracker"
APP_VERSION: str = "1.0.0"
DATABASE_NAME: str = "energy_tracker.db"

# Exercise category definitions with associated colors
EXERCISE_CATEGORIES: Dict[str, Dict[str, Any]] = {
    'physical': {
        'color': '#FFD93D',  # Yellow
        'color_bright': '#FFE066',
        'text_color': '#000000',
        'examples': ['拉筋', 'Running', 'Yoga', 'Walking']
    },
    'mental': {
        'color': '#4A90E2',  # Blue
        'color_bright': '#6BA3E8',
        'text_color': '#FFFFFF',
        'examples': ['Meditation', 'Reading', 'Journaling', 'Planning']
    },
    'sleepiness': {
        'color': '#FF6B6B',  # Red
        'color_bright': '#FF8E8E',
        'text_color': '#FFFFFF',
        'examples': ['Sleep Quality', 'Nap', 'Rest', 'Recovery']
    }
}

# Measurement units
VALID_UNITS: List[str] = ['reps', 'sets', 'minutes', 'km', 'hours']

# UI color scheme (dark theme)
UI_COLORS: Dict[str, str] = {
    'background_main': '#1E1E1E',
    'background_widget': '#2D2D2D',
    'text_primary': '#FFFFFF',
    'text_secondary': '#AAAAAA',
    'border': '#555555',
    'progress_bg': '#3D3D3D',
    'success': '#4CAF50',
    'warning': '#FFC107',
    'error': '#F44336'
}

# Widget dimensions
WIDGET_DIMENSIONS: Dict[str, int] = {
    'ring_chart_size': 400,
    'calendar_width': 400,
    'calendar_height': 400,
    'progress_bar_height': 20,
    'progress_bar_width': 300,
    'window_width': 1200,
    'window_height': 800
}

# Default exercises for new installations
DEFAULT_EXERCISES: List[Dict[str, Any]] = [
    {
        'name': '拉筋',
        'category': 'physical',
        'target_value': 30,
        'unit': 'minutes'
    }
]


def get_category_color(category: str, over_achieved: bool = False) -> str:
    """
    Retrieve color for exercise category.
    
    Args:
        category: Exercise category ('cardio', 'strength', 'flexibility')
        over_achieved: Whether to return brighter color for over-achievement
        
    Returns:
        Hex color code string
        
    Raises:
        KeyError: If category is invalid
    """
    try:
        color_key = 'color_bright' if over_achieved else 'color'
        return EXERCISE_CATEGORIES[category][color_key]
    except KeyError as e:
        raise KeyError(f"Invalid category: {category}") from e


def get_text_color(category: str) -> str:
    """
    Retrieve text color for category (ensures readability).
    
    Args:
        category: Exercise category name
        
    Returns:
        Hex color code for text overlay
        
    Raises:
        KeyError: If category is invalid
    """
    try:
        return EXERCISE_CATEGORIES[category]['text_color']
    except KeyError as e:
        raise KeyError(f"Invalid category: {category}") from e


def validate_unit(unit: str) -> bool:
    """
    Check if measurement unit is valid.
    
    Args:
        unit: Unit string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return unit in VALID_UNITS
