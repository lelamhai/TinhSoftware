"""Test ONNX Runtime import."""
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print()

try:
    import onnxruntime as ort
    print("✅ ONNX Runtime imported successfully!")
    print("Version:", ort.__version__)
    print("Available providers:", ort.get_available_providers())
except Exception as e:
    print("❌ Failed to import ONNX Runtime:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    import traceback
    traceback.print_exc()
