"""
Energy Tracker application entry point.

Initializes the PyQt6 application and launches the main window with
proper path handling for both development and PyInstaller frozen environments.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui import MainWindow
from utils import APP_NAME


def get_base_path() -> Path:
    """
    Get the application's base directory path.
    
    Returns:
        Path: Base directory - _MEIPASS in frozen mode, script directory otherwise
    
    Notes:
        PyInstaller extracts bundled files to sys._MEIPASS temporary directory.
        This path should be used for read-only resources (icons, templates).
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Frozen/Packaged environment
        return Path(sys._MEIPASS)
    else:
        # Development environment
        return Path(__file__).parent.resolve()


def get_data_path() -> Path:
    """
    Get the user data directory path for persistent storage.
    
    Returns:
        Path: Directory for database and user-generated files
    
    Notes:
        Database and history files must be stored outside the bundled
        executable to persist across application restarts.
    """
    if getattr(sys, 'frozen', False):
        # Frozen: Use executable's parent directory
        return Path(sys.executable).parent / 'data'
    else:
        # Development: Use project root
        return Path(__file__).parent / 'data'


def initialize_application_directories() -> None:
    """
    Create required directory structure for application data.
    
    Creates:
        - data/: Root data directory
        - data/history/: Historical reports storage
    
    Raises:
        OSError: If directory creation fails due to permission or disk issues
        
    Notes:
        Uses exist_ok=True to safely handle pre-existing directories.
    """
    try:
        data_dir = get_data_path()
        history_dir = data_dir / 'history'
        
        # Create directories with proper permissions
        history_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Data directory initialized: {data_dir}")
        
    except OSError as e:
        error_msg = f"Failed to initialize application directories: {e}"
        print(error_msg, file=sys.stderr)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during directory initialization: {e}"
        print(error_msg, file=sys.stderr)
        raise RuntimeError(error_msg) from e


def configure_application_paths() -> None:
    """
    Configure global path constants for the application.
    
    Notes:
        This function should be called before importing modules that
        depend on path configurations (e.g., DatabaseManager).
    """
    # Store paths as environment-like globals for cross-module access
    import os
    os.environ['APP_BASE_PATH'] = str(get_base_path())
    os.environ['APP_DATA_PATH'] = str(get_data_path())


def main() -> int:
    """
    Application entry point.
    
    Initializes Qt application, configures paths, creates main window,
    and starts the event loop.
    
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
        
        # Phase 3: Configure Qt application
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Phase 4: Create application instance
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        
        # Phase 5: Create and display main window
        window = MainWindow()
        window.show()
        
        # Phase 6: Start event loop
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
