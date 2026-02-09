"""
Energy Tracker application entry point.

Initializes the PyQt6 application and launches the main window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui import MainWindow
from utils import APP_NAME


def main():
    """
    Application entry point.
    
    Initializes Qt application, creates main window, and starts event loop.
    
    Returns:
        Exit code from Qt application
    """
    try:
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Create application instance
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        return app.exec()
        
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
