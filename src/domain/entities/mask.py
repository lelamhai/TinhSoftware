"""Mask entity."""
from dataclasses import dataclass
import numpy as np


@dataclass
class Mask:
    """Binary or probability mask."""
    
    # Mask data (H, W), values 0..1 (float32)
    data: np.ndarray
    
    # Metadata
    width: int
    height: int
    is_binary: bool = False  # True if thresholded, False if probabilities
    
    def __post_init__(self):
        """Validate mask."""
        if self.data.ndim != 2:
            raise ValueError(f"Expected 2D array (H, W), got {self.data.ndim}D")
        
        h, w = self.data.shape
        if h != self.height or w != self.width:
            raise ValueError(
                f"Data shape {(h, w)} doesn't match metadata {(self.height, self.width)}"
            )
        
        # Ensure values are in range [0, 1]
        if self.data.min() < 0 or self.data.max() > 1:
            raise ValueError("Mask values must be in range [0, 1]")
    
    @property
    def shape(self) -> tuple[int, int]:
        """Get mask shape (H, W)."""
        return self.data.shape
    
    def as_uint8(self) -> np.ndarray:
        """Convert to uint8 (0-255)."""
        return (self.data * 255).astype(np.uint8)
    
    def threshold(self, threshold: float = 0.5) -> "Mask":
        """Apply threshold to create binary mask."""
        binary_data = (self.data >= threshold).astype(np.float32)
        return Mask(
            data=binary_data,
            width=self.width,
            height=self.height,
            is_binary=True
        )
