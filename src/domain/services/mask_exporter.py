"""Mask export service."""
import numpy as np

from ..entities.mask import Mask
from ..entities.image_output import ImageOutput


class MaskExporter:
    """Service for exporting masks in various formats."""
    
    @staticmethod
    def export_as_grayscale(mask: Mask) -> ImageOutput:
        """
        Export mask as grayscale PNG (0-255).
        
        Args:
            mask: Mask to export
            
        Returns:
            ImageOutput with grayscale mask
        """
        # Normalize mask to 0-255
        mask_data = mask.data.astype(np.float32)
        if mask_data.max() <= 1.0:
            mask_data = mask_data * 255.0
        
        # Ensure 2D
        if mask_data.ndim == 3:
            mask_data = mask_data[:, :, 0]
        
        mask_uint8 = np.clip(mask_data, 0, 255).astype(np.uint8)
        
        # Convert to RGB (grayscale)
        rgb = np.stack([mask_uint8, mask_uint8, mask_uint8], axis=2)
        
        # Add alpha channel (full opacity)
        rgba = np.dstack([rgb, np.full_like(mask_uint8, 255)])
        
        return ImageOutput(
            data=rgba,
            width=mask.width,
            height=mask.height,
            format="RGBA"
        )
    
    @staticmethod
    def export_as_binary(mask: Mask, threshold: float = 0.5) -> ImageOutput:
        """
        Export mask as binary black/white PNG.
        
        Args:
            mask: Mask to export
            threshold: Threshold for binarization (0-1)
            
        Returns:
            ImageOutput with binary mask
        """
        # Normalize mask to 0-1
        mask_data = mask.data.astype(np.float32)
        if mask_data.max() > 1.0:
            mask_data = mask_data / 255.0
        
        # Ensure 2D
        if mask_data.ndim == 3:
            mask_data = mask_data[:, :, 0]
        
        # Binarize
        binary = (mask_data >= threshold).astype(np.uint8) * 255
        
        # Convert to RGB
        rgb = np.stack([binary, binary, binary], axis=2)
        
        # Add alpha channel (full opacity)
        rgba = np.dstack([rgb, np.full_like(binary, 255)])
        
        return ImageOutput(
            data=rgba,
            width=mask.width,
            height=mask.height,
            format="RGBA"
        )
    
    @staticmethod
    def export_as_alpha_only(mask: Mask) -> ImageOutput:
        """
        Export mask as alpha-only PNG (transparent = black, opaque = white).
        
        Args:
            mask: Mask to export
            
        Returns:
            ImageOutput with alpha channel representing mask
        """
        # Normalize mask to 0-255
        mask_data = mask.data.astype(np.float32)
        if mask_data.max() <= 1.0:
            mask_data = mask_data * 255.0
        
        # Ensure 2D
        if mask_data.ndim == 3:
            mask_data = mask_data[:, :, 0]
        
        mask_uint8 = np.clip(mask_data, 0, 255).astype(np.uint8)
        
        # Create white RGB with mask as alpha
        white = np.full((mask.height, mask.width, 3), 255, dtype=np.uint8)
        rgba = np.dstack([white, mask_uint8])
        
        return ImageOutput(
            data=rgba,
            width=mask.width,
            height=mask.height,
            format="RGBA"
        )
