"""
Ring chart widget for exercise progress visualization.

Displays circular progress chart with category-colored segments
showing HP (completion rate) and FP (progress rate).
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont

from managers import ExerciseManager
from utils import get_today, get_category_color


class RingChartWidget(QWidget):
    """
    Circular progress chart widget.
    
    Renders a ring chart with colored segments representing exercise
    categories, displays HP/FP percentages in center.
    """
    
    def __init__(self, exercise_manager: ExerciseManager, parent=None):
        """
        Initialize ring chart widget.
        
        Args:
            exercise_manager: Manager for exercise data
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._exercise_manager = exercise_manager
        self._current_date = get_today()
        self._chart_data = None
        self._manual_points = None  # Store manual points input
        
        self.setMinimumSize(400, 400)
        
        self._load_data()
        self._connect_signals()
    
    def update_from_points(self, points: dict) -> None:
        """
        Update ring chart from manual points input.
        
        Args:
            points: Dictionary with 'physical', 'mental', 'sleepiness' keys (all 0-10)
        """
        self._manual_points = points
        
        # Calculate HP as: physical + mental - sleepiness
        # All values are 0-10
        # HP range: (0+0-10) to (10+10-0) = -10 to 20 (31 values)
        # Convert to percentage: (HP + 10) / 30 * 100
        hp_raw = points['physical'] + points['mental'] - points['sleepiness']
        hp = ((hp_raw + 10) / 30.0) * 100  # Normalize to 0-100%
        hp = max(0, min(100, hp))  # Clamp to 0-100
        
        # Create segments based on ACTUAL POINTS (not percentage)
        # The angle is proportional to the actual point value
        total_points = points['physical'] + points['mental'] + points['sleepiness']
        
        # If total is 0, show empty ring
        if total_points == 0:
            self._chart_data = {
                'hp': round(hp, 0),
                'segments': []
            }
            self.update()
            return
        
        segments = []
        
        # Physical segment - angle based on actual points
        if points['physical'] > 0:
            segments.append({
                'name': 'Physical',
                'category': 'physical',
                'actual_points': points['physical'],  # Store actual points
                'angle': (points['physical'] / total_points) * 360,
                'color': get_category_color('physical')
            })
        
        # Mental segment - angle based on actual points
        if points['mental'] > 0:
            segments.append({
                'name': 'Mental',
                'category': 'mental',
                'actual_points': points['mental'],  # Store actual points
                'angle': (points['mental'] / total_points) * 360,
                'color': get_category_color('mental')
            })
        
        # Sleepiness segment - angle based on actual points
        if points['sleepiness'] > 0:
            segments.append({
                'name': 'Sleepiness',
                'category': 'sleepiness',
                'actual_points': points['sleepiness'],  # Store actual points
                'angle': (points['sleepiness'] / total_points) * 360,
                'color': get_category_color('sleepiness')
            })
        
        self._chart_data = {
            'hp': round(hp, 0),
            'segments': segments
        }
        
        self.update()  # Trigger repaint
    
    def _connect_signals(self) -> None:
        """Connect to manager signals for auto-refresh."""
        self._exercise_manager.data_changed.connect(self._load_data)
        self._exercise_manager.log_updated.connect(self._on_log_updated)
    
    def _on_log_updated(self, date: str) -> None:
        """
        Handle log update signal.
        
        Args:
            date: Date of updated log
        """
        if date == self._current_date:
            self._load_data()
    
    def _load_data(self) -> None:
        """Load ring chart data from manual points (not from exercise manager)."""
        try:
            # If manual points are set, use them; otherwise show empty
            if self._manual_points:
                self.update_from_points(self._manual_points)
            else:
                # Default: all at 0
                # HP = 0 + 0 - 0 = 0, normalized: (0+10)/30 * 100 ≈ 33%
                self._chart_data = {
                    'hp': 33.0,  # (0+0-0+10)/30 * 100
                    'segments': []
                }
                self.update()
        except Exception as e:
            print(f"Error loading ring chart data: {e}")
            self._chart_data = {'hp': 0, 'segments': []}
            self.update()
    
    def paintEvent(self, event) -> None:
        """
        Paint the ring chart.
        
        Args:
            event: QPaintEvent
        """
        if not self._chart_data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Center point
        center_x = width / 2
        center_y = height / 2
        
        # Ring dimensions
        outer_radius = size / 2 - 20
        inner_radius = outer_radius - 50
        
        # Draw segments
        self._draw_segments(
            painter,
            center_x,
            center_y,
            outer_radius,
            inner_radius
        )
        
        # Draw center metrics
        self._draw_center_metrics(
            painter,
            center_x,
            center_y,
            inner_radius
        )
        
        # Draw legend
        self._draw_legend(painter, 20, height - 100)
    
    def _draw_segments(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float
    ) -> None:
        """
        Draw colored ring segments using overlapping complete rings.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
        """
        segments = self._chart_data.get('segments', [])
        
        if not segments:
            # Draw empty smooth ring (no creases)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            self._draw_smooth_ring(
                painter,
                center_x,
                center_y,
                outer_radius,
                inner_radius,
                '#555555'
            )
            return
        
        # Enable antialiasing for smooth edges
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Calculate cumulative angles
        start_angle = 90  # Start from top (12 o'clock)
        
        # Draw all segments
        for segment in segments:
            angle = segment['angle']
            color = segment['color']
            
            if angle > 0:
                # Use QPainter arc methods for smoother rendering
                self._draw_smooth_segment(
                    painter,
                    center_x,
                    center_y,
                    outer_radius,
                    inner_radius,
                    start_angle,
                    angle,
                    color
                )
                start_angle += angle
        
        # Fill remaining space if needed
        total_angle = sum(s['angle'] for s in segments)
        if total_angle < 360:
            remaining = 360 - total_angle
            self._draw_smooth_segment(
                painter,
                center_x,
                center_y,
                outer_radius,
                inner_radius,
                start_angle,
                remaining,
                '#3D3D3D'
            )
    
    def _draw_smooth_segment(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float,
        start_angle: float,
        span_angle: float,
        color: str
    ) -> None:
        """
        Draw a smooth ring segment using pie chart technique.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
            start_angle: Start angle in degrees
            span_angle: Span angle in degrees
            color: Hex color string
        """
        # Convert angles to Qt's system (1/16th degree, clockwise from 3 o'clock)
        qt_start = int((90 - start_angle) * 16)
        qt_span = int(-span_angle * 16)
        
        # Set color
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw outer arc as pie
        outer_rect = QRectF(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )
        painter.drawPie(outer_rect, qt_start, qt_span)
        
        # Erase inner part to create ring
        if inner_radius > 0:
            # Use background color to "erase" inner circle
            painter.setBrush(QBrush(QColor('#2D2D2D')))  # Match background
            inner_rect = QRectF(
                center_x - inner_radius,
                center_y - inner_radius,
                inner_radius * 2,
                inner_radius * 2
            )
            painter.drawEllipse(inner_rect)
    
    def _draw_smooth_ring(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float,
        color: str
    ) -> None:
        """
        Draw a complete smooth ring without segments.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
            color: Hex color string
        """
        # Create smooth ring path
        path = QPainterPath()
        
        # Outer circle
        outer_rect = QRectF(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )
        path.addEllipse(outer_rect)
        
        # Inner circle (subtract)
        inner_rect = QRectF(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        inner_path = QPainterPath()
        inner_path.addEllipse(inner_rect)
        
        # Subtract inner from outer
        path = path.subtracted(inner_path)
        
        # Fill with color (no border)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QBrush(QColor(color)))
    
    def _draw_ring_segment(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float,
        start_angle: float,
        span_angle: float,
        color: str
    ) -> None:
        """
        Draw a single ring segment (arc) without borders.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
            start_angle: Start angle in degrees
            span_angle: Span angle in degrees
            color: Hex color string
        """
        # Ensure no border for smooth appearance
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Create path for ring segment
        path = QPainterPath()
        
        # Outer arc
        outer_rect = QRectF(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )
        
        # Inner arc (reverse direction)
        inner_rect = QRectF(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        
        # Qt uses 1/16th degree units and clockwise from 3 o'clock
        # Convert our angles (degrees from 12 o'clock)
        qt_start = (90 - start_angle) * 16
        qt_span = -span_angle * 16
        
        path.arcMoveTo(outer_rect, 90 - start_angle)
        path.arcTo(outer_rect, 90 - start_angle, -span_angle)
        
        # Line to inner arc
        end_angle = start_angle + span_angle
        inner_end_x = center_x + inner_radius * self._cos_deg(end_angle)
        inner_end_y = center_y - inner_radius * self._sin_deg(end_angle)
        path.lineTo(inner_end_x, inner_end_y)
        
        # Inner arc (reverse)
        path.arcTo(inner_rect, 90 - end_angle, span_angle)
        
        path.closeSubpath()
        
        # Fill segment without border
        painter.fillPath(path, QBrush(QColor(color)))
    
    def _cos_deg(self, degrees: float) -> float:
        """Calculate cosine from degrees."""
        import math
        return math.cos(math.radians(degrees))
    
    def _sin_deg(self, degrees: float) -> float:
        """Calculate sine from degrees."""
        import math
        return math.sin(math.radians(degrees))
    
    def _draw_center_metrics(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        inner_radius: float
    ) -> None:
        """
        Draw HP percentage in center.
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            inner_radius: Inner ring radius
        """
        hp = self._chart_data.get('hp', 0)
        
        # Set font
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor('#FFFFFF'))
        
        # Draw HP (centered, no label below)
        hp_text = f"HP {hp:.0f}"
        hp_rect = QRectF(
            center_x - inner_radius,
            center_y - 15,
            inner_radius * 2,
            30
        )
        painter.drawText(hp_rect, Qt.AlignmentFlag.AlignCenter, hp_text)
    
    def _draw_legend(
        self,
        painter: QPainter,
        x: float,
        y: float
    ) -> None:
        """
        Draw category legend with actual points (not percentages).
        
        Args:
            painter: QPainter instance
            x: Legend X position
            y: Legend Y position
        """
        segments = self._chart_data.get('segments', [])
        
        if not segments:
            return
        
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        
        current_y = y
        
        for segment in segments:
            # Color box
            color = QColor(segment['color'])
            painter.fillRect(int(x), int(current_y), 15, 15, color)
            
            # Label with actual points (not percentage)
            painter.setPen(QColor('#FFFFFF'))
            actual_points = segment.get('actual_points', 0)
            text = f"{segment['name']}: {actual_points} pts"
            painter.drawText(
                int(x + 20),
                int(current_y + 12),
                text
            )
            
            current_y += 20
    
    def set_date(self, date: str) -> None:
        """
        Change displayed date.
        
        Args:
            date: Date in ISO format
        """
        self._current_date = date
        self._load_data()