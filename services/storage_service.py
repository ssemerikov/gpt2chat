import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Сервіс для збереження та завантаження діалогів"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_conversation(self) -> str:
        """Створення нової розмови"""
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            "conversation_id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "metadata": {
                "total_messages": 0,
                "model_config": {}
            }
        }

        self._save_conversation(conversation_id, conversation_data)
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model_config: Optional[Dict] = None
    ):
        """Додавання повідомлення до розмови"""
        conversation = self.load_conversation(conversation_id)

        if conversation is None:
            raise ValueError(f"Conversation {conversation_id} not found")

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        conversation["messages"].append(message)
        conversation["updated_at"] = datetime.now().isoformat()
        conversation["metadata"]["total_messages"] = len(conversation["messages"])

        if model_config:
            conversation["metadata"]["model_config"] = model_config

        self._save_conversation(conversation_id, conversation)

    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Завантаження розмови"""
        file_path = self._get_file_path(conversation_id)

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id}: {e}")
            return None

    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Отримання повідомлень з розмови"""
        conversation = self.load_conversation(conversation_id)

        if conversation is None:
            return []

        messages = conversation["messages"]

        if limit:
            return messages[-limit:]

        return messages

    def list_conversations(self) -> List[str]:
        """Список всіх розмов"""
        return [f.stem for f in self.data_dir.glob("*.json")]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Видалення розмови"""
        file_path = self._get_file_path(conversation_id)

        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted conversation: {conversation_id}")
            return True

        return False

    def _save_conversation(self, conversation_id: str, data: Dict):
        """Внутрішній метод збереження"""
        file_path = self._get_file_path(conversation_id)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_file_path(self, conversation_id: str) -> Path:
        """Отримання шляху до файлу розмови"""
        return self.data_dir / f"{conversation_id}.json"
