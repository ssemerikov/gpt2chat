# Runtime Compatibility Testing

## Issue Identified

Some models have correct file structure (`decoder_model_merged_quantized.onnx`) but fail during **text generation** with ONNX Runtime error code 2.

## Error Example: Llama2 Stories Models

```
Error: failed to call OrtRun(). error code = 2.
Inputs given to model: past_key_values.0.key, past_key_values.0.value, ...
```

**Location**: During generation in `modelManager.js:150`
**Stage**: After model loads successfully, during first text generation
**Error Type**: ONNX Runtime execution error (not file loading)

## ✅ CORRECTION: llama2.c Models ARE COMPATIBLE!

### Llama2.c Stories Family (VERIFIED WORKING - 2025-12-04)
- ✅ Xenova/llama2.c-stories15M - **WORKS** (6.7s total)
- ✅ Xenova/llama2.c-stories42M - **WORKS** (12.9s total)
- ✅ Xenova/llama2.c-stories110M - **WORKS** (19.5s total)

**Previous assumption was incorrect!** These models work perfectly in ONNX Runtime Web and are among the fastest, most efficient models available.

## Testing Approach Needed

### Phase 1: File Structure ✅ (COMPLETED)
- Verify `decoder_model_merged_quantized.onnx` exists
- Result: 61 models found

### Phase 2: Runtime Generation ⚠️ (IN PROGRESS)
- Load model
- Attempt text generation
- Verify successful completion
- **This phase reveals compatibility issues**

## Recommended Action

1. **Create runtime test script** that:
   - Loads each model
   - Attempts to generate text (simple prompt)
   - Records success/failure
   - Identifies ONNX Runtime errors

2. **Update model list** to include only models that:
   - ✅ Have correct file structure
   - ✅ Load successfully
   - ✅ **Generate text successfully**

3. **Categorize models**:
   - **Verified Working**: Full generation test passed
   - **Load Only**: Model loads but generation fails
   - **Incompatible**: File structure issues

## Next Steps

```javascript
// Proposed test function
async function testModelGeneration(modelName) {
  try {
    const generator = await pipeline('text-generation', modelName);
    const result = await generator('Hello', { max_length: 10 });
    return { model: modelName, status: 'SUCCESS', result };
  } catch (error) {
    return { model: modelName, status: 'FAILED', error: error.message };
  }
}
```

## Expected Outcome

- Some models will be removed from the "verified" list
- Users will only see models that actually work end-to-end
- Reduce false positives from file structure check only

## Model Architecture Compatibility

### Likely Compatible
- GPT-2 family (proven architecture)
- GPT-Neo family
- OPT family
- BLOOM family
- Most CodeGen models

### Potentially Incompatible
- llama2.c (simplified/custom architecture)
- Tiny random models (testing stubs)
- Some Falcon variants
- Models with custom attention mechanisms

## Resources

- [HuggingFace Discussion: llama2.c ONNX errors](https://huggingface.co/Xenova/llama2.c-stories42M/discussions/1)
- [Transformers.js GitHub](https://github.com/xenova/transformers.js/)
- [ONNX Runtime Web Documentation](https://www.npmjs.com/package/@xenova/transformers)

---

**Status**: ✅ COMPLETE - All 61 models tested (2025-12-04)
**Results**: 46 working models, 15 removed (4 ONNX errors, 11 timeouts)
**Impact**: HTML dropdown now contains only verified working models

See **VERIFIED_MODELS.md** for complete test results and recommendations.
