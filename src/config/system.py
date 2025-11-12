from pathlib import Path

import torch
from pydantic_settings import BaseSettings

from src.config.model import HFEmbeddingModelConfig, ModelConfig, VisionModelConfig, \
    OpenAIGenerationModelConfig

env_path = Path(__file__).parent.parent.parent / ".env"

print("env_path", env_path)

env_path = env_path.resolve()


class SystemConfig(BaseSettings):
    app_name: str = "Hybrid Resume Screening"
    app_description: str = "Pipeline for resume screening and evaluation"
    api_version: str = "v1"
    log_filename: str = "app.log"
    hf_token: str = ""
    openai_api_key: str = ""
    reranking_model: ModelConfig = HFEmbeddingModelConfig(name="BAAI/bge-reranker-v2-m3", embed_dim=1024,
                                                          max_input_token_size=2048)
    embedding_model: ModelConfig = HFEmbeddingModelConfig(name="Qwen/Qwen3-Embedding-0.6B", embed_dim=1024,
                                                          max_input_token_size=2048)
    text_generation_model: ModelConfig = OpenAIGenerationModelConfig(name="gpt-4o-mini", max_input_token_size=2048,
                                                                     max_output_token_size=4192)
    image_ocr_model: ModelConfig = VisionModelConfig(name="Qwen/Qwen3-VL-8B-Instruct", max_output_token_size=1024)
    use_gpu: bool = False
    gpu_available: bool = True if torch.cuda.is_available() else False

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"


cfg = SystemConfig()
