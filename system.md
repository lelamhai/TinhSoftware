# Ứng dụng Xóa Background (BiRefNet ONNX + ONNX Runtime)
> Tài liệu thiết kế để “vibe coding”: kiến trúc, wireframe, folder structure, clean architecture, roadmap.

---

## 1) Mục tiêu & phạm vi
- **Input:** 1 ảnh (JPG/PNG/WebP).
- **Process:** chạy **BiRefNet ONNX** bằng **ONNX Runtime** để tạo **mask foreground/background**.
- **Post-process (MVP):** smoothing viền nhẹ (optional), threshold (optional).
- **Output:** **PNG RGBA nền trong suốt** + tuỳ chọn preview trước/sau.
- **Ưu tiên:** offline, đơn giản, dễ maintain, có thể mở rộng batch + GPU sau.

---

## 2) Kiến trúc tổng thể (ASCII)

### 2.1 Kiến trúc logic (Clean-ish)
```
+--------------------------- UI (Desktop) ----------------------------+
|  Screen: Home                                                     |
|   - Chọn ảnh  - Xem preview  - Remove BG  - Lưu PNG                |
|   - Settings (model path, device: CPU/GPU, threshold, smooth)      |
+------------------------------|-------------------------------------+
                               |
                               v
+--------------------------- Application Layer -----------------------+
| Use Cases:                                                         |
|  - RemoveBackgroundUseCase                                         |
|  - LoadImageUseCase / SaveImageUseCase                              |
|  - UpdateSettingsUseCase                                           |
| Interfaces (Ports):                                                |
|  - IBackgroundRemovalEngine                                        |
|  - IImageIO                                                        |
|  - ISettingsStore                                                  |
+------------------------------|-------------------------------------+
                               |
                               v
+----------------------------- Domain Layer --------------------------+
| Entities / Value Objects:                                          |
|  - ImageInput, ImageOutput, Mask, Settings                         |
| Domain Services (pure):                                            |
|  - PostProcessMask (smooth/threshold)                              |
|  - AlphaCompose (RGBA)                                             |
| Domain Errors:                                                     |
|  - ModelNotFound, InvalidImage, InferenceFailed                     |
+------------------------------|-------------------------------------+
                               |
                               v
+--------------------------- Infrastructure Layer --------------------+
| Adapters:                                                          |
|  - OnnxRuntimeBiRefNetEngine (implements IBackgroundRemovalEngine) |
|  - LocalImageIO (SkiaSharp/ImageSharp) implements IImageIO         |
|  - JsonSettingsStore implements ISettingsStore                     |
| Details:                                                           |
|  - Ort.InferenceSession, provider CPU/CUDA/DirectML                |
|  - Preprocess/Normalize/Resize -> Tensor                           |
+---------------------------------------------------------------------+
```

### 2.2 Dataflow xử lý ảnh
```
[Open Image] -> (Decode RGB) -> (Resize/Normalize) -> [BiRefNet ONNX]
                                         |
                                         v
                                 [Mask Probabilities]
                                         |
                                         v
                          [PostProcessMask: smooth/threshold]
                                         |
                                         v
                         [AlphaCompose: RGBA = RGB + Alpha(mask)]
                                         |
                                         v
                            [Preview] -> [Save PNG (transparent)]
```

### 2.3 Deployment (MVP offline)
```
+------------------- Desktop App -------------------+
| UI (PyQt6/CustomTkinter)                          |
| Application + Domain                              |
| Infrastructure: ONNX Runtime + Pillow/OpenCV      |
|  - Model: ./assets/models/birefnet.onnx           |
|  - Settings: ~/.config/removebg/settings.json     |
|  - Virtual env: venv/                             |
+---------------------------------------------------+
```

---

## 3) Wireframe (ASCII)

### 3.1 Màn hình chính
```
+----------------------------------------------------------------------------------+
|  RemoveBG Desktop (BiRefNet)                                                     |
+----------------------------------------------------------------------------------+
| [Open Image]  [Remove BG]  [Save PNG]  [Reset]                     (i) About    |
|----------------------------------------------------------------------------------|
|  Left: Input Preview                          |  Right: Output Preview           |
| +-------------------------------------------+ | +--------------------------------+ |
| |                                           | | |                                | |
| |           (Ảnh gốc hiển thị)              | | |     (Ảnh nền trong suốt)       | |
| |                                           | | |     (checkerboard background) | |
| +-------------------------------------------+ | +--------------------------------+ |
|----------------------------------------------------------------------------------|
| Settings                                                                          |
|  Model: [./assets/models/birefnet.onnx]  [Browse...]                             |
|  Device: (•) CPU   ( ) GPU-CUDA   ( ) GPU-DirectML                               |
|  Threshold: [0.50]   Smooth: [  2 px]   Feather: [  1 px]                        |
|  Output:  [PNG RGBA]  Background Preview: [Checkerboard v]                       |
|----------------------------------------------------------------------------------|
| Status: Ready | Time: 0ms | Mask Quality: -                                      |
+----------------------------------------------------------------------------------+
```

### 3.2 Dialog chọn model (optional)
```
+------------------------- Select ONNX Model -------------------------+
| Path: [C:\...\birefnet.onnx] [Browse...]                          |
| Providers detected: CPU, DirectML (if installed), CUDA (if installed)|
| [OK] [Cancel]                                                       |
+---------------------------------------------------------------------+
```

---

## 4) Cấu trúc folder (đề xuất)
> Kiến trúc Python với Clean Architecture, sử dụng PyQt6/CustomTkinter cho UI.

```
removebg-birefnet/
├─ system.md
├─ README.md
├─ requirements.txt                   # onnxruntime, Pillow, PyQt6/customtkinter, numpy, opencv-python
├─ setup.py
├─ .env.example
├─ assets/
│  ├─ models/
│  │  └─ birefnet.onnx
│  └─ samples/
│     ├─ input.jpg
│     └─ output.png
├─ src/
│  ├─ __init__.py
│  ├─ main.py                         # Entry point
│  ├─ ui/                             # UI Layer (PyQt6/CustomTkinter)
│  │  ├─ __init__.py
│  │  ├─ main_window.py
│  │  ├─ widgets/
│  │  │  ├─ __init__.py
│  │  │  ├─ image_preview.py
│  │  │  └─ settings_panel.py
│  │  └─ view_models/
│  │     ├─ __init__.py
│  │     └─ main_view_model.py
│  ├─ application/                    # Application Layer
│  │  ├─ __init__.py
│  │  ├─ use_cases/
│  │  │  ├─ __init__.py
│  │  │  ├─ remove_background_use_case.py
│  │  │  ├─ load_image_use_case.py
│  │  │  └─ save_image_use_case.py
│  │  └─ ports/
│  │     ├─ __init__.py
│  │     ├─ background_removal_engine.py  # ABC interface
│  │     ├─ image_io.py
│  │     └─ settings_store.py
│  ├─ domain/                         # Domain Layer
│  │  ├─ __init__.py
│  │  ├─ entities/
│  │  │  ├─ __init__.py
│  │  │  ├─ image_input.py
│  │  │  ├─ image_output.py
│  │  │  ├─ mask.py
│  │  │  └─ settings.py
│  │  ├─ services/
│  │  │  ├─ __init__.py
│  │  │  ├─ post_process_mask.py
│  │  │  └─ alpha_compose.py
│  │  └─ errors/
│  │     ├─ __init__.py
│  │     └─ exceptions.py
│  └─ infrastructure/                  # Infrastructure Layer
│     ├─ __init__.py
│     ├─ engines/
│     │  ├─ __init__.py
│     │  └─ onnx_birefnet_engine.py
│     ├─ image_io/
│     │  ├─ __init__.py
│     │  └─ local_image_io.py         # Pillow/OpenCV
│     ├─ settings/
│     │  ├─ __init__.py
│     │  └─ json_settings_store.py
│     └─ preprocessing/
│        ├─ __init__.py
│        ├─ image_preprocessor.py
│        └─ tensor_converters.py
├─ tests/
│  ├─ __init__.py
│  ├─ test_domain/
│  │  └─ test_post_process.py
│  ├─ test_application/
│  │  └─ test_remove_bg_use_case.py
│  └─ test_infrastructure/
│     └─ test_onnx_engine.py
├─ tools/
│  ├─ model_info.py                   # Script xem ONNX model info
│  └─ benchmark.py
└─ venv/                              # Virtual environment (gitignore)
```

---

## 5) Cấu trúc code (Clean Architecture dễ maintain)

### 5.1 Quy tắc phụ thuộc (Dependency Rule)
- **UI** chỉ gọi **Application**.
- **Application** dùng **Ports (interfaces)** và gọi **Domain**.
- **Infrastructure** implements Ports, không được “kéo ngược” vào Domain.
- **Domain** thuần: không phụ thuộc thư viện ONNX, UI, file system…

### 5.2 Interfaces (Ports) cốt lõi
- `BackgroundRemovalEngine` (ABC)
  - `async def predict_mask(image_input: ImageInput) -> Mask`
- `ImageIO` (ABC)
  - `async def load_image(path: str) -> ImageInput`
  - `async def save_png_rgba(output: ImageOutput, path: str) -> None`
- `SettingsStore` (ABC)
  - `def load() -> Settings`
  - `def save(settings: Settings) -> None`

