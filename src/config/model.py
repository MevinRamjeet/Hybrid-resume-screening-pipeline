from dataclasses import dataclass
from typing import Callable, Union

from src.prompts.template import qwen_prompt_template, openai_prompt_template


@dataclass
class ModelConfig:
    name: str

@dataclass
class GenerationModelConfig(ModelConfig):
    max_output_token_size: int
    max_input_token_size: int
    prompt_template: Union[str, Callable]

@dataclass
class EmbeddingModelConfig(ModelConfig):
    embed_dim: int
    max_input_token_size: int

@dataclass
class VisionModelConfig(ModelConfig):
    max_output_token_size: int

@dataclass
class HFEmbeddingModelConfig(EmbeddingModelConfig):
    # embed_func: callable = hf_embed
    pass

@dataclass
class HFGenerationModelConfig(GenerationModelConfig):
    # model_func: callable = hf_model_complete
    pass

@dataclass
class QwenGenerationModelConfig(HFGenerationModelConfig):
    prompt_template: str = qwen_prompt_template

@dataclass
class OpenAIGenerationModelConfig(GenerationModelConfig):
    prompt_template: Callable = openai_prompt_template
