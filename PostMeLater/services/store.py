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
                user_id text not null default 'default',
                platform text not null,
                username text not null default '',
                display_name text not null default '',
                profile_id text not null default '',
                raw_json text not null default '{}',
                updated_at text not null
            );

            create table if not exists zernio_settings (
                user_id text primary key,
                api_key text not null default '',
                profile_id text not null default '',
                updated_at text not null
            );

            create table if not exists ai_settings (
                user_id text primary key,
                provider text not null default 'gemini',
                api_key text not null default '',
                model text not null default '',
                base_url text not null default '',
                updated_at text not null
            );

            create table if not exists ideas (
                user_id text not null default 'default',
                id text not null,
                title text not null default '',
                notes text not null default '',
                status text not null default 'inbox',
                source text not null default '',
                created_at text not null,
                updated_at text not null,
                primary key (user_id, id)
            );

            create table if not exists content_templates (
                user_id text not null default 'default',
                id text not null,
                name text not null default '',
                prompt text not null default '',
                created_at text not null,
                updated_at text not null,
                primary key (user_id, id)
            );

            create table if not exists campaigns (
                user_id text not null default 'default',
                id text not null,
                name text not null default '',
                goal text not null default '',
                created_at text not null,
                updated_at text not null,
                primary key (user_id, id)
            );

            create table if not exists brand_settings (
                user_id text primary key,
                voice text not null default '',
                audience text not null default '',
                keywords text not null default '',
                updated_at text not null
            );
            """
        )
        _ensure_column(conn, "drafts", "user_id", "text not null default 'default'")
        _ensure_column(conn, "posts", "user_id", "text not null default 'default'")
        _ensure_column(conn, "ai_settings", "base_url", "text not null default ''")
        _migrate_accounts_table(conn)


def _ensure_column(
    conn: sqlite3.Connection, table: str, column: str, definition: str
) -> None:
    columns = {row["name"] for row in conn.execute(f"pragma table_info({table})")}
    if column not in columns:
        conn.execute(f"alter table {table} add column {column} {definition}")


def _migrate_accounts_table(conn: sqlite3.Connection) -> None:
    rows = conn.execute("pragma table_info(accounts)").fetchall()
    columns = {row["name"] for row in rows}
    pk_columns = [row["name"] for row in rows if row["pk"]]
    if columns and pk_columns != ["user_id", "id"]:
        conn.executescript(
            """
            create table if not exists accounts_new (
                user_id text not null default 'default',
                id text not null,
                platform text not null,
                username text not null default '',
                display_name text not null default '',
                profile_id text not null default '',
                raw_json text not null default '{}',
                updated_at text not null,
                primary key (user_id, id)
            );
            """
        )
        source_user = "user_id" if "user_id" in columns else "'default'"
        conn.execute(
            f"""
            insert or ignore into accounts_new
            (user_id, id, platform, username, display_name, profile_id, raw_json, updated_at)
            select {source_user}, id, platform, username, display_name, profile_id, raw_json, updated_at
            from accounts
            """
        )
        conn.executescript(
            """
            drop table accounts;
            alter table accounts_new rename to accounts;
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


def list_drafts(user_id: str = "default") -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from drafts where user_id = ? order by created_at desc",
            (user_id,),
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


def save_draft(draft: dict[str, Any], user_id: str = "default") -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            insert or replace into drafts
            (id, user_id, body, topic, audience, keywords, tone, platforms_json, created_at)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                draft["id"],
                user_id,
                draft["body"],
                draft.get("topic", ""),
                draft.get("audience", ""),
                draft.get("keywords", ""),
                draft.get("tone", "Professional"),
                json.dumps(draft.get("platforms", [])),
                draft["created_at"],
            ),
        )


def delete_draft(draft_id: str, user_id: str = "default") -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "delete from drafts where id = ? and user_id = ?", (draft_id, user_id)
        )


def list_posts(user_id: str = "default") -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from posts where user_id = ? order by scheduled_at asc, created_at desc",
            (user_id,),
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


def save_post(post: dict[str, Any], user_id: str = "default") -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        existing = conn.execute(
            "select created_at from posts where id = ? and user_id = ?",
            (post["id"], user_id),
        ).fetchone()
        conn.execute(
            """
            insert or replace into posts
            (
                id, user_id, zernio_post_id, body, platforms_json, account, account_id,
                scheduled_at, scheduled_date, scheduled_time, cadence, status,
                tone, engagement, error, created_at, updated_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post["id"],
                user_id,
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


def delete_post(post_id: str, user_id: str = "default") -> None:
    init_db()
    with _connect() as conn:
        conn.execute("delete from posts where id = ? and user_id = ?", (post_id, user_id))


def save_accounts(accounts: list[dict[str, Any]], user_id: str = "default") -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute("delete from accounts where user_id = ?", (user_id,))
        for account in accounts:
            account_id = str(
                account.get("_id")
                or account.get("id")
                or account.get("accountId")
                or ""
            )
            if not account_id:
                continue
            profile = account.get("profileId") or account.get("profile_id") or ""
            if isinstance(profile, dict):
                profile = profile.get("_id") or profile.get("id") or ""
            username = str(account.get("username") or account.get("handle") or "")
            display_name = str(
                account.get("displayName")
                or account.get("name")
                or username
                or f"{str(account.get('platform') or 'Social').title()} account"
            )
            conn.execute(
                """
                insert or replace into accounts
                (user_id, id, platform, username, display_name, profile_id, raw_json, updated_at)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    account_id,
                    str(account.get("platform") or ""),
                    username,
                    display_name,
                    str(profile),
                    json.dumps(account),
                    now,
                ),
            )


