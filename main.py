"""
Energy Tracker Application Entry Point.

Initializes application paths, creates Qt application with global
font settings, and launches the main window.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui import MainWindow
from utils import APP_NAME


def get_base_path() -> Path:
    """
    Get base application path (handles PyInstaller bundling).
    
    Returns:
        Path: Base directory path
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


def get_data_path() -> Path:
    """
    Get data directory path for database and reports.
    
    Returns:
        Path: Data directory path
    """
    return get_base_path() / "data"


def initialize_application_directories() -> None:
    """
    Create required application directories if they don't exist.
    
    Creates:
        - data/: For database storage
        - data/history/: For monthly reports
    """
    data_path = get_data_path()
    data_path.mkdir(exist_ok=True)
    
    history_path = data_path / "history"
    history_path.mkdir(exist_ok=True)


def configure_application_paths() -> None:
    """
    Configure global application paths for cross-module access.
    
    Notes:
        This function should be called before importing modules that
        depend on path configurations (e.g., DatabaseManager).
    """
    # Store paths as environment-like globals for cross-module access
    import os
    os.environ['APP_BASE_PATH'] = str(get_base_path())
    os.environ['APP_DATA_PATH'] = str(get_data_path())


def apply_global_font_settings(app: QApplication) -> None:
    """
    Apply persistent font settings to entire application.
    
    This ensures all widgets (including dynamically created ones)
    inherit the correct font configuration without needing
    individual widget-level application.
    
    Args:
        app: QApplication instance to apply settings to
    """
    from utils import SettingsManager
    
    settings = SettingsManager()
    scale = settings.get_ui_scale()
    text_offset = settings.get_text_size_offset()
    
    # Create global font with user settings
    base_font = QFont()
    base_font.setFamily("Segoe UI")  # Professional, widely available font
    
    base_size = 12
    adjusted_size = int(base_size * scale) + text_offset
    adjusted_size = max(8, adjusted_size)  # Enforce minimum readable size
    
    base_font.setPointSize(adjusted_size)
    
    # Apply to application - affects ALL widgets
    app.setFont(base_font)
    
    print(f"[Settings] Global font applied: {adjusted_size}pt (scale={scale:.2f}, offset={text_offset:+d})")


def main() -> int:
    """
    Application entry point.
    
    Initializes Qt application, configures paths, applies global settings,
    creates main window, and starts the event loop.
    
    Returns:
        int: Exit code from Qt application (0 for success)
        
    Raises:
        RuntimeError: If critical initialization fails
    """
    try:
        # Phase 1: Configure application paths
        configure_application_paths()
        
        # Phase 2: Initialize directory structure
        initialize_application_directories()
        
        # Phase 3: Configure Qt for high DPI displays
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Phase 4: Create application instance
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        
        # Phase 5: Apply global font settings BEFORE window creation
        # This ensures all widgets inherit correct fonts
        apply_global_font_settings(app)
        
        # Phase 6: Create and display main window
        window = MainWindow()
        window.show()
        
        # Phase 7: Start event loop
        return app.exec()
        
    except RuntimeError as e:
        print(f"Critical initialization error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Fatal error starting application: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
