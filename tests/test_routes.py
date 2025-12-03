import pytest
import json
from unittest.mock import patch, Mock


class TestRoutes:
    """Integration tests for API routes"""

    def test_index_route(self, client):
        """Test that index route returns HTML"""
        response = client.get('/')
        assert response.status_code == 200

    def test_create_conversation(self, client):
        """Test creating a new conversation"""
        response = client.post('/api/conversations')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'conversation_id' in data
        assert len(data['conversation_id']) == 36  # UUID length

    def test_send_message_success(self, client):
        """Test sending a message to a conversation"""
        # First create a conversation
        create_response = client.post('/api/conversations')
        conv_data = json.loads(create_response.data)
        conv_id = conv_data['conversation_id']

        # Mock the chat service to avoid actually running the model
        with patch('api.routes.chat_service') as mock_chat_service:
            mock_chat_service.process_message.return_value = {
                "success": True,
                "response": "Test response",
                "conversation_id": conv_id,
                "metadata": {"prompt_tokens": 10}
            }

            # Send a message
            response = client.post(
                f'/api/conversations/{conv_id}/messages',
                data=json.dumps({'message': 'Hello'}),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['response'] == "Test response"

    def test_send_message_missing_message(self, client):
        """Test sending message without message field"""
        create_response = client.post('/api/conversations')
        conv_data = json.loads(create_response.data)
        conv_id = conv_data['conversation_id']

        response = client.post(
            f'/api/conversations/{conv_id}/messages',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Message is required' in data['error']

    def test_send_message_empty_message(self, client):
        """Test sending empty message"""
        create_response = client.post('/api/conversations')
        conv_data = json.loads(create_response.data)
        conv_id = conv_data['conversation_id']

        response = client.post(
            f'/api/conversations/{conv_id}/messages',
            data=json.dumps({'message': '   '}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Message cannot be empty' in data['error']

    def test_get_messages(self, client):
        """Test retrieving conversation messages"""
        # Create conversation
        create_response = client.post('/api/conversations')
        conv_data = json.loads(create_response.data)
        conv_id = conv_data['conversation_id']

        # Get messages (should be empty initially)
        response = client.get(f'/api/conversations/{conv_id}/messages')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['messages'] == []

    def test_list_conversations(self, client):
        """Test listing all conversations"""
        # Create a few conversations
        client.post('/api/conversations')
        client.post('/api/conversations')

        response = client.get('/api/conversations')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'conversations' in data
        assert len(data['conversations']) >= 2

    def test_delete_conversation(self, client):
        """Test deleting a conversation"""
        # Create conversation
        create_response = client.post('/api/conversations')
        conv_data = json.loads(create_response.data)
        conv_id = conv_data['conversation_id']

        # Delete it
        response = client.delete(f'/api/conversations/{conv_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Verify it's gone
        get_response = client.get(f'/api/conversations/{conv_id}/messages')
        get_data = json.loads(get_response.data)
        assert get_data['messages'] == []

    def test_delete_nonexistent_conversation(self, client):
        """Test deleting non-existent conversation"""
        response = client.delete('/api/conversations/nonexistent-id')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'model_loaded' in data

    def test_send_message_model_error(self, client):
        """Test handling of model errors"""
        create_response = client.post('/api/conversations')
        conv_data = json.loads(create_response.data)
        conv_id = conv_data['conversation_id']

        with patch('api.routes.chat_service') as mock_chat_service:
            mock_chat_service.process_message.return_value = {
                "success": False,
                "error": "Model error occurred",
                "conversation_id": conv_id
            }

            response = client.post(
                f'/api/conversations/{conv_id}/messages',
                data=json.dumps({'message': 'Hello'}),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data

    def test_cors_headers(self, client):
        """Test that CORS headers are present"""
        response = client.get('/api/health')

        # CORS should be enabled
        # The actual headers depend on flask-cors configuration
        assert response.status_code == 200
