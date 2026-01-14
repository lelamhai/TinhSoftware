"""Main view model."""
from pathlib import Path
from typing import Optional

from src.application.use_cases.remove_background_use_case import (
    RemoveBackgroundUseCase,
    RemoveBackgroundResult
)
from src.application.ports.image_io import ImageIO
from src.domain.entities.settings import Settings


class MainViewModel:
    """View model for main window."""
    
    def __init__(
        self,
        use_case: RemoveBackgroundUseCase,
        image_io: ImageIO,
        settings: Settings
    ):
        """
        Initialize view model.
        
        Args:
            use_case: Remove background use case
            image_io: Image I/O adapter
            settings: Application settings
        """
        self.use_case = use_case
        self.image_io = image_io
        self.settings = settings
        self.last_result: Optional[RemoveBackgroundResult] = None
    
    async def remove_background(self, image_path: Path) -> RemoveBackgroundResult:
        """
        Remove background from image.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Result with output and metadata
        """
        result = await self.use_case.execute(image_path)
        self.last_result = result
        return result
    
    async def save_output(self, output_path: Path) -> None:
        """
        Save last result to file.
        
        Args:
            output_path: Destination path
        """
        if not self.last_result:
            raise ValueError("No result to save")
        
        await self.image_io.save_png_rgba(self.last_result.output, output_path)
