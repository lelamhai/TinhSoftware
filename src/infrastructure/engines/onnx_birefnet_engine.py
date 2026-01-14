"""ONNX BiRefNet engine implementation."""
from pathlib import Path
import numpy as np
from typing import Dict, Optional
import logging
import onnxruntime as ort

from ...application.ports.background_removal_engine import BackgroundRemovalEngine
from ...domain.entities.image_input import ImageInput
from ...domain.entities.mask import Mask
from ...domain.entities.settings import Settings
from ...domain.errors.exceptions import ModelNotFoundError, InferenceFailedError
from ..preprocessing.image_preprocessor import ImagePreprocessor
from .provider_manager import ProviderManager

logger = logging.getLogger(__name__)


class OnnxBiRefNetEngine(BackgroundRemovalEngine):
    """Background removal engine using BiRefNet ONNX model."""
    
    # Class-level session cache
    _session_cache: Dict[str, ort.InferenceSession] = {}
    
    def __init__(self, settings: Settings, enable_caching: bool = True):
        """
        Initialize ONNX engine.
        
        Args:
            settings: Application settings with model path and provider
            enable_caching: Whether to cache and reuse sessions
        """
        self.settings = settings
        self.enable_caching = enable_caching
        self.session: Optional[ort.InferenceSession] = None
        self.preprocessor = ImagePreprocessor(
            target_size=1024,
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225),
            normalize=True
        )
        self.is_warmed_up = False
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize ONNX Runtime session with caching."""
        if not self.settings.model_path.exists():
            raise ModelNotFoundError(f"Model not found: {self.settings.model_path}")
        
        # Create cache key
        cache_key = f"{self.settings.model_path}_{self.settings.execution_provider}"
        
        # Check cache first
        if self.enable_caching and cache_key in self._session_cache:
            self.session = self._session_cache[cache_key]
            logger.info(f"Reusing cached session for {cache_key}")
            return
        
        # Map execution provider
        provider = ProviderManager.map_provider_name(self.settings.execution_provider)
        
        # Validate provider availability
        if not ProviderManager.validate_provider(self.settings.execution_provider):
            logger.warning(
                f"Provider {self.settings.execution_provider} not available, "
                f"falling back to CPU"
            )
            provider = "CPUExecutionProvider"
        
        try:
            # Session options for optimization
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.enable_mem_pattern = True
            sess_options.enable_cpu_mem_arena = True
            
            # Create session
            self.session = ort.InferenceSession(
                str(self.settings.model_path),
                sess_options=sess_options,
                providers=[provider]
            )
            
            # Cache session if enabled
            if self.enable_caching:
                self._session_cache[cache_key] = self.session
            
            logger.info(f"Initialized session with provider: {provider}")
            
        except Exception as e:
            raise ModelNotFoundError(f"Failed to load model: {e}")
    
    async def remove_background(self, image: ImageInput) -> Mask:
        """
        Remove background from image.
        
        Args:
            image: Input image
            
        Returns:
            Binary mask (foreground=255, background=0)
        """
        # Warm up on first inference
        if not self.is_warmed_up:
            self._warmup()
        
        try:
            # Preprocess image
            input_tensor, original_size = self.preprocessor.preprocess(image.data)
            
            # Get input/output names
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name
            
            # Run inference
            outputs = self.session.run(
                [output_name],
                {input_name: input_tensor}
            )
            
            # Get mask output
            mask_raw = outputs[0]  # (1, 1, H, W) or similar
            
            # Postprocess: resize to original size
            mask_data = self.preprocessor.postprocess_mask(mask_raw, original_size)
            
            return Mask(
                data=mask_data,
                width=image.width,
                height=image.height,
                is_binary=False
            )
            
        except Exception as e:
            raise InferenceFailedError(f"Inference failed: {e}")
    
    def _warmup(self, warmup_size: int = 512):
        """
        Warm up the model with a dummy inference.
        
        Args:
            warmup_size: Size of dummy input (smaller = faster warmup)
        """
        if self.is_warmed_up:
            return
        
        try:
            logger.info("Warming up ONNX session...")
            
            # Create dummy input
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name
            
            dummy_input = np.random.randn(1, 3, warmup_size, warmup_size).astype(np.float32)
            
            # Run dummy inference
            _ = self.session.run([output_name], {input_name: dummy_input})
            
            self.is_warmed_up = True
            logger.info("Warm-up complete")
            
        except Exception as e:
            logger.warning(f"Warm-up failed: {e}")
    
    @classmethod
    def clear_cache(cls):
        """Clear the session cache."""
        cls._session_cache.clear()
        logger.info("Session cache cleared")
    
    async def predict_mask(self, image: ImageInput) -> Mask:
        """
        Predict mask for image (alias for remove_background).
        
        Args:
            image: Input image
            
        Returns:
            Binary mask
        """
        return await self.remove_background(image)
    
    def get_info(self) -> Dict:
        """Get engine information."""
        if self.session is None:
            return {}
        
        providers = self.session.get_providers()
        
        return {
            "model_path": str(self.settings.model_path),
            "provider": providers[0] if providers else "Unknown",
            "all_providers": providers,
            "is_warmed_up": self.is_warmed_up,
            "cached": self.enable_caching
        }
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        if self.session is None:
            return {}
        
        inputs = self.session.get_inputs()
        outputs = self.session.get_outputs()
        
        return {
            "model_path": str(self.settings.model_path),
            "provider": self.session.get_providers()[0],
            "inputs": [
                {
                    "name": inp.name,
                    "shape": inp.shape,
                    "type": inp.type
                }
                for inp in inputs
            ],
            "outputs": [
                {
                    "name": out.name,
                    "shape": out.shape,
                    "type": out.type
                }
                for out in outputs
            ]
        }
