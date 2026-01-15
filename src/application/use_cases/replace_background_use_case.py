"""Replace background use case."""
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional
import time

from ..ports.background_removal_engine import BackgroundRemovalEngine
from ..ports.image_io import ImageIO
from ...domain.entities.image_output import ImageOutput
from ...domain.entities.settings import Settings
from ...domain.services.post_process_mask import PostProcessMask
from ...domain.services.background_replacer import BackgroundReplacer
from ...domain.services.auto_crop import AutoCrop


@dataclass
class ReplaceBackgroundResult:
    """Result of background replacement."""
    output: ImageOutput
    processing_time_ms: float
    crop_bounds: Optional[Tuple[int, int, int, int]] = None


class ReplaceBackgroundUseCase:
    """Use case for replacing image background."""
    
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
    
    async def execute_with_color(
        self,
        image_path: Path,
        color: Tuple[int, int, int]
    ) -> ReplaceBackgroundResult:
        """
        Replace background with solid color.
        
        Args:
            image_path: Input image path
            color: RGB color tuple (0-255)
            
        Returns:
            ReplaceBackgroundResult
        """
        start_time = time.perf_counter()
        
        # Step 1: Load image
        image_input = await self.image_io.load_image(image_path)
        
        # Step 2: Predict mask
        mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(mask, self.settings)
        
        # Step 4: Replace background
        output = BackgroundReplacer.replace_with_color(
            image_input,
            processed_mask,
            color,
            original_path=image_path
        )
        
        # Step 5: Auto-crop if enabled
        crop_bounds = None
        if self.settings.auto_crop_output:
            output, crop_bounds = AutoCrop.crop_to_content(output)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000
        
        return ReplaceBackgroundResult(
            output=output,
            processing_time_ms=processing_time,
            crop_bounds=crop_bounds
        )
    
    async def execute_with_image(
        self,
        image_path: Path,
        background_path: Path
    ) -> ReplaceBackgroundResult:
        """
        Replace background with another image.
        
        Args:
            image_path: Input image path
            background_path: Background image path
            
        Returns:
            ReplaceBackgroundResult
        """
        start_time = time.perf_counter()
        
        # Step 1: Load images
        image_input = await self.image_io.load_image(image_path)
        background_input = await self.image_io.load_image(background_path)
        
        # Step 2: Predict mask
        mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(mask, self.settings)
        
        # Step 4: Replace background
        output = BackgroundReplacer.replace_with_image(
            image_input,
            processed_mask,
            background_input,
            original_path=image_path
        )
        
        # Step 5: Auto-crop if enabled
        crop_bounds = None
        if self.settings.auto_crop_output:
            output, crop_bounds = AutoCrop.crop_to_content(output)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000
        
        return ReplaceBackgroundResult(
            output=output,
            processing_time_ms=processing_time,
            crop_bounds=crop_bounds
        )
    
    async def execute_with_blur(
        self,
        image_path: Path,
        blur_strength: int = 51
    ) -> ReplaceBackgroundResult:
        """
        Replace background with blurred version.
        
        Args:
            image_path: Input image path
            blur_strength: Blur kernel size (must be odd)
            
        Returns:
            ReplaceBackgroundResult
        """
        start_time = time.perf_counter()
        
        # Step 1: Load image
        image_input = await self.image_io.load_image(image_path)
        
        # Step 2: Predict mask
        mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(mask, self.settings)
        
        # Step 4: Replace background with blur
        output = BackgroundReplacer.replace_with_blur(
            image_input,
            processed_mask,
            blur_strength,
            original_path=image_path
        )
        
        # Step 5: Auto-crop if enabled
        crop_bounds = None
        if self.settings.auto_crop_output:
            output, crop_bounds = AutoCrop.crop_to_content(output)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000
        
        return ReplaceBackgroundResult(
            output=output,
            processing_time_ms=processing_time,
            crop_bounds=crop_bounds
        )
