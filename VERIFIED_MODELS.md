# Verified Working Models - Runtime Compatibility Test Results

**Test Date:** 2025-12-04
**Test Method:** Individual runtime testing with actual text generation
**Test Parameters:** prompt="Hello, this is a test.", max_new_tokens=20, temperature=0.7

## Summary

- **Total Models Tested:** 61
- **✅ Verified Working:** 46 models
- **❌ Incompatible/Slow:** 15 models

## Testing Methodology

Each model was tested individually in a fresh Playwright browser session:
1. Load the model from HuggingFace
2. Generate text with test prompt
3. Record load time, generation time, and output
4. Classify as success/timeout/error

Models that exceeded 120 seconds or encountered ONNX Runtime errors were marked as incompatible.

---

## ✅ Verified Working Models (46)

### Ultra Fast Models (< 10s total time)

| Model | Load Time | Gen Time | Total Time | Notes |
|-------|-----------|----------|------------|-------|
| Xenova/tiny-random-PhiForCausalLM | 1.9s | 0.2s | 2.1s | Test stub |
| Xenova/tiny-random-Starcoder2ForCausalLM | 2.4s | 0.2s | 2.6s | Test stub |
| Xenova/tiny-random-StableLmForCausalLM | 2.4s | 0.3s | 2.7s | Test stub |
| Xenova/tiny-random-mistral | 2.4s | 1.0s | 3.4s | Test stub |
| Xenova/really-tiny-falcon-testing | 2.6s | 2.3s | 4.9s | Test stub |
| Xenova/TinyLLama-v0 | 4.9s | 0.8s | 5.7s | Working model |
| Xenova/llama2.c-stories15M | 4.9s | 1.8s | 6.7s | **Stories - WORKS!** |
| Xenova/pythia-31m | 6.7s | 1.2s | 7.9s | Smallest Pythia |
| Xenova/pythia-14m | 6.4s | 2.2s | 8.6s | Ultra fast |
| Xenova/tamillama_tiny_30m | 8.5s | 1.2s | 9.7s | Tamil language |

### Fast Models (10-20s total time)

| Model | Load Time | Gen Time | Total Time |
|-------|-----------|----------|------------|
| Xenova/llama-68m | 9.1s | 1.2s | 10.3s |
| Xenova/pythia-70m | 10.5s | 1.6s | 12.1s |
| Xenova/pythia-70m-deduped | 11.0s | 1.8s | 12.8s |
| Xenova/llama2.c-stories42M | 11.3s | 1.6s | 12.9s |
| Xenova/gpt-neo-125M | 16.3s | 2.4s | 18.7s |
| Xenova/gpt2 | 15.9s | 2.5s | 18.4s |
| Xenova/llama2.c-stories110M | 16.2s | 3.3s | 19.5s |

### Medium Models (20-30s total time)

| Model | Load Time | Gen Time | Total Time |
|-------|-----------|----------|------------|
| Xenova/LaMini-GPT-124M | 17.6s | 3.1s | 20.7s |
| Xenova/llama-160m | 19.1s | 1.5s | 20.6s |
| Xenova/LaMini-Neo-125M | 17.0s | 2.3s | 19.3s |
| Xenova/distilgpt2 | 14.9s | 7.1s | 22.0s |
| Xenova/tiny-random-falcon-7b | 15.2s | 7.5s | 22.7s |
| Xenova/gpt-neo-romanian-125m | 19.3s | 4.8s | 24.1s |
| Xenova/pythia-160m | 21.5s | 2.8s | 24.3s |
| Xenova/pythia-160m-deduped | 21.9s | 2.5s | 24.4s |
| Xenova/LaMini-Cerebras-111M | 20.7s | 6.9s | 27.6s |

### Large Models (30-60s total time)

| Model | Load Time | Gen Time | Total Time |
|-------|-----------|----------|------------|
| Xenova/LaMini-Cerebras-256M | 29.6s | 3.1s | 32.7s |
| Xenova/tiny_starcoder_py | 33.8s | 2.2s | 36.0s |
| Xenova/J-350M | 41.4s | 3.9s | 45.3s |
| Xenova/kogpt-j-350m | 42.1s | 4.7s | 46.8s |
| Xenova/slovak-gpt-j-405M | 46.1s | 4.9s | 51.0s |
| Xenova/ipt-350m | 40.4s | 7.1s | 47.5s |
| Xenova/codegen-350M-mono | 45.6s | 2.9s | 48.5s |
| Xenova/pythia-410m | 45.8s | 3.5s | 49.3s |
| Xenova/Qwen1.5-0.5B-Chat | 49.2s | 0.8s | 50.0s |
| Xenova/codegen-350M-multi | 48.6s | 3.1s | 51.7s |
| Xenova/codegen-350M-nl | 55.8s | 5.5s | 61.3s |
| Xenova/pythia-410m-deduped | 51.2s | 5.5s | 56.7s |
| Xenova/LiteLlama-460M-1T | 52.0s | 7.7s | 59.7s |

