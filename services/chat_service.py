from typing import List, Dict
from models.gpt2_model import GPT2ChatModel
from services.storage_service import StorageService
from config import Config
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """Сервіс для обробки чат-логіки"""

    def __init__(self, storage_service: StorageService, config: Config):
        self.storage = storage_service
        self.config = config
        self.model = GPT2ChatModel()
        self.model.load_model(config.MODEL_NAME)

    def format_conversation_history(
        self,
        messages: List[Dict],
        max_tokens: int
    ) -> str:
        """
        Форматування історії діалогу для GPT-2

        Стратегія:
        1. Форматуємо у вигляді "User: ... Assistant: ..."
        2. Обрізаємо старі повідомлення якщо перевищено ліміт токенів
        3. Завжди залишаємо останнє повідомлення користувача
        """
        if not messages:
            return ""

        # Форматування повідомлень
        formatted_lines = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_lines.append(f"{role}: {msg['content']}")

        # Об'єднання в один текст
        full_text = "\n".join(formatted_lines)

        # Перевірка кількості токенів
        token_count = self.model.count_tokens(full_text)

        # Якщо перевищено ліміт - обрізаємо старі повідомлення
        while token_count > max_tokens and len(formatted_lines) > 2:
            formatted_lines.pop(0)  # Видаляємо найстаріше
            full_text = "\n".join(formatted_lines)
            token_count = self.model.count_tokens(full_text)

        return full_text

    def create_prompt(self, conversation_history: str, new_message: str) -> str:
        """
        Створення prompt для моделі

        Формат:
        [Історія діалогу]
        User: [Нове повідомлення]
        Assistant:
        """
        if conversation_history:
            prompt = f"{conversation_history}\nUser: {new_message}\nAssistant:"
        else:
            prompt = f"User: {new_message}\nAssistant:"

        return prompt

    def extract_response(self, generated_text: str) -> str:
        """
        Витяг чистої відповіді з згенерованого тексту

        Обробка:
        - Видалення зайвих символів
        - Обрізання до першого переходу на нову роль
        - Обмеження довжини
        """
        response = generated_text.strip()

        # Обрізаємо якщо модель почала генерувати наступну репліку
        if "\nUser:" in response:
            response = response.split("\nUser:")[0].strip()

        if "\nAssistant:" in response:
            response = response.split("\nAssistant:")[0].strip()

        # Видалення префіксів якщо модель їх згенерувала
        for prefix in ["Assistant:", "Bot:", "AI:"]:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        return response

    def process_message(
        self,
        conversation_id: str,
        user_message: str
    ) -> Dict:
        """
        Обробка повідомлення користувача

        Returns:
            Dict з відповіддю та метаданими
        """
        try:
            # Збереження повідомлення користувача
            self.storage.add_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )

            # Завантаження історії
            messages = self.storage.get_messages(
                conversation_id,
                limit=self.config.MAX_HISTORY_MESSAGES
            )

            # Видалення останнього повідомлення (щойно додане) для форматування
            history_messages = messages[:-1]

            # Форматування історії
            conversation_history = self.format_conversation_history(
                history_messages,
                max_tokens=self.config.MAX_CONTEXT_TOKENS - 100
            )

            # Створення prompt
            prompt = self.create_prompt(conversation_history, user_message)

            logger.info(f"Prompt length: {self.model.count_tokens(prompt)} tokens")

            # Генерація відповіді
            generated = self.model.generate_response(
                prompt=prompt,
                max_length=self.config.MAX_LENGTH,
                temperature=self.config.TEMPERATURE,
                top_k=self.config.TOP_K,
                top_p=self.config.TOP_P,
                repetition_penalty=self.config.REPETITION_PENALTY
            )

            # Витяг відповіді
            response = self.extract_response(generated)

            # Збереження відповіді асистента
            model_config = {
                "temperature": self.config.TEMPERATURE,
                "max_length": self.config.MAX_LENGTH,
                "top_k": self.config.TOP_K,
                "top_p": self.config.TOP_P
            }

            self.storage.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response,
                model_config=model_config
            )

            return {
                "success": True,
                "response": response,
                "conversation_id": conversation_id,
                "metadata": {
                    "prompt_tokens": self.model.count_tokens(prompt),
                    "model_config": model_config
                }
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }
