# Energy Tracker

A personal energy and productivity tracking application with exercise monitoring, task management, and calendar organization.

## Features

- **Exercise Tracking**: Track daily exercises with progress bars showing actual/target ratios
- **Ring Chart Visualization**: Circular progress display with HP/FP metrics and category segments
- **Task Checklist**: Organize tasks by category with completion tracking
- **Calendar Integration**: Manage events with monthly calendar view and date highlighting
- **Dark Theme UI**: Professional dark-themed interface

## Requirements

- Python 3.10 or higher
- Windows/macOS/Linux

## Installation

### 1. Clone or Download the Project

```bash
cd energy_tracker
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Usage

### Exercise Tracking

1. The application initializes with 4 default exercises (伏地挺身, 深蹲, 跑步, 拉筋)
2. Click checkboxes to mark exercises as complete
3. Click the edit button (✏) to enter actual values achieved
4. Progress bars show actual/target ratios with category-based colors
5. Summary displays completion rate and total progress

### Ring Chart

- **HP (Health Points)**: Overall completion percentage (exercises completed / total exercises)
- **FP (Focus Points)**: Overall progress percentage (actual values / target values)
- Color-coded segments represent exercise categories:
  - **Red**: Cardio
  - **Cyan**: Strength
  - **Yellow**: Flexibility

### Task Management

1. Click "Add Task" to create new tasks
2. Organize tasks by category (e.g., 收拾書包)
3. Check boxes to mark tasks as complete
4. Use "Clear Completed" to remove finished tasks

### Calendar

1. View monthly calendar with event highlighting
2. Select dates to view events
3. Click "Add Event" to create new calendar entries
4. Events are highlighted in cyan on the calendar

## Project Structure

```
energy_tracker/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── ui/                      # User interface components
│   ├── main_window.py       # Main application window
│   └── widgets/             # Custom widgets
│       ├── ring_chart.py
│       ├── exercise_checklist.py
│       ├── task_checklist.py
│       └── calendar_widget.py
├── managers/                # Business logic
│   ├── exercise_manager.py
│   ├── task_manager.py
│   └── event_manager.py
├── models/                  # Data models
│   ├── exercise.py
│   ├── task.py
│   └── event.py
├── database/                # Data persistence
│   ├── db_manager.py
│   └── schema.sql
└── utils/                   # Utilities
    ├── config.py
    └── date_helpers.py
```

## Database

Data is stored in SQLite database (`energy_tracker.db`) in the application directory. The database includes:
- Exercise definitions and daily logs
- Task checklist items
- Calendar events

## Customization

### Adding New Exercises

1. Click "Add Exercise" in the exercise checklist
2. Enter exercise name, category, target value, and unit
3. Exercise will appear in the list with a progress bar

### Modifying Default Exercises

Edit `utils/config.py` and modify the `DEFAULT_EXERCISES` list:

```python
DEFAULT_EXERCISES = [
    {
        'name': 'Your Exercise',
        'category': 'cardio',  # or 'strength', 'flexibility'
        'target_value': 30,
        'unit': 'reps'  # or 'sets', 'minutes', 'km'
    },
    # Add more...
]
```

## Troubleshooting

### Application won't start

1. Verify Python version: `python --version` (should be 3.10+)
2. Ensure virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Database errors

1. Delete `energy_tracker.db` file (creates fresh database on next run)
2. Restart application

### Display issues

1. Check display scaling in system settings
2. Try running with: `python main.py --disable-high-dpi-scaling`

## Development

### Code Style

- PEP 8 compliant
- Type hints throughout
- Google-style docstrings

### Testing

Run the application:
```bash
python main.py
```

## License

This project is for personal use.

## Version

1.0.0
