"""Remove background use case."""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import time

from ..ports.background_removal_engine import BackgroundRemovalEngine
from ..ports.image_io import ImageIO
from ...domain.entities.image_output import ImageOutput
from ...domain.entities.settings import Settings
from ...domain.services.post_process_mask import PostProcessMask
from ...domain.services.alpha_compose import AlphaCompose
from ...domain.services.auto_crop import AutoCrop


@dataclass
class RemoveBackgroundResult:
    """Result of background removal operation."""
    output: ImageOutput
    processing_time_ms: float
    input_size: tuple[int, int]  # (width, height)
    output_size_mb: float
    was_cropped: bool = False
    crop_bounds: tuple[int, int, int, int] | None = None  # (x, y, width, height)
    raw_mask: any = None  # Raw mask from AI (before post-processing)
    original_image: any = None  # Original ImageInput for reprocessing


class RemoveBackgroundUseCase:
    """Use case for removing background from images."""
    
    def __init__(
        self,
        engine: BackgroundRemovalEngine,
        image_io: ImageIO,
        settings: Settings
    ):
        """
        Initialize use case.
        
        Args:
            engine: Background removal engine
            image_io: Image I/O adapter
            settings: Application settings
        """
        self.engine = engine
        self.image_io = image_io
        self.settings = settings
    
    async def execute(self, image_path: Path) -> RemoveBackgroundResult:
        """
        Execute background removal pipeline.
        
        Args:
            image_path: Path to input image
            
        Returns:
            RemoveBackgroundResult with output and metadata
            
        Raises:
            FileNotFoundError: If image not found
            InvalidImageError: If image is invalid
            InferenceFailedError: If inference fails
        """
        start_time = time.perf_counter()
        
        # Step 1: Load image
        image_input = await self.image_io.load_image(image_path)
        
        # Step 2: Predict mask
        raw_mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(raw_mask, self.settings)
        
        # Step 4: Compose RGBA
        output = AlphaCompose.compose(image_input, processed_mask)
        
        # Step 5: Auto-crop if enabled
        was_cropped = False
        crop_bounds = None
        if self.settings.auto_crop_output:
            crop_bounds = AutoCrop.get_crop_bounds(output)
            output = AutoCrop.crop_to_content(output)
            was_cropped = True
        
        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000
        
        return RemoveBackgroundResult(
            output=output,
            processing_time_ms=processing_time_ms,
            input_size=(image_input.width, image_input.height),
            output_size_mb=output.size_mb,
            was_cropped=was_cropped,
            crop_bounds=crop_bounds,
            raw_mask=raw_mask,
            original_image=image_input
        )
