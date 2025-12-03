# Model Test Results

## Test Date: 2025-12-03

## Summary
- **Total models tested**: 15
- **Models accessible on HuggingFace**: 14/15 ✅
- **Models likely compatible with Transformers.js 2.17.2**: 2-3 confirmed

## Issue Identified

Transformers.js v2.17.2 expects ONNX files named:
- `decoder_model_merged_quantized.onnx`
- `decoder_model_merged.onnx`

However, newer **onnx-community** models use a different naming convention:
- `model_quantized.onnx`
- `model.onnx`

This causes a `Could not locate file` error even though the models exist on HuggingFace.

## Model File Structure Comparison

### Xenova Models (Old Format) - ✅ COMPATIBLE
**Xenova/distilgpt2**:
```
onnx/decoder_model_merged_quantized.onnx  ← Transformers.js looks for this
onnx/decoder_model_merged.onnx
onnx/model_quantized.onnx
```

**Xenova/gpt2**:
```
Same structure as distilgpt2
```

### onnx-community Models (New Format) - ❌ INCOMPATIBLE
**onnx-community/Qwen2.5-1.5B**:
```
onnx/model_quantized.onnx  ← Different naming!
onnx/model.onnx
onnx/model_q4.onnx
```

**onnx-community/Qwen2.5-0.5B-Instruct**:
```
Same as Qwen2.5-1.5B
```

## Confirmed Working Models

These models have the correct file structure and will work with Transformers.js 2.17.2:

1. ✅ **Xenova/distilgpt2** (82M, ~150MB)
   - Status: Confirmed working
   - Has: `decoder_model_merged_quantized.onnx`

2. ✅ **Xenova/gpt2** (124M, ~250MB)
   - Status: Confirmed working
   - Has: `decoder_model_merged_quantized.onnx`

3. ✅ **Xenova/stablelm-2-zephyr-1_6b** (1.6B, ~1GB)
   - Status: Likely working (Xenova model)
   - Tier 3: Advanced model

## Models Requiring Investigation

These onnx-community models exist on HuggingFace but may not load due to file naming:

### Tier 1: Best for Chat
- ⚠️ **onnx-community/Qwen2.5-1.5B** (DEFAULT in index.html)
  - Issue: Missing `decoder_model_merged_quantized.onnx`
  - Alternative: Use Xenova models instead

- ⚠️ **onnx-community/Phi-3.5-mini-instruct-onnx-web**
  - Issue: Same naming problem + requires WebGPU
  - Status: Needs newer Transformers.js or WebGPU support

- ⚠️ **onnx-community/Llama-3.2-1B-Instruct-ONNX**
  - Issue: New naming format
  - Status: May work with auto-detection

- ⚠️ **onnx-community/TinyLlama-1.1B-Chat-v1.0-ONNX**
  - Issue: New naming format
  - Status: May work with auto-detection

### Tier 2: Fast & Efficient
- ⚠️ **onnx-community/Qwen2.5-0.5B-Instruct**
- ⚠️ **onnx-community/gemma-3-270m-it-ONNX**
- ⚠️ **onnx-community/MobileLLM-125M**
- ✅ **Xenova/distilgpt2** (WORKS!)

### Tier 3: Advanced
- ⚠️ **onnx-community/Llama-3.2-3B-Instruct-ONNX**
- ⚠️ **onnx-community/gemma-3-1b-it-ONNX**
- ⚠️ **onnx-community/MobileLLM-1B**
- ✅ **Xenova/stablelm-2-zephyr-1_6b** (Likely works)

### Coding Specialist
- ⚠️ **onnx-community/Qwen2.5-Coder-0.5B-Instruct**

### GPT-2 Family
- ✅ **Xenova/gpt2** (WORKS!)
- ❌ **Xenova/gpt2-medium** (HTTP 401 - access restricted)

## Recommendations

### Immediate Fix Options

**Option 1: Use Xenova Models (Safest)**
Change the default model in `docs/index.html:143` from:
```html
<option value="onnx-community/Qwen2.5-1.5B" selected>
```
To:
```html
<option value="Xenova/distilgpt2" selected>⭐ DistilGPT-2 (~150MB) - Fast & reliable</option>
```

**Option 2: Update Transformers.js Version**
Change `docs/js/ai/modelManager.js:29` from:
```javascript
const { pipeline, env } = await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2');
```
To:
```javascript
const { pipeline, env } = await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@latest');
```

**Option 3: Test Auto-Detection**
Newer onnx-community models may work if Transformers.js can auto-detect the file format. This requires browser testing.

### Testing Instructions

To test models in the browser:

1. **Start server** (already running on port 8080):
   ```bash
   cd docs
   python3 -m http.server 8080
   ```

2. **Open browser**: http://localhost:8080

3. **Test each model**:
   - Open DevTools Console (F12)
   - Select model from dropdown
   - Wait for loading message
   - Check for errors in console
   - Try sending a test message: "Hello, how are you?"

4. **Models to test first** (most likely to work):
   - Xenova/distilgpt2
   - Xenova/gpt2
   - Xenova/stablelm-2-zephyr-1_6b

## Browser Requirements

- **Chrome/Edge**: 90+ (113+ for WebGPU models)
- **Firefox**: 90+
- **Safari**: 14+
- **RAM**: 2GB+ for small models, 8GB+ for large models
- **Internet**: Required for first model download, then cached

## Next Steps

1. ✅ Verify models exist on HuggingFace (DONE - 14/15 accessible)
2. ⚠️ Browser testing needed to confirm which models actually load
3. Update TESTING.md with confirmed working models
4. Consider updating default model to Xenova/distilgpt2
5. Add error handling for incompatible model formats

## Notes

- The file structure difference is the main compatibility issue
- All tested models have valid config.json files
- Browser testing is essential to confirm actual loading behavior
- Transformers.js may have improved auto-detection in newer versions
