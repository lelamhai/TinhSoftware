"""Settings store port."""
from abc import ABC, abstractmethod
from ...domain.entities.settings import Settings


class SettingsStore(ABC):
    """Port for settings persistence."""
    
    @abstractmethod
    def load(self) -> Settings:
        """
        Load settings from storage.
        
        Returns:
            Settings object, or default if not found
        """
        pass
    
    @abstractmethod
    def save(self, settings: Settings) -> None:
        """
        Save settings to storage.
        
        Args:
            settings: Settings to save
            
        Raises:
            IOError: If save fails
        """
        pass
