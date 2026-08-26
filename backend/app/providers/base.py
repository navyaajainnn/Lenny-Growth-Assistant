from typing import Protocol


class LLMProviderError(Exception):
    """Base error for failures communicating with an LLM provider."""


class LLMProvider(Protocol):
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
