# Phase 1 MVP - Testing Instructions

## Prerequisites

Before testing, you need the BiRefNet ONNX model:

### Download BiRefNet ONNX Model

1. **Option 1: Export from PyTorch**
   ```bash
   # Clone BiRefNet repository
   git clone https://github.com/ZhengPeng7/BiRefNet
   
   # Export to ONNX (follow their documentation)
   # Place the exported .onnx file in: assets/models/birefnet.onnx
   ```

2. **Option 2: Pre-converted Model**
   - Download pre-converted BiRefNet ONNX from Hugging Face or model zoo
   - Place in `assets/models/birefnet.onnx`

## Running the Application

### 1. Activate Virtual Environment

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Run the Application

```bash
python src/main.py
```

## Testing Workflow

### Manual Test Checklist

- [ ] **Open Image**
  - Click "Open Image" button
  - Select a JPG/PNG image
  - Verify image displays in "Input Preview"

- [ ] **Remove Background**
  - Click "Remove BG" button
  - Wait for processing
  - Verify output displays in "Output Preview"
  - Check status bar shows processing time

- [ ] **Adjust Settings**
  - Move "Threshold" slider (0.0 - 1.0)
  - Move "Smooth" slider (0-10 px)
  - Move "Feather" slider (0-10 px)
  - Process again to see effects

- [ ] **Save Output**
  - Click "Save PNG" button
  - Choose destination
  - Verify PNG file has transparency

- [ ] **Reset**
  - Click "Reset" button
  - Verify UI clears

### Test Images

Place test images in `assets/samples/`:
- Portrait photos
- Product images
- Complex backgrounds
- Various resolutions (test 1080p, 4K)

### Expected Behavior

1. **Input Formats**: JPG, PNG, WebP supported
2. **Output Format**: PNG with alpha channel (RGBA)
3. **Performance**: ~1-5 seconds per image (CPU), faster on GPU
4. **Memory**: ~500MB-2GB depending on image size

## Troubleshooting

### Model Not Found
```
Error: Model not found: assets/models/birefnet.onnx
```
**Solution**: Download and place BiRefNet ONNX model in correct location

### ONNX Runtime Error
```
Error: Failed to load ONNX model
```
**Solution**: Check model compatibility with onnxruntime version

### GPU Not Working
```
Provider: CPUExecutionProvider
```
**Solution**: 
- For CUDA: Install `onnxruntime-gpu`
- For DirectML: Install `onnxruntime-directml`

### Memory Error
```
MemoryError: Unable to allocate array
```
**Solution**: Reduce image size or use GPU

## Unit Tests

Run tests with pytest:

```bash
pytest tests/ -v
```

## Performance Benchmark

Test performance:

```bash
python tools/benchmark.py assets/models/birefnet.onnx 1024 10
```

## Model Information

Check model details:

```bash
python tools/model_info.py assets/models/birefnet.onnx
```

## Phase 1 Done Criteria

✅ Application launches successfully
✅ Can open and preview images
✅ Can remove background from images
✅ Can save PNG with transparency
✅ Settings controls work
✅ Error handling works
✅ Status bar shows useful info

## Next Steps: Phase 2

After Phase 1 is verified, proceed to Phase 2:
- Better checkerboard preview
- Zoom/pan functionality
- Improved edge quality
- Batch processing
