import os
from pathlib import Path

class Config:
    """Конфігурація додатку"""

    # Базові налаштування
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data" / "conversations"

    # Налаштування моделі GPT-2
    MODEL_NAME = "openai-community/gpt2"
    MAX_LENGTH = 100              # Максимальна довжина генерації
    MAX_CONTEXT_TOKENS = 512      # Максимум токенів контексту (GPT-2 max = 1024)
    TEMPERATURE = 0.7             # Креативність (0.1-1.0)
    TOP_K = 50                    # Top-k sampling
    TOP_P = 0.9                   # Nucleus sampling
    REPETITION_PENALTY = 1.2      # Штраф за повторення

    # Налаштування історії діалогу
    MAX_HISTORY_MESSAGES = 10     # Скільки повідомлень зберігати в контексті

    # Flask налаштування
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "True") == "True"
