import reflex as rx

from PostMeLater.states.app_state import AppState


def signin_modal() -> rx.Component:
    return rx.cond(
        AppState.signin_modal_open,
        rx.el.div(
            rx.el.div(
                on_click=AppState.close_signin,
                class_name="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("mail", class_name="h-5 w-5 text-indigo-600"),
                        rx.el.h3(
                            "Sign in to PostMeLater",
                            class_name="font-semibold text-slate-900",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=AppState.close_signin,
                        class_name="p-1.5 rounded-md text-slate-400 hover:bg-slate-100",
                    ),
                    class_name="flex items-center justify-between p-5 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.cond(
                        AppState.signin_sent,
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "mail-check",
                                    class_name="h-6 w-6 text-emerald-600",
                                ),
                                class_name="h-12 w-12 rounded-xl bg-emerald-50 flex items-center justify-center mb-4",
                            ),
                            rx.el.h4(
                                "Check your inbox",
                                class_name="text-base font-semibold text-slate-900",
                            ),
                            rx.el.p(
                                "A sign-in link has been sent to ",
                                rx.el.span(
                                    AppState.signin_email,
                                    class_name="font-semibold text-slate-900",
                                ),
                                ".",
                                class_name="text-sm text-slate-600 mt-2 leading-relaxed",
                            ),
                            rx.el.p(
                                "Open the link from the same browser to continue.",
                                class_name="text-xs text-slate-500 mt-3",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Enter your email and I'll send a one-time sign-in link.",
                                class_name="text-sm text-slate-600 mb-4",
                            ),
                            rx.el.label(
                                "Email",
                                class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                            ),
                            rx.el.input(
                                type="email",
                                placeholder="you@example.com",
                                value=AppState.signin_email,
                                on_change=AppState.set_signin_email,
                                class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder-slate-400",
                            ),
                            rx.cond(
                                AppState.signin_error != "",
                                rx.el.p(
                                    AppState.signin_error,
                                    class_name="text-sm text-red-600 mt-3",
                                ),
                                rx.fragment(),
                            ),
                        ),
                    ),
                    class_name="p-5",
                ),
                rx.el.div(
                    rx.cond(
                        AppState.signin_sent,
                        rx.el.button(
                            "Done",
                            on_click=AppState.close_signin,
                            class_name="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors",
                        ),
                        rx.el.button(
                            rx.cond(AppState.signin_loading, "Sending...", "Send link"),
                            on_click=AppState.send_magic_link,
                            disabled=AppState.signin_loading,
                            class_name="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-60",
                        ),
                    ),
                    class_name="flex items-center justify-end gap-2 p-5 border-t border-slate-200 bg-slate-50 rounded-b-2xl",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-white rounded-2xl border border-slate-200 z-50 shadow-2xl",
            ),
        ),
        rx.fragment(),
    )
