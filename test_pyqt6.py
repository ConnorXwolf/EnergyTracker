"""
Minimal PyQt6 test to verify GUI framework works.

If this runs, PyQt6 is installed correctly.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

def main():
    try:
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        
        print("Creating window...")
        window = QMainWindow()
        window.setWindowTitle("PyQt6 Test")
        window.setGeometry(100, 100, 400, 200)
        
        label = QLabel("✓ PyQt6 is working!\n\nIf you see this, the GUI framework is OK.", window)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; padding: 20px;")
        window.setCentralWidget(label)
        
        print("Showing window...")
        window.show()
        
        print("✓ SUCCESS - Window should be visible")
        print("Close the window to exit.")
        
        return app.exec()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
