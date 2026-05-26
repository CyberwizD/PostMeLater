import reflex as rx

from PostMeLater.services import supabase_auth


class AppState(rx.State):
    in_app: bool = False
    active_view: str = "dashboard"
    mobile_nav_open: bool = False
    signin_modal_open: bool = False
    signin_email: str = ""
    signin_sent: bool = False
    signin_error: str = ""
    signin_loading: bool = False
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
        self.signin_modal_open = True
        self.signin_sent = False
        self.signin_error = ""

    @rx.event
    def close_signin(self):
        self.signin_modal_open = False
        self.signin_loading = False

    @rx.event
    def set_signin_email(self, value: str):
        self.signin_email = value
        self.signin_error = ""

    @rx.event
    def send_magic_link(self):
        email = self.signin_email.strip().lower()
        if "@" not in email or "." not in email:
            self.signin_error = "Enter a valid email address."
            return
        self.signin_email = email
        self.signin_loading = True
        self.signin_error = ""
        yield
        try:
            supabase_auth.send_magic_link(email)
            self.signin_sent = True
        except Exception as exc:
            self.signin_error = str(exc)
        self.signin_loading = False

    @rx.event
    def confirm_magic_link(self):
        params = self.router.page.params
        token_hash = str(params.get("token_hash", "") or "")
        otp_type = str(params.get("type", "email") or "email")
        if not token_hash:
            self.auth_error = "This sign-in link is missing its token."
            return
        try:
            data = supabase_auth.verify_token_hash(token_hash, otp_type)
            user = data.get("user") or {}
            self.auth_email = str(user.get("email") or "")
            self.auth_error = ""
            self.in_app = True
            self.active_view = "dashboard"
            self.signin_modal_open = False
            return rx.redirect("/")
        except Exception as exc:
            self.auth_error = str(exc)
