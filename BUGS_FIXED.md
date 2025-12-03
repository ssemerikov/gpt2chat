# Bugs Fixed

This document lists all bugs identified and fixed in the GPT-2 chatbot codebase.

## Critical Bugs

### 1. Incorrect pad_token_id Type (models/gpt2_model.py:90)
**Severity**: High
**Location**: `models/gpt2_model.py:90`

**Issue**:
```python
pad_token_id=self.tokenizer.eos_token,  # WRONG - this is a string
```

**Problem**: The code was passing `self.tokenizer.eos_token` (which is a string like `"<|endoftext|>"`) instead of `self.tokenizer.eos_token_id` (an integer). PyTorch's `generate()` method expects an integer token ID, not a string.

**Fix**:
```python
pad_token_id=self.tokenizer.eos_token_id,  # CORRECT - this is an integer
```

**Impact**: This would cause a runtime error when the model tries to generate responses, as it cannot use a string as a token ID.

---

### 2. Incorrect Response Extraction (models/gpt2_model.py:98)
**Severity**: Critical
**Location**: `models/gpt2_model.py:94-98`

**Issue**:
```python
# Декодування
generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# Видалення prompt з результату
response = generated_text[len(prompt):].strip()  # WRONG
```

**Problem**: The code attempted to remove the prompt from the generated text using character-based slicing `[len(prompt):]`. This is incorrect because:
1. The tokenizer may add/remove whitespace during encoding/decoding
2. The decoded text may have different formatting than the original prompt
3. This can result in cutting off the actual response or including parts of the prompt

**Fix**:
```python
# Декодування тільки нових токенів (без prompt)
# outputs[0] містить всі токени (prompt + згенеровані)
# inputs.shape[1] - кількість токенів у prompt
new_tokens = outputs[0][inputs.shape[1]:]
response = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
```

**Impact**: This bug would cause garbled or incorrect responses, potentially including parts of the user's prompt in the assistant's response, or cutting off the beginning of the actual response.

---

### 3. Insufficient Context Truncation (services/chat_service.py:47)
**Severity**: Medium
**Location**: `services/chat_service.py:47`

**Issue**:
```python
while token_count > max_tokens and len(formatted_lines) > 2:  # WRONG
```

**Problem**: The loop exits when there are only 2 formatted lines remaining, even if those 2 lines still exceed the token limit. This could cause:
1. Exceeding the model's context window (1024 tokens for GPT-2)
2. Runtime errors during generation
3. Poor model performance due to truncated prompts

**Fix**:
```python
while token_count > max_tokens and len(formatted_lines) > 1:  # CORRECT
```

**Impact**: This ensures we continue truncating until we're under the limit, keeping at least 1 message (the most recent one).

---

## Test Suite Created

A comprehensive test suite was created with 45 tests covering:

- **StorageService** (13 tests): Conversation creation, message storage, retrieval, deletion
- **GPT2ChatModel** (8 tests): Model loading, generation, token counting, error handling
- **ChatService** (14 tests): History formatting, prompt creation, response extraction, message processing
- **API Routes** (12 tests): All endpoints, error handling, CORS

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_storage_service.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Results

All 45 tests pass successfully:
```
======================== 45 passed, 2 warnings in 0.31s ========================
```

## Dependencies Added

Added to `requirements.txt`:
- `pytest==7.4.3`
- `pytest-flask==1.3.0`
- `pytest-mock==3.12.0`
