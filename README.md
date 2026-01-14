# RemoveBG - BiRefNet Background Removal

Desktop application xóa phông nền ảnh sử dụng BiRefNet ONNX model.

## Yêu cầu hệ thống

- **Python 3.12** hoặc cao hơn  
- **Windows 10/11** (64-bit)
- **Visual C++ Redistributable 2015-2022** (cho ONNX Runtime)

## Cài đặt

### 1. Cài đặt dependencies

```powershell
pip install PyQt6 qasync numpy pillow opencv-python onnxruntime-directml
```

### 2. Tải BiRefNet ONNX model

1. Tải model từ: [Hugging Face - BiRefNet ONNX](https://huggingface.co/ZhengPeng7/BiRefNet-general/tree/main/onnx)
2. Đặt file `birefnet.onnx` vào: `assets/models/birefnet.onnx`

```powershell
# Tạo thư mục
New-Item -ItemType Directory -Force -Path "assets\models"

# Di chuyển model (sau khi tải)
Move-Item path\to\your\birefnet.onnx assets\models\birefnet.onnx
```

## Chạy ứng dụng

### Option 1: Chạy với ONNX model (cần Visual C++ Redistributable)

```powershell
python run.py
```

**Nếu gặp lỗi DLL:**

```
ImportError: DLL load failed while importing onnxruntime_pybind11_state
```

👉 **Cài Visual C++ Redistributable:**
1. Tải từ: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Chạy và cài đặt
3. Restart máy tính
4. Chạy lại `python run.py`

### Option 2: Chạy với Mock Engine (không cần ONNX)

Dùng để test UI mà không cần model/ONNX Runtime:

```powershell
python run_mock.py
```

Mock engine sẽ tạo mask hình tròn đơn giản thay vì AI model thật.

## Cấu trúc Project

```
D:\TinhSoftware\
├── run.py                 # Launch script (với ONNX)
├── run_mock.py            # Launch script (Mock engine)
├── assets\
│   └── models\
│       └── birefnet.onnx  # BiRefNet ONNX model (phải tải)
├── src\
│   ├── main.py            # Application entry point
│   ├── domain\            # Domain entities & rules
│   ├── application\       # Use cases & ports
│   ├── infrastructure\    # Implementations (ONNX, I/O)
│   └── ui\                # PyQt6 UI components
└── settings.json          # User settings (auto-generated)
```

## Tính năng

### Phase 0-4 (✅ Đã hoàn thành)

- ✅ **MVP**: Single image background removal
- ✅ **UX**: Checkerboard background, zoom/pan controls, auto-crop
- ✅ **Performance**: GPU support (CUDA/DirectML), session caching, batch processing
- ✅ **Advanced**: Background replacement, mask export, drag & drop

### Sử dụng

1. **Mở ảnh**: File > Open Image hoặc kéo thả file vào cửa sổ
2. **Xóa phông**: Click "Remove Background"
3. **Xem kết quả**: 
   - Trái: Ảnh gốc
   - Phải: Ảnh đã xóa phông (với checkerboard)
4. **Zoom/Pan**: Dùng zoom slider hoặc scroll wheel
5. **Thay phông**: Background > Replace Background
6. **Xuất mask**: File > Export Mask
7. **Lưu ảnh**: File > Save As PNG

### Cài đặt

- **Settings > Execution Provider**: Chọn CPU/GPU (CUDA/DirectML)
- **View > Show Checkerboard**: Bật/tắt checkerboard pattern
- **Processing > Auto-crop**: Tự động crop ảnh theo foreground

## Xử lý lỗi

### Lỗi: Model not found

```
BiRefNet ONNX model not found at: assets/models/birefnet.onnx
```

**Giải pháp**: Tải model và đặt đúng đường dẫn (xem phần Cài đặt).

### Lỗi: DLL load failed

```
ImportError: DLL load failed while importing onnxruntime_pybind11_state
```

**Giải pháp 1**: Cài Visual C++ Redistributable (khuyến nghị)
- https://aka.ms/vs/17/release/vc_redist.x64.exe

**Giải pháp 2**: Dùng Mock Engine để test UI
```powershell
python run_mock.py
```

### Lỗi: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'PyQt6'
```

**Giải pháp**: Cài lại dependencies
```powershell
pip install PyQt6 qasync numpy pillow opencv-python onnxruntime-directml
```

## Performance Tips

1. **GPU Acceleration**: Settings > Execution Provider > DirectML (Windows) hoặc CUDA (NVIDIA)
2. **Session Caching**: Enabled by default - model chỉ load 1 lần
3. **Batch Processing**: Dùng Processing > Batch Process cho nhiều ảnh

## Known Issues

- **Windows only**: DirectML chỉ chạy trên Windows 10+
- **ONNX Runtime DLL**: Cần Visual C++ Redistributable 2015-2022
- **Large images**: Ảnh > 4K có thể chậm trên CPU

## Liên hệ

- **Project**: D:\TinhSoftware
- **Architecture**: Clean Architecture (Domain-Application-Infrastructure-UI)
- **Framework**: PyQt6 + ONNX Runtime + BiRefNet

---

**Enjoy removing backgrounds! 🎨**