def list_accounts(user_id: str = "default") -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from accounts where user_id = ? order by platform asc, username asc",
            (user_id,),
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


def save_zernio_settings(
    user_id: str, api_key: str, profile_id: str = ""
) -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            insert or replace into zernio_settings
            (user_id, api_key, profile_id, updated_at)
            values (?, ?, ?, ?)
            """,
            (user_id, api_key.strip(), profile_id.strip(), now),
        )


def get_zernio_settings(user_id: str) -> dict[str, str]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "select api_key, profile_id from zernio_settings where user_id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        return {"api_key": "", "profile_id": ""}
    return {"api_key": row["api_key"], "profile_id": row["profile_id"]}


def delete_zernio_settings(user_id: str) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("delete from zernio_settings where user_id = ?", (user_id,))


def save_ai_settings(
    user_id: str,
    api_key: str,
    model: str = "",
    provider: str = "gemini",
    base_url: str = "",
) -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            insert or replace into ai_settings
            (user_id, provider, api_key, model, base_url, updated_at)
            values (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                provider.strip() or "gemini",
                api_key.strip(),
                model.strip(),
                base_url.strip(),
                now,
            ),
        )


def get_ai_settings(user_id: str) -> dict[str, str]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "select provider, api_key, model, base_url from ai_settings where user_id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        return {"provider": "gemini", "api_key": "", "model": "", "base_url": ""}
    return {
        "provider": row["provider"],
        "api_key": row["api_key"],
        "model": row["model"],
        "base_url": row["base_url"],
    }


def delete_ai_settings(user_id: str) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("delete from ai_settings where user_id = ?", (user_id,))


def list_ideas(user_id: str = "default") -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from ideas where user_id = ? order by created_at desc",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_idea(idea: dict[str, Any], user_id: str = "default") -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        existing = conn.execute(
            "select created_at from ideas where id = ? and user_id = ?",
            (idea["id"], user_id),
        ).fetchone()
        conn.execute(
            """
            insert or replace into ideas
            (user_id, id, title, notes, status, source, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                idea["id"],
                idea.get("title", ""),
                idea.get("notes", ""),
                idea.get("status", "inbox"),
                idea.get("source", ""),
                existing["created_at"] if existing else now,
                now,
            ),
        )


def delete_idea(idea_id: str, user_id: str = "default") -> None:
    init_db()
    with _connect() as conn:
        conn.execute("delete from ideas where id = ? and user_id = ?", (idea_id, user_id))


def update_idea_status(
    idea_id: str, status: str, user_id: str = "default"
) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "update ideas set status = ?, updated_at = ? where id = ? and user_id = ?",
            (status, datetime.utcnow().isoformat(), idea_id, user_id),
        )


def list_templates(user_id: str = "default") -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from content_templates where user_id = ? order by created_at desc",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_template(template: dict[str, Any], user_id: str = "default") -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        existing = conn.execute(
            "select created_at from content_templates where id = ? and user_id = ?",
            (template["id"], user_id),
        ).fetchone()
        conn.execute(
            """
            insert or replace into content_templates
            (user_id, id, name, prompt, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                template["id"],
                template.get("name", ""),
                template.get("prompt", ""),
                existing["created_at"] if existing else now,
                now,
            ),
        )


def delete_template(template_id: str, user_id: str = "default") -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "delete from content_templates where id = ? and user_id = ?",
            (template_id, user_id),
        )


def list_campaigns(user_id: str = "default") -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "select * from campaigns where user_id = ? order by created_at desc",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_campaign(campaign: dict[str, Any], user_id: str = "default") -> None:
    init_db()
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        existing = conn.execute(
            "select created_at from campaigns where id = ? and user_id = ?",
            (campaign["id"], user_id),
        ).fetchone()
        conn.execute(
            """
            insert or replace into campaigns
            (user_id, id, name, goal, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                campaign["id"],
                campaign.get("name", ""),
                campaign.get("goal", ""),
                existing["created_at"] if existing else now,
                now,
            ),
        )


def delete_campaign(campaign_id: str, user_id: str = "default") -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "delete from campaigns where id = ? and user_id = ?",
            (campaign_id, user_id),
        )


def get_brand_settings(user_id: str = "default") -> dict[str, str]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "select voice, audience, keywords from brand_settings where user_id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        return {"voice": "", "audience": "", "keywords": ""}
    return {
        "voice": row["voice"],
        "audience": row["audience"],
        "keywords": row["keywords"],
    }


def save_brand_settings(
    user_id: str, voice: str, audience: str, keywords: str
) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            insert or replace into brand_settings
            (user_id, voice, audience, keywords, updated_at)
            values (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                voice.strip(),
                audience.strip(),
                keywords.strip(),
                datetime.utcnow().isoformat(),
            ),
        )
