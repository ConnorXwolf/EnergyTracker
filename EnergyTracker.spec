# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Energy Tracker.

This properly bundles all resources and handles PyQt6 dependencies.

Usage:
    pyinstaller EnergyTracker.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database/schema.sql', 'database'),
        ('database/__init__.py', 'database'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pydantic',
        'pydantic.types',
        'pydantic.fields',
        'pydantic.main',
        'pydantic_core',
        'sqlite3',
        'dateutil',
        'ui.main_window',
        'ui.settings_dialog',
        'ui.task_manager_window',
        'ui.exercise_manager_window',
        'ui.widgets',
        'ui.widgets.ring_chart',
        'ui.widgets.calendar_widget',
        'ui.widgets.task_checklist',
        'ui.widgets.exercise_checklist',
        'ui.widgets.exercise_progress_bar',
        'managers',
        'managers.exercise_manager',
        'managers.task_manager',
        'managers.event_manager',
        'models',
        'models.exercise',
        'models.task',
        'models.event',
        'database',
        'database.db_manager',
        'utils',
        'utils.config',
        'utils.date_helpers',
        'utils.settings_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EnergyTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # IMPORTANT: Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Uncomment if you have an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EnergyTracker',
)
