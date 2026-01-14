"""Image output entity."""
from dataclasses import dataclass
import numpy as np
from pathlib import Path


@dataclass
class ImageOutput:
    """Output image with alpha channel."""
    
    # RGBA image data (uint8)
    data: np.ndarray
    
    # Metadata
    width: int
    height: int
    original_path: Path
    
    def __post_init__(self):
        """Validate image output."""
        if self.data.ndim != 3:
            raise ValueError(f"Expected 3D array (H, W, C), got {self.data.ndim}D")
        
        h, w, c = self.data.shape
        if c != 4:
            raise ValueError(f"Expected 4 channels (RGBA), got {c}")
        
        if h != self.height or w != self.width:
            raise ValueError(
                f"Data shape {(h, w)} doesn't match metadata {(self.height, self.width)}"
            )
        
        if not isinstance(self.original_path, Path):
            self.original_path = Path(self.original_path)
    
    @property
    def shape(self) -> tuple[int, int, int]:
        """Get image shape (H, W, C)."""
        return self.data.shape
    
    @property
    def rgb(self) -> np.ndarray:
        """Get RGB channels only."""
        return self.data[:, :, :3]
    
    @property
    def alpha(self) -> np.ndarray:
        """Get alpha channel only."""
        return self.data[:, :, 3]
    
    @property
    def size_mb(self) -> float:
        """Get image size in MB."""
        return self.data.nbytes / (1024 * 1024)
