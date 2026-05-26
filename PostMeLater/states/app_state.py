import json

import reflex as rx

from PostMeLater.services import supabase_auth


class AppState(rx.State):
    in_app: bool = False
    active_view: str = "dashboard"
    mobile_nav_open: bool = False
    auth_error: str = ""
    auth_email: str = ""

    @rx.event
    def enter_app(self):
        self.in_app = True
        self.active_view = "dashboard"

    @rx.event
    def exit_app(self):
        self.in_app = False
        self.mobile_nav_open = False

    @rx.event
    def set_view(self, view: str):
        self.active_view = view
        self.mobile_nav_open = False

    @rx.event
    def toggle_mobile_nav(self):
        self.mobile_nav_open = not self.mobile_nav_open

    @rx.event
    def open_signin(self):
        try:
            url = supabase_auth.google_oauth_url()
            return rx.call_script(f"window.location.assign({json.dumps(url)})")
        except Exception as exc:
            return rx.toast(str(exc))

    @rx.event
    def confirm_auth(self):
        params = self.router.page.params
        code = str(params.get("code", "") or "")
        if code:
            state = str(params.get("state", "") or "")
            try:
                data = supabase_auth.exchange_oauth_code(code, state)
                user = data.get("user") or {}
                self.auth_email = str(user.get("email") or "")
                self.auth_error = ""
                self.in_app = True
                self.active_view = "dashboard"
                return rx.redirect("/")
            except Exception as exc:
                self.auth_error = str(exc)
                return

        self.auth_error = "This Google sign-in callback is missing its code."
