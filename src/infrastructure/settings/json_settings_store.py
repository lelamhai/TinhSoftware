"""JSON settings store implementation."""
import json
from pathlib import Path
from ...application.ports.settings_store import SettingsStore
from ...domain.entities.settings import Settings


class JsonSettingsStore(SettingsStore):
    """Settings store using JSON file."""
    
    def __init__(self, settings_path: Path | None = None):
        """
        Initialize JSON settings store.
        
        Args:
            settings_path: Path to settings file. If None, uses default location.
        """
        if settings_path is None:
            # Default: ~/.config/removebg/settings.json on Linux/Mac
            # or %APPDATA%/removebg/settings.json on Windows
            config_dir = Path.home() / '.config' / 'removebg'
            settings_path = config_dir / 'settings.json'
        
        self.settings_path = Path(settings_path)
    
    def load(self) -> Settings:
        """Load settings from JSON file."""
        if not self.settings_path.exists():
            return Settings.default()
        
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert model_path string to Path
            if 'model_path' in data:
                data['model_path'] = Path(data['model_path'])
            
            return Settings(**data)
            
        except Exception:
            # If loading fails, return default
            return Settings.default()
    
    def save(self, settings: Settings) -> None:
        """Save settings to JSON file."""
        # Ensure directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert Settings to dict
        data = {
            'model_path': str(settings.model_path),
            'execution_provider': settings.execution_provider,
            'threshold': settings.threshold,
            'smooth_pixels': settings.smooth_pixels,
            'feather_pixels': settings.feather_pixels,
            'preview_background': settings.preview_background,
            'default_save_folder': settings.default_save_folder,
            'auto_crop_output': settings.auto_crop_output,
        }
        
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
