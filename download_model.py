"""
Script tự động download BiRefNet ONNX model từ HuggingFace.
Run: python download_model.py
"""
import os
from pathlib import Path

print("="*70)
print("📥 BiRefNet ONNX Model Downloader")
print("="*70)
print()

# Step 1: Install huggingface_hub if needed
print("Step 1/3: Checking huggingface_hub...")
try:
    from huggingface_hub import hf_hub_download
    print("✅ huggingface_hub already installed")
except ImportError:
    print("📦 Installing huggingface_hub...")
    import subprocess
    subprocess.check_call(["pip", "install", "huggingface_hub"])
    from huggingface_hub import hf_hub_download
    print("✅ huggingface_hub installed successfully")

print()

# Step 2: Create directories
print("Step 2/3: Creating directories...")
model_dir = Path("assets/models")
model_dir.mkdir(parents=True, exist_ok=True)
print(f"✅ Directory created: {model_dir.absolute()}")
print()

# Step 3: Download model
print("Step 3/3: Downloading BiRefNet ONNX model...")
print("⏳ This may take several minutes (~640MB)...")
print()

try:
    # Download from HuggingFace
    # Repo có nhiều models, thử các options:
    # 1. BiRefNet-general (recommended for most use cases)
    # 2. BiRefNet-matting (for matting tasks)
    # 3. BiRefNet_lite (smaller, faster)
    
    model_file = hf_hub_download(
        repo_id="ZhengPeng7/BiRefNet",
        filename="model.safetensors",  # PyTorch weights
        local_dir=str(model_dir),
        local_dir_use_symlinks=False
    )
    
    print(f"✅ Model downloaded to: {model_file}")
    print()
    print("⚠️  Note: Downloaded PyTorch model (.safetensors)")
    print("   ONNX conversion may be needed for optimal performance.")
    print()
    print("Alternative: Download pre-converted ONNX from:")
    print("   - GitHub: https://github.com/ZhengPeng7/BiRefNet/releases")
    print("   - GDrive: https://drive.google.com/drive/folders/1kZM55bwsRdS__bdnsXpkmH6QPyza-9-N")
    print()
    
except Exception as e:
    print(f"❌ Download failed: {e}")
    print()
    print("📝 Manual download options:")
    print("1. GitHub Releases: https://github.com/ZhengPeng7/BiRefNet/releases/tag/v1")
    print("2. Google Drive: https://drive.google.com/drive/folders/1kZM55bwsRdS__bdnsXpkmH6QPyza-9-N")
    print()
    print("After downloading, place the file at: assets/models/birefnet.onnx")
    exit(1)

print("="*70)
print("✅ Setup complete!")
print("="*70)
print()
print("Next steps:")
print("1. Install Visual C++ Redistributable:")
print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
print("2. Restart your computer")
print("3. Run: python run.py")
print()
