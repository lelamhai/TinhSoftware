"""Image I/O port."""
from abc import ABC, abstractmethod
from pathlib import Path
from ...domain.entities.image_input import ImageInput
from ...domain.entities.image_output import ImageOutput


class ImageIO(ABC):
    """Port for image loading and saving."""
    
    @abstractmethod
    async def load_image(self, path: Path) -> ImageInput:
        """
        Load image from file.
        
        Args:
            path: Path to image file
            
        Returns:
            ImageInput entity
            
        Raises:
            InvalidImageError: If image is invalid or corrupted
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @abstractmethod
    async def save_png_rgba(self, output: ImageOutput, path: Path) -> None:
        """
        Save RGBA image as PNG with transparency.
        
        Args:
            output: Image output with alpha channel
            path: Destination path
            
        Raises:
            IOError: If save fails
        """
        pass
