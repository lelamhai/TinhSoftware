# Xử lý lỗi RemoveBG

## Lỗi ONNX Runtime DLL

### Triệu chứng

```
ImportError: DLL load failed while importing onnxruntime_pybind11_state: 
A dynamic link library (DLL) initialization routine failed.
```

### Nguyên nhân

ONNX Runtime trên Windows cần Visual C++ Redistributable để load native DLLs.

### Giải pháp

#### Option 1: Cài Visual C++ Redistributable (Khuyến nghị)

1. **Tải về**:
   - Link: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Hoặc search "Visual C++ Redistributable 2015-2022 x64"

2. **Cài đặt**:
   ```powershell
   # Tải file vc_redist.x64.exe
   # Double-click và cài đặt
   # Restart máy tính
   ```

3. **Kiểm tra**:
   ```powershell
   python -c "import onnxruntime; print(onnxruntime.__version__)"
   ```

#### Option 2: Dùng Mock Engine (Test UI)

Chạy với Mock Engine không cần ONNX Runtime:

```powershell
python run_mock.py
```

Mock engine tạo mask đơn giản (không dùng AI) để test UI.

#### Option 3: Thử onnxruntime CPU version

```powershell
pip uninstall onnxruntime-directml
pip install onnxruntime==1.23.2
```

Sau đó chạy lại:
```powershell
python run.py
```

---

## Lỗi Model Not Found

### Triệu chứng

```
Model not found: assets/models/birefnet.onnx
```

### Giải pháp

1. **Tải model**:
   - URL: https://huggingface.co/ZhengPeng7/BiRefNet-general/tree/main/onnx
   - File: `birefnet.onnx` (hoặc tương tự)

2. **Đặt đúng đường dẫn**:
   ```powershell
   New-Item -ItemType Directory -Force -Path "assets\models"
   Move-Item Downloads\birefnet.onnx assets\models\birefnet.onnx
   ```

3. **Kiểm tra**:
   ```powershell
   Test-Path "assets\models\birefnet.onnx"
   # Kết quả phải là True
   ```

---

## Lỗi Module Not Found

### Triệu chứng

```
ModuleNotFoundError: No module named 'PyQt6'
```

### Giải pháp

Cài đầy đủ dependencies:

```powershell
pip install -r requirements.txt
```

Hoặc cài thủ công:

```powershell
pip install PyQt6==6.10.2 qasync==0.28.0
pip install numpy pillow opencv-python
pip install onnxruntime-directml==1.23.0
```

---

## Lỗi Import Errors

### Triệu chứng

```
ImportError: attempted relative import beyond top-level package
```

### Giải pháp

Chạy qua launcher script:

```powershell
# ✅ Đúng
python run.py

# ❌ Sai - không chạy trực tiếp
python src/main.py
```

---

## Lỗi Syntax Error

### Triệu chứng

```
SyntaxError: closing parenthesis ')' does not match opening parenthesis '{'
```

### Giải pháp

Code bị corrupt. Checkout lại từ git hoặc report issue.

---

## UI không hiển thị

### Triệu chứng

- Application chạy nhưng không có window
- Console không có error

### Giải pháp

1. **Kiểm tra Python version**:
   ```powershell
   python --version
   # Phải >= 3.12
   ```

2. **Kiểm tra PyQt6**:
   ```powershell
   python -c "from PyQt6.QtWidgets import QApplication; print('OK')"
   ```

3. **Chạy với verbose**:
   ```powershell
   python -v run.py
   ```

---

## Performance Issues

### Triệu chứng

- Processing ảnh chậm (> 10 giây)
- CPU usage cao

### Giải pháp

1. **Bật GPU acceleration**:
   - Settings > Execution Provider > DirectML (Windows)
   - Hoặc CUDA (NVIDIA GPU)

2. **Giảm resolution**:
   - Processing > Image Size > 1024px (thay vì 2048px)

3. **Enable caching**:
   - Settings > Enable Session Caching ✅

---

## Checklist khi gặp lỗi

- [ ] Python >= 3.12
- [ ] Đã cài requirements.txt
- [ ] Visual C++ Redistributable đã cài
- [ ] Model file tồn tại: `assets/models/birefnet.onnx`
- [ ] Chạy qua `run.py`, không phải `python src/main.py`
- [ ] Restart máy tính sau khi cài VC++ Redistributable

---

## Liên hệ hỗ trợ

Nếu vẫn gặp lỗi, thu thập thông tin:

```powershell
# System info
python --version
pip list | Select-String "onnx|PyQt|numpy"

# Test ONNX
python test_onnx.py

# Run với verbose
python run.py > output.txt 2>&1
```

Sau đó báo cáo kèm file `output.txt`.
