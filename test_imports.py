"""
Test all imports before building EXE.

Run this to make sure all modules can be imported correctly.
If this works, PyInstaller should also work.
"""

import sys
import traceback

print("=" * 60)
print("Energy Tracker - Import Test")
print("=" * 60)
print()

tests = [
    ("PyQt6.QtWidgets", lambda: __import__('PyQt6.QtWidgets')),
    ("PyQt6.QtCore", lambda: __import__('PyQt6.QtCore')),
    ("PyQt6.QtGui", lambda: __import__('PyQt6.QtGui')),
    ("pydantic", lambda: __import__('pydantic')),
    ("sqlite3", lambda: __import__('sqlite3')),
    ("dateutil", lambda: __import__('dateutil')),
    ("utils", lambda: __import__('utils')),
    ("utils.config", lambda: __import__('utils.config')),
    ("utils.date_helpers", lambda: __import__('utils.date_helpers')),
    ("utils.settings_manager", lambda: __import__('utils.settings_manager')),
    ("models", lambda: __import__('models')),
    ("models.exercise", lambda: __import__('models.exercise')),
    ("models.task", lambda: __import__('models.task')),
    ("models.event", lambda: __import__('models.event')),
    ("database", lambda: __import__('database')),
    ("database.db_manager", lambda: __import__('database.db_manager')),
    ("managers", lambda: __import__('managers')),
    ("managers.exercise_manager", lambda: __import__('managers.exercise_manager')),
    ("managers.task_manager", lambda: __import__('managers.task_manager')),
    ("managers.event_manager", lambda: __import__('managers.event_manager')),
    ("ui.widgets", lambda: __import__('ui.widgets')),
    ("ui.widgets.ring_chart", lambda: __import__('ui.widgets.ring_chart')),
    ("ui.widgets.calendar_widget", lambda: __import__('ui.widgets.calendar_widget')),
    ("ui.widgets.task_checklist", lambda: __import__('ui.widgets.task_checklist')),
    ("ui.widgets.exercise_checklist", lambda: __import__('ui.widgets.exercise_checklist')),
    ("ui.widgets.exercise_progress_bar", lambda: __import__('ui.widgets.exercise_progress_bar')),
    ("ui.settings_dialog", lambda: __import__('ui.settings_dialog')),
    ("ui.task_manager_window", lambda: __import__('ui.task_manager_window')),
    ("ui.exercise_manager_window", lambda: __import__('ui.exercise_manager_window')),
    ("ui.main_window", lambda: __import__('ui.main_window')),
    ("ui", lambda: __import__('ui')),
]

failed = []
passed = 0

for name, test_func in tests:
    try:
        test_func()
        print(f"✓ {name}")
        passed += 1
    except Exception as e:
        print(f"✗ {name}: {e}")
        failed.append((name, e))

print()
print("=" * 60)
print(f"Results: {passed}/{len(tests)} passed")
print("=" * 60)

if failed:
    print()
    print("FAILED IMPORTS:")
    for name, error in failed:
        print(f"  - {name}")
        print(f"    Error: {error}")
    print()
    print("Please fix these import errors before building EXE.")
    sys.exit(1)
else:
    print()
    print("✓ All imports successful!")
    print("You can now build the EXE with: build_fixed.bat")
    print()
