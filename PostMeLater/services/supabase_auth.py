"""Supabase Auth helpers."""

from __future__ import annotations

import base64
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import httpx

from PostMeLater.services.config import get_setting


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_DIR = ROOT_DIR / ".states"
DB_PATH = DB_DIR / "supabase_oauth.sqlite3"


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
    ).rstrip("/")


def _auth_callback_url() -> str:
    return f"{_redirect_url()}/auth/confirm"


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            create table if not exists oauth_flows (
                state text primary key,
                code_verifier text not null,
                created_at text not null
            )
            """
        )


def _save_oauth_flow(state: str, code_verifier: str) -> None:
    _init_db()
    cutoff = (datetime.utcnow() - timedelta(minutes=15)).isoformat()
    with _connect() as conn:
        conn.execute("delete from oauth_flows where created_at < ?", (cutoff,))
        conn.execute(
            """
            insert or replace into oauth_flows (state, code_verifier, created_at)
            values (?, ?, ?)
            """,
            (state, code_verifier, datetime.utcnow().isoformat()),
        )


def _pop_oauth_flow(state: str) -> str:
    _init_db()
    with _connect() as conn:
        row = conn.execute(
            "select code_verifier from oauth_flows where state = ?",
            (state,),
        ).fetchone()
        conn.execute("delete from oauth_flows where state = ?", (state,))
    if row is None:
        raise SupabaseAuthError("The Google sign-in session expired. Try again.")
    return str(row["code_verifier"])


def _code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def google_oauth_url() -> str:
    """Create a Supabase Google OAuth authorization URL."""
    supabase_url = get_setting("SUPABASE_URL").rstrip("/")
    if not supabase_url:
        raise SupabaseAuthError("Supabase is not configured. Add SUPABASE_URL.")
    code_verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(32)
    _save_oauth_flow(state, code_verifier)
    params = {
        "provider": "google",
        "redirect_to": _auth_callback_url(),
        "flow_type": "pkce",
        "code_challenge": _code_challenge(code_verifier),
        "code_challenge_method": "S256",
        "state": state,
    }
    return f"{supabase_url}/auth/v1/authorize?{urlencode(params)}"


def exchange_oauth_code(code: str, state: str) -> dict:
    """Exchange a Supabase OAuth authorization code for a session."""
    supabase_url = get_setting("SUPABASE_URL").rstrip("/")
    anon_key = get_setting("SUPABASE_ANON_KEY")
    if not supabase_url or not anon_key:
        raise SupabaseAuthError(
            "Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY."
        )
    if not code:
        raise SupabaseAuthError("Missing Google sign-in code.")
    code_verifier = _pop_oauth_flow(state)
    try:
        response = httpx.post(
            f"{supabase_url}/auth/v1/token?grant_type=pkce",
            headers={
                "apikey": anon_key,
                "Authorization": f"Bearer {anon_key}",
                "Content-Type": "application/json",
            },
            json={"auth_code": code, "code_verifier": code_verifier},
            timeout=30,
        )
    except httpx.HTTPError as exc:
        raise SupabaseAuthError("Could not finish Google sign-in.") from exc

    if response.status_code >= 400:
        try:
            payload = response.json()
        except ValueError:
            payload = {"message": response.text}
        message = str(
            payload.get("msg")
            or payload.get("message")
            or payload.get("error_description")
            or "Google sign-in failed."
        )
        raise SupabaseAuthError(message)
    return response.json()
