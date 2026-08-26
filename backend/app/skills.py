from dataclasses import dataclass


@dataclass(frozen=True)
class WritingSkill:
    name: str
    instructions: str


SHIP_30_FOR_30 = WritingSkill(
    name="ship_30_for_30_essay",
    instructions=(
        "Write an approximately 1,250-word Ship 30 for 30-style essay. "
        "Use a strong specific hook, a clear narrative progression, short skimmable paragraphs, "
        "descriptive headings, purposeful bullets, selective bold emphasis, and one concrete takeaway. "
        "Make claims traceable to the supplied transcript context. Do not invent quotes, facts, or sources. "
        "If the context is insufficient, say so instead of filling gaps."
    ),
)


def build_artifact_prompt(conversation: str, context: str, output_format: str) -> str:
    format_rules = (
        "Return only valid Markdown, with no surrounding code fence."
        if output_format == "markdown"
        else "Return a complete HTML fragment suitable for a sandboxed viewer. Do not include scripts, event handlers, forms, or external resources."
    )
    return (
        f"{SHIP_30_FOR_30.instructions}\n{format_rules}\n\n"
        f"Transcript context:\n{context or '[No relevant transcript context found]'}\n\n"
        f"Conversation:\n{conversation}"
    )
