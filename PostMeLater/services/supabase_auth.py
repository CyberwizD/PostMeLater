"""Supabase Auth helpers."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import sqlite3
import time
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
        conn.executescript(
            """
            create table if not exists oauth_flows (
                state text primary key,
                code_verifier text not null,
                created_at text not null
            );

            create table if not exists auth_sessions (
                id text primary key,
                access_token text not null,
                refresh_token text not null,
                expires_at integer not null default 0,
                user_json text not null default '{}',
                created_at text not null,
                updated_at text not null
            );
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


def _session_expiry(data: dict) -> int:
    expires_at = data.get("expires_at")
    if expires_at:
        return int(expires_at)
    return int(time.time()) + int(data.get("expires_in") or 3600)


def _user_profile(user: dict) -> dict:
    metadata = user.get("user_metadata") or {}
    return {
        "id": str(user.get("id") or ""),
        "email": str(user.get("email") or ""),
        "name": str(
            metadata.get("full_name")
            or metadata.get("name")
            or user.get("email")
            or "PostMeLater user"
        ),
        "avatar_url": str(metadata.get("avatar_url") or metadata.get("picture") or ""),
    }


def create_app_session(auth_data: dict) -> str:
    """Persist a Supabase session and return an opaque app session id."""
    _init_db()
    session_id = secrets.token_urlsafe(32)
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            insert into auth_sessions
            (id, access_token, refresh_token, expires_at, user_json, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                str(auth_data.get("access_token") or ""),
                str(auth_data.get("refresh_token") or ""),
                _session_expiry(auth_data),
                json.dumps(auth_data.get("user") or {}),
                now,
                now,
            ),
        )
    return session_id


def _refresh_auth_session(session_id: str, refresh_token: str) -> dict | None:
    supabase_url = get_setting("SUPABASE_URL").rstrip("/")
    anon_key = get_setting("SUPABASE_ANON_KEY")
    if not supabase_url or not anon_key or not refresh_token:
        return None
    try:
        response = httpx.post(
            f"{supabase_url}/auth/v1/token?grant_type=refresh_token",
            headers={
                "apikey": anon_key,
                "Authorization": f"Bearer {anon_key}",
                "Content-Type": "application/json",
            },
            json={"refresh_token": refresh_token},
            timeout=30,
        )
    except httpx.HTTPError:
        return None
    if response.status_code >= 400:
        return None
    data = response.json()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            update auth_sessions
            set access_token = ?, refresh_token = ?, expires_at = ?, user_json = ?, updated_at = ?
            where id = ?
            """,
            (
                str(data.get("access_token") or ""),
                str(data.get("refresh_token") or refresh_token),
                _session_expiry(data),
                json.dumps(data.get("user") or {}),
                now,
                session_id,
            ),
        )
    return data.get("user") or {}


def get_app_session(session_id: str) -> dict | None:
    """Return a normalized user profile for an app session."""
    if not session_id:
        return None
    _init_db()
    with _connect() as conn:
        row = conn.execute(
            "select * from auth_sessions where id = ?",
            (session_id,),
        ).fetchone()
    if row is None:
        return None

    user = json.loads(row["user_json"] or "{}")
    if int(row["expires_at"] or 0) <= int(time.time()) + 60:
        refreshed_user = _refresh_auth_session(session_id, row["refresh_token"])
        if refreshed_user is None:
            delete_app_session(session_id)
            return None
        user = refreshed_user
    return _user_profile(user)


def delete_app_session(session_id: str) -> None:
    if not session_id:
        return
    _init_db()
    with _connect() as conn:
        conn.execute("delete from auth_sessions where id = ?", (session_id,))
