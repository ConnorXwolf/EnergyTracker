"""
Settings dialog for UI customization.

Provides interface for adjusting UI scale and text size with
live preview and reset options.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QPushButton, QGroupBox, QFormLayout,
    QDialogButtonBox, QSpinBox, QWidget, QApplication  # ← 添加 QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication  # ← 添加 QCoreApplication
from PyQt6.QtGui import QFont

from utils.settings_manager import SettingsManager


class SettingsDialog(QDialog):
    """
    Settings dialog for UI customization.
    
    Allows users to adjust interface scaling and text sizes
    with immediate preview and persistent storage.
    
    Signals:
        settings_changed: Emitted when settings are applied
    """
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._settings = SettingsManager()
        
        self.setWindowTitle("Interface Settings")
        self.setModal(True)
        self.setMinimumWidth(600)   
        self.setMinimumHeight(500)  
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self) -> None:
        """Initialize dialog UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Customize Interface")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # UI Scale Section
        scale_group = self._create_scale_section()
        layout.addWidget(scale_group)
        
        # Text Size Section
        text_group = self._create_text_size_section()
        layout.addWidget(text_group)
        
        # Preview label
        self.preview_label = QLabel("Preview: Sample Text")
        self.preview_label.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 4px;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._apply_and_close)
        button_box.rejected.connect(self.reject)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(button_box)
        
        layout.addLayout(button_layout)
    
    def _create_scale_section(self) -> QGroupBox:
        """
        Create UI scale adjustment section.
        
        Returns:
            QGroupBox containing scale controls
        """
        group = QGroupBox("Interface Scale (Magnitude)")
        form = QFormLayout(group)
        
        # Scale slider
        scale_layout = QHBoxLayout()
        
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(50)   # 0.5x
        self.scale_slider.setMaximum(200)  # 2.0x
        self.scale_slider.setValue(100)    # 1.0x default
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.setTickInterval(25)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        
        self.scale_value_label = QLabel("100%")
        self.scale_value_label.setMinimumWidth(50)
        self.scale_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_value_label)
        
        form.addRow("Scale:", scale_layout)
        
        return group
    
    def _create_text_size_section(self) -> QGroupBox:
        """
        Create text size adjustment section.
        
        Returns:
            QGroupBox containing text size controls
        """
        group = QGroupBox("Text Size")
        form = QFormLayout(group)
        
        # Text size spinbox
        size_layout = QHBoxLayout()
        
        self.text_size_spinbox = QSpinBox()
        self.text_size_spinbox.setMinimum(-10)
        self.text_size_spinbox.setMaximum(10)
        self.text_size_spinbox.setValue(0)
        self.text_size_spinbox.setSuffix(" pt")
        self.text_size_spinbox.valueChanged.connect(self._on_text_size_changed)
        
        size_layout.addWidget(self.text_size_spinbox)
        size_layout.addStretch()
              
        form.addRow("Size Adjustment:", size_layout)

        return group
    
    def _load_current_settings(self) -> None:
        """Load current settings into UI controls."""
        # Load scale
        scale = self._settings.get_ui_scale()
        self.scale_slider.setValue(int(scale * 100))
        
        # Load text size offset
        offset = self._settings.get_text_size_offset()
        self.text_size_spinbox.setValue(offset)
        
        # Update preview
        self._update_preview()
    
    def _on_scale_changed(self, value: int) -> None:
        """
        Handle scale slider change.
        
        Args:
            value: Slider value (50-200)
        """
        scale = value / 100.0
        self.scale_value_label.setText(f"{value}%")
        self._update_preview()
    
    def _on_text_size_changed(self, value: int) -> None:
        """
        Handle text size change.
        
        Args:
            value: Size offset (-4 to +8)
        """
        self._update_preview()
    
    def _update_preview(self) -> None:
        """Update preview label with current settings."""
        scale = self.scale_slider.value() / 100.0
        text_offset = self.text_size_spinbox.value()
        
        # Calculate preview text size
        base_size = 12
        preview_size = int(base_size * scale) + text_offset
        
        # Apply to preview
        font = self.preview_label.font()
        font.setPointSize(max(8, preview_size))  # Minimum 8pt
        self.preview_label.setFont(font)
    
    def _reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.scale_slider.setValue(100)
        self.text_size_spinbox.setValue(0)
        self._update_preview()

    def _apply_and_close(self) -> None:
        """Save settings to storage and close dialog."""
        # Save scale
        scale = self.scale_slider.value() / 100.0
        self._settings.set_ui_scale(scale)
        
        # Save text size offset
        offset = self.text_size_spinbox.value()
        self._settings.set_text_size_offset(offset)
        
        print(f"[SettingsDialog] Settings saved: scale={scale:.2f}, offset={offset:+d}")
        
        # ========== CRITICAL: Just close, don't emit signal ==========
        # Parent will apply settings after dialog closes
        self.accept()
        # =============================================================
    
    def get_current_scale(self) -> float:
        """
        Get current scale value from slider.
        
        Returns:
            Scale multiplier (0.5 - 2.0)
        """
        return self.scale_slider.value() / 100.0
    
    def get_current_text_offset(self) -> int:
        """
        Get current text size offset from spinbox.
        
        Returns:
            Text size offset (-4 to +8)
        """
        return self.text_size_spinbox.value()