### Extra Large Models (60-100s total time)

| Model | Load Time | Gen Time | Total Time |
|-------|-----------|----------|------------|
| Xenova/bloomz-560m | 62.7s | 15.0s | 77.7s |
| Xenova/bloom-560m | 64.0s | 14.4s | 78.4s |
| Xenova/Qwen1.5-0.5B | 54.3s | 17.5s | 71.8s |
| Xenova/LaMini-Cerebras-590M | 73.8s | 5.7s | 79.5s |
| Xenova/LaMini-GPT-774M | 81.5s | 0.7s | 82.2s |
| Xenova/gpt2-large-conversational | 90.6s | 11.0s | 101.6s |
| Xenova/dlite-v2-774m | 87.7s | 12.5s | 100.2s |

---

## ❌ Incompatible/Removed Models (15)

### ONNX Runtime Errors (4 models)

These models have fundamental incompatibility with ONNX Runtime Web:

| Model | Error | Reason |
|-------|-------|--------|
| Xenova/TinyLlama-1.1B-Chat-v1.0 | `offset is out of bounds` | Memory access violation |
| Xenova/opt-125m | `OrtRun() error code = 1` | ONNX execution failure |
| Xenova/opt-350m | `OrtRun() error code = 1` | ONNX execution failure |
| Xenova/pygmalion-350m | `OrtRun() error code = 1` | ONNX execution failure |

### Timeout Errors (11 models)

These models exceeded 120 seconds (too slow for browser use):

- Xenova/Qwen1.5-1.8B-Chat
- Xenova/Qwen1.5-1.8B
- Xenova/WizardCoder-1B-V1.0
- Xenova/deepseek-coder-1.3b-instruct
- Xenova/deepseek-coder-1.3b-base
- Xenova/phi-1_5_dev
- Xenova/starcoderbase-1b
- Xenova/starcoderbase-1b-sft
- Xenova/falcon-rw-1b
- Xenova/stablelm-2-zephyr-1_6b
- Xenova/stablelm-2-1_6b

**Note:** These models may work on faster hardware or with longer timeouts, but are impractical for typical browser use.

---

## Key Findings

### ✅ llama2.c Models ARE COMPATIBLE

Contrary to earlier documentation, all three llama2.c story models work perfectly:
- **Xenova/llama2.c-stories15M** - 6.7s total ✅
- **Xenova/llama2.c-stories42M** - 12.9s total ✅
- **Xenova/llama2.c-stories110M** - 19.5s total ✅

These are among the fastest and most efficient models available.

### 🚀 Recommended Models for Low-End Devices

**Top 5 for speed and quality:**
1. Xenova/llama2.c-stories15M (6.7s) - Best balance
2. Xenova/pythia-14m (8.6s) - Fastest general model
3. Xenova/distilgpt2 (22s) - DEFAULT, good quality
4. Xenova/llama2.c-stories110M (19.5s) - Better quality stories
5. Xenova/gpt2 (18.4s) - Classic OpenAI

### 📊 Model Architecture Compatibility

**Working Architectures:**
- ✅ GPT-2 family (all working)
- ✅ GPT-Neo family (all working)
- ✅ Pythia family (all working)
- ✅ llama2.c family (all working - corrected!)
- ✅ BLOOM family (working, but slow)
- ✅ CodeGen family (most working)
- ✅ LaMini family (all working)

**Problematic Architectures:**
- ❌ OPT family (ONNX errors)
- ⏱️ StableLM 1.6B+ (too slow)
- ⏱️ StarCoder 1B+ (too slow)
- ⏱️ DeepSeek 1.3B+ (too slow)
- ⏱️ Falcon 1B+ (too slow)

---

## Testing Infrastructure

All testing performed using:
- **Tool:** `test_models_individually.py` + `test_one_model.js`
- **Browser:** Chromium (Playwright)
- **Environment:** Node.js + Python 3
- **Timeout:** 120 seconds per model
- **Results:** Saved to `individual_test_results.json`

**Test Script Location:** `/home/cc/claude_code/gpt2chat/`

---

## Changelog

**2025-12-04:**
- Initial comprehensive runtime testing
- Tested all 61 models individually
- Removed 15 incompatible/slow models from HTML
- Verified 46 working models
- **Corrected llama2.c compatibility** (previously marked as broken)