### 5.3 Use case cốt lõi
`RemoveBackgroundUseCase`
- Input: `image_path: str`, `settings: Settings`
- Steps:
  1) `await image_io.load_image(image_path)`
  2) `await engine.predict_mask(image_input)`
  3) `PostProcessMask.apply(mask, settings)`
  4) `AlphaCompose.compose(rgb, alpha_mask)`
  5) return `ImageOutput`

### 5.4 Infrastructure: OnnxRuntime engine (tóm tắt responsibilities)
- Load `birefnet.onnx` -> tạo `ort.InferenceSession`
- Chọn provider: `CPUExecutionProvider` / `CUDAExecutionProvider` / `DmlExecutionProvider`
- Preprocess:
  - Decode image -> RGB numpy array (float32)
  - Resize to model input size (ví dụ 1024/512 tùy model)
  - Normalize (mean/std nếu model yêu cầu): `(img - mean) / std`
  - NCHW tensor: `np.transpose(img, (2, 0, 1))` -> `np.expand_dims(..., axis=0)`
- Inference -> `session.run(output_names, {input_name: tensor})`
- Postprocess:
  - Resize mask về size gốc (cv2.resize hoặc PIL)
  - (optional) sigmoid / clip 0..1 (tùy output): `np.clip(mask, 0, 1)`
- Trả về `Mask`

---

## 6) Roadmap & danh sách task (phân kỳ rõ ràng)

### Phase 0 — Chuẩn bị (0.5–1 ngày)
- [ ] Chọn **BiRefNet ONNX** cụ thể (general/DIS, input size, output node).
- [ ] Xác nhận runtime target: CPU trước (GPU sau).
- [ ] Quyết định stack UI: PyQt6 (modern, native), CustomTkinter (đơn giản), hoặc Tkinter.
- [ ] Setup virtual environment: `python -m venv venv`
- [ ] Install dependencies: `pip install -r requirements.txt`

### Phase 1 — MVP “1 ảnh vào, 1 PNG ra” (1–3 ngày)
- [ ] Implement `LocalImageIO` (Pillow: load image, save PNG RGBA với alpha channel).
- [ ] Implement `OnnxBiRefNetEngine` (onnxruntime CPUExecutionProvider).
- [ ] Implement `RemoveBackgroundUseCase` với async/await.
- [ ] UI (PyQt6/CustomTkinter): Open file dialog, Preview, Remove button, Save dialog.
- [ ] Status bar: thời gian inference, kích thước ảnh, memory usage.
- [ ] Test bằng 10 ảnh mẫu.

**Done criteria:** chọn ảnh -> remove -> save PNG trong suốt (alpha channel).

### Phase 2 — Chất lượng biên & UX (2–4 ngày)
- [ ] Postprocess: threshold, feather, blur nhẹ.
- [ ] Checkerboard preview + zoom/pan.
- [ ] Auto-crop / fit view.
- [ ] Save as: PNG + chọn folder mặc định.
- [ ] Error handling “model not found / invalid image / inference failed”.

### Phase 3 — Hiệu năng & thiết bị (2–5 ngày)
- [ ] GPU provider: `CUDAExecutionProvider` (NVIDIA), `DmlExecutionProvider` (Windows DirectML).
- [ ] Warm-up session: chạy 1 dummy inference để optimize lần đầu.
- [ ] Cache InferenceSession + reuse numpy arrays để giảm allocation.
- [ ] Multithreading với ThreadPoolExecutor cho batch processing.
- [ ] Benchmark: ảnh 1080p/4K với timeit/cProfile.

### Phase 4 — Nâng cấp tính năng (tuỳ chọn)
- [ ] Batch folder (nhiều ảnh) + progress bar.
- [ ] Replace background (solid color / image).
- [ ] Export mask riêng (PNG mask).
- [ ] Tích hợp matting refine (nếu cần “tóc mượt” hơn): BiRefNet mask -> refine alpha.

---

## 7) Ghi chú “vibe coding” (định hướng thực dụng)
- MVP: làm được pipeline end-to-end trước, rồi mới tối ưu.
- Đừng over-engineer: 3 project (UI/Application+Domain/Infrastructure) cũng được, nhưng giữ nguyên ranh giới.
- Chốt “contract” tensor sớm: input size, normalize, output map.
- Log mọi thông tin model: input name, output name, expected shape.

---

## 8) Phần mở rộng: checklist kiểm tra ONNX model
- [ ] Input tensor name & shape (NCHW hay NHWC?).
- [ ] Kích thước input cố định hay dynamic?
- [ ] Output có sigmoid chưa?
- [ ] Output shape (1x1xHxW?) hay (1xHxW?).
- [ ] Normalize: mean/std và scale 0..1 hay 0..255?

---

*Hết.*
