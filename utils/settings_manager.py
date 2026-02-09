"""
Settings manager for UI customization.

Stores and retrieves user preferences for interface scaling
and text size adjustments.
"""

import json
from pathlib import Path
from typing import Dict, Any


class SettingsManager:
    """
    Manages application settings with file persistence.
    
    Singleton pattern ensures consistent settings across application.
    """
    
    _instance = None
    _settings_file = Path.cwd() / "settings.json"
    
    # Default settings
    _default_settings = {
        'ui_scale': 1.0,          # Interface scale multiplier (0.5 - 2.0)
        'text_size_offset': 0,    # Text size adjustment (-10 to +10)
        'window_width': 1200,
        'window_height': 800
    }
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize settings manager and load settings."""
        if self._initialized:
            return
        
        self._settings = self._load_settings()
        self._initialized = True
    
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file or use defaults.
        
        Returns:
            Dictionary of settings
        """
        try:
            if self._settings_file.exists():
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    return {**self._default_settings, **loaded}
            else:
                return self._default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self._default_settings.copy()
    
    def _save_settings(self) -> bool:
        """
        Save current settings to file.
        
        Returns:
            True if saved successfully
        """
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set setting value and save to file.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if saved successfully
        """
        self._settings[key] = value
        return self._save_settings()
    
    def get_ui_scale(self) -> float:
        """Get UI scale multiplier (0.5 - 2.0)."""
        return self._settings.get('ui_scale', 1.0)
    
    def set_ui_scale(self, scale: float) -> bool:
        """
        Set UI scale multiplier.
        
        Args:
            scale: Scale value (0.5 - 2.0)
            
        Returns:
            True if saved successfully
        """
        # Clamp to valid range
        scale = max(0.5, min(2.0, scale))
        return self.set('ui_scale', scale)
    
    def get_text_size_offset(self) -> int:
        """Get text size adjustment offset (-10 to +10)."""
        return self._settings.get('text_size_offset', 0)
    
    def set_text_size_offset(self, offset: int) -> bool:
        """
        Set text size adjustment offset.
        
        Args:
            offset: Size adjustment (-10 to +10)
            
        Returns:
            True if saved successfully
        """
        # Clamp to valid range
        offset = max(-10, min(10, offset))
        return self.set('text_size_offset', offset)
    
    def get_window_size(self) -> tuple[int, int]:
        """
        Get saved window dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        width = self._settings.get('window_width', 1200)
        height = self._settings.get('window_height', 800)
        return (width, height)
    
    def set_window_size(self, width: int, height: int) -> bool:
        """
        Save window dimensions.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            
        Returns:
            True if saved successfully
        """
        self._settings['window_width'] = width
        self._settings['window_height'] = height
        return self._save_settings()
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to default values.
        
        Returns:
            True if reset successfully
        """
        self._settings = self._default_settings.copy()
        return self._save_settings()
