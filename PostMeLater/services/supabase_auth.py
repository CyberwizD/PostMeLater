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


def verify_token_hash(token_hash: str, otp_type: str = "email") -> dict:
    """Verify a Supabase email token hash and return the auth response."""
    supabase_url = get_setting("SUPABASE_URL").rstrip("/")
    anon_key = get_setting("SUPABASE_ANON_KEY")
    if not supabase_url or not anon_key:
        raise SupabaseAuthError(
            "Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY."
        )
    if not token_hash:
        raise SupabaseAuthError("Missing Supabase token hash.")

    try:
        response = httpx.post(
            f"{supabase_url}/auth/v1/verify",
            headers={
                "apikey": anon_key,
                "Authorization": f"Bearer {anon_key}",
                "Content-Type": "application/json",
            },
            json={"type": otp_type or "email", "token_hash": token_hash},
            timeout=30,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Could not verify the Supabase sign-in link.") from exc

    if response.status_code >= 400:
        try:
            payload = response.json()
        except ValueError:
            payload = {"message": response.text}
        message = str(
            payload.get("msg")
            or payload.get("message")
            or payload.get("error_description")
            or "The sign-in link is invalid or expired."
        )
        raise SupabaseAuthError(message)
    return response.json()
