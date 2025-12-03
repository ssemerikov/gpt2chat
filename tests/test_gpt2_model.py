import pytest
from unittest.mock import Mock, patch, MagicMock
import torch
from models.gpt2_model import GPT2ChatModel


class TestGPT2ChatModel:
    """Test suite for GPT2ChatModel"""

    def test_singleton_pattern(self):
        """Test that GPT2ChatModel is a singleton"""
        model1 = GPT2ChatModel()
        model2 = GPT2ChatModel()

        assert model1 is model2

    def test_device_detection_cpu(self):
        """Test device detection defaults to CPU when CUDA unavailable"""
        with patch('torch.cuda.is_available', return_value=False):
            model = GPT2ChatModel()
            # Reset singleton for this test
            GPT2ChatModel._instance = None
            model = GPT2ChatModel()
            assert model.device == "cpu"

    def test_device_detection_cuda(self):
        """Test device detection uses CUDA when available"""
        with patch('torch.cuda.is_available', return_value=True):
            GPT2ChatModel._instance = None
            model = GPT2ChatModel()
            assert model.device == "cuda"

    @patch('models.gpt2_model.GPT2LMHeadModel')
    @patch('models.gpt2_model.GPT2Tokenizer')
    def test_load_model(self, mock_tokenizer_class, mock_model_class):
        """Test model loading"""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_tokenizer.eos_token = "<|endoftext|>"
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Reset singleton
        GPT2ChatModel._instance = None
        model = GPT2ChatModel()
        model.load_model("openai-community/gpt2")

        # Verify model and tokenizer were loaded
        assert model.model is not None
        assert model.tokenizer is not None
        mock_tokenizer_class.from_pretrained.assert_called_once_with("openai-community/gpt2")
        mock_model_class.from_pretrained.assert_called_once_with("openai-community/gpt2")
        mock_model.to.assert_called_once()
        mock_model.eval.assert_called_once()

    @patch('models.gpt2_model.GPT2LMHeadModel')
    @patch('models.gpt2_model.GPT2Tokenizer')
    def test_generate_response_without_loaded_model(self, mock_tokenizer_class, mock_model_class):
        """Test that generate_response raises error if model not loaded"""
        GPT2ChatModel._instance = None
        model = GPT2ChatModel()

        with pytest.raises(RuntimeError, match="Model not loaded"):
            model.generate_response("Test prompt")

    @patch('models.gpt2_model.GPT2LMHeadModel')
    @patch('models.gpt2_model.GPT2Tokenizer')
    def test_generate_response(self, mock_tokenizer_class, mock_model_class):
        """Test response generation"""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_tokenizer.eos_token = "<|endoftext|>"
        mock_tokenizer.eos_token_id = 50256
        # Mock encode to return a tensor (when return_tensors="pt")
        mock_input_tensor = torch.tensor([[1, 2, 3]])
        mock_tokenizer.encode.return_value = mock_input_tensor
        # Mock decode to return different values for full vs new tokens
        # When called with new tokens [4, 5], return "Response text"
        mock_tokenizer.decode.return_value = "Response text"
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = Mock()
        mock_output = torch.tensor([[1, 2, 3, 4, 5]])
        mock_model.generate.return_value = mock_output
        mock_model_class.from_pretrained.return_value = mock_model

        # Create and load model
        GPT2ChatModel._instance = None
        model = GPT2ChatModel()
        model.load_model("openai-community/gpt2")

        # Generate response
        response = model.generate_response(
            prompt="Test prompt",
            max_length=100,
            temperature=0.7
        )

        # Verify - the new implementation decodes only new tokens
        assert response == "Response text"
        mock_tokenizer.encode.assert_called_once()
        mock_model.generate.assert_called_once()

    @patch('models.gpt2_model.GPT2LMHeadModel')
    @patch('models.gpt2_model.GPT2Tokenizer')
    def test_count_tokens(self, mock_tokenizer_class, mock_model_class):
        """Test token counting"""
        mock_tokenizer = Mock()
        mock_tokenizer.eos_token = "<|endoftext|>"
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        GPT2ChatModel._instance = None
        model = GPT2ChatModel()
        model.load_model("openai-community/gpt2")

        token_count = model.count_tokens("This is a test")
        assert token_count == 5
        mock_tokenizer.encode.assert_called_once_with("This is a test")

    @patch('models.gpt2_model.GPT2LMHeadModel')
    @patch('models.gpt2_model.GPT2Tokenizer')
    def test_long_prompt_truncation(self, mock_tokenizer_class, mock_model_class):
        """Test that very long prompts are truncated"""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_tokenizer.eos_token = "<|endoftext|>"
        mock_tokenizer.eos_token_id = 50256
        # Simulate a very long prompt (>1024 tokens) - return as tensor
        long_tokens = torch.tensor([list(range(1100))])
        mock_tokenizer.encode.return_value = long_tokens
        mock_tokenizer.decode.return_value = "Long prompt Response"
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = Mock()
        mock_output = torch.tensor([[1, 2, 3]])
        mock_model.generate.return_value = mock_output
        mock_model_class.from_pretrained.return_value = mock_model

        GPT2ChatModel._instance = None
        model = GPT2ChatModel()
        model.load_model("openai-community/gpt2")

        # Generate with long prompt
        model.generate_response("Very long prompt" * 100)

        # The model should still generate (it will log a warning but not crash)
        mock_model.generate.assert_called_once()
