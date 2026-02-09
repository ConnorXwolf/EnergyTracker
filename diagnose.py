"""
Diagnostic script to identify Energy Tracker startup issues.

Run this to see which component is causing problems.
"""

import sys
import traceback

print("=" * 60)
print("Energy Tracker Diagnostic Tool")
print("=" * 60)
print()

# Test 1: Python version
print("[1/8] Checking Python version...")
print(f"    Python {sys.version}")
if sys.version_info < (3, 10):
    print("    ⚠ WARNING: Python 3.10+ recommended")
else:
    print("    ✓ OK")
print()

# Test 2: PyQt6
print("[2/8] Testing PyQt6 import...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("    ✓ PyQt6 imported successfully")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    print("    FIX: pip install PyQt6 --force-reinstall")
    sys.exit(1)
print()

# Test 3: Pydantic
print("[3/8] Testing Pydantic import...")
try:
    import pydantic
    print(f"    ✓ Pydantic {pydantic.__version__} imported")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    print("    FIX: pip install pydantic")
    sys.exit(1)
print()

# Test 4: Utils module
print("[4/8] Testing utils module...")
try:
    from utils import get_today, APP_NAME
    print(f"    ✓ Utils imported: {APP_NAME}")
    print(f"    ✓ Today's date: {get_today()}")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
print()

# Test 5: Models
print("[5/8] Testing data models...")
try:
    from models import Exercise, Task, CalendarEvent
    test_exercise = Exercise(
        name="Test",
        category="cardio",
        color="#FF6B6B",
        target_value=10,
        unit="reps"
    )
    print(f"    ✓ Models imported and validated")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
print()

# Test 6: Database
print("[6/8] Testing database initialization...")
try:
    from database import DatabaseManager
    db = DatabaseManager()
    print("    ✓ Database initialized")
    db.close()
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    traceback.print_exc()
    print("    TRY: Delete energy_tracker.db and retry")
    sys.exit(1)
print()

# Test 7: Managers
print("[7/8] Testing business logic managers...")
try:
    from managers import ExerciseManager, TaskManager, EventManager
    em = ExerciseManager()
    tm = TaskManager()
    evm = EventManager()
    print("    ✓ All managers initialized")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
print()

# Test 8: UI Components
print("[8/8] Testing UI components...")
try:
    from ui import MainWindow
    print("    ✓ MainWindow imported")
except Exception as e:
    print(f"    ✗ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
print()

# Final test: Create QApplication
print("=" * 60)
print("ATTEMPTING TO START APPLICATION...")
print("=" * 60)
print()

try:
    app = QApplication(sys.argv)
    window = MainWindow()
    print("✓ Application created successfully!")
    print()
    print("Opening window in 2 seconds...")
    print("(Close the window to complete diagnostic)")
    print()
    
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(2000, window.show)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"✗ FATAL ERROR: {e}")
    print()
    traceback.print_exc()
    print()
    print("=" * 60)
    print("DIAGNOSTIC COMPLETE - ERRORS FOUND")
    print("=" * 60)
    sys.exit(1)
