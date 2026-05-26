"""Gemini text generation client."""

from __future__ import annotations

import logging

import httpx

from PostMeLater.services.config import get_setting


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiError(RuntimeError):
    """Raised when Gemini cannot generate a response."""


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


def generate_text(prompt: str) -> str:
    """Generate text using Gemini's REST API."""
    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured.")

    model = get_setting("GEMINI_MODEL", default="gemini-2.0-flash")
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
    except httpx.HTTPError as exc:
        logging.exception("Gemini request failed")
        raise GeminiError("Gemini could not generate content right now.") from exc
    return _extract_text(response.json())


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

