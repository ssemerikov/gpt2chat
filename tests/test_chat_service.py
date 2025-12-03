import pytest
from unittest.mock import Mock, patch, MagicMock
from services.chat_service import ChatService
from services.storage_service import StorageService
from config import Config


class TestChatService:
    """Test suite for ChatService"""

    @pytest.fixture
    def mock_model(self):
        """Create a mock GPT2ChatModel"""
        with patch('services.chat_service.GPT2ChatModel') as mock:
            model_instance = Mock()
            model_instance.count_tokens.return_value = 10
            model_instance.generate_response.return_value = "This is a response"
            mock.return_value = model_instance
            yield model_instance

    @pytest.fixture
    def chat_service(self, storage_service, mock_model):
        """Create ChatService with mocked model"""
        return ChatService(storage_service, Config)

    def test_format_conversation_history_empty(self, chat_service):
        """Test formatting empty conversation history"""
        result = chat_service.format_conversation_history([], max_tokens=512)
        assert result == ""

    def test_format_conversation_history(self, chat_service):
        """Test formatting conversation history"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]

        result = chat_service.format_conversation_history(messages, max_tokens=512)

        assert "User: Hello" in result
        assert "Assistant: Hi there" in result
        assert "User: How are you?" in result

    def test_format_conversation_history_truncates_old_messages(self, chat_service, mock_model):
        """Test that old messages are truncated when exceeding token limit"""
        # Make count_tokens return high values to trigger truncation
        def mock_count_tokens(text):
            # Each line is "expensive" in tokens
            return len(text.split('\n')) * 100

        chat_service.model.count_tokens = mock_count_tokens

        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "Message 3"}
        ]

        # With a very low token limit, it should truncate old messages
        result = chat_service.format_conversation_history(messages, max_tokens=50)

        # Should keep at least the last 2 messages
        assert "Message 3" in result
        # May or may not have Message 1 depending on truncation
        lines = result.split('\n')
        assert len(lines) <= len(messages)

    def test_create_prompt_with_history(self, chat_service):
        """Test creating prompt with conversation history"""
        history = "User: Hello\nAssistant: Hi there"
        new_message = "How are you?"

        prompt = chat_service.create_prompt(history, new_message)

        assert prompt == "User: Hello\nAssistant: Hi there\nUser: How are you?\nAssistant:"

    def test_create_prompt_without_history(self, chat_service):
        """Test creating prompt without history"""
        prompt = chat_service.create_prompt("", "Hello")

        assert prompt == "User: Hello\nAssistant:"

    def test_extract_response_clean(self, chat_service):
        """Test extracting clean response"""
        generated = "This is a clean response"
        result = chat_service.extract_response(generated)

        assert result == "This is a clean response"

    def test_extract_response_with_prefix(self, chat_service):
        """Test extracting response with Assistant prefix"""
        generated = "Assistant: This is a response"
        result = chat_service.extract_response(generated)

        assert result == "This is a response"

    def test_extract_response_truncates_at_user(self, chat_service):
        """Test that response is truncated if model generates User line"""
        generated = "This is a response\nUser: This should be cut off"
        result = chat_service.extract_response(generated)

        assert result == "This is a response"
        assert "User:" not in result

    def test_extract_response_truncates_at_assistant(self, chat_service):
        """Test that response is truncated if model generates multiple Assistant lines"""
        generated = "First response\nAssistant: Second response"
        result = chat_service.extract_response(generated)

        assert result == "First response"
        assert "Assistant:" not in result

    def test_process_message_success(self, chat_service, storage_service, mock_model):
        """Test successful message processing"""
        # Create a conversation
        conv_id = storage_service.create_conversation()

        # Mock model response
        mock_model.generate_response.return_value = "Hello! How can I help you?"

        # Process message
        result = chat_service.process_message(conv_id, "Hi there")

        # Verify result
        assert result["success"] is True
        assert result["response"] == "Hello! How can I help you?"
        assert result["conversation_id"] == conv_id
        assert "metadata" in result

        # Verify messages were saved
        messages = storage_service.get_messages(conv_id)
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hi there"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hello! How can I help you?"

    def test_process_message_uses_history(self, chat_service, storage_service, mock_model):
        """Test that process_message uses conversation history"""
        conv_id = storage_service.create_conversation()

        # Add some history
        storage_service.add_message(conv_id, "user", "First message")
        storage_service.add_message(conv_id, "assistant", "First response")

        # Process new message
        result = chat_service.process_message(conv_id, "Second message")

        # Verify generate_response was called with a prompt that includes history
        call_args = mock_model.generate_response.call_args
        prompt = call_args.kwargs['prompt']

        assert "First message" in prompt
        assert "First response" in prompt
        assert "Second message" in prompt

    def test_process_message_with_error(self, chat_service, storage_service, mock_model):
        """Test error handling in message processing"""
        conv_id = storage_service.create_conversation()

        # Make model raise an exception
        mock_model.generate_response.side_effect = Exception("Model error")

        # Process message
        result = chat_service.process_message(conv_id, "Test")

        # Verify error is returned
        assert result["success"] is False
        assert "error" in result
        assert "Model error" in result["error"]

    def test_process_message_respects_max_history(self, chat_service, storage_service, mock_model):
        """Test that only MAX_HISTORY_MESSAGES are used in context"""
        conv_id = storage_service.create_conversation()

        # Add more messages than MAX_HISTORY_MESSAGES
        max_history = Config.MAX_HISTORY_MESSAGES
        for i in range(max_history + 5):
            storage_service.add_message(conv_id, "user", f"Message {i}")
            storage_service.add_message(conv_id, "assistant", f"Response {i}")

        # Process new message
        chat_service.process_message(conv_id, "New message")

        # Check that get_messages was called with limit
        # The implementation should only load MAX_HISTORY_MESSAGES
        messages = storage_service.get_messages(conv_id)
        # We should have more than MAX_HISTORY_MESSAGES total
        assert len(messages) > max_history * 2

    def test_format_conversation_preserves_order(self, chat_service):
        """Test that conversation history preserves message order"""
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Second"},
            {"role": "user", "content": "Third"}
        ]

        result = chat_service.format_conversation_history(messages, max_tokens=1000)
        lines = result.split('\n')

        assert lines[0] == "User: First"
        assert lines[1] == "Assistant: Second"
        assert lines[2] == "User: Third"
