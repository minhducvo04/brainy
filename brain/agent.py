"""answer(question, user): recall from the user's readable memory, then one cited LLM
call through the Respan gateway (OpenAI SDK, base_url https://api.respan.ai/api)."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from brain import memory

RESPAN_BASE_URL = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-5-mini")
CANT_SEE = "I can't see that"

SYSTEM_PROMPT = f"""You answer questions for an engineering team using ONLY the context below.
The context is passages from GitHub PRs/issues and Slack threads the asker is allowed to see.
Rules:
- Cite every fact inline with its source label, e.g. [github repo pr #12] or [slack #eng | alice | 1712.3].
- If the context does not contain the answer, reply exactly: "{CANT_SEE}." and nothing else.
- Never guess, never use outside knowledge, keep it under 120 words."""


def respan_trace(fn):
    """TODO(respan-tracing): the event README names the respan-ai SDK (`Respan()` at
    startup plus a decorator on the request handler) but not the decorator's exact
    name, and the package is not installed. Wire it here once confirmed. Every LLM
    call already goes through the Respan gateway, which logs model, tokens, cost and
    latency."""
    return fn


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(base_url=RESPAN_BASE_URL, api_key=os.environ["RESPAN_API_KEY"])


def format_context(context: list[dict]) -> str:
    return "\n\n---\n\n".join(c["text"].strip() for c in context)


@respan_trace
async def answer(question: str, user: str) -> dict:
    recalled = await memory.recall(question, user)
    if not recalled["context"]:
        return {"answer": f"{CANT_SEE}.", "sources": [], "datasets": recalled["datasets"]}
    resp = await _client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{format_context(recalled['context'])}\n\nQuestion: {question}",
            },
        ],
    )
    text = (resp.choices[0].message.content or "").strip()
    sources = [] if text.startswith(CANT_SEE) else recalled["sources"]
    return {"answer": text, "sources": sources, "datasets": recalled["datasets"]}
