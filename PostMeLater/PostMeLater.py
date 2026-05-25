import reflex as rx
from PostMeLater.states.app_state import AppState
from PostMeLater.states.content_state import ContentState
from PostMeLater.components.landing import landing_page
from PostMeLater.components.shell import app_shell


def index() -> rx.Component:
    return rx.el.main(
        rx.cond(AppState.in_app, app_shell(), landing_page()),
        class_name="font-['Inter'] antialiased text-slate-900",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/", on_load=ContentState.init_seed)