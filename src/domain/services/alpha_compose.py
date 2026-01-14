"""Alpha composition service."""
import numpy as np
from ..entities.image_input import ImageInput
from ..entities.image_output import ImageOutput
from ..entities.mask import Mask


class AlphaCompose:
    """Domain service for composing RGBA from RGB + mask."""
    
    @staticmethod
    def compose(image: ImageInput, mask: Mask) -> ImageOutput:
        """
        Compose RGBA image from RGB image and alpha mask.
        
        Args:
            image: Input RGB image
            mask: Alpha mask (0 = transparent, 1 = opaque)
            
        Returns:
            RGBA image with transparent background
        """
        # Validate dimensions match
        if image.height != mask.height or image.width != mask.width:
            raise ValueError(
                f"Image size {(image.height, image.width)} doesn't match "
                f"mask size {(mask.height, mask.width)}"
            )
        
        # Get RGB data
        rgb = image.data  # (H, W, 3) uint8
        
        # Get alpha channel (0..1) and convert to uint8
        alpha = (mask.data * 255).astype(np.uint8)  # (H, W)
        
        # Expand alpha to (H, W, 1) for concatenation
        alpha_channel = alpha[:, :, np.newaxis]
        
        # Concatenate RGB + Alpha -> RGBA
        rgba = np.concatenate([rgb, alpha_channel], axis=2)
        
        return ImageOutput(
            data=rgba,
            width=image.width,
            height=image.height,
            original_path=image.file_path
        )
