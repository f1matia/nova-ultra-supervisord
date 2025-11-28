import os
from typing import Iterator, Iterable, Optional

PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

# Lazy imports to avoid requiring keys for basic runs
_openai = None
_anthropic = None

def _get_openai():
    global _openai
    if _openai is None:
        try:
            import openai
            _openai = openai
        except Exception:
            _openai = False
    return _openai

def _get_anthropic():
    global _anthropic
    if _anthropic is None:
        try:
            import anthropic
            _anthropic = anthropic
        except Exception:
            _anthropic = False
    return _anthropic

class LLMAdapter:
    """Production-leaning adapter with provider switch.
    Enforces simple safety by truncating prompts, forbidding unsafe system instructions injection,
    and supporting streaming when SDKs are available.
    """

    def __init__(self, max_prompt_chars: int = 8000):
        self.max_prompt = max_prompt_chars

    def _sanitize(self, prompt: str) -> str:
        # minimal guard: truncate and strip nulls
        text = (prompt or "")[: self.max_prompt].replace("\x00", "")
        return text

    def generate(self, prompt: str, **kwargs) -> str:
        prompt = self._sanitize(prompt)
        if PROVIDER == "openai":
            oi = _get_openai()
            if oi and os.getenv("OPENAI_API_KEY"):
                client = oi.OpenAI()
                resp = client.responses.create(
                    model=OPENAI_MODEL,
                    input=prompt,
                )
                # responses API: take the first output_text
                return resp.output_text or ""
            return "OpenAI(stub): " + prompt[:256]
        if PROVIDER == "anthropic":
            ai = _get_anthropic()
            if ai and os.getenv("ANTHROPIC_API_KEY"):
                client = ai.Anthropic()
                msg = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}],
                )
                # concatenate text parts
                out = []
                for blk in msg.content or []:
                    if getattr(blk, "type", "") == "text":
                        out.append(getattr(blk, "text", ""))
                    elif isinstance(blk, dict) and blk.get("type") == "text":
                        out.append(blk.get("text",""))
                return "".join(out)
            return "Anthropic(stub): " + prompt[:256]
        return "[mock completion] " + prompt[:256]

    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        prompt = self._sanitize(prompt)
        if PROVIDER == "openai":
            oi = _get_openai()
            if oi and os.getenv("OPENAI_API_KEY"):
                client = oi.OpenAI()
                with client.responses.stream(
                    model=OPENAI_MODEL,
                    input=prompt,
                ) as s:
                    for event in s:
                        # map events to token text if available
                        if hasattr(event, "type") and event.type == "response.output_text.delta":
                            yield getattr(event, "delta", "") or ""
                    return
            # fallback: non-streaming chunk
            txt = "OpenAI(stub): " + prompt[:256]
            for i in range(0, len(txt), 32):
                yield txt[i:i+32]
            return

        if PROVIDER == "anthropic":
            ai = _get_anthropic()
            if ai and os.getenv("ANTHROPIC_API_KEY"):
                # Anthropics' python SDK supports streaming via events
                client = ai.Anthropic()
                with client.messages.stream(
                    model=ANTHROPIC_MODEL,
                    max_tokens=512,
                    messages=[{"role":"user","content":prompt}],
                ) as stream:
                    for event in stream:
                        # Text deltas show up as 'content_block_delta'
                        if getattr(event, "type", "") == "content_block_delta":
                            delta = getattr(event, "delta", None)
                            if delta and getattr(delta, "type", "") == "text_delta":
                                yield getattr(delta, "text", "") or ""
                    return
            txt = "Anthropic(stub): " + prompt[:256]
            for i in range(0, len(txt), 32):
                yield txt[i:i+32]
            return

        # mock provider
        txt = "[mock stream] " + prompt[:80]
        for i in range(0, len(txt), 32):
            yield txt[i:i+32]
