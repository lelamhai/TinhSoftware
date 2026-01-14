"""Background removal engine port."""
from abc import ABC, abstractmethod
from ...domain.entities.image_input import ImageInput
from ...domain.entities.mask import Mask


class BackgroundRemovalEngine(ABC):
    """Port for background removal inference engine."""
    
    @abstractmethod
    async def predict_mask(self, image: ImageInput) -> Mask:
        """
        Predict foreground mask for the input image.
        
        Args:
            image: Input image
            
        Returns:
            Mask with probabilities (0 = background, 1 = foreground)
            
        Raises:
            ModelNotFoundError: If model file not found
            InferenceFailedError: If inference fails
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """
        Get model information.
        
        Returns:
            Dict with model metadata (input shape, providers, etc.)
        """
        pass
