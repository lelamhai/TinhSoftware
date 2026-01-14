"""Auto-crop service for removing empty transparent areas."""
import numpy as np
from ..entities.image_output import ImageOutput


class AutoCrop:
    """Domain service for auto-cropping transparent images."""
    
    @staticmethod
    def crop_to_content(output: ImageOutput, threshold: int = 10) -> ImageOutput:
        """
        Crop image to non-transparent content.
        
        Args:
            output: Image with alpha channel
            threshold: Alpha threshold (0-255). Pixels with alpha < threshold are considered transparent.
            
        Returns:
            Cropped image
        """
        # Get alpha channel
        alpha = output.data[:, :, 3]
        
        # Find bounding box of non-transparent pixels
        rows = np.any(alpha >= threshold, axis=1)
        cols = np.any(alpha >= threshold, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            # Completely transparent, return original
            return output
        
        row_min, row_max = np.where(rows)[0][[0, -1]]
        col_min, col_max = np.where(cols)[0][[0, -1]]
        
        # Crop image
        cropped_data = output.data[row_min:row_max+1, col_min:col_max+1]
        
        new_height, new_width = cropped_data.shape[:2]
        
        return ImageOutput(
            data=cropped_data,
            width=new_width,
            height=new_height,
            original_path=output.original_path
        )
    
    @staticmethod
    def get_crop_bounds(output: ImageOutput, threshold: int = 10) -> tuple[int, int, int, int]:
        """
        Get crop bounds without actually cropping.
        
        Args:
            output: Image with alpha channel
            threshold: Alpha threshold
            
        Returns:
            Tuple of (x, y, width, height)
        """
        alpha = output.data[:, :, 3]
        
        rows = np.any(alpha >= threshold, axis=1)
        cols = np.any(alpha >= threshold, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return (0, 0, output.width, output.height)
        
        row_min, row_max = np.where(rows)[0][[0, -1]]
        col_min, col_max = np.where(cols)[0][[0, -1]]
        
        x = col_min
        y = row_min
        width = col_max - col_min + 1
        height = row_max - row_min + 1
        
        return (x, y, width, height)
