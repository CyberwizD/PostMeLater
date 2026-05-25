import reflex as rx


class AppState(rx.State):
    in_app: bool = False
    active_view: str = "dashboard"
    mobile_nav_open: bool = False

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