"""Image preprocessing utilities."""
import numpy as np
import cv2
from typing import Tuple


class ImagePreprocessor:
    """Preprocess images for ONNX model input."""
    
    def __init__(
        self,
        target_size: int = 1024,
        mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
        normalize: bool = True
    ):
        """
        Initialize preprocessor.
        
        Args:
            target_size: Target size for model input (assumed square)
            mean: Mean values for normalization (RGB)
            std: Std values for normalization (RGB)
            normalize: Whether to apply normalization
        """
        self.target_size = target_size
        self.mean = np.array(mean, dtype=np.float32).reshape(1, 1, 3)
        self.std = np.array(std, dtype=np.float32).reshape(1, 1, 3)
        self.normalize = normalize
    
    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image (H, W, 3) uint8 RGB
            
        Returns:
            Tuple of:
                - Preprocessed tensor (1, 3, H, W) float32 NCHW
                - Original size (height, width)
        """
        original_size = image.shape[:2]  # (H, W)
        
        # Resize to target size
        resized = cv2.resize(
            image,
            (self.target_size, self.target_size),
            interpolation=cv2.INTER_LINEAR
        )
        
        # Convert to float32 and scale to [0, 1]
        image_float = resized.astype(np.float32) / 255.0
        
        # Normalize if enabled
        if self.normalize:
            image_float = (image_float - self.mean) / self.std
        
        # Convert HWC -> CHW
        image_chw = np.transpose(image_float, (2, 0, 1))
        
        # Add batch dimension: CHW -> NCHW
        image_nchw = np.expand_dims(image_chw, axis=0)
        
        return image_nchw, original_size
    
    def postprocess_mask(self, mask: np.ndarray, original_size: Tuple[int, int]) -> np.ndarray:
        """
        Postprocess mask output from model.
        
        Args:
            mask: Model output mask (1, 1, H, W) or (1, H, W) or (H, W)
            original_size: Original image size (height, width)
            
        Returns:
            Resized mask (H, W) float32 [0, 1]
        """
        # Remove batch and channel dimensions
        if mask.ndim == 4:  # (1, 1, H, W)
            mask = mask[0, 0]
        elif mask.ndim == 3:  # (1, H, W)
            mask = mask[0]
        
        # Ensure 2D
        if mask.ndim != 2:
            raise ValueError(f"Expected 2D mask after squeeze, got {mask.ndim}D")
        
        # Resize back to original size
        h, w = original_size
        mask_resized = cv2.resize(
            mask,
            (w, h),
            interpolation=cv2.INTER_LINEAR
        )
        
        # Clip to [0, 1]
        mask_resized = np.clip(mask_resized, 0.0, 1.0)
        
        return mask_resized.astype(np.float32)
