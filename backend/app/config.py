"""Configuration management for KnowledgeVault."""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
from pydantic import Field  # 用于提供默认值说明

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "127.0.0.1"
    port: int = 8000


class StorageConfig(BaseModel):
    """Storage configuration."""
    data_dir: str = "./data"
    max_file_size: int = 100 * 1024 * 1024  # 100MB


class ClassificationRule(BaseModel):
    """Single classification rule."""
    category: str
    keywords: list[str] = []
    file_types: list[str] = []
    path_patterns: list[str] = []


class ClassificationConfig(BaseModel):
    """Classification configuration."""
    auto_classify: bool = True
    use_ai: bool = False
    # AI Provider: "ollama" or "deepseek"
    ai_provider: str = "deepseek"
    # Ollama settings
    ollama_model: str = "qwen2.5:7b"
    ollama_url: str = "http://localhost:11434"
    # DeepSeek settings
    deepseek_api_key: str = Field(
        default_factory=lambda: os.getenv("KNOWLEDGEVAULT_DEEPSEEK_API_KEY", ""),
        description="DeepSeek API Key. Read from environment variable 'KNOWLEDGEVAULT_DEEPSEEK_API_KEY'."
    )
    deepseek_model: str = "deepseek-chat"
    deepseek_url: str = "https://api.deepseek.com/v1/chat/completions"
    rules: list[ClassificationRule] = []


class ImportConfig(BaseModel):
    """Import configuration."""
    extract_text: bool = True
    generate_thumbnails: bool = True
    deduplicate: bool = True


class Settings(BaseSettings):
    """Application settings."""

    # Base paths
    base_dir: Path = Path(__file__).parent.parent.parent.parent
    config_file: str = "config.yaml"

    # Sub-configs (loaded from YAML)
    server: ServerConfig = ServerConfig()
    storage: StorageConfig = StorageConfig()
    classification: ClassificationConfig = ClassificationConfig()
    import_config: ImportConfig = ImportConfig()

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/vault.db"

    class Config:
        env_prefix = "KVAULT_"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_config_file()

    def _load_config_file(self):
        """Load configuration from YAML file if it exists."""
        config_path = self.base_dir / self.config_file
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f) or {}

            if "server" in config_data:
                self.server = ServerConfig(**config_data["server"])
            if "storage" in config_data:
                self.storage = StorageConfig(**config_data["storage"])
            if "classification" in config_data:
                self.classification = ClassificationConfig(**config_data["classification"])
            if "import" in config_data:
                self.import_config = ImportConfig(**config_data["import"])

        # Override with environment variables
        if os.getenv("DEEPSEEK_API_KEY"):
            self.classification.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if os.getenv("AI_PROVIDER"):
            self.classification.ai_provider = os.getenv("AI_PROVIDER")

    @property
    def data_path(self) -> Path:
        """Get the data directory path."""
        return self.base_dir / self.storage.data_dir

    @property
    def files_path(self) -> Path:
        """Get the files storage path."""
        return self.data_path / "files"

    @property
    def thumbnails_path(self) -> Path:
        """Get the thumbnails storage path."""
        return self.data_path / "thumbnails"

    def ensure_directories(self):
        """Ensure all required directories exist."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.files_path.mkdir(parents=True, exist_ok=True)
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
