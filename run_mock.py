"""
BiRefNet Background Removal Application
Sử dụng ONNX model thật với BiRefNet AI
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("="*70)
    print("🚀 BiRefNet - AI Background Removal")
    print("="*70)
    print()
    
    from src.main import main
    sys.exit(main())
