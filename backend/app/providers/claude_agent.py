from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query
from claude_agent_sdk import ClaudeSDKError

from app.config import Settings
from app.providers.base import LLMProviderError


class ClaudeAgentConfigurationError(LLMProviderError):
    """Claude Agent SDK is selected without an API key."""


class ClaudeAgentResponseError(LLMProviderError):
    """Claude Agent SDK could not produce a text response."""


class ClaudeAgentProvider:
    def __init__(self, settings: Settings) -> None:
        if not settings.anthropic_api_key:
            raise ClaudeAgentConfigurationError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=claude_agent"
            )
        self._settings = settings

    async def generate(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
        timeout_seconds: float | None = None,
    ) -> str:
        options = ClaudeAgentOptions(
            model=self._settings.anthropic_model,
            max_turns=1,
            allowed_tools=[],
            disallowed_tools=["Bash", "Write", "Edit", "Read", "WebFetch", "WebSearch"],
            system_prompt=(
                "Answer only from the transcript context supplied in the user prompt. "
                "Do not invent facts, quotes, or sources."
            ),
            env={"ANTHROPIC_API_KEY": self._settings.anthropic_api_key},
        )
        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    text = "".join(
                        block.text for block in message.content if isinstance(block, TextBlock)
                    )
                    if text:
                        return text
        except ClaudeSDKError as error:
            raise ClaudeAgentResponseError(f"Claude Agent SDK failed: {error}") from error
        raise ClaudeAgentResponseError("Claude Agent SDK returned no text")
