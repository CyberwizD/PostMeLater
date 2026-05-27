"""Small Zernio REST client."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from PostMeLater.services.config import app_timezone, get_setting


ZERNIO_BASE_URL = "https://zernio.com/api/v1"

PLATFORM_TO_API = {
    "Twitter / X": "twitter",
    "X": "twitter",
    "Twitter": "twitter",
    "LinkedIn": "linkedin",
    "Instagram": "instagram",
    "Facebook": "facebook",
    "Threads": "threads",
}


class ZernioError(RuntimeError):
    """Raised for Zernio API failures."""

    def __init__(self, message: str, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.payload = payload or {}


def api_key() -> str:
    """Return the configured Zernio API key.

    LATE_API_KEY is supported because older Late keys may still be present
    after the Zernio rebrand.
    """
    return get_setting("ZERNIO_API_KEY", "LATE_API_KEY")


def default_account_id() -> str:
    """Return the optional fallback account id from the environment."""
    return get_setting("ZERNIO_ACCOUNT_ID", "ACCOUNT_ID")


def default_profile_id() -> str:
    """Return the optional Zernio profile id from the environment."""
    return get_setting("ZERNIO_PROFILE_ID", "PROFILE_ID")


def configured(key: str = "") -> bool:
    """Return whether Zernio calls can be attempted."""
    return bool(key or api_key())


def platform_api_name(label: str) -> str:
    """Map UI platform labels to Zernio API platform values."""
    return PLATFORM_TO_API.get(label, label.lower().replace(" / x", "").replace(" ", ""))


def _request(
    method: str,
    path: str,
    *,
    api_key_override: str | None = None,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = api_key() if api_key_override is None else api_key_override
    if not key:
        raise ZernioError("Zernio API key is not configured.")
    url = f"{ZERNIO_BASE_URL}{path}"
    try:
        response = httpx.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json=json,
            params=params,
            timeout=30,
        )
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {"error": response.text}
            message = str(payload.get("error") or payload.get("message") or "Zernio request failed.")
            raise ZernioError(message, payload)
        if not response.content:
            return {}
        return response.json()
    except ZernioError:
        raise
    except httpx.HTTPError as exc:
        logging.exception("Zernio request failed")
        raise ZernioError("Could not reach Zernio right now.") from exc


def list_accounts(api_key_override: str | None = None) -> list[dict[str, Any]]:
    """List connected Zernio accounts."""
    data = _request("GET", "/accounts", api_key_override=api_key_override)
    accounts = data.get("accounts") or data.get("data") or []
    return list(accounts) if isinstance(accounts, list) else []


def list_profiles(api_key_override: str | None = None) -> list[dict[str, Any]]:
    """List Zernio profiles available to the API key."""
    data = _request(
        "GET",
        "/profiles",
        api_key_override=api_key_override,
        params={"includeOverLimit": "true"},
    )
    profiles = data.get("profiles") or data.get("data") or []
    return list(profiles) if isinstance(profiles, list) else []


def create_profile(
    name: str = "PostMeLater Workspace", api_key_override: str | None = None
) -> dict[str, Any]:
    """Create a Zernio profile for connected social accounts."""
    data = _request(
        "POST",
        "/profiles",
        api_key_override=api_key_override,
        json={
            "name": name,
            "description": "Social accounts connected from PostMeLater.",
        },
    )
    return data.get("profile") or data.get("data") or data


def resolve_profile_id(
    api_key_override: str | None = None, profile_id: str = ""
) -> str:
    """Find or create the Zernio profile used for account connections."""
    configured_profile_id = profile_id or default_profile_id()
    if configured_profile_id:
        return configured_profile_id

    profiles = list_profiles(api_key_override=api_key_override)
    if profiles:
        default_profile = next(
            (profile for profile in profiles if profile.get("isDefault")),
            profiles[0],
        )
        return str(
            default_profile.get("_id")
            or default_profile.get("id")
            or default_profile.get("profileId")
            or ""
        )

    profile = create_profile(api_key_override=api_key_override)
    return str(profile.get("_id") or profile.get("id") or profile.get("profileId") or "")


def get_connect_url(
    platform: str,
    redirect_url: str,
    api_key_override: str | None = None,
    profile_id: str = "",
) -> str:
    """Return a hosted OAuth URL for connecting a social account."""
    resolved_profile_id = resolve_profile_id(
        api_key_override=api_key_override, profile_id=profile_id
    )
    if not resolved_profile_id:
        raise ZernioError("Create a Zernio profile before connecting accounts.")
    data = _request(
        "GET",
        f"/connect/{platform_api_name(platform)}",
        api_key_override=api_key_override,
        params={"profileId": resolved_profile_id, "redirect_url": redirect_url},
    )
    auth_url = str(data.get("authUrl") or data.get("auth_url") or "")
    if not auth_url:
        raise ZernioError("Zernio did not return a connection URL.")
    return auth_url


def list_posts(
    limit: int = 50, status: str = "", api_key_override: str | None = None
) -> list[dict[str, Any]]:
    """List posts from Zernio."""
    params: dict[str, Any] = {"limit": limit}
    if status:
        params["status"] = status
    data = _request("GET", "/posts", api_key_override=api_key_override, params=params)
    posts = data.get("posts") or data.get("data") or []
    return list(posts) if isinstance(posts, list) else []


def create_post(
    *,
    content: str,
    scheduled_for: str | None,
    platforms: list[dict[str, str]],
    api_key_override: str | None = None,
) -> dict[str, Any]:
    """Create a scheduled post or draft in Zernio."""
    payload: dict[str, Any] = {
        "content": content,
        "platforms": platforms,
    }
    if scheduled_for:
        payload["scheduledFor"] = scheduled_for
        payload["timezone"] = app_timezone()
    data = _request("POST", "/posts", api_key_override=api_key_override, json=payload)
    return data.get("post") or data.get("data") or data


def delete_post(post_id: str, api_key_override: str | None = None) -> None:
    """Delete a post from Zernio."""
    _request("DELETE", f"/posts/{post_id}", api_key_override=api_key_override)


def retry_post(post_id: str, api_key_override: str | None = None) -> dict[str, Any]:
    """Retry a failed Zernio post."""
    data = _request(
        "POST", f"/posts/{post_id}/retry", api_key_override=api_key_override
    )
    return data.get("post") or data.get("data") or data


def update_post(
    *,
    post_id: str,
    content: str | None = None,
    scheduled_for: str | None = None,
    api_key_override: str | None = None,
) -> dict[str, Any]:
    """Update a Zernio post, with fallback for older edit endpoint naming."""
    payload: dict[str, Any] = {}
    if content is not None:
        payload["content"] = content
    if scheduled_for is not None:
        payload["scheduledFor"] = scheduled_for
        payload["scheduled_for"] = scheduled_for
        payload["timezone"] = app_timezone()
    try:
        data = _request(
            "PUT",
            f"/posts/{post_id}",
            api_key_override=api_key_override,
            json=payload,
        )
    except ZernioError:
        data = _request(
            "POST",
            f"/posts/{post_id}/edit",
            api_key_override=api_key_override,
            json=payload,
        )
    return data.get("post") or data.get("data") or data
