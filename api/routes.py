from flask import Blueprint, request, jsonify, render_template
from services.chat_service import ChatService
from services.storage_service import StorageService
from config import Config
import logging

logger = logging.getLogger(__name__)

# Створення blueprint
api_bp = Blueprint('api', __name__)

# Ініціалізація сервісів
storage_service = StorageService(Config.DATA_DIR)
chat_service = ChatService(storage_service, Config)

@api_bp.route('/')
def index():
    """Головна сторінка"""
    return render_template('index.html')

@api_bp.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Створення нової розмови"""
    try:
        conversation_id = storage_service.create_conversation()
        return jsonify({
            "success": True,
            "conversation_id": conversation_id
        })
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Відправка повідомлення"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400

        user_message = data['message'].strip()

        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400

        # Обробка повідомлення
        result = chat_service.process_message(conversation_id, user_message)

        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error in send_message: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/conversations/<conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """Отримання історії повідомлень"""
    try:
        messages = storage_service.get_messages(conversation_id)
        return jsonify({
            "success": True,
            "messages": messages
        })
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/conversations', methods=['GET'])
def list_conversations():
    """Список всіх розмов"""
    try:
        conversations = storage_service.list_conversations()
        return jsonify({
            "success": True,
            "conversations": conversations
        })
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Видалення розмови"""
    try:
        success = storage_service.delete_conversation(conversation_id)
        return jsonify({
            "success": success
        })
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/api/health', methods=['GET'])
def health_check():
    """Перевірка стану системи"""
    return jsonify({
        "status": "healthy",
        "model_loaded": chat_service.model.model is not None
    })
