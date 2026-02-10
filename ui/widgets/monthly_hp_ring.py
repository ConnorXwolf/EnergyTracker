"""
Monthly HP Ring Chart Widget.

Displays 31-day circular visualization with color-coded HP segments.
Supports mouse interaction for day selection.
"""

from typing import Dict, Optional
import math

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath

from models.hp_data import HPData


class MonthlyHPRingWidget(QWidget):
    """
    Circular ring chart displaying 31 days of HP data.
    
    Each day is represented as an arc segment colored by HP value.
    Clicking a segment emits the day number for detail display.
    
    Signals:
        day_selected: Emitted with day number (1-31) when clicked
    """
    
    day_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """
        Initialize ring chart widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._hp_data: Dict[int, HPData] = {}
        self._selected_day: Optional[int] = None
        self._days_in_month: int = 31  # Default to 31, will be updated
        
        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)
    
    def set_hp_data(
        self,
        hp_data: Dict[int, HPData],
        days_in_month: int
    ) -> None:
        """
        Update HP data for display.
        
        Args:
            hp_data: Dictionary mapping day number to HPData
            days_in_month: Number of days in current month (28-31)
        """
        self._hp_data = hp_data
        self._days_in_month = days_in_month
        self._selected_day = None
        self.update()
    
    def set_selected_day(self, day: Optional[int]) -> None:
        """
        Highlight specific day segment.
        
        Args:
            day: Day number to highlight (None to clear)
        """
        self._selected_day = day
        self.update()
    
    def paintEvent(self, event) -> None:
        """
        Render the ring chart.
        
        Args:
            event: QPaintEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        center_x = width / 2
        center_y = height / 2
        
        outer_radius = size / 2 - 30
        inner_radius = outer_radius - 60
        
        # Draw segments
        self._draw_segments(
            painter,
            center_x,
            center_y,
            outer_radius,
            inner_radius
        )
        
        # Draw day numbers
        self._draw_day_numbers(
            painter,
            center_x,
            center_y,
            outer_radius + 15
        )
    
    def _draw_segments(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float
    ) -> None:
        """
        Draw colored arc segments for each day.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
        """
        segment_angle = 360.0 / self._days_in_month
        start_angle = 90  # Start from top (12 o'clock)
        
        painter.setPen(Qt.PenStyle.NoPen)
        
        for day in range(1, self._days_in_month + 1):
            # Get HP data for this day
            hp_data = self._hp_data.get(day, None)
            color = self._get_color_for_hp(hp_data)
            
            # Highlight selected day
            if day == self._selected_day:
                painter.setPen(QPen(QColor('#FFFFFF'), 3))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
            
            painter.setBrush(QBrush(QColor(color)))
            
            # Draw segment using pie chart technique
            outer_rect = QRectF(
                center_x - outer_radius,
                center_y - outer_radius,
                outer_radius * 2,
                outer_radius * 2
            )
            
            # Qt uses 1/16th degree units, clockwise from 3 o'clock
            qt_start = int((start_angle - (day - 1) * segment_angle) * 16)
            qt_span = int(-segment_angle * 16)
            
            painter.drawPie(outer_rect, qt_start, qt_span)
            
            # Erase inner circle to create ring
            painter.setBrush(QBrush(QColor('#2D2D2D')))
            painter.setPen(Qt.PenStyle.NoPen)
            inner_rect = QRectF(
                center_x - inner_radius,
                center_y - inner_radius,
                inner_radius * 2,
                inner_radius * 2
            )
            painter.drawEllipse(inner_rect)
    
    def _draw_day_numbers(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        text_radius: float
    ) -> None:
        """
        Draw day numbers around the ring.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            text_radius: Radius for text placement
        """
        segment_angle = 360.0 / self._days_in_month
        
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor('#FFFFFF'))
        
        for day in range(1, self._days_in_month + 1):
            angle_deg = 90 - (day - 1) * segment_angle
            angle_rad = math.radians(angle_deg)
            
            x = center_x + text_radius * math.cos(angle_rad)
            y = center_y - text_radius * math.sin(angle_rad)
            
            # Draw text centered at position
            text = str(day)
            text_rect = QRectF(x - 15, y - 10, 30, 20)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter,
                text
            )
    
    def _get_color_for_hp(self, hp_data: Optional[HPData]) -> str:
        """
        Determine segment color based on HP value.
        
        Args:
            hp_data: HP data for the day (None if no data)
            
        Returns:
            Hex color code string
        """
        if hp_data is None:
            return '#FF6B6B'  # Red (None)
        
        hp = hp_data.hp
        
        if hp < 33:
            return '#FF6B6B'  # Red (None/Very Poor)
        elif 33 <= hp < 44:
            return '#FFA500'  # Orange (Very Low)
        elif 44 <= hp < 55:
            return '#FFD93D'  # Yellow (Low)
        elif 55 <= hp < 66:
            return '#C8E6C9'  # Light Green (Moderate)
        elif 66 <= hp < 77:
            return '#81C784'  # Green (High)
        elif 77 <= hp < 88:
            return '#4CAF50'  # High Green (Very High)
        else:  # 88-100
            return '#2E7D32'  # Dark Green (Maximum)
    
    def mousePressEvent(self, event) -> None:
        """
        Handle mouse click to select day segment.
        
        Args:
            event: QMouseEvent
        """
        try:
            # Calculate dimensions
            width = self.width()
            height = self.height()
            size = min(width, height)
            
            center_x = width / 2
            center_y = height / 2
            
            outer_radius = size / 2 - 30
            inner_radius = outer_radius - 60
            
            # Get click position relative to center
            click_x = event.position().x() - center_x
            click_y = center_y - event.position().y()  # Invert Y
            
            # Check if click is within ring
            distance = math.sqrt(click_x**2 + click_y**2)
            if distance < inner_radius or distance > outer_radius:
                return
            
            # Calculate angle (in degrees, 0° = right, counter-clockwise)
            angle_rad = math.atan2(click_y, click_x)
            angle_deg = math.degrees(angle_rad)
            
            # Convert to our coordinate system (90° = top, clockwise)
            adjusted_angle = 90 - angle_deg
            if adjusted_angle < 0:
                adjusted_angle += 360
            
            # Calculate day from angle
            segment_angle = 360.0 / self._days_in_month
            day = int(adjusted_angle / segment_angle) + 1
            
            # Clamp to valid range
            if 1 <= day <= self._days_in_month:
                self._selected_day = day
                self.day_selected.emit(day)
                self.update()
        
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")
            import traceback
            traceback.print_exc()