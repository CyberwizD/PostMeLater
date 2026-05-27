"""Gemini text generation client."""

from __future__ import annotations

import logging

import httpx

from PostMeLater.services.config import get_setting


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
OPENAI_BASE_URL = "https://api.openai.com/v1"
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"


class GeminiError(RuntimeError):
    """Raised when Gemini cannot generate a response."""


def default_model(provider: str) -> str:
    """Return the default model for an AI provider."""
    provider = provider.lower().strip()
    if provider == "openai":
        return "gpt-5-mini"
    if provider == "anthropic":
        return "claude-sonnet-4-20250514"
    return get_setting("GEMINI_MODEL", default="gemini-2.0-flash")


def _extract_text(payload: dict) -> str:
    parts = (
        payload.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "\n".join(str(part.get("text", "")) for part in parts).strip()
    if not text:
        raise GeminiError("Gemini returned an empty response.")
    return text


def _extract_openai_text(payload: dict) -> str:
    output_text = str(payload.get("output_text") or "").strip()
    if output_text:
        return output_text
    chunks: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict):
                chunks.append(str(content.get("text") or ""))
    text = "\n".join(chunk for chunk in chunks if chunk).strip()
    if not text:
        raise GeminiError("OpenAI returned an empty response.")
    return text


def _extract_anthropic_text(payload: dict) -> str:
    chunks = [
        str(part.get("text") or "")
        for part in payload.get("content", [])
        if isinstance(part, dict) and part.get("type") == "text"
    ]
    text = "\n".join(chunk for chunk in chunks if chunk).strip()
    if not text:
        raise GeminiError("Claude returned an empty response.")
    return text


def _raise_provider_error(provider: str, exc: httpx.HTTPStatusError) -> None:
    status = exc.response.status_code
    label = {
        "openai": "OpenAI",
        "anthropic": "Claude",
        "gemini": "Gemini",
    }.get(provider, "AI provider")
    if status == 429:
        raise GeminiError(
            f"{label} quota or rate limit reached. Add another API key in Settings or try again later."
        ) from exc
    if status in {401, 403}:
        raise GeminiError(
            f"{label} rejected the API key. Check the key saved in Settings."
        ) from exc
    logging.exception("%s request failed", label)
    raise GeminiError(f"{label} could not generate content right now.") from exc


def generate_text(
    prompt: str,
    api_key_override: str | None = None,
    model_override: str = "",
    provider: str = "gemini",
) -> str:
    """Generate text using the configured AI provider."""
    provider = (provider or "gemini").lower().strip()
    if provider == "openai":
        return _generate_openai(prompt, api_key_override, model_override)
    if provider == "anthropic":
        return _generate_anthropic(prompt, api_key_override, model_override)
    return _generate_gemini(prompt, api_key_override, model_override)


def _generate_gemini(
    prompt: str, api_key_override: str | None = None, model_override: str = ""
) -> str:
    api_key = api_key_override or get_setting("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured.")

    model = model_override or default_model("gemini")
    url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "topP": 0.95,
            "maxOutputTokens": 450,
        },
    }
    try:
        response = httpx.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            json=body,
            timeout=30,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_provider_error("gemini", exc)
    except httpx.HTTPError as exc:
        logging.exception("Gemini request failed")
        raise GeminiError("Gemini could not generate content right now.") from exc
    return _extract_text(response.json())


def _generate_openai(
    prompt: str, api_key_override: str | None = None, model_override: str = ""
) -> str:
    api_key = api_key_override or get_setting("OPENAI_API_KEY")
    if not api_key:
        raise GeminiError("OpenAI API key is not configured.")
    body = {
        "model": model_override or default_model("openai"),
        "input": prompt,
        "max_output_tokens": 450,
    }
    try:
        response = httpx.post(
            f"{OPENAI_BASE_URL}/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=45,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_provider_error("openai", exc)
    except httpx.HTTPError as exc:
        logging.exception("OpenAI request failed")
        raise GeminiError("OpenAI could not generate content right now.") from exc
    return _extract_openai_text(response.json())


def _generate_anthropic(
    prompt: str, api_key_override: str | None = None, model_override: str = ""
) -> str:
    api_key = api_key_override or get_setting("ANTHROPIC_API_KEY")
    if not api_key:
        raise GeminiError("Claude API key is not configured.")
    body = {
        "model": model_override or default_model("anthropic"),
        "max_tokens": 450,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        response = httpx.post(
            f"{ANTHROPIC_BASE_URL}/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=45,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_provider_error("anthropic", exc)
    except httpx.HTTPError as exc:
        logging.exception("Claude request failed")
        raise GeminiError("Claude could not generate content right now.") from exc
    return _extract_anthropic_text(response.json())


def build_post_prompt(
    *,
    topic: str,
    audience: str,
    keywords: str,
    goal: str,
    tone: str,
    platforms: list[str],
) -> str:
    """Create the social post generation prompt."""
    return (
        "Write one polished social media post.\n"
        f"Topic: {topic or 'A useful update for my audience'}\n"
        f"Audience: {audience or 'creators, founders, and operators'}\n"
        f"Goal: {goal}\n"
        f"Tone: {tone}\n"
        f"Platforms: {', '.join(platforms) or 'LinkedIn and Twitter/X'}\n"
        f"Keywords: {keywords or 'growth, consistency, content'}\n\n"
        "Requirements:\n"
        "- Return only the post text.\n"
        "- Keep it concise, specific, and ready to publish.\n"
        "- Include a clear hook and a soft call-to-action.\n"
        "- Use line breaks where helpful.\n"
        "- Add 1-3 relevant hashtags only if they fit the selected platforms."
    )


def build_rewrite_prompt(content: str, instruction: str) -> str:
    """Create a rewrite prompt for existing post content."""
    return (
        f"{instruction}\n\n"
        "Return only the revised post text. Preserve the original meaning.\n\n"
        f"Post:\n{content}"
    )
