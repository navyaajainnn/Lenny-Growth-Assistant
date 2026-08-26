import httpx

from app.config import Settings
from app.providers.base import LLMProviderError


class AnthropicConfigurationError(LLMProviderError):
    """Anthropic is selected but is not configured."""


class AnthropicConnectionError(LLMProviderError):
    """Anthropic could not be reached."""


class AnthropicResponseError(LLMProviderError):
    """Anthropic returned an unsuccessful or invalid response."""


class AnthropicProvider:
    def __init__(
        self,
        settings: Settings,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not settings.anthropic_api_key:
            raise AnthropicConfigurationError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic"
            )
        self._settings = settings
        self._client = client

    async def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
        timeout_seconds: float | None = None,
    ) -> str:
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            base_url=self._settings.anthropic_url,
            timeout=timeout_seconds or self._settings.anthropic_timeout_seconds,
        )
        try:
            response = await client.post(
                "/v1/messages",
                headers={
                    "x-api-key": self._settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self._settings.anthropic_model,
                    "max_tokens": max_output_tokens or 2048,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        except httpx.RequestError as error:
            raise AnthropicConnectionError("Could not connect to Anthropic") from error
        finally:
            if owns_client:
                await client.aclose()

        if response.is_error:
            raise AnthropicResponseError(
                f"Anthropic returned HTTP {response.status_code}: {response.text}"
            )
        try:
            content = response.json().get("content", [])
            text = content[0].get("text") if content else None
        except (AttributeError, IndexError, TypeError, ValueError) as error:
            raise AnthropicResponseError("Anthropic returned invalid content") from error
        if not isinstance(text, str):
            raise AnthropicResponseError("Anthropic response did not contain text")
        return text
