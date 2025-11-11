import os
import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.logger import configured_logger
from src.config.system import cfg
from src.config.model import OpenAIGenerationModelConfig, QwenGenerationModelConfig, GenerationModelConfig
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
HF_AVAILABLE = True
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


class LLMStrategy(ABC):
    """Abstract base class for LLM strategies."""
    
    def __init__(self, config: GenerationModelConfig):
        """Initialize the strategy with a model configuration."""
        self.config = config
    
    @abstractmethod
    def call(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> Optional[str]:
        """Call the LLM with the given messages and temperature."""
        pass


class OpenAIStrategy(LLMStrategy):
    """Strategy for OpenAI models."""
    
    def __init__(self, config: OpenAIGenerationModelConfig):
        super().__init__(config)
        api_key = cfg.openai_api_key
        self.client = OpenAI(api_key=api_key)
    
    def call(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> Optional[str]:
        try:
            # Apply prompt template if it's a callable
            if callable(self.config.prompt_template) and len(messages) >= 2:
                # Assume messages[0] is system and messages[1] is user
                system_msg = messages[0].get('content', '')
                user_msg = messages[1].get('content', '')
                formatted_messages = self.config.prompt_template(system_msg, user_msg)
                
                # Convert langchain messages to OpenAI format if needed
                if formatted_messages and hasattr(formatted_messages[0], 'content'):
                    formatted_messages = [
                        {
                            "role": "system" if hasattr(msg, 'type') and msg.type == "system" else "user",
                            "content": msg.content
                        }
                        for msg in formatted_messages
                    ]
            else:
                formatted_messages = messages
            
            response = self.client.chat.completions.create(
                model=self.config.name,
                temperature=temperature,
                messages=formatted_messages,
                max_tokens=self.config.max_output_token_size
            )
            return response.choices[0].message.content
        except Exception as e:
            configured_logger.error(f"Error calling OpenAI LLM: {e}")
            return None


class QwenStrategy(LLMStrategy):
    """Strategy for Qwen models (HuggingFace)."""
    
    def __init__(self, config: QwenGenerationModelConfig):
        super().__init__(config)
        self.tokenizer = None
        self.model = None
        
        # Initialize HuggingFace model if available
        if HF_AVAILABLE:
            try:
                hf_token = os.environ.get("HF_TOKEN", cfg.hf_token)
                self.tokenizer = AutoTokenizer.from_pretrained(
                    config.name, 
                    token=hf_token if hf_token else None
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    config.name,
                    token=hf_token if hf_token else None,
                    torch_dtype=torch.float16 if cfg.use_gpu and cfg.gpu_available else torch.float32,
                    device_map="auto" if cfg.use_gpu and cfg.gpu_available else None
                )
                configured_logger.info(f"Successfully loaded Qwen model: {config.name}")
            except Exception as e:
                configured_logger.error(f"Failed to load Qwen model {config.name}: {e}")
                self.tokenizer = None
                self.model = None
    
    def call(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> Optional[str]:
        try:
            # Apply prompt template if available
            if hasattr(self.config, 'prompt_template') and self.config.prompt_template:
                # Convert messages to text using the prompt template (string format)
                if len(messages) >= 2:
                    system_msg = messages[0].get('content', '')
                    user_msg = messages[1].get('content', '')
                    # Format the string template with the messages
                    formatted_prompt = self.config.prompt_template.format(
                        system_message=system_msg,
                        user_task=user_msg
                    )
                else:
                    # Single message case
                    content = messages[0].get('content', '') if messages else ''
                    formatted_prompt = self.config.prompt_template.format(
                        system_message='',
                        user_task=content
                    )
            else:
                # Fallback: concatenate all message contents
                formatted_prompt = '\n'.join([msg.get('content', '') for msg in messages])
            
            # Use actual HuggingFace model if available
            if self.model is not None and self.tokenizer is not None:
                # Tokenize the prompt
                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
                
                # Move to GPU if available
                if cfg.use_gpu and cfg.gpu_available:
                    inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=self.config.max_output_token_size,
                        temperature=temperature,
                        do_sample=temperature > 0,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                # Decode response (exclude the input tokens)
                input_length = inputs['input_ids'].shape[1]
                response_tokens = outputs[0][input_length:]
                response = self.tokenizer.decode(response_tokens, skip_special_tokens=True)
                
                return response.strip()
            else:
                # Fallback to mock response
                configured_logger.warning("Qwen model not available. Using mock response.")
                return f"Mock Qwen response for: {formatted_prompt[:100]}..."
            
        except Exception as e:
            configured_logger.error(f"Error calling Qwen LLM: {e}")
            return None


class LLMContext:
    """Context class that uses different LLM strategies."""
    
    def __init__(self, model_config):
        self.strategy = self._create_strategy(model_config)
    
    def _create_strategy(self, model_config) -> LLMStrategy:
        """Factory method to create the appropriate strategy based on model config."""
        if isinstance(model_config, OpenAIGenerationModelConfig):
            return OpenAIStrategy(model_config)
        elif isinstance(model_config, QwenGenerationModelConfig):
            return QwenStrategy(model_config)
        else:
            raise ValueError(f"Unsupported model config type: {type(model_config)}")
    
    def call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> Optional[str]:
        """Call the LLM using the current strategy."""
        return self.strategy.call(messages, temperature)


# Global LLM context instance
_llm_context = LLMContext(cfg.text_generation_model)


def call_llm(messages: List[Dict[str, str]], temperature: float = 0.0) -> Optional[str]:
    """
    Main function to call LLM using the configured strategy.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Sampling temperature (0.0 for deterministic, higher for more random)
        
    Returns:
        Generated response string or None if error occurred
        
    Example:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        response = call_llm(messages, temperature=0.1)
    """
    return _llm_context.call_llm(messages, temperature)


def set_llm_strategy(model_config):
    """
    Function to change the LLM strategy at runtime.
    
    Args:
        model_config: Either OpenAIGenerationModelConfig or QwenGenerationModelConfig
        
    Example:
        from src.config.model import QwenGenerationModelConfig
        from src.prompts.template import qwen_prompt_template
        
        qwen_config = QwenGenerationModelConfig(
            name="Qwen/Qwen2.5-0.5B",
            max_input_token_size=2048,
            max_output_token_size=512,
            prompt_template=qwen_prompt_template
        )
        set_llm_strategy(qwen_config)
    """
    global _llm_context
    _llm_context = LLMContext(model_config)


def get_current_strategy_info() -> Dict[str, Any]:
    """
    Get information about the currently active LLM strategy.
    
    Returns:
        Dictionary with strategy information
    """
    strategy = _llm_context.strategy
    return {
        "strategy_type": type(strategy).__name__,
        "model_name": strategy.config.name,
        "model_config_type": type(strategy.config).__name__,
        "max_output_tokens": strategy.config.max_output_token_size,
        "max_input_tokens": strategy.config.max_input_token_size
    }
