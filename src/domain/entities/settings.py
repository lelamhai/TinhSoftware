"""Settings entity."""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ExecutionProvider = Literal["CPU", "CUDA", "DirectML"]


@dataclass
class Settings:
    """Application settings."""
    
    # Model settings
    model_path: Path
    execution_provider: ExecutionProvider = "CPU"
    
    # Post-processing settings
    threshold: float = 0.5
    smooth_pixels: int = 2
    feather_pixels: int = 1
    
    # UI settings
    preview_background: str = "checkerboard"  # checkerboard, white, black
    default_save_folder: str = ""  # Empty = ask each time
    auto_crop_output: bool = False
    
    def __post_init__(self):
        """Validate settings."""
        if not isinstance(self.model_path, Path):
            self.model_path = Path(self.model_path)
        
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        if self.smooth_pixels < 0:
            raise ValueError("Smooth pixels must be >= 0")
        
        if self.feather_pixels < 0:
            raise ValueError("Feather pixels must be >= 0")
    
    @staticmethod
    def default() -> "Settings":
        """Create default settings."""
        return Settings(
            model_path=Path("assets/models/birefnet.onnx"),
            execution_provider="CPU",
            threshold=0.5,
            smooth_pixels=2,
            feather_pixels=1,
            preview_background="checkerboard",
            default_save_folder="",
            auto_crop_output=False
        )
