# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GPT-2 chatbot web application with Flask backend and conversation history persistence. The app uses HuggingFace's Transformers library to run GPT-2 locally for conversational AI.

## Development Commands

### Running the Application
```bash
python app.py
```
Starts Flask server on http://localhost:5000. The GPT-2 model will download automatically on first run (~500MB).

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Layer Structure

The application follows a clean 3-layer architecture:

1. **API Layer** (`api/routes.py`): Flask blueprint with REST endpoints, handles HTTP requests/responses
2. **Service Layer** (`services/`): Business logic, orchestrates between storage and model
3. **Model Layer** (`models/gpt2_model.py`): GPT-2 wrapper, handles tokenization and generation

### Key Components

**GPT2ChatModel** (`models/gpt2_model.py`):
- Singleton pattern - only one model instance loads into memory
- Automatically detects CUDA/CPU on initialization
- Thread-safe model loading with `_initialized` flag
- Token counting method used for context management

**ChatService** (`services/chat_service.py`):
- Core conversation flow: format history → create prompt → generate → extract response
- Context window management: enforces 512 token limit for prompt (leaves 512 for generation)
- Conversation formatting: "User: {msg}\nAssistant: {response}" pattern for GPT-2
- Response extraction: strips prefixes, handles model hallucinating extra turns

**StorageService** (`services/storage_service.py`):
- JSON file-based storage in `data/conversations/`
- Each conversation = one UUID-named JSON file
- Messages stored with role, content, timestamp
- Metadata tracks total_messages and last model_config used

### Request Flow

```
User message → API routes → ChatService.process_message() →
  1. Save user message to storage
  2. Load last N messages (MAX_HISTORY_MESSAGES)
  3. Format conversation history with token limit
  4. Create prompt with "Assistant:" suffix
  5. Generate response via GPT2ChatModel
  6. Extract and clean response text
  7. Save assistant response to storage
  8. Return response with metadata
```

### Context Management Strategy

GPT-2 has 1024 token context window. The app:
- Reserves 512 tokens for conversation history (MAX_CONTEXT_TOKENS)
- Reserves remaining tokens for generation (MAX_LENGTH default 100)
- Truncates old messages from beginning if token limit exceeded
- Always preserves the most recent user message
- Token counting happens before generation to prevent overflow

### Model Generation Parameters

Configured in `config.py`:
- `TEMPERATURE` (0.7): Controls randomness. Higher = more creative, lower = more deterministic
- `TOP_K` (50): Considers top 50 most likely next tokens
- `TOP_P` (0.9): Nucleus sampling threshold
- `REPETITION_PENALTY` (1.2): Penalizes repeated tokens to reduce loops
- `MAX_LENGTH` (100): Maximum tokens to generate per response

### Service Initialization

Services are initialized at module import time in `api/routes.py`:
```python
storage_service = StorageService(Config.DATA_DIR)
chat_service = ChatService(storage_service, Config)
```

The ChatService constructor loads the GPT-2 model, so first request may be slow. Model stays loaded in memory for subsequent requests.

## Configuration

All configuration is in `config.py` as a single Config class:
- Model parameters (temperature, max_length, etc.)
- Context limits (MAX_HISTORY_MESSAGES, MAX_CONTEXT_TOKENS)
- File paths (DATA_DIR)
- Flask settings (DEBUG, SECRET_KEY from environment)

## Common Issues

**Model loading fails**: Requires internet connection on first run. Model downloads from HuggingFace Hub to `~/.cache/huggingface/`.

**Out of memory**: Reduce MAX_CONTEXT_TOKENS or MAX_LENGTH in config.py. GPT-2 requires ~500MB RAM minimum.

**Slow generation on CPU**: Normal behavior. GPT-2 takes 5-10 seconds per response without GPU. The model automatically uses CUDA if available.

**Context overflow**: If prompt exceeds 1024 tokens, model truncates to last 1000 tokens (hardcoded in `gpt2_model.py:77`).

## API Endpoints

- `POST /api/conversations` - Create new conversation (returns UUID)
- `POST /api/conversations/{id}/messages` - Send message, get AI response
- `GET /api/conversations/{id}/messages` - Load conversation history
- `GET /api/conversations` - List all conversation IDs
- `DELETE /api/conversations/{id}` - Delete conversation file
- `GET /api/health` - Check if model is loaded

## Testing

### Running Tests

The project has a comprehensive test suite with 45 tests covering all components.

```bash
# Run all tests
pytest

# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_storage_service.py

# Run tests with coverage
pytest --cov=. --cov-report=html
```

### Test Structure

- `tests/test_storage_service.py` - Tests for conversation storage and retrieval
- `tests/test_gpt2_model.py` - Tests for GPT-2 model wrapper (uses mocking to avoid loading actual model)
- `tests/test_chat_service.py` - Tests for conversation formatting and message processing logic
- `tests/test_routes.py` - Integration tests for Flask API endpoints
- `tests/conftest.py` - Shared pytest fixtures

### Manual Testing

To test the application manually:
1. Start server with `python app.py` (or `python3 app.py`)
2. Open browser to http://localhost:5000
3. Send messages and verify responses
4. Check `data/conversations/` for JSON files

## Dependencies

- Flask 3.0.0: Web framework
- flask-cors 4.0.0: CORS support for API
- torch 2.1.2: PyTorch for model inference
- transformers 4.36.2: HuggingFace library for GPT-2
- python-dotenv 1.0.0: Environment variable loading
