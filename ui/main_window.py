"""
Main application window.

Integrates all widgets into the primary UI layout and manages
application-level interactions with UI scaling support.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMenuBar, QMenu, QMessageBox, QSpinBox, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont

from managers import ExerciseManager, TaskManager, EventManager
from .widgets import (
    RingChartWidget,
    CalendarWidget,
    TaskChecklistWidget,
    ExerciseChecklistWidget
)
from .settings_dialog import SettingsDialog
from .task_manager_window import TaskManagerWindow
from .exercise_manager_window import ExerciseManagerWindow
from utils import APP_NAME, APP_VERSION, DEFAULT_EXERCISES, get_today, SettingsManager
from .monthly_hp_tracker_window import MonthlyHPTrackerWindow
from PyQt6.QtWidgets import QApplication

class MainWindow(QMainWindow):
    """
    Main application window.
    
    Provides the primary UI layout with ring chart, calendar,
    task checklist, and exercise checklist widgets with support
    for UI scaling and text size customization.
    """
    
    def __init__(self):
        """Initialize main window and all components."""
        super().__init__()
        
        # Initialize managers
        self._exercise_manager = ExerciseManager()
        self._task_manager = TaskManager()
        self._event_manager = EventManager()
        
        # Initialize settings
        self._settings = SettingsManager()
        
        # Initialize report generator
        from utils import ReportGenerator
        self._report_generator = ReportGenerator(
            self._exercise_manager,
            self._task_manager
        )
        
        # Initialize points storage
        self._current_points = {
            'physical': 0,
            'mental': 0,
            'sleepiness': 0
        }
        
        # Track current selected date (defaults to today)
        self._current_date = get_today()
        
        self._setup_ui()
        self._create_menu_bar()
        self._connect_signals()
        self._apply_settings()
        self._initialize_default_data()
        
        # Load data for current date (today by default)
        self._load_date_data(self._current_date)
    
    def _setup_ui(self) -> None:
        """Initialize main window UI and layout."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        
        # Load saved window size
        width, height = self._settings.get_window_size()
        self.setMinimumSize(width, height)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4ECDC4;
                color: #000000;
                border: none;
                padding: 14px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6FE4DB;
            }
            QPushButton:pressed {
                background-color: #3DB8AF;
            }
            QListWidget {
                background-color: #2D2D2D;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #3D3D3D;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top section: Ring chart + Calendar
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        # Ring chart
        self.ring_chart = RingChartWidget(self._exercise_manager)
        self.ring_chart.setFixedSize(400, 400)
        
        # Calendar (expanded to red line) - NOW WITH TASK INTEGRATION
        self.calendar = CalendarWidget(self._event_manager, self._task_manager)
        self.calendar.setFixedWidth(1050)
        
        top_layout.addWidget(self.ring_chart)
        top_layout.addWidget(self.calendar)
        top_layout.addStretch()
        
        # Middle section: Points Input Area
        points_group = QWidget()
        points_layout = QVBoxLayout(points_group)
        points_layout.setSpacing(10)
        
        # Header with title only (date label removed)
        points_title = QLabel("Daily Points")
        points_title_font = QFont()
        points_title_font.setPointSize(16)
        points_title_font.setBold(True)
        points_title.setFont(points_title_font)
        points_layout.addWidget(points_title)
        
        # Points input row
        points_input_layout = QHBoxLayout()
        
        # Physical input (0-10)
        phys_layout = QVBoxLayout()
        phys_label = QLabel("Physical:")
        self.physical_input = QSpinBox()
        self.physical_input.setMinimum(0)
        self.physical_input.setMaximum(10)
        self.physical_input.setValue(0)
        phys_layout.addWidget(phys_label)
        phys_layout.addWidget(self.physical_input)
        
        # Mental input (0-10)
        mental_layout = QVBoxLayout()
        mental_label = QLabel("Mental:")
        self.mental_input = QSpinBox()
        self.mental_input.setMinimum(0)
        self.mental_input.setMaximum(10)
        self.mental_input.setValue(0)
        mental_layout.addWidget(mental_label)
        mental_layout.addWidget(self.mental_input)
        
        # Sleepiness input (0-10)
        sleep_layout = QVBoxLayout()
        sleep_label = QLabel("Sleepiness:")
        self.sleepiness_input = QSpinBox()
        self.sleepiness_input.setMinimum(0)
        self.sleepiness_input.setMaximum(10)
        self.sleepiness_input.setValue(0)
        sleep_layout.addWidget(sleep_label)
        sleep_layout.addWidget(self.sleepiness_input)
        
        # Save button
        save_button = QPushButton("Save Points")
        save_button.clicked.connect(self._save_daily_points)
        
        points_input_layout.addLayout(phys_layout)
        points_input_layout.addLayout(mental_layout)
        points_input_layout.addLayout(sleep_layout)
        points_input_layout.addWidget(save_button)
        points_input_layout.addStretch()
        
        points_layout.addLayout(points_input_layout)
        
        # Bottom section: Task and Exercise Summary (read-only)
        summary_layout = QHBoxLayout()
        
        # Task summary
        task_summary_group = QWidget()
        task_summary_layout = QVBoxLayout(task_summary_group)
        task_summary_title = QLabel("Tasks")
        task_summary_title.setFont(points_title_font)
        task_summary_layout.addWidget(task_summary_title)
        
        # Task checklist (simple checkboxes showing today's tasks)
        self.task_checklist_layout = QVBoxLayout()
        task_summary_layout.addLayout(self.task_checklist_layout)
        
        task_manage_button = QPushButton("Manage Tasks")
        task_manage_button.clicked.connect(self._open_task_manager)
        task_summary_layout.addWidget(task_manage_button)
        task_summary_layout.addStretch()
        
        # Exercise summary
        exercise_summary_group = QWidget()
        exercise_summary_layout = QVBoxLayout(exercise_summary_group)
        exercise_summary_title = QLabel("Exercises")
        exercise_summary_title.setFont(points_title_font)
        exercise_summary_layout.addWidget(exercise_summary_title)
        
        # Exercise checklist (simple checkboxes)
        self.exercise_checklist_layout = QVBoxLayout()
        exercise_summary_layout.addLayout(self.exercise_checklist_layout)
        
        exercise_manage_button = QPushButton("Manage Exercises")
        exercise_manage_button.clicked.connect(self._open_exercise_manager)
        exercise_summary_layout.addWidget(exercise_manage_button)
        exercise_summary_layout.addStretch()
        
        summary_layout.addWidget(task_summary_group)
        summary_layout.addWidget(exercise_summary_group)
        
        # Assembly
        main_layout.addLayout(top_layout)
        main_layout.addWidget(points_group)
        main_layout.addLayout(summary_layout)
    
    def _create_menu_bar(self) -> None:
        """Create application menu bar."""
        menubar = self.menuBar()

        menu_font = QFont()
        menu_font.setPointSize(16)
        menubar.setFont(menu_font)

        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Data menu
        data_menu = menubar.addMenu("Data")
        
        refresh_action = QAction("Refresh All", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_all_widgets)
        data_menu.addAction(refresh_action)
        
        reset_action = QAction("Initialize Default Exercises", self)
        reset_action.triggered.connect(self._initialize_default_data)
        data_menu.addAction(reset_action)
        
        data_menu.addSeparator()
        
        # Generate Report action
        report_action = QAction("Generate Report", self)
        report_action.setShortcut("Ctrl+R")
        report_action.triggered.connect(self._generate_daily_report)
        data_menu.addAction(report_action)
        
        # ==================== MORE MENU (UPDATED) ====================
        more_menu = menubar.addMenu("More")

        # Monthly HP Tracker action
        hp_tracker_action = QAction("Monthly HP Tracker", self)
        hp_tracker_action.setShortcut("Ctrl+M")
        hp_tracker_action.triggered.connect(self._open_monthly_hp_tracker)
        more_menu.addAction(hp_tracker_action)
        # =========================================================
        
        # Settings menu (between Data and Help)
        settings_menu = menubar.addMenu("Settings")
        
        settings_action = QAction("Preferences...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings_dialog)
        settings_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _connect_signals(self) -> None:
        """Connect inter-widget signals."""
        # Update summaries when data changes
        self._task_manager.data_changed.connect(self._update_task_summary)
        self._exercise_manager.data_changed.connect(self._update_exercise_summary)
        
        # When calendar date is selected, could update other widgets
        self.calendar.date_selected.connect(self._on_date_selected)
    
    def _on_date_selected(self, date_str: str) -> None:
        """
        Handle calendar date selection - load all data for that date.
        
        Args:
            date_str: Selected date in ISO format (YYYY-MM-DD)
        """
        self._current_date = date_str
        self._load_date_data(date_str)
    
    def _load_date_data(self, date_str: str) -> None:
        """
        Load all data for a specific date and update UI.
        
        Args:
            date_str: Date in ISO format (YYYY-MM-DD)
        """
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            
            # Load daily points from database
            result = db.fetch_one("""
                SELECT physical, mental, sleepiness, hp, updated_at
                FROM daily_points
                WHERE date = ?
            """, (date_str,))
            
            if result:
                # Found existing data for this date
                physical, mental, sleepiness, hp, updated_at = result
                
                # Update spinboxes
                self.physical_input.setValue(physical)
                self.mental_input.setValue(mental)
                self.sleepiness_input.setValue(sleepiness)
                
                # Update current points
                self._current_points = {
                    'physical': physical,
                    'mental': mental,
                    'sleepiness': sleepiness
                }
                
                # Update ring chart
                self.ring_chart.update_from_points(self._current_points)
                
                print(f"Loaded data for {date_str} (last updated: {updated_at})")
            else:
                # No data for this date - reset to defaults
                self.physical_input.setValue(0)
                self.mental_input.setValue(0)
                self.sleepiness_input.setValue(0)
                
                self._current_points = {
                    'physical': 0,
                    'mental': 0,
                    'sleepiness': 0
                }
                
                self.ring_chart.update_from_points(self._current_points)
                
                print(f"No data for {date_str} - showing defaults")
            
            # Update exercise display for selected date
            self._update_exercise_summary_for_date(date_str)
            
            # Update task display for selected date
            self._update_task_summary_for_date(date_str)
            
        except Exception as e:
            print(f"Error loading date data: {e}")
            import traceback
            traceback.print_exc()
            
    def _open_monthly_hp_tracker(self) -> None:
        """Open Monthly HP Tracker window."""
        try:
            from datetime import date
            today = date.today()
            
            dialog = MonthlyHPTrackerWindow(
                parent=self,
                initial_year=today.year,
                initial_month=today.month
            )
            dialog.exec()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open HP Tracker:\n{str(e)}"
            )
            print(f"Error opening HP tracker: {e}")
            import traceback
            traceback.print_exc()

    def _save_daily_points(self) -> None:
        """Save daily points input for current selected date and update ring chart."""
        physical = self.physical_input.value()
        mental = self.mental_input.value()
        sleepiness = self.sleepiness_input.value()
        
        # Calculate HP
        hp_raw = physical + mental - sleepiness
        hp = int(((hp_raw + 10) / 30.0) * 100)
        hp = max(0, min(100, hp))
        
        # Store points for ring chart
        self._current_points = {
            'physical': physical,
            'mental': mental,
            'sleepiness': sleepiness
        }
        
        # Save to database with timestamp for CURRENT SELECTED DATE
        try:
            from database import DatabaseManager
            from datetime import datetime
            
            db = DatabaseManager()
            target_date = self._current_date  # Use selected date, not today
            now = datetime.now().isoformat()
            
            # UPSERT daily points
            db.execute("""
                INSERT INTO daily_points (date, physical, mental, sleepiness, hp, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    physical = excluded.physical,
                    mental = excluded.mental,
                    sleepiness = excluded.sleepiness,
                    hp = excluded.hp,
                    updated_at = excluded.updated_at
            """, (target_date, physical, mental, sleepiness, hp, now, now))
            
            print(f"Saved points for {target_date} at {now}: P={physical}, M={mental}, S={sleepiness}, HP={hp}")
            
        except Exception as e:
            print(f"Error saving daily points: {e}")
        
        # Update ring chart with new points (no popup)
        self.ring_chart.update_from_points(self._current_points)
    
    def _update_task_summary(self) -> None:
        """Update task summary display for TODAY."""
        self._update_task_summary_for_date(get_today())
    
    def _update_task_summary_for_date(self, date_str: str) -> None:
        """
        Update task checklist display for a specific date.
        
        Args:
            date_str: Date in ISO format (YYYY-MM-DD)
        """
        try:
            print(f"[MainWindow] _update_task_summary_for_date called with: {date_str}")
            
            # Clear existing checkboxes
            while self.task_checklist_layout.count():
                child = self.task_checklist_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Get tasks for specific date from TaskManager
            try:
                tasks = self._task_manager.get_tasks_by_date(date_str)
                print(f"[MainWindow] Loaded {len(tasks)} tasks for {date_str}")
            except Exception as e:
                print(f"[MainWindow] ERROR fetching tasks: {e}")
                import traceback
                traceback.print_exc()
                error_label = QLabel(f"Error loading tasks")
                error_label.setStyleSheet("color: #FF6B6B;")
                self.task_checklist_layout.addWidget(error_label)
                return
            
            if not tasks:
                no_task_label = QLabel(f"No tasks for {date_str}")
                no_task_label.setStyleSheet("color: #AAAAAA;")
                self.task_checklist_layout.addWidget(no_task_label)
                return
            
            # Create checkbox for each task
            for task in tasks:
                try:
                    display_text = f"{task.title}"
                    if task.category:
                        display_text += f" ({task.category})"
                    
                    checkbox = QCheckBox(display_text)
                    checkbox.setChecked(task.is_completed)
                    
                    # White checkbox styling, 16pt font
                    checkbox.setStyleSheet("""
                        QCheckBox {
                            color: white;
                        }
                        QCheckBox::indicator {
                            width: 18px;
                            height: 18px;
                            border: 2px solid white;
                            border-radius: 3px;
                            background-color: transparent;
                        }
                        QCheckBox::indicator:checked {
                            background-color: #4ECDC4;
                            border: 2px solid white;
                        }
                    """)
                    
                    # Connect to update handler for current date
                    checkbox.stateChanged.connect(
                        lambda state, tid=task.id: self._on_task_toggled_on_home(tid, state)
                    )
                    
                    self.task_checklist_layout.addWidget(checkbox)
                    print(f"[MainWindow] Added checkbox for task: {task.title}")
                    
                except Exception as e:
                    print(f"[MainWindow] ERROR creating checkbox for task {task.id}: {e}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            print(f"[MainWindow] ERROR in _update_task_summary_for_date: {e}")
            import traceback
            traceback.print_exc()
            error_label = QLabel("Error loading tasks")
            error_label.setStyleSheet("color: #FF6B6B;")
            self.task_checklist_layout.addWidget(error_label)
    
    def _update_exercise_summary(self) -> None:
        """Update exercise checklist display with checkboxes for TODAY."""
        self._update_exercise_summary_for_date(get_today())
    
    def _update_exercise_summary_for_date(self, date_str: str) -> None:
        """
        Update exercise checklist display for a specific date.
        
        Args:
            date_str: Date in ISO format (YYYY-MM-DD)
        """
        try:
            print(f"[MainWindow] _update_exercise_summary_for_date called with: {date_str}")
            
            # Clear existing checkboxes
            while self.exercise_checklist_layout.count():
                child = self.exercise_checklist_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Get exercises for specified date
            exercises_data = self._exercise_manager.get_logs_for_date(date_str)
            print(f"[MainWindow] Loaded {len(exercises_data)} exercises for {date_str}")
            
            if not exercises_data:
                no_exercise_label = QLabel(f"No exercises for {date_str}")
                no_exercise_label.setStyleSheet("color: #AAAAAA;")
                self.exercise_checklist_layout.addWidget(no_exercise_label)
                return
            
            # Create checkbox for each exercise
            for exercise, log in exercises_data:
                checkbox = QCheckBox(f"{exercise.name} - {log.actual_value}/{log.target_value} {log.unit}")
                checkbox.setChecked(log.completed)
                
                # White checkbox styling, 16pt font
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: white;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border: 2px solid white;
                        border-radius: 3px;
                        background-color: transparent;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #32CD32;
                        border: 2px solid white;
                    }
                """)
                
                # Connect to update handler for current date
                checkbox.stateChanged.connect(
                    lambda state, eid=exercise.id, d=date_str: self._on_exercise_toggled_for_date(eid, state, d)
                )
                
                self.exercise_checklist_layout.addWidget(checkbox)
                print(f"[MainWindow] Added checkbox for exercise: {exercise.name}")
                
        except Exception as e:
            print(f"[MainWindow] ERROR in _update_exercise_summary_for_date: {e}")
            import traceback
            traceback.print_exc()
            no_exercise_label = QLabel("Error loading exercises")
            no_exercise_label.setStyleSheet("color: #FF6B6B;")
            self.exercise_checklist_layout.addWidget(no_exercise_label)
    
    def _on_home_exercise_toggled(self, exercise_id: int, state: int) -> None:
        """
        Handle exercise checkbox toggle on home page for TODAY.
        
        Args:
            exercise_id: Exercise being toggled
            state: Qt.CheckState value
        """
        self._on_exercise_toggled_for_date(exercise_id, state, get_today())
    
    def _on_exercise_toggled_for_date(self, exercise_id: int, state: int, date_str: str) -> None:
        """
        Handle exercise checkbox toggle for a specific date.
        
        Args:
            exercise_id: Exercise being toggled
            state: Qt.CheckState value
            date_str: Date in ISO format
        """
        try:
            is_checked = (state == Qt.CheckState.Checked.value)
            
            # Get current exercise to get target_value
            exercise = self._exercise_manager.get_exercise_by_id(exercise_id)
            if not exercise:
                print(f"Exercise {exercise_id} not found")
                return
            
            # Update completion status
            # If checking: set actual_value = target_value
            # If unchecking: set actual_value = 0
            actual_value = exercise.target_value if is_checked else 0
            
            self._exercise_manager.update_progress(
                exercise_id,
                date_str,
                actual_value,
                is_checked
            )
            
            # Refresh display for current date
            self._update_exercise_summary_for_date(date_str)
            
            # Only refresh ring chart if editing current selected date
            if date_str == self._current_date:
                self.ring_chart._load_data()
            
        except Exception as e:
            print(f"Error toggling exercise for {date_str}: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_task_toggled_on_home(self, task_id: int, state: int) -> None:
        """
        Handle task checkbox toggle on home page.
        
        Args:
            task_id: Task being toggled
            state: Qt.CheckState value
        """
        try:
            is_checked = (state == Qt.CheckState.Checked.value)
            
            # Update task completion status
            self._task_manager.toggle_task_completion(task_id)
            
            # Refresh display for current date
            self._update_task_summary_for_date(self._current_date)
            
        except Exception as e:
            print(f"Error toggling task: {e}")
    
    def _open_task_manager(self) -> None:
        """Open task management window for current selected date."""
        dialog = TaskManagerWindow(self._task_manager, self)
        # Set current date in the task manager dialog
        if hasattr(dialog, 'task_checklist') and hasattr(dialog.task_checklist, 'set_current_date'):
            dialog.task_checklist.set_current_date(self._current_date)
        dialog.exec()
        # Refresh display for current date
        self._update_task_summary_for_date(self._current_date)
    
    def _open_exercise_manager(self) -> None:
        """Open exercise management window."""
        dialog = ExerciseManagerWindow(self._exercise_manager, self)
        dialog.exec()
        self._update_exercise_summary()
        self.ring_chart._load_data()  # Refresh ring chart
    
    def _refresh_all_widgets(self) -> None:
        """Refresh all data displays."""
        try:
            self.ring_chart._load_data()
            self.calendar._load_events()
            self._update_task_summary()
            self._update_exercise_summary()
        except Exception as e:
            print(f"Error refreshing widgets: {e}")
    
    def _initialize_default_data(self) -> None:
        """Initialize database with default exercises if empty."""
        try:
            existing_exercises = self._exercise_manager.get_all_exercises()
            
            if not existing_exercises:
                # Create default exercises
                for exercise_data in DEFAULT_EXERCISES:
                    self._exercise_manager.create_exercise(
                        name=exercise_data['name'],
                        category=exercise_data['category'],
                        target_value=exercise_data['target_value'],
                        unit=exercise_data['unit']
                    )
                
                QMessageBox.information(
                    self,
                    "Default Exercises Created",
                    f"Created {len(DEFAULT_EXERCISES)} default exercises."
                )
                
            # Initialize summaries
            self._update_task_summary()
            self._update_exercise_summary()
        except Exception as e:
            print(f"Error initializing default data: {e}")

    def _show_settings_dialog(self) -> None:
        """Display settings dialog for UI customization."""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()
    
    def _apply_settings(self) -> None:
        """
        Apply UI scale settings to widgets.
        
        Font settings are handled globally by QApplication.setFont().
        This method only scales widget sizes and spacing.
        """
        scale = self._settings.get_ui_scale()
        text_offset = self._settings.get_text_size_offset()
        
        # Apply global font to QApplication (affects ALL widgets)
        from PyQt6.QtGui import QFont
        app = QApplication.instance()
        
        base_font = QFont()
        base_font.setFamily("Segoe UI")
        base_size = 12  # MUST MATCH main.py base_size
        adjusted_size = int(base_size * scale) + text_offset
        adjusted_size = max(8, adjusted_size)
        base_font.setPointSize(adjusted_size)
        
        app.setFont(base_font)
        
        # Scale widget sizes (not fonts)
        self._scale_widgets(scale)
        
        # Force repaint
        self.update()
        
        print(f"[Settings] Applied: Scale={scale:.2f}, Text offset={text_offset:+d}pt, Final size={adjusted_size}pt")
    
    def _scale_widgets(self, scale: float) -> None:
        """
        Apply scaling to fixed-size widgets only.
        
        Fonts are handled globally, this only affects widget dimensions.
        
        Args:
            scale: Scale multiplier
        """
        # Scale ring chart
        base_ring_size = 400
        scaled_size = int(base_ring_size * scale)
        self.ring_chart.setFixedSize(scaled_size, scaled_size)
        
        # Scale calendar width
        base_calendar_width = 1050
        scaled_width = int(base_calendar_width * scale)
        self.calendar.setFixedWidth(scaled_width)
        
        # Adjust spacing
        base_spacing = 15
        scaled_spacing = int(base_spacing * scale)
        self.centralWidget().layout().setSpacing(scaled_spacing)
    
    def _show_about_dialog(self) -> None:
        """Display about dialog."""
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p>Version {APP_VERSION}</p>
        <p>A personal energy and productivity tracking application.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Exercise tracking with progress visualization</li>
            <li>Task checklist management</li>
            <li>Calendar event organization</li>
            <li>Ring chart progress display</li>
            <li>Customizable interface scaling and text size</li>
        </ul>
        <p>Built with Python and PyQt6</p>
        """
        
        QMessageBox.about(self, f"About {APP_NAME}", about_text)
    
    def _generate_daily_report(self) -> None:
        """Generate and save daily report."""
        try:
            # Get current HP value from ring chart
            hp_value = self.ring_chart._chart_data.get('hp', 0)
            
            # Generate report
            report_path = self._report_generator.generate_daily_report(
                hp_value=hp_value,
                points=self._current_points
            )
            
            QMessageBox.information(
                self,
                "Report Generated",
                f"Daily report has been saved to:\n{report_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate report:\n{str(e)}"
            )
    
    def closeEvent(self, event) -> None:
        """
        Handle application close event.
        
        Args:
            event: QCloseEvent
        """
        # Save window size
        self._settings.set_window_size(self.width(), self.height())
        event.accept()