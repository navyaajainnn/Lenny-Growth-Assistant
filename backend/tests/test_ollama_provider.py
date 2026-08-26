import json

import httpx
import pytest

from app.config import Settings
from app.providers.ollama import (
    OllamaProvider,
    OllamaResponseError,
    OllamaTimeoutError,
)
from app.providers.anthropic import AnthropicProvider
from app.providers.claude_agent import ClaudeAgentConfigurationError, ClaudeAgentProvider
from app.providers.factory import create_provider


def make_settings() -> Settings:
    return Settings(
        ollama_url="http://ollama.test",
        ollama_model="qwen3:4b",
    )


@pytest.mark.anyio
async def test_generate_posts_prompt_and_returns_response() -> None:
    request_data: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        request_data.update(json.loads(request.content))
        return httpx.Response(200, json={"response": "A useful answer"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://ollama.test") as client:
        provider = OllamaProvider(make_settings(), client=client)
        result = await provider.generate("How do I improve activation?")

    assert result == "A useful answer"
    assert request_data == {
        "model": "qwen3:4b",
        "prompt": "How do I improve activation?",
        "stream": False,
    }


@pytest.mark.anyio
async def test_generate_raises_for_unsuccessful_response() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(500, text="model unavailable")
    )

    async with httpx.AsyncClient(transport=transport, base_url="http://ollama.test") as client:
        provider = OllamaProvider(make_settings(), client=client)

        with pytest.raises(OllamaResponseError, match="HTTP 500"):
            await provider.generate("hello")


@pytest.mark.anyio
async def test_generate_raises_for_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://ollama.test") as client:
        provider = OllamaProvider(make_settings(), client=client)

        with pytest.raises(OllamaTimeoutError):
            await provider.generate("hello")


@pytest.mark.anyio
async def test_anthropic_provider_uses_configured_model_and_key() -> None:
    request_headers: dict[str, str] = {}
    request_data: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        request_headers.update(request.headers)
        request_data.update(json.loads(request.content))
        return httpx.Response(200, json={"content": [{"text": "Cloud answer"}]})

    settings = Settings(
        anthropic_api_key="test-key",
        anthropic_model="claude-test",
        anthropic_url="http://anthropic.test",
    )
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://anthropic.test") as client:
        result = await AnthropicProvider(settings, client=client).generate("hello")

    assert result == "Cloud answer"
    assert request_headers["x-api-key"] == "test-key"
    assert request_data["model"] == "claude-test"


def test_claude_agent_requires_api_key() -> None:
    provider_class = ClaudeAgentProvider
    settings = Settings()
    with pytest.raises(ClaudeAgentConfigurationError):
        provider_class(settings)


def test_factory_selects_claude_agent_provider() -> None:
    provider = create_provider(Settings(llm_provider="claude_agent", anthropic_api_key="test-key"))

    assert isinstance(provider, ClaudeAgentProvider)
