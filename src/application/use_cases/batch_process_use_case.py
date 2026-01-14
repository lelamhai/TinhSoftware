"""Batch processing use case."""
from pathlib import Path
from dataclasses import dataclass
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from ..ports.background_removal_engine import BackgroundRemovalEngine
from ..ports.image_io import ImageIO
from ...domain.entities.image_output import ImageOutput
from ...domain.entities.settings import Settings
from .remove_background_use_case import RemoveBackgroundUseCase, RemoveBackgroundResult


@dataclass
class BatchProgress:
    """Progress information for batch processing."""
    total: int
    completed: int
    failed: int
    current_file: str
    elapsed_time_ms: float
    
    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        return (self.completed + self.failed) / self.total * 100 if self.total > 0 else 0.0
    
    @property
    def eta_ms(self) -> float:
        """Estimate time remaining in milliseconds."""
        if self.completed == 0:
            return 0.0
        avg_time = self.elapsed_time_ms / self.completed
        remaining = self.total - (self.completed + self.failed)
        return avg_time * remaining


@dataclass
class BatchResult:
    """Result of batch processing."""
    total: int
    successful: int
    failed: int
    results: List[RemoveBackgroundResult]
    errors: List[tuple[Path, str]]  # (file_path, error_message)
    total_time_ms: float
    
    @property
    def success_rate(self) -> float:
        """Get success rate percentage."""
        return self.successful / self.total * 100 if self.total > 0 else 0.0


class BatchProcessUseCase:
    """Use case for batch processing multiple images."""
    
    def __init__(
        self,
        engine: BackgroundRemovalEngine,
        image_io: ImageIO,
        settings: Settings,
        max_workers: int = 4
    ):
        """
        Initialize batch process use case.
        
        Args:
            engine: Background removal engine
            image_io: Image I/O adapter
            settings: Application settings
            max_workers: Maximum concurrent workers
        """
        self.engine = engine
        self.image_io = image_io
        self.settings = settings
        self.max_workers = max_workers
        self.use_case = RemoveBackgroundUseCase(engine, image_io, settings)
    
    async def execute(
        self,
        image_paths: List[Path],
        output_folder: Path,
        progress_callback=None
    ) -> BatchResult:
        """
        Execute batch processing.
        
        Args:
            image_paths: List of input image paths
            output_folder: Output folder for results
            progress_callback: Optional callback for progress updates
            
        Returns:
            BatchResult with statistics
        """
        start_time = time.perf_counter()
        
        # Ensure output folder exists
        output_folder.mkdir(parents=True, exist_ok=True)
        
        total = len(image_paths)
        completed = 0
        failed = 0
        results = []
        errors = []
        
        # Process images with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for image_path in image_paths:
                future = executor.submit(
                    self._process_single,
                    image_path,
                    output_folder
                )
                futures.append((image_path, future))
            
            # Collect results
            for image_path, future in futures:
                elapsed = (time.perf_counter() - start_time) * 1000
                
                # Update progress
                if progress_callback:
                    progress = BatchProgress(
                        total=total,
                        completed=completed,
                        failed=failed,
                        current_file=str(image_path.name),
                        elapsed_time_ms=elapsed
                    )
                    await progress_callback(progress)
                
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                except Exception as e:
                    errors.append((image_path, str(e)))
                    failed += 1
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        
        return BatchResult(
            total=total,
            successful=completed,
            failed=failed,
            results=results,
            errors=errors,
            total_time_ms=total_time
        )
    
    def _process_single(self, image_path: Path, output_folder: Path) -> RemoveBackgroundResult:
        """
        Process single image (runs in thread pool).
        
        Args:
            image_path: Input image path
            output_folder: Output folder
            
        Returns:
            RemoveBackgroundResult
        """
        # Run async use case in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Execute removal
            result = loop.run_until_complete(
                self.use_case.execute(image_path)
            )
            
            # Save output
            output_path = output_folder / f"{image_path.stem}_nobg.png"
            loop.run_until_complete(
                self.image_io.save_png_rgba(result.output, output_path)
            )
            
            return result
            
        finally:
            loop.close()
