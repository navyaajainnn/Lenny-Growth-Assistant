from app.config import Settings
from app.providers.anthropic import AnthropicProvider
from app.providers.base import LLMProvider, LLMProviderError
from app.providers.ollama import OllamaProvider


class ProviderConfigurationError(LLMProviderError):
    """The configured provider is not supported."""


def create_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings)
    if settings.llm_provider == "anthropic":
        return AnthropicProvider(settings)
    raise ProviderConfigurationError(
        f"Unsupported LLM_PROVIDER: {settings.llm_provider}"
    )
