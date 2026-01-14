"""Image input entity."""
from dataclasses import dataclass
import numpy as np
from pathlib import Path


@dataclass
class ImageInput:
    """Input image data."""
    
    # Original image data (RGB, uint8)
    data: np.ndarray
    
    # Image metadata
    width: int
    height: int
    file_path: Path
    
    def __post_init__(self):
        """Validate image input."""
        if self.data.ndim != 3:
            raise ValueError(f"Expected 3D array (H, W, C), got {self.data.ndim}D")
        
        h, w, c = self.data.shape
        if c != 3:
            raise ValueError(f"Expected 3 channels (RGB), got {c}")
        
        if h != self.height or w != self.width:
            raise ValueError(
                f"Data shape {(h, w)} doesn't match metadata {(self.height, self.width)}"
            )
        
        if not isinstance(self.file_path, Path):
            self.file_path = Path(self.file_path)
    
    @property
    def shape(self) -> tuple[int, int, int]:
        """Get image shape (H, W, C)."""
        return self.data.shape
    
    @property
    def size_mb(self) -> float:
        """Get image size in MB."""
        return self.data.nbytes / (1024 * 1024)
