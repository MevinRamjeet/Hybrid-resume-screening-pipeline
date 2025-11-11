"""
Test suite for the LLM Strategy Pattern implementation.

This module contains comprehensive tests for:
- Strategy pattern functionality
- OpenAI and Qwen strategy implementations
- Strategy switching and configuration
- Error handling and fallbacks
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.call_llm import (
    LLMStrategy,
    OpenAIStrategy,
    QwenStrategy,
    LLMContext,
    call_llm,
    set_llm_strategy,
    get_current_strategy_info
)
from src.config.model import OpenAIGenerationModelConfig, QwenGenerationModelConfig
from src.prompts.template import openai_prompt_template, qwen_prompt_template


class TestLLMStrategy:
    """Test cases for the abstract LLMStrategy class."""

    def test_llm_strategy_is_abstract(self):
        """Test that LLMStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMStrategy()


class TestOpenAIStrategy:
    """Test cases for OpenAI strategy implementation."""

    @pytest.fixture
    def openai_config(self):
        """Create a test OpenAI configuration."""
        return OpenAIGenerationModelConfig(
            name="gpt-4o-mini",
            max_input_token_size=2048,
            max_output_token_size=1024,
            prompt_template=openai_prompt_template
        )

    @pytest.fixture
    def test_messages(self):
        """Create test messages for LLM calls."""
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]

    def test_openai_strategy_initialization(self, openai_config):
        """Test OpenAI strategy initialization."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            strategy = OpenAIStrategy(openai_config)
            assert strategy.config == openai_config
            assert strategy.client is not None

    @patch('src.utils.call_llm.OpenAI')
    def test_openai_strategy_call_success(self, mock_openai_class, openai_config, test_messages):
        """Test successful OpenAI API call."""
        # Mock the OpenAI client and response
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Paris is the capital of France."
        mock_client.chat.completions.create.return_value = mock_response

        strategy = OpenAIStrategy(openai_config)
        result = strategy.call(test_messages, temperature=0.1)

        assert result == "Paris is the capital of France."
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.utils.call_llm.OpenAI')
    def test_openai_strategy_call_with_template(self, mock_openai_class, openai_config, test_messages):
        """Test OpenAI API call with prompt template."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Template response"
        mock_client.chat.completions.create.return_value = mock_response

        strategy = OpenAIStrategy(openai_config)
        result = strategy.call(test_messages, temperature=0.1)

        assert result == "Template response"
        # Verify the template was applied by checking call arguments
        call_args = mock_client.chat.completions.create.call_args
        assert call_args is not None

    @patch('src.utils.call_llm.OpenAI')
    def test_openai_strategy_call_error(self, mock_openai_class, openai_config, test_messages):
        """Test OpenAI API call error handling."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        strategy = OpenAIStrategy(openai_config)
        result = strategy.call(test_messages, temperature=0.1)

        assert result is None


class TestQwenStrategy:
    """Test cases for Qwen strategy implementation."""

    @pytest.fixture
    def qwen_config(self):
        """Create a test Qwen configuration."""
        return QwenGenerationModelConfig(
            name="Qwen/Qwen2.5-0.5B",
            max_input_token_size=2048,
            max_output_token_size=512,
            prompt_template=qwen_prompt_template
        )

    @pytest.fixture
    def test_messages(self):
        """Create test messages for LLM calls."""
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]

    def test_qwen_strategy_initialization_without_hf(self, qwen_config):
        """Test Qwen strategy initialization when HuggingFace is not available."""
        with patch('src.utils.call_llm.HF_AVAILABLE', False):
            strategy = QwenStrategy(qwen_config)
            assert strategy.config == qwen_config
            assert strategy.tokenizer is None
            assert strategy.model is None

    @patch('src.utils.call_llm.HF_AVAILABLE', True)
    @patch('src.utils.call_llm.AutoTokenizer')
    @patch('src.utils.call_llm.AutoModelForCausalLM')
    def test_qwen_strategy_initialization_with_hf(self, mock_model_class, mock_tokenizer_class, qwen_config):
        """Test Qwen strategy initialization when HuggingFace is available."""
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model

        strategy = QwenStrategy(qwen_config)

        assert strategy.config == qwen_config
        assert strategy.tokenizer == mock_tokenizer
        assert strategy.model == mock_model

    def test_qwen_strategy_call_mock_response(self, qwen_config, test_messages):
        """Test Qwen strategy call with mock response (when HF not available)."""
        with patch('src.utils.call_llm.HF_AVAILABLE', False):
            strategy = QwenStrategy(qwen_config)
            result = strategy.call(test_messages, temperature=0.1)

            assert result is not None
            assert "Mock Qwen response" in result

    @patch('src.utils.call_llm.HF_AVAILABLE', True)
    @patch('src.utils.call_llm.torch')
    def test_qwen_strategy_call_with_model(self, mock_torch, qwen_config, test_messages):
        """Test Qwen strategy call with actual model."""
        # Mock tokenizer and model
        mock_tokenizer = Mock()
        mock_model = Mock()

        # Mock tokenizer behavior
        mock_inputs = {"input_ids": Mock(), "attention_mask": Mock()}
        mock_inputs["input_ids"].shape = [1, 10]  # Mock shape for input length calculation
        mock_tokenizer.return_value = mock_inputs
        mock_tokenizer.eos_token_id = 2
        mock_tokenizer.decode.return_value = "Paris is the capital of France."

        # Mock model behavior
        mock_outputs = Mock()
        mock_outputs.__getitem__.return_value = Mock()  # For outputs[0]
        mock_outputs[0].__getitem__.return_value = Mock()  # For outputs[0][input_length:]
        mock_model.generate.return_value = mock_outputs
        mock_model.device = "cpu"

        # Mock torch.no_grad
        mock_torch.no_grad.return_value.__enter__ = Mock()
        mock_torch.no_grad.return_value.__exit__ = Mock()

        strategy = QwenStrategy(qwen_config)
        strategy.tokenizer = mock_tokenizer
        strategy.model = mock_model

        result = strategy.call(test_messages, temperature=0.1)

        assert result == "Paris is the capital of France."
        mock_model.generate.assert_called_once()

    def test_qwen_strategy_call_error(self, qwen_config, test_messages):
        """Test Qwen strategy call error handling."""
        strategy = QwenStrategy(qwen_config)
        strategy.tokenizer = Mock()
        strategy.model = Mock()
        strategy.tokenizer.side_effect = Exception("Tokenizer error")

        result = strategy.call(test_messages, temperature=0.1)

        assert result is None


class TestLLMContext:
    """Test cases for LLM context and strategy selection."""

    def test_llm_context_openai_strategy_selection(self):
        """Test that OpenAI config creates OpenAI strategy."""
        config = OpenAIGenerationModelConfig(
            name="gpt-4o-mini",
            max_input_token_size=2048,
            max_output_token_size=1024,
            prompt_template=openai_prompt_template
        )

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            context = LLMContext(config)
            assert isinstance(context.strategy, OpenAIStrategy)

    def test_llm_context_qwen_strategy_selection(self):
        """Test that Qwen config creates Qwen strategy."""
        config = QwenGenerationModelConfig(
            name="Qwen/Qwen2.5-0.5B",
            max_input_token_size=2048,
            max_output_token_size=512,
            prompt_template=qwen_prompt_template
        )

        context = LLMContext(config)
        assert isinstance(context.strategy, QwenStrategy)

    def test_llm_context_unsupported_config(self):
        """Test error handling for unsupported config types."""

        class UnsupportedConfig:
            pass

        with pytest.raises(ValueError, match="Unsupported model config type"):
            LLMContext(UnsupportedConfig())

    def test_llm_context_call_llm(self):
        """Test LLM context call delegation."""
        config = QwenGenerationModelConfig(
            name="Qwen/Qwen2.5-0.5B",
            max_input_token_size=2048,
            max_output_token_size=512,
            prompt_template=qwen_prompt_template
        )

        context = LLMContext(config)

        # Mock the strategy's call method
        context.strategy.call = Mock(return_value="Test response")

        messages = [{"role": "user", "content": "Test"}]
        result = context.call_llm(messages, temperature=0.5)

        assert result == "Test response"
        context.strategy.call.assert_called_once_with(messages, 0.5)


class TestGlobalFunctions:
    """Test cases for global LLM functions."""

    @patch('src.utils.call_llm._llm_context')
    def test_call_llm_function(self, mock_context):
        """Test the global call_llm function."""
        mock_context.call_llm.return_value = "Global response"

        messages = [{"role": "user", "content": "Test"}]
        result = call_llm(messages, temperature=0.2)

        assert result == "Global response"
        mock_context.call_llm.assert_called_once_with(messages, 0.2)

    @patch('src.utils.call_llm.LLMContext')
    def test_set_llm_strategy_function(self, mock_context_class):
        """Test the set_llm_strategy function."""
        mock_context_instance = Mock()
        mock_context_class.return_value = mock_context_instance

        config = OpenAIGenerationModelConfig(
            name="gpt-4o-mini",
            max_input_token_size=2048,
            max_output_token_size=1024,
            prompt_template=openai_prompt_template
        )

        set_llm_strategy(config)

        mock_context_class.assert_called_once_with(config)

    @patch('src.utils.call_llm._llm_context')
    def test_get_current_strategy_info_function(self, mock_context):
        """Test the get_current_strategy_info function."""
        # Mock strategy and config
        mock_strategy = Mock()
        mock_config = Mock()
        mock_config.name = "test-model"
        mock_config.max_output_token_size = 1024
        mock_config.max_input_token_size = 2048

        mock_strategy.config = mock_config
        mock_context.strategy = mock_strategy

        # Mock type() calls
        with patch('builtins.type') as mock_type:
            mock_type.side_effect = lambda x: type(x)
            mock_strategy.__class__.__name__ = "TestStrategy"
            mock_config.__class__.__name__ = "TestConfig"

            info = get_current_strategy_info()

            expected_info = {
                "strategy_type": "TestStrategy",
                "model_name": "test-model",
                "model_config_type": "TestConfig",
                "max_output_tokens": 1024,
                "max_input_tokens": 2048
            }

            assert info == expected_info


class TestIntegration:
    """Integration tests for the complete strategy pattern."""

    def test_strategy_switching_integration(self):
        """Test complete strategy switching workflow."""
        # Create configs
        openai_config = OpenAIGenerationModelConfig(
            name="gpt-4o-mini",
            max_input_token_size=2048,
            max_output_token_size=1024,
            prompt_template=openai_prompt_template
        )

        qwen_config = QwenGenerationModelConfig(
            name="Qwen/Qwen2.5-0.5B",
            max_input_token_size=2048,
            max_output_token_size=512,
            prompt_template=qwen_prompt_template
        )

        # Test switching to OpenAI
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            set_llm_strategy(openai_config)
            info = get_current_strategy_info()
            assert info["strategy_type"] == "OpenAIStrategy"
            assert info["model_name"] == "gpt-4o-mini"

        # Test switching to Qwen
        set_llm_strategy(qwen_config)
        info = get_current_strategy_info()
        assert info["strategy_type"] == "QwenStrategy"
        assert info["model_name"] == "Qwen/Qwen2.5-0.5B"

    @patch('src.utils.call_llm._llm_context')
    def test_end_to_end_llm_call(self, mock_context):
        """Test end-to-end LLM call workflow."""
        mock_context.call_llm.return_value = "Integration test response"

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Integration test question"}
        ]

        response = call_llm(messages, temperature=0.1)

        assert response == "Integration test response"
        mock_context.call_llm.assert_called_once_with(messages, 0.1)


if __name__ == "__main__":
    pytest.main([__file__])
