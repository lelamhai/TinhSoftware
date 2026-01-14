"""Export mask use case."""
from pathlib import Path
from dataclasses import dataclass
import time

from ..ports.background_removal_engine import BackgroundRemovalEngine
from ..ports.image_io import ImageIO
from ...domain.entities.image_output import ImageOutput
from ...domain.entities.settings import Settings
from ...domain.services.post_process_mask import PostProcessMask
from ...domain.services.mask_exporter import MaskExporter


@dataclass
class ExportMaskResult:
    """Result of mask export."""
    output: ImageOutput
    processing_time_ms: float
    format: str  # "grayscale", "binary", "alpha"


class ExportMaskUseCase:
    """Use case for exporting masks separately."""
    
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
    
    async def execute_grayscale(
        self,
        image_path: Path
    ) -> ExportMaskResult:
        """
        Export mask as grayscale PNG.
        
        Args:
            image_path: Input image path
            
        Returns:
            ExportMaskResult with grayscale mask
        """
        start_time = time.perf_counter()
        
        # Step 1: Load image
        image_input = await self.image_io.load_image(image_path)
        
        # Step 2: Predict mask
        mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(mask, self.settings)
        
        # Step 4: Export as grayscale
        output = MaskExporter.export_as_grayscale(processed_mask)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000
        
        return ExportMaskResult(
            output=output,
            processing_time_ms=processing_time,
            format="grayscale"
        )
    
    async def execute_binary(
        self,
        image_path: Path,
        threshold: float = 0.5
    ) -> ExportMaskResult:
        """
        Export mask as binary black/white PNG.
        
        Args:
            image_path: Input image path
            threshold: Binarization threshold (0-1)
            
        Returns:
            ExportMaskResult with binary mask
        """
        start_time = time.perf_counter()
        
        # Step 1: Load image
        image_input = await self.image_io.load_image(image_path)
        
        # Step 2: Predict mask
        mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(mask, self.settings)
        
        # Step 4: Export as binary
        output = MaskExporter.export_as_binary(processed_mask, threshold)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000
        
        return ExportMaskResult(
            output=output,
            processing_time_ms=processing_time,
            format="binary"
        )
    
    async def execute_alpha(
        self,
        image_path: Path
    ) -> ExportMaskResult:
        """
        Export mask as alpha-only PNG.
        
        Args:
            image_path: Input image path
            
        Returns:
            ExportMaskResult with alpha mask
        """
        start_time = time.perf_counter()
        
        # Step 1: Load image
        image_input = await self.image_io.load_image(image_path)
        
        # Step 2: Predict mask
        mask = await self.engine.predict_mask(image_input)
        
        # Step 3: Post-process mask
        processed_mask = PostProcessMask.apply(mask, self.settings)
        
        # Step 4: Export as alpha
        output = MaskExporter.export_as_alpha_only(processed_mask)
        
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000
        
        return ExportMaskResult(
            output=output,
            processing_time_ms=processing_time,
            format="alpha"
        )
