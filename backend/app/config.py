from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env."""

    app_name: str = "Lenny Growth Assistant API"
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth_assistant"
    transcript_directory: Path = Path(__file__).resolve().parents[2] / "data" / "transcripts"
    llm_provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"
    ollama_timeout_seconds: float = 60.0
    ollama_max_output_tokens: int = 512
    ollama_artifact_timeout_seconds: float = 180.0
    ollama_artifact_max_output_tokens: int = 1800
    anthropic_api_key: str | None = None
    anthropic_url: str = "https://api.anthropic.com"
    anthropic_model: str = "claude-3-5-haiku-latest"
    anthropic_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
