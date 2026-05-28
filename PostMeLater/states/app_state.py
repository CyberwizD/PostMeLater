import json
import logging

import reflex as rx

from PostMeLater.services import supabase_auth


class AppState(rx.State):
    session_id: str = rx.Cookie("", name="pml_session", max_age=60 * 60 * 24 * 30)
    oauth_code_verifier: str = rx.Cookie(
        "", name="pml_oauth_verifier", max_age=60 * 15
    )
    in_app: bool = False
    active_view: str = "dashboard"
    mobile_nav_open: bool = False
    auth_error: str = ""
    auth_email: str = ""
    user_id: str = ""
    user_name: str = "PostMeLater user"
    user_email: str = ""
    user_avatar: str = ""

    @rx.event
    def enter_app(self):
        if self._load_session():
            self.active_view = "dashboard"
            return
        return self.open_signin()

    @rx.event
    def exit_app(self):
        self.in_app = False
        self.mobile_nav_open = False

    @rx.event
    async def set_view(self, view: str):
        self.active_view = view
        self.mobile_nav_open = False
        if view in {"dashboard", "analytics", "planner", "scheduling", "studio"}:
            try:
                from PostMeLater.states.content_state import ContentState

                content_state = await self.get_state(ContentState)
                owner_id = self.user_id or self.user_email or "default"
                content_state.sync_post_statuses_for_user(owner_id)
            except Exception:
                logging.exception("Could not sync Zernio statuses while switching views")

    @rx.event
    def toggle_mobile_nav(self):
        self.mobile_nav_open = not self.mobile_nav_open

    @rx.event
    def open_signin(self):
        if self._load_session():
            self.active_view = "dashboard"
            return
        try:
            code_verifier = supabase_auth.create_pkce_verifier()
            self.oauth_code_verifier = code_verifier
            url = supabase_auth.google_oauth_url(code_verifier)
            cookie = (
                f"pml_oauth_verifier={code_verifier}; "
                "Max-Age=900; Path=/; SameSite=Lax"
            )
            return rx.call_script(
                "document.cookie = "
                + json.dumps(cookie)
                + "; window.location.assign("
                + json.dumps(url)
                + ")"
            )
        except Exception as exc:
            return rx.toast(str(exc))

    def _apply_user(self, user: dict):
        self.user_id = user.get("id") or ""
        self.user_name = user.get("name") or "PostMeLater user"
        self.user_email = user.get("email") or ""
        self.user_avatar = user.get("avatar_url") or (
            "https://api.dicebear.com/9.x/notionists/svg?seed="
            + (self.user_email or "postmelater")
        )
        self.auth_email = self.user_email

    def _load_session(self) -> bool:
        user = supabase_auth.get_app_session(self.session_id)
        if not user:
            self.in_app = False
            return False
        self._apply_user(user)
        self.auth_error = ""
        self.in_app = True
        return True

    @rx.event
    def load_session(self):
        self._load_session()

    @rx.event
    def confirm_auth(self):
        params = self.router.page.params
        code = str(params.get("code", "") or "")
        if code:
            try:
                data = supabase_auth.exchange_oauth_code(
                    code, self.oauth_code_verifier
                )
                self.session_id = supabase_auth.create_app_session(data)
                self.oauth_code_verifier = ""
                user = supabase_auth.get_app_session(self.session_id)
                if user:
                    self._apply_user(user)
                self.auth_error = ""
                self.in_app = True
                self.active_view = "dashboard"
                return rx.redirect("/")
            except Exception as exc:
                self.auth_error = str(exc)
                return

        self.auth_error = "This Google sign-in callback is missing its code."
