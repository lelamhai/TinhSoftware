"""Post-process mask service."""
import numpy as np
import cv2
from ..entities.mask import Mask
from ..entities.settings import Settings


class PostProcessMask:
    """Domain service for mask post-processing."""
    
    @staticmethod
    def apply(mask: Mask, settings: Settings) -> Mask:
        """
        Apply post-processing to mask.
        
        Args:
            mask: Input mask (probabilities or binary)
            settings: Processing settings
            
        Returns:
            Processed mask
        """
        processed_data = mask.data.copy()
        
        # 1. Threshold if not already binary
        if not mask.is_binary and settings.threshold > 0:
            processed_data = (processed_data >= settings.threshold).astype(np.float32)
        
        # 2. Morphological smoothing (remove noise)
        if settings.smooth_pixels > 0:
            kernel_size = settings.smooth_pixels * 2 + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            
            # Convert to uint8 for morphological operations
            mask_uint8 = (processed_data * 255).astype(np.uint8)
            
            # Open (erosion + dilation) to remove small noise
            mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Close (dilation + erosion) to fill small holes
            mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            processed_data = mask_uint8.astype(np.float32) / 255.0
        
        # 3. Feathering (edge blur for smooth transition)
        if settings.feather_pixels > 0:
            # Convert to uint8
            mask_uint8 = (processed_data * 255).astype(np.uint8)
            
            # Gaussian blur for soft edges
            kernel_size = settings.feather_pixels * 2 + 1
            blurred = cv2.GaussianBlur(mask_uint8, (kernel_size, kernel_size), 0)
            
            processed_data = blurred.astype(np.float32) / 255.0
        
        return Mask(
            data=processed_data,
            width=mask.width,
            height=mask.height,
            is_binary=False  # After feathering, no longer strictly binary
        )
