"""
Monthly HP Tracker Window.

Dialog displaying HP data for a selected month with navigation controls.
"""

from typing import Dict, Optional
from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database import DatabaseManager
from models.hp_data import HPData
from ui.widgets.monthly_hp_ring import MonthlyHPRingWidget


class MonthlyHPTrackerWindow(QDialog):
    """
    Monthly HP tracker dialog window.
    
    Displays circular ring chart of HP values for all days in a month
    with navigation controls and detailed day information panel.
    """
    
    def __init__(
        self,
        parent=None,
        initial_year: Optional[int] = None,
        initial_month: Optional[int] = None
    ):
        """
        Initialize monthly HP tracker window.
        
        Args:
            parent: Parent widget
            initial_year: Starting year (defaults to current)
            initial_month: Starting month (defaults to current)
        """
        super().__init__(parent)
        
        self._db = DatabaseManager()
        
        # Set initial date
        today = date.today()
        self._current_year = initial_year if initial_year else today.year
        self._current_month = initial_month if initial_month else today.month
        
        self._hp_data: Dict[int, HPData] = {}
        
        self.setWindowTitle("HP Tracker")
        self.setModal(False)
        self.setMinimumSize(700, 800)
        
        self._setup_ui()
        self._load_month_data()
    
    def _setup_ui(self) -> None:
        """Initialize window UI components and layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4ECDC4;
                color: #000000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #6FE4DB;
            }
        """)
        
        # Header section
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("HP Tracker")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Month navigation
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ Prev")
        self.prev_button.clicked.connect(lambda: self._navigate_month(-1))
        
        self.month_label = QLabel()
        month_font = QFont()
        month_font.setPointSize(16)
        self.month_label.setFont(month_font)
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_month_label()
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(lambda: self._navigate_month(1))
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.month_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        
        header_layout.addWidget(title_label)
        header_layout.addLayout(nav_layout)
        
        # Ring chart
        self.ring_widget = MonthlyHPRingWidget()
        self.ring_widget.day_selected.connect(self._on_day_selected)
        
        # Detail panel
        detail_container = QWidget()
        detail_container.setStyleSheet("""
            QWidget {
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        detail_layout = QVBoxLayout(detail_container)
        
        detail_header = QLabel("Selected Day Details")
        detail_header_font = QFont()
        detail_header_font.setPointSize(14)
        detail_header_font.setBold(True)
        detail_header.setFont(detail_header_font)
        
        self.detail_label = QLabel("Click on a day to view details")
        self.detail_label.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        self.detail_label.setWordWrap(True)
        
        detail_layout.addWidget(detail_header)
        detail_layout.addWidget(self.detail_label)
        
        # Assembly
        layout.addLayout(header_layout)
        layout.addWidget(self.ring_widget, stretch=1)
        layout.addWidget(detail_container)
    
    def _update_month_label(self) -> None:
        """Update month display label with current month/year."""
        try:
            month_date = date(self._current_year, self._current_month, 1)
            month_name = month_date.strftime("%B %Y")
            self.month_label.setText(month_name)
        except Exception as e:
            print(f"Error updating month label: {e}")
            self.month_label.setText(f"{self._current_month}/{self._current_year}")
    
    def _load_month_data(self) -> None:
        """
        Load HP data from database for current month.
        
        Queries daily_points table and updates ring chart display.
        Handles HP = 33 as default/uninitialized state.
        """
        try:
            # Calculate days in month
            if self._current_month == 12:
                next_month = date(self._current_year + 1, 1, 1)
            else:
                next_month = date(self._current_year, self._current_month + 1, 1)
            
            first_day = date(self._current_year, self._current_month, 1)
            last_day = next_month - timedelta(days=1)
            days_in_month = last_day.day
            
            # Query database
            date_pattern = f"{self._current_year:04d}-{self._current_month:02d}-%"
            
            cursor = self._db._connection.cursor()
            cursor.execute(
                """
                SELECT date, hp, physical, mental, sleepiness
                FROM daily_points
                WHERE date LIKE ?
                ORDER BY date ASC
                """,
                (date_pattern,)
            )
            
            rows = cursor.fetchall()
            
            # Convert to dictionary
            self._hp_data = {}
            for row in rows:
                date_str = row['date']
                day = int(date_str.split('-')[2])
                
                # Store HP data regardless of value (including HP=33 default)
                self._hp_data[day] = HPData(
                    hp=row['hp'],
                    physical=row['physical'],
                    mental=row['mental'],
                    sleepiness=row['sleepiness'],
                    date_str=date_str
                )
            
            # Update ring chart
            self.ring_widget.set_hp_data(self._hp_data, days_in_month)
            
            # Clear detail panel
            self.detail_label.setText("Click on a day to view details")
            
            print(f"Loaded {len(self._hp_data)} HP records for {self._current_year}-{self._current_month:02d}")
        
        except Exception as e:
            print(f"Error loading month data: {e}")
            import traceback
            traceback.print_exc()
            
            self.detail_label.setText(
                f"Error loading data for {self._current_year}-{self._current_month:02d}"
            )
    
    def _navigate_month(self, delta: int) -> None:
        """
        Navigate to previous or next month.
        
        Args:
            delta: Month offset (+1 for next, -1 for previous)
        """
        try:
            self._current_month += delta
            
            # Handle year boundaries
            if self._current_month > 12:
                self._current_month = 1
                self._current_year += 1
            elif self._current_month < 1:
                self._current_month = 12
                self._current_year -= 1
            
            # Update display
            self._update_month_label()
            self._load_month_data()
        
        except Exception as e:
            print(f"Error navigating month: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_day_selected(self, day: int) -> None:
        """
        Handle day selection from ring chart.
        
        Displays HP breakdown with special handling for default state (HP=33).
        
        Args:
            day: Selected day number (1-31)
        """
        try:
            # Get HP data for selected day
            hp_data = self._hp_data.get(day, None)
            
            if hp_data is None:
                # No database record for this day
                self.detail_label.setText(
                    f"Day {day}\n\n"
                    f"No HP data recorded for this day."
                )
                self.detail_label.setStyleSheet("color: #FF6B6B; font-size: 13px;")
            
            elif hp_data.hp == 33:
                # HP = 33 indicates default/uninitialized state
                self.detail_label.setText(
                    f"Day {day} - {hp_data.date_str}\n\n"
                    f"HP: 33 (Default - No points entered)\n"
                    f"Physical: {hp_data.physical} | "
                    f"Mental: {hp_data.mental} | "
                    f"Sleepiness: {hp_data.sleepiness}"
                )
                self.detail_label.setStyleSheet("color: #B0B0B0; font-size: 13px;")
            
            else:
                # Normal HP data with valid category
                detail_text = (
                    f"Day {day} - {hp_data.date_str}\n\n"
                    f"{hp_data.format_display()}"
                )
                
                self.detail_label.setText(detail_text)
                
                # Color code based on HP category
                color = self._get_detail_color(hp_data.hp)
                self.detail_label.setStyleSheet(f"color: {color}; font-size: 13px;")
            
            # Update ring chart highlight
            self.ring_widget.set_selected_day(day)
        
        except Exception as e:
            print(f"Error displaying day details: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_detail_color(self, hp: int) -> str:
        """
        Determine text color for detail panel based on HP value.
        
        Args:
            hp: HP value (0-100)
            
        Returns:
            Hex color code for text display
        """
        if hp == 33:
            return '#B0B0B0'  # Light Gray (Default)
        elif hp < 34:
            return '#FF6B6B'  # Red (None)
        elif 34 <= hp <= 45:
            return '#FFA500'  # Orange (Very Low)
        elif 46 <= hp <= 57:
            return '#FFD93D'  # Yellow (Low)
        elif 58 <= hp <= 69:
            return '#C8E6C9'  # Light Green (Moderate)
        elif 70 <= hp <= 81:
            return '#81C784'  # Green (High)
        elif 82 <= hp <= 91:
            return '#4CAF50'  # High Green (Very High)
        else:  # 92-100
            return '#2E7D32'  # Dark Green (Maximum)
