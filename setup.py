"""
Setup script for cx_Freeze to build Energy Tracker executable.

Usage:
    python setup.py build
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": [
        "PyQt6",
        "sqlite3",
        "pydantic",
        "dateutil"
    ],
    "include_files": [
        ("database/schema.sql", "database/schema.sql"),
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "email",
        "http",
        "xml",
        "pydoc"
    ]
}

# Base for Windows GUI (hides console)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="EnergyTracker",
    version="1.0.0",
    description="Personal Energy and Productivity Tracker",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="EnergyTracker.exe",
            # icon="icon.ico"  # Uncomment if you have an icon
        )
    ]
)
