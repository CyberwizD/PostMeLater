"""Supabase Auth helpers."""

from __future__ import annotations

import httpx

from PostMeLater.services.config import get_setting


class SupabaseAuthError(RuntimeError):
    """Raised when a Supabase Auth request cannot be completed."""


def configured() -> bool:
    return bool(get_setting("SUPABASE_URL") and get_setting("SUPABASE_ANON_KEY"))


def _redirect_url() -> str:
    return get_setting(
        "APP_BASE_URL",
        "SITE_URL",
        "REFLEX_PUBLIC_URL",
        default="http://localhost:3000",
    )


def send_magic_link(email: str) -> None:
    """Send a Supabase passwordless sign-in link to the given email."""
    supabase_url = get_setting("SUPABASE_URL").rstrip("/")
    anon_key = get_setting("SUPABASE_ANON_KEY")
    if not supabase_url or not anon_key:
        raise SupabaseAuthError(
            "Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY."
        )

    try:
        response = httpx.post(
            f"{supabase_url}/auth/v1/otp",
            headers={
                "apikey": anon_key,
                "Authorization": f"Bearer {anon_key}",
                "Content-Type": "application/json",
            },
            json={
                "email": email,
                "create_user": True,
                "options": {"email_redirect_to": _redirect_url()},
            },
            timeout=30,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Could not reach Supabase Auth.") from exc

    if response.status_code >= 400:
        try:
            payload = response.json()
        except ValueError:
            payload = {"message": response.text}
        message = str(
            payload.get("msg")
            or payload.get("message")
            or payload.get("error_description")
            or "Supabase could not send the sign-in link."
        )
        raise SupabaseAuthError(message)
