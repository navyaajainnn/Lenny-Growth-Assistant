from collections.abc import Mapping

import httpx

from app.config import Settings
from app.providers.base import LLMProviderError


class OllamaConnectionError(LLMProviderError):
    """Ollama could not be reached."""


class OllamaTimeoutError(LLMProviderError):
    """Ollama did not respond before the configured timeout."""


class OllamaResponseError(LLMProviderError):
    """Ollama returned an invalid or unsuccessful response."""


class OllamaProvider:
    def __init__(
        self,
        settings: Settings,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._client = client

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self._settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        }
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            base_url=self._settings.ollama_url,
            timeout=self._settings.ollama_timeout_seconds,
        )

        try:
            response = await client.post("/api/generate", json=payload)
        except httpx.TimeoutException as error:
            raise OllamaTimeoutError("Ollama request timed out") from error
        except httpx.RequestError as error:
            raise OllamaConnectionError(
                f"Could not connect to Ollama at {self._settings.ollama_url}"
            ) from error
        finally:
            if owns_client:
                await client.aclose()

        if response.is_error:
            raise OllamaResponseError(
                f"Ollama returned HTTP {response.status_code}: {response.text}"
            )

        try:
            data: Mapping[str, object] = response.json()
        except ValueError as error:
            raise OllamaResponseError("Ollama returned invalid JSON") from error

        generated_text = data.get("response")
        if not isinstance(generated_text, str):
            raise OllamaResponseError("Ollama response did not contain text")
        return generated_text
