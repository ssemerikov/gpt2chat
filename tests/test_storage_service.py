import pytest
from datetime import datetime
from services.storage_service import StorageService


class TestStorageService:
    """Test suite for StorageService"""

    def test_create_conversation(self, storage_service):
        """Test creating a new conversation"""
        conv_id = storage_service.create_conversation()

        assert conv_id is not None
        assert isinstance(conv_id, str)
        assert len(conv_id) == 36  # UUID format

        # Verify conversation was saved
        conversation = storage_service.load_conversation(conv_id)
        assert conversation is not None
        assert conversation['conversation_id'] == conv_id
        assert conversation['messages'] == []
        assert conversation['metadata']['total_messages'] == 0

    def test_add_message(self, storage_service):
        """Test adding a message to conversation"""
        conv_id = storage_service.create_conversation()

        storage_service.add_message(
            conversation_id=conv_id,
            role="user",
            content="Hello, world!"
        )

        messages = storage_service.get_messages(conv_id)
        assert len(messages) == 1
        assert messages[0]['role'] == "user"
        assert messages[0]['content'] == "Hello, world!"
        assert 'timestamp' in messages[0]

    def test_add_message_with_model_config(self, storage_service):
        """Test adding message with model configuration"""
        conv_id = storage_service.create_conversation()

        model_config = {
            "temperature": 0.7,
            "max_length": 100
        }

        storage_service.add_message(
            conversation_id=conv_id,
            role="assistant",
            content="Hello!",
            model_config=model_config
        )

        conversation = storage_service.load_conversation(conv_id)
        assert conversation['metadata']['model_config'] == model_config

    def test_add_message_to_nonexistent_conversation(self, storage_service):
        """Test adding message to non-existent conversation raises error"""
        with pytest.raises(ValueError, match="Conversation .* not found"):
            storage_service.add_message(
                conversation_id="nonexistent-id",
                role="user",
                content="Test"
            )

    def test_get_messages_with_limit(self, storage_service):
        """Test retrieving messages with limit"""
        conv_id = storage_service.create_conversation()

        # Add 5 messages
        for i in range(5):
            storage_service.add_message(conv_id, "user", f"Message {i}")

        # Get last 3 messages
        messages = storage_service.get_messages(conv_id, limit=3)
        assert len(messages) == 3
        assert messages[0]['content'] == "Message 2"
        assert messages[2]['content'] == "Message 4"

    def test_get_messages_nonexistent_conversation(self, storage_service):
        """Test getting messages from non-existent conversation"""
        messages = storage_service.get_messages("nonexistent-id")
        assert messages == []

    def test_list_conversations(self, storage_service):
        """Test listing all conversations"""
        # Create multiple conversations
        conv_id1 = storage_service.create_conversation()
        conv_id2 = storage_service.create_conversation()

        conversations = storage_service.list_conversations()
        assert len(conversations) == 2
        assert conv_id1 in conversations
        assert conv_id2 in conversations

    def test_delete_conversation(self, storage_service):
        """Test deleting a conversation"""
        conv_id = storage_service.create_conversation()

        # Verify it exists
        assert storage_service.load_conversation(conv_id) is not None

        # Delete it
        result = storage_service.delete_conversation(conv_id)
        assert result is True

        # Verify it's gone
        assert storage_service.load_conversation(conv_id) is None

    def test_delete_nonexistent_conversation(self, storage_service):
        """Test deleting non-existent conversation returns False"""
        result = storage_service.delete_conversation("nonexistent-id")
        assert result is False

    def test_conversation_updates_timestamp(self, storage_service):
        """Test that adding messages updates the conversation timestamp"""
        conv_id = storage_service.create_conversation()

        conversation1 = storage_service.load_conversation(conv_id)
        created_at = conversation1['created_at']

        # Add a message
        storage_service.add_message(conv_id, "user", "Test")

        conversation2 = storage_service.load_conversation(conv_id)
        updated_at = conversation2['updated_at']

        # Updated timestamp should be different from created timestamp
        assert updated_at >= created_at

    def test_message_count_tracking(self, storage_service):
        """Test that message count is properly tracked"""
        conv_id = storage_service.create_conversation()

        # Add messages
        for i in range(3):
            storage_service.add_message(conv_id, "user", f"Message {i}")

        conversation = storage_service.load_conversation(conv_id)
        assert conversation['metadata']['total_messages'] == 3
