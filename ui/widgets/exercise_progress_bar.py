"""
Custom progress bar widget for exercise tracking.

Provides category-colored progress bars with actual/target display
and over-achievement indication.
"""

from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from models import ExerciseLog


class ExerciseProgressBar(QProgressBar):
    """
    Custom progress bar for exercise visualization.
    
    Features:
        - Category-based coloring
        - Over-achievement visual indication (brighter color)
        - Custom text format showing actual/target values
        - Percentage display
    """
    
    def __init__(self, exercise_log: ExerciseLog, color: str, parent=None):
        """
        Initialize progress bar with exercise data.
        
        Args:
            exercise_log: ExerciseLog model with progress data
            color: Base hex color for category
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._log = exercise_log
        self._base_color = color
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure progress bar appearance and behavior."""
        # Set range (always percentage)
        self.setMinimum(0)
        self.setMaximum(100)
        
        # Set current value (capped at 100 for display)
        self.setValue(int(self._log.display_percentage))
        
        # Enable text display
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set custom format text
        self.setFormat(self._log.format_progress_text())
        
        # Apply styling based on achievement status
        self._apply_style()
        
        # Set fixed height for consistency
        self.setFixedHeight(20)
        self.setMinimumWidth(300)
    
    def _apply_style(self) -> None:
        """Apply  green styling for all progress bars."""
        # Always use e green color
        fill_color = "#178117"  #  green
        
        if self._log.actual_value == 0:
            fill_color = '#555555'  # Gray for zero progress
        
        # Determine text color (ensure readability)
        text_color = '#FFFFFF'
        
        # Build stylesheet (14px font)
        stylesheet = f"""
            QProgressBar {{
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3D3D3D;
                text-align: center;
                color: {text_color};
                font-size: 14px;
                font-weight: bold;
                padding: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {fill_color};
                border-radius: 2px;
            }}
        """
        
        self.setStyleSheet(stylesheet)
    
    def _brighten_color(self, hex_color: str, factor: float = 1.3) -> str:
        """
        Brighten hex color for over-achievement indication.
        
        Args:
            hex_color: Base color in hex format (#RRGGBB)
            factor: Brightness multiplier (>1.0 brightens)
            
        Returns:
            Brightened hex color string
        """
        try:
            # Parse hex color
            color = QColor(hex_color)
            
            # Get HSV components
            h, s, v, a = color.getHsvF()
            
            # Increase value (brightness) and decrease saturation slightly
            v = min(1.0, v * factor)
            s = max(0.0, s * 0.9)
            
            # Create new color
            bright_color = QColor.fromHsvF(h, s, v, a)
            
            return bright_color.name()
            
        except Exception as e:
            print(f"Error brightening color: {e}")
            return hex_color
    
    def update_progress(self, exercise_log: ExerciseLog) -> None:
        """
        Update progress bar with new log data.
        
        Args:
            exercise_log: Updated ExerciseLog model
        """
        self._log = exercise_log
        
        # Update value and text
        self.setValue(int(exercise_log.display_percentage))
        self.setFormat(exercise_log.format_progress_text())
        
        # Reapply styling (color may change with over-achievement)
        self._apply_style()
