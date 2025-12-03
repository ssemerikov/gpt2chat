from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class GPT2ChatModel:
    """Singleton клас для роботи з GPT-2 моделлю"""

    _instance: Optional['GPT2ChatModel'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        self.model = None
        self.tokenizer = None
        self._initialized = True

    def load_model(self, model_name: str = "openai-community/gpt2"):
        """Завантаження моделі та токенізатора"""
        if self.model is None:
            logger.info(f"Loading model: {model_name}")
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()

            # Встановлення pad_token (GPT-2 не має його за замовчуванням)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.info("Model loaded successfully")

    def generate_response(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        repetition_penalty: float = 1.2,
        num_return_sequences: int = 1
    ) -> str:
        """
        Генерація відповіді на основі prompt

        Args:
            prompt: Текстовий prompt (історія + нове повідомлення)
            max_length: Максимальна довжина генерації
            temperature: Креативність (вище = більше креативності)
            top_k: Розглядати top-k найімовірніших токенів
            top_p: Nucleus sampling параметр
            repetition_penalty: Штраф за повторення слів
            num_return_sequences: Кількість варіантів відповіді

        Returns:
            Згенерована відповідь
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Токенізація prompt
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        # Перевірка довжини prompt
        if inputs.shape[1] > 1024:  # GPT-2 max context
            logger.warning(f"Prompt too long ({inputs.shape[1]} tokens), truncating...")
            inputs = inputs[:, -1000:]  # Залишаємо останні 1000 токенів

        # Генерація
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token,
                eos_token_id=self.tokenizer.eos_token_id
            )

        # Декодування
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Видалення prompt з результату
        response = generated_text[len(prompt):].strip()

        return response

    def count_tokens(self, text: str) -> int:
        """Підрахунок токенів в тексті"""
        return len(self.tokenizer.encode(text))
