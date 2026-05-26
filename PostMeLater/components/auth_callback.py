import reflex as rx

from PostMeLater.states.app_state import AppState


def auth_confirm_page() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    AppState.auth_error != "",
                    rx.icon("triangle-alert", class_name="h-6 w-6 text-red-600"),
                    rx.icon("loader-circle", class_name="h-6 w-6 text-indigo-600 animate-spin"),
                ),
                class_name=rx.cond(
                    AppState.auth_error != "",
                    "h-12 w-12 rounded-xl bg-red-50 flex items-center justify-center mb-4",
                    "h-12 w-12 rounded-xl bg-indigo-50 flex items-center justify-center mb-4",
                ),
            ),
            rx.el.h1(
                rx.cond(
                    AppState.auth_error != "",
                    "Sign-in link could not be verified",
                    "Signing you in with Google",
                ),
                class_name="text-2xl font-bold text-slate-900",
            ),
            rx.el.p(
                rx.cond(
                    AppState.auth_error != "",
                    AppState.auth_error,
                    "Please wait while PostMeLater finishes Google sign-in.",
                ),
                class_name="text-sm text-slate-600 mt-2 leading-relaxed",
            ),
            rx.cond(
                AppState.auth_error != "",
                rx.el.a(
                    "Back to sign in",
                    href="/",
                    class_name="inline-flex mt-6 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
                rx.fragment(),
            ),
            class_name="w-[92%] max-w-md bg-white border border-slate-200 rounded-2xl p-6 shadow-xl",
        ),
        class_name="font-['Inter'] antialiased min-h-screen bg-slate-50 text-slate-900 flex items-center justify-center px-4",
    )
