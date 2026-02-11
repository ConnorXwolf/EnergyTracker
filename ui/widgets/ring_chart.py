"""
Ring chart widget for exercise progress visualization.

Displays dual-ring circular progress chart with category-colored segments
showing Stamina (outer ring) and Mana (inner ring) independently.
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont

from managers import ExerciseManager
from utils import get_today, get_category_color


class RingChartWidget(QWidget):
    """
    Dual-ring circular progress chart widget.
    
    Renders two concentric rings:
    - Outer ring: Stamina progress (0-10 points → 0-360°)
    - Inner ring: Mana progress (0-10 points → 0-360°)
    
    Displays HP value in center based on combined points.
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
        Update ring chart from manual points input with dual-ring display.
        
        Each category occupies an independent ring with its own 360° range:
        - Stamina: Outer ring (blue)
        - Mana: Inner ring (gold)
        
        Args:
            points: Dictionary with 'physical', 'mental' keys (each 0-10)
        
        Examples:
            >>> update_from_points({'physical': 6, 'mental': 4})
            # Outer ring (Stamina): 216° arc (60% of full circle)
            # Inner ring (Mana): 144° arc (40% of full circle)
            # HP: 60 points
            
            >>> update_from_points({'physical': 3, 'mental': 2})
            # Outer ring: 108° arc (30%)
            # Inner ring: 72° arc (20%)
            # HP: 40 points
        """
        self._manual_points = points
        
        # Calculate HP: physical + mental (0-20 range)
        raw_hp = points['physical'] + points['mental']
        hp = 20 + (raw_hp * 4)  # Normalize to 20-100 scale
        hp = max(20, min(100, hp))  # Clamp to valid range
        
        # Constants
        MAX_POINTS_PER_CATEGORY = 10  # Maximum value for each category
        FULL_CIRCLE_DEGREES = 360
        
        # Calculate independent angles for each ring
        physical_angle = (points['physical'] / MAX_POINTS_PER_CATEGORY) * FULL_CIRCLE_DEGREES
        mental_angle = (points['mental'] / MAX_POINTS_PER_CATEGORY) * FULL_CIRCLE_DEGREES
        
        # Create dual-ring structure
        rings = {}
        
        # Outer ring - Stamina (Physical)
        rings['outer_ring'] = {
            'name': 'Stamina',  # ← 修改：從 'Physical' 改為 'Stamina'
            'category': 'physical',
            'actual_points': points['physical'],
            'angle': physical_angle,
            'color': get_category_color('physical'),
            'show': points['physical'] > 0
        }
        
        # Inner ring - Mana (Mental)
        rings['inner_ring'] = {
            'name': 'Mana',  # ← 修改：從 'Mental' 改為 'Mana'
            'category': 'mental',
            'actual_points': points['mental'],
            'angle': mental_angle,
            'color': get_category_color('mental'),
            'show': points['mental'] > 0
        }
        
        self._chart_data = {
            'hp': round(hp, 0),
            'rings': rings
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
                self._chart_data = {
                    'hp': 20.0,
                    'rings': {
                        'outer_ring': {
                            'name': 'Stamina',  # ← 修改：從 'Physical' 改為 'Stamina'
                            'actual_points': 0,
                            'angle': 0,
                            'color': get_category_color('physical'),
                            'show': False
                        },
                        'inner_ring': {
                            'name': 'Mana',  # ← 修改：從 'Mental' 改為 'Mana'
                            'actual_points': 0,
                            'angle': 0,
                            'color': get_category_color('mental'),
                            'show': False
                        }
                    }
                }
                self.update()
        except Exception as e:
            print(f"Error loading ring chart data: {e}")
            self._chart_data = {'hp': 20, 'rings': {}}
            self.update()
    
    def paintEvent(self, event) -> None:
        """
        Paint the dual-ring chart.
        
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
        
        # Draw dual rings
        self._draw_dual_rings(
            painter,
            center_x,
            center_y,
            outer_radius
        )
        
        # Draw center metrics
        self._draw_center_metrics(
            painter,
            center_x,
            center_y,
            outer_radius - 100  # Inner radius of inner ring
        )
        
        # Draw legend
        self._draw_legend(painter, 175, height - 200)
    
    def _draw_dual_rings(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float
    ) -> None:
        """
        Draw two concentric rings with independent progress arcs.
        
        Ring structure (configurable):
        - Outer ring: Stamina
        - Gap: Adjustable spacing
        - Inner ring: Mana
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer boundary radius
        """
        rings = self._chart_data.get('rings', {})
        
        # ========== Configuration Constants ==========
        RING_WIDTH = 40        # Width of each ring (px)
        RING_GAP = 20          # Gap between rings (px)
        # ============================================
        
        # Calculate ring dimensions
        OUTER_RING_OUTER = outer_radius
        OUTER_RING_INNER = outer_radius - RING_WIDTH
        INNER_RING_OUTER = OUTER_RING_INNER - RING_GAP
        INNER_RING_INNER = INNER_RING_OUTER - RING_WIDTH
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # === Draw Outer Ring (Stamina) ===
        outer_ring_data = rings.get('outer_ring', {})
        
        # 1. Draw outer ring background (full gray circle)
        self._draw_ring_background(
            painter,
            center_x,
            center_y,
            OUTER_RING_OUTER,
            OUTER_RING_INNER,
            '#3D3D3D'
        )
        
        # 2. Draw outer ring progress (if any)
        if outer_ring_data.get('show', False):
            self._draw_ring_progress(
                painter,
                center_x,
                center_y,
                OUTER_RING_OUTER,
                OUTER_RING_INNER,
                outer_ring_data['angle'],
                outer_ring_data['color']
            )
        
        # === Draw Inner Ring (Mana) ===
        inner_ring_data = rings.get('inner_ring', {})
        
        # 3. Draw inner ring background (full gray circle)
        self._draw_ring_background(
            painter,
            center_x,
            center_y,
            INNER_RING_OUTER,
            INNER_RING_INNER,
            '#3D3D3D'
        )
        
        # 4. Draw inner ring progress (if any)
        if inner_ring_data.get('show', False):
            self._draw_ring_progress(
                painter,
                center_x,
                center_y,
                INNER_RING_OUTER,
                INNER_RING_INNER,
                inner_ring_data['angle'],
                inner_ring_data['color']
            )
    
    def _draw_ring_background(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float,
        color: str
    ) -> None:
        """
        Draw a complete ring as background (360° gray circle).
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
            color: Hex color string for background
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(color)))
        
        # Draw outer circle
        outer_rect = QRectF(
            center_x - outer_radius,
            center_y - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )
        painter.drawEllipse(outer_rect)
        
        # Erase inner circle to create ring
        painter.setBrush(QBrush(QColor('#2D2D2D')))  # Background color
        inner_rect = QRectF(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        painter.drawEllipse(inner_rect)
    
    def _draw_ring_progress(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        inner_radius: float,
        angle: float,
        color: str
    ) -> None:
        """
        Draw progress arc on a ring starting from 12 o'clock (90°).
        
        Args:
            painter: QPainter instance
            center_x: Center X coordinate
            center_y: Center Y coordinate
            outer_radius: Outer ring radius
            inner_radius: Inner ring radius
            angle: Progress angle in degrees (0-360)
            color: Hex color string for progress arc
        """
        if angle <= 0:
            return
        
        # Qt uses 1/16th degree units, clockwise from 3 o'clock
        # Our system: 90° = 12 o'clock, clockwise
        qt_start = int(90 * 16)  # Start at 12 o'clock
        qt_span = int(-angle * 16)  # Clockwise (negative)
        
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
        
        # Erase inner circle to create ring shape
        painter.setBrush(QBrush(QColor('#2D2D2D')))
        inner_rect = QRectF(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        painter.drawEllipse(inner_rect)
    
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
        
        # Draw HP (centered)
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
        Draw dual-ring legend with actual points for each category.
        
        Args:
            painter: QPainter instance
            x: Legend X position
            y: Legend Y position
        """
        rings = self._chart_data.get('rings', {})
        
        if not rings:
            return
        
        font = QFont()
        font.setPointSize(15)
        painter.setFont(font)
        
        current_y = y
        
        # Draw legend for each ring
        for ring_key in ['outer_ring', 'inner_ring']:
            ring_data = rings.get(ring_key, {})
            
            if not ring_data:
                continue
            
            # Color box
            color = QColor(ring_data['color'])
            painter.fillRect(int(x), int(current_y), 15, 15, color)
            
            # Label with actual points (顯示 Stamina/Mana)
            painter.setPen(QColor("#FFFFFF"))
            actual_points = ring_data.get('actual_points', 0)
            text = f"{ring_data['name']}: {actual_points} pts"  # ← 這裡會自動顯示 'Stamina' 或 'Mana'
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