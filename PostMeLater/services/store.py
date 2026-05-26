"""SQLite persistence for drafts, posts, and connected account metadata."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
DB_DIR = ROOT_DIR / ".states"
DB_PATH = DB_DIR / "postmelater.sqlite3"


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    with _connect() as conn:
        conn.executescript(
            """
            create table if not exists drafts (
                id text primary key,
                body text not null,
                topic text not null default '',
                audience text not null default '',
                keywords text not null default '',
                tone text not null default 'Professional',
                platforms_json text not null default '[]',
                created_at text not null
            );

            create table if not exists posts (
                id text primary key,
                zernio_post_id text,
                body text not null,
                platforms_json text not null default '[]',
                account text not null default '',
                account_id text not null default '',
                scheduled_at text not null default '',
                scheduled_date text not null default '',
                scheduled_time text not null default '',
                cadence text not null default 'One-time',
                status text not null default 'scheduled',
                tone text not null default 'Professional',
                engagement integer not null default 0,
                error text not null default '',
                created_at text not null,
                updated_at text not null
            );

            create table if not exists accounts (
                id text primary key,
                platform text not null,
                username text not null default '',
                display_name text not null default '',
                profile_id text not null default '',
                raw_json text not null default '{}',
                updated_at text not null
            );
            """
        )


def _loads_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return []
    return list(data) if isinstance(data, list) else []


def list_drafts() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from drafts order by created_at desc"
        ).fetchall()
    return [
        {
            "id": row["id"],
            "body": row["body"],
            "topic": row["topic"],
            "audience": row["audience"],
            "keywords": row["keywords"],
            "tone": row["tone"],
            "platforms": _loads_list(row["platforms_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def save_draft(draft: dict[str, Any]) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            insert or replace into drafts
            (id, body, topic, audience, keywords, tone, platforms_json, created_at)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                draft["id"],
                draft["body"],
                draft.get("topic", ""),
                draft.get("audience", ""),
                draft.get("keywords", ""),
                draft.get("tone", "Professional"),
                json.dumps(draft.get("platforms", [])),
                draft["created_at"],
            ),
        )


def delete_draft(draft_id: str) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("delete from drafts where id = ?", (draft_id,))


def list_posts() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from posts order by scheduled_at asc, created_at desc"
        ).fetchall()
    return [
        {
            "id": row["id"],
            "zernio_post_id": row["zernio_post_id"] or "",
            "body": row["body"],
            "platforms": _loads_list(row["platforms_json"]),
            "account": row["account"],
            "account_id": row["account_id"],
            "scheduled_at": row["scheduled_at"],
            "scheduled_date": row["scheduled_date"],
            "scheduled_time": row["scheduled_time"],
            "cadence": row["cadence"],
            "status": row["status"],
            "tone": row["tone"],
            "engagement": int(row["engagement"] or 0),
            "error": row["error"] or "",
        }
        for row in rows
    ]


def save_post(post: dict[str, Any]) -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        existing = conn.execute(
            "select created_at from posts where id = ?", (post["id"],)
        ).fetchone()
        conn.execute(
            """
            insert or replace into posts
            (
                id, zernio_post_id, body, platforms_json, account, account_id,
                scheduled_at, scheduled_date, scheduled_time, cadence, status,
                tone, engagement, error, created_at, updated_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post["id"],
                post.get("zernio_post_id", ""),
                post["body"],
                json.dumps(post.get("platforms", [])),
                post.get("account", ""),
                post.get("account_id", ""),
                post.get("scheduled_at", ""),
                post.get("scheduled_date", ""),
                post.get("scheduled_time", ""),
                post.get("cadence", "One-time"),
                post.get("status", "scheduled"),
                post.get("tone", "Professional"),
                int(post.get("engagement", 0) or 0),
                post.get("error", ""),
                existing["created_at"] if existing else now,
                now,
            ),
        )


def delete_post(post_id: str) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("delete from posts where id = ?", (post_id,))


def save_accounts(accounts: list[dict[str, Any]]) -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        for account in accounts:
            account_id = str(
                account.get("_id")
                or account.get("id")
                or account.get("accountId")
                or ""
            )
            if not account_id:
                continue
            conn.execute(
                """
                insert or replace into accounts
                (id, platform, username, display_name, profile_id, raw_json, updated_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    str(account.get("platform") or ""),
                    str(account.get("username") or account.get("handle") or ""),
                    str(account.get("displayName") or account.get("name") or ""),
                    str(account.get("profileId") or account.get("profile_id") or ""),
                    json.dumps(account),
                    now,
                ),
            )


def list_accounts() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from accounts order by platform asc, username asc"
        ).fetchall()
    return [
        {
            "id": row["id"],
            "platform": row["platform"],
            "username": row["username"],
            "display_name": row["display_name"],
            "profile_id": row["profile_id"],
        }
        for row in rows
    ]

