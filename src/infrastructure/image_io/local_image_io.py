"""Local image I/O implementation using Pillow."""
from pathlib import Path
from PIL import Image
import numpy as np

from ...application.ports.image_io import ImageIO
from ...domain.entities.image_input import ImageInput
from ...domain.entities.image_output import ImageOutput
from ...domain.errors.exceptions import InvalidImageError


class LocalImageIO(ImageIO):
    """Image I/O using Pillow (PIL)."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    
    async def load_image(self, path: Path) -> ImageInput:
        """Load image from file."""
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise InvalidImageError(
                f"Unsupported format {path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            # Load image with Pillow
            pil_image = Image.open(path)
            
            # Convert to RGB (handle RGBA, L, etc.)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array (H, W, 3) uint8
            image_array = np.array(pil_image)
            
            height, width = image_array.shape[:2]
            
            return ImageInput(
                data=image_array,
                width=width,
                height=height,
                file_path=path
            )
            
        except Exception as e:
            raise InvalidImageError(f"Failed to load image {path}: {e}")
    
    async def save_png_rgba(self, output: ImageOutput, path: Path) -> None:
        """Save RGBA image as PNG with transparency."""
        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(output.data, mode='RGBA')
            
            # Save as PNG (PNG supports transparency)
            pil_image.save(path, format='PNG', optimize=True)
            
        except Exception as e:
            raise IOError(f"Failed to save image to {path}: {e}")
