"""
Chạy với PyTorch model thay vì ONNX (tránh lỗi DLL)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print("="*70)
print("🚀 BiRefNet - Background Removal (PyTorch)")
print("="*70)
print()
print("⚠️  Note: Using PyTorch instead of ONNX to avoid DLL issues")
print("   Install: pip install torch transformers")
print()

from src.main import main
sys.exit(main())
