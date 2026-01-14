"""
Download BiRefNet ONNX model từ GitHub Releases.
"""
import urllib.request
import os
from pathlib import Path

print("="*70)
print("📥 Downloading BiRefNet ONNX Model from GitHub Releases")
print("="*70)
print()

# Model URLs from GitHub Releases
MODELS = {
    "BiRefNet-general": {
        "url": "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-epoch_244.onnx",
        "size": "~640MB",
        "description": "General use (recommended)"
    },
    "BiRefNet-DIS": {
        "url": "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-DIS-epoch_590.onnx", 
        "size": "~640MB",
        "description": "Dichotomous Image Segmentation"
    },
    "BiRefNet-lite": {
        "url": "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet_lite-epoch_245.onnx",
        "size": "~140MB", 
        "description": "Lightweight version (faster)"
    }
}

# Choose model
print("Available models:")
for i, (name, info) in enumerate(MODELS.items(), 1):
    print(f"{i}. {name}: {info['description']} ({info['size']})")
print()

choice = input("Select model (1-3) [default: 1]: ").strip() or "1"
model_names = list(MODELS.keys())
selected_model = model_names[int(choice) - 1]
model_info = MODELS[selected_model]

print()
print(f"Selected: {selected_model}")
print(f"URL: {model_info['url']}")
print()

# Create directory
model_dir = Path("assets/models")
model_dir.mkdir(parents=True, exist_ok=True)

# Download with progress
output_path = model_dir / "birefnet.onnx"

def download_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100)
    mb_downloaded = downloaded / (1024 * 1024)
    mb_total = total_size / (1024 * 1024)
    print(f"\r⏳ Downloading: {mb_downloaded:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)", end="")

print(f"Downloading to: {output_path.absolute()}")
print()

try:
    urllib.request.urlretrieve(
        model_info['url'],
        output_path,
        reporthook=download_progress
    )
    print()
    print()
    print(f"✅ Download complete: {output_path.absolute()}")
    print(f"📊 File size: {output_path.stat().st_size / (1024*1024):.1f}MB")
    print()
    print("="*70)
    print("✅ Model ready!")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Install Visual C++ Redistributable:")
    print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print("2. Restart computer")
    print("3. Run: python run.py")
    
except Exception as e:
    print()
    print(f"❌ Download failed: {e}")
    print()
    print("Manual download:")
    print(f"1. Open: {model_info['url']}")
    print(f"2. Save to: {output_path.absolute()}")
