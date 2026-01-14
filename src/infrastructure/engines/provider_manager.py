"""ONNX Runtime provider utilities."""
from typing import List, Dict
import onnxruntime as ort


class ProviderManager:
    """Manage ONNX Runtime execution providers."""
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """
        Get list of available execution providers.
        
        Returns:
            List of provider names
        """
        return ort.get_available_providers()
    
    @staticmethod
    def get_provider_info() -> Dict[str, Dict]:
        """
        Get detailed information about available providers.
        
        Returns:
            Dict mapping provider name to info
        """
        available = ort.get_available_providers()
        
        provider_info = {
            "CPUExecutionProvider": {
                "name": "CPU",
                "display_name": "CPU",
                "description": "Run on CPU (always available)",
                "requirements": "None",
                "available": "CPUExecutionProvider" in available
            },
            "CUDAExecutionProvider": {
                "name": "CUDA",
                "display_name": "GPU-CUDA",
                "description": "Run on NVIDIA GPU with CUDA",
                "requirements": "NVIDIA GPU + CUDA toolkit + onnxruntime-gpu",
                "available": "CUDAExecutionProvider" in available
            },
            "DmlExecutionProvider": {
                "name": "DirectML",
                "display_name": "GPU-DirectML",
                "description": "Run on GPU using DirectML (Windows)",
                "requirements": "Windows 10+ + DirectX 12 GPU + onnxruntime-directml",
                "available": "DmlExecutionProvider" in available
            },
            "TensorrtExecutionProvider": {
                "name": "TensorRT",
                "display_name": "GPU-TensorRT",
                "description": "Run on NVIDIA GPU with TensorRT optimization",
                "requirements": "NVIDIA GPU + TensorRT + onnxruntime-gpu",
                "available": "TensorrtExecutionProvider" in available
            }
        }
        
        return {k: v for k, v in provider_info.items() if v["available"]}
    
    @staticmethod
    def get_recommended_provider() -> str:
        """
        Get recommended execution provider based on available hardware.
        
        Returns:
            Provider name (CUDA > DirectML > CPU)
        """
        available = ort.get_available_providers()
        
        # Priority: CUDA (fastest) > DirectML (Windows GPU) > CPU (fallback)
        if "CUDAExecutionProvider" in available:
            return "CUDA"
        elif "DmlExecutionProvider" in available:
            return "DirectML"
        else:
            return "CPU"
    
    @staticmethod
    def map_provider_name(friendly_name: str) -> str:
        """
        Map friendly provider name to ONNX Runtime provider name.
        
        Args:
            friendly_name: User-friendly name (CPU, CUDA, DirectML)
            
        Returns:
            ONNX Runtime provider name (CPUExecutionProvider, etc.)
        """
        mapping = {
            "CPU": "CPUExecutionProvider",
            "CUDA": "CUDAExecutionProvider",
            "DirectML": "DmlExecutionProvider",
            "TensorRT": "TensorrtExecutionProvider"
        }
        return mapping.get(friendly_name, "CPUExecutionProvider")
    
    @staticmethod
    def validate_provider(provider_name: str) -> bool:
        """
        Check if provider is available.
        
        Args:
            provider_name: Friendly provider name
            
        Returns:
            True if available
        """
        ort_provider = ProviderManager.map_provider_name(provider_name)
        return ort_provider in ort.get_available_providers()
