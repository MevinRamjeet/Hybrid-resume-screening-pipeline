import torch
from pydantic_settings import BaseSettings

from src.config.model import HFEmbeddingModelConfig, ModelConfig, QwenGenerationModelConfig, VisionModelConfig


class SystemConfig(BaseSettings):
    app_name: str = "SIL Extractor"
    app_description: str = "API service for data extraction"
    api_version: str = "v1"
    log_filename: str = "../app.log"
    hf_token: str = ""
    report_structure: str = DEFAULT_REPORT_STRUCTURE
    reporting_for: str = "Federal Ministry of Agriculture"
    planner_model: str = "gpt-4o-mini"
    writer_model: str = "gpt-4o-mini"
    embedding_model: ModelConfig = HFEmbeddingModelConfig(name="Qwen/Qwen3-Embedding-0.6B", embed_dim=1024,
                                                          max_input_token_size=2048)
    text_generation_model: ModelConfig = QwenGenerationModelConfig(name="Qwen/Qwen2.5-0.5B", max_input_token_size=32768,
                                                                 max_output_token_size=8192)
    image_ocr_model: ModelConfig = VisionModelConfig(name="Qwen/Qwen3-VL-8B-Instruct", max_output_token_size=1024)
    use_gpu: bool = False
    gpu_available: bool = True if torch.cuda.is_available() else False

    class SystemConfig:
        env_file = '.env'
        env_file_encoding = "utf-8"


cfg = SystemConfig()
