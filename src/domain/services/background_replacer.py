"""Background replacement service."""
import numpy as np
from typing import Tuple, Optional
from pathlib import Path

from ..entities.image_input import ImageInput
from ..entities.image_output import ImageOutput
from ..entities.mask import Mask


class BackgroundReplacer:
    """Service for replacing image backgrounds."""
    
    @staticmethod
    def replace_with_color(
        original: ImageInput,
        mask: Mask,
        color: Tuple[int, int, int],
        original_path: Path = None
    ) -> ImageOutput:
        """
        Replace background with solid color.
        
        Args:
            original: Original RGB image
            mask: Foreground mask (0-1, float)
            color: RGB color tuple (0-255)
            original_path: Path to original image file
            
        Returns:
            ImageOutput with replaced background
        """
        # Ensure mask is same size as image
        if mask.data.shape[:2] != (original.height, original.width):
            raise ValueError("Mask size must match image size")
        
        # Get RGB data
        rgb = original.data[:, :, :3].astype(np.float32)
        
        # Normalize mask to 0-1
        alpha = mask.data.astype(np.float32)
        if alpha.max() > 1.0:
            alpha = alpha / 255.0
        
        # Ensure alpha is 2D
        if alpha.ndim == 3:
            alpha = alpha[:, :, 0]
        
        # Expand alpha to 3 channels
        alpha_3ch = np.expand_dims(alpha, axis=2)
        
        # Create background with color
        background = np.full_like(rgb, color, dtype=np.float32)
        
        # Composite: foreground * alpha + background * (1 - alpha)
        result = rgb * alpha_3ch + background * (1 - alpha_3ch)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Create RGBA output (with full alpha)
        rgba = np.dstack([result, np.full((original.height, original.width), 255, dtype=np.uint8)])
        
        return ImageOutput(
            data=rgba,
            width=original.width,
            height=original.height,
            original_path=original_path or Path("output.png")
        )
    
    @staticmethod
    def replace_with_image(
        original: ImageInput,
        mask: Mask,
        background_image: ImageInput,
        original_path: Path = None
    ) -> ImageOutput:
        """
        Replace background with another image.
        
        Args:
            original: Original RGB image
            mask: Foreground mask (0-1, float)
            background_image: Background image (will be resized to match)
            original_path: Path to original image file
            
        Returns:
            ImageOutput with replaced background
        """
        # Ensure mask is same size as image
        if mask.data.shape[:2] != (original.height, original.width):
            raise ValueError("Mask size must match image size")
        
        # Get RGB data
        rgb = original.data[:, :, :3].astype(np.float32)
        
        # Normalize mask to 0-1
        alpha = mask.data.astype(np.float32)
        if alpha.max() > 1.0:
            alpha = alpha / 255.0
        
        # Ensure alpha is 2D
        if alpha.ndim == 3:
            alpha = alpha[:, :, 0]
        
        # Expand alpha to 3 channels
        alpha_3ch = np.expand_dims(alpha, axis=2)
        
        # Resize background to match original
        import cv2
        bg_data = background_image.data[:, :, :3].astype(np.float32)
        if (background_image.height, background_image.width) != (original.height, original.width):
            bg_data = cv2.resize(
                bg_data,
                (original.width, original.height),
                interpolation=cv2.INTER_LANCZOS4
            )
        
        # Composite: foreground * alpha + background * (1 - alpha)
        result = rgb * alpha_3ch + bg_data * (1 - alpha_3ch)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Create RGBA output (with full alpha)
        rgba = np.dstack([result, np.full((original.height, original.width), 255, dtype=np.uint8)])
        
        return ImageOutput(
            data=rgba,
            width=original.width,
            height=original.height,
            original_path=original_path or Path("output.png")
        )
    
    @staticmethod
    def replace_with_blur(
        original: ImageInput,
        mask: Mask,
        blur_strength: int = 51,
        original_path: Path = None
    ) -> ImageOutput:
        """
        Replace background with blurred version of original.
        
        Args:
            original: Original RGB image
            mask: Foreground mask (0-1, float)
            blur_strength: Gaussian blur kernel size (must be odd)
            original_path: Path to original image file
            
        Returns:
            ImageOutput with blurred background
        """
        import cv2
        
        # Ensure mask is same size as image
        if mask.data.shape[:2] != (original.height, original.width):
            raise ValueError("Mask size must match image size")
        
        # Ensure blur strength is odd
        if blur_strength % 2 == 0:
            blur_strength += 1
        
        # Get RGB data
        rgb = original.data[:, :, :3].astype(np.float32)
        
        # Normalize mask to 0-1
        alpha = mask.data.astype(np.float32)
        if alpha.max() > 1.0:
            alpha = alpha / 255.0
        
        # Ensure alpha is 2D
        if alpha.ndim == 3:
            alpha = alpha[:, :, 0]
        
        # Expand alpha to 3 channels
        alpha_3ch = np.expand_dims(alpha, axis=2)
        
        # Create blurred background
        blurred = cv2.GaussianBlur(
            rgb.astype(np.uint8),
            (blur_strength, blur_strength),
            0
        ).astype(np.float32)
        
        # Composite: foreground * alpha + blurred * (1 - alpha)
        result = rgb * alpha_3ch + blurred * (1 - alpha_3ch)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Create RGBA output (with full alpha)
        rgba = np.dstack([result, np.full((original.height, original.width), 255, dtype=np.uint8)])
        
        return ImageOutput(
            data=rgba,
            width=original.width,
            height=original.height,
            original_path=original_path or Path("output.png")
        )
