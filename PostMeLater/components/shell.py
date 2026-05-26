import reflex as rx
from PostMeLater.states.app_state import AppState
from PostMeLater.components.views import dashboard_view, studio_view, scheduling_view
from PostMeLater.components.settings import settings_view


NAV_ITEMS = [
    ("dashboard", "Dashboard", "layout-dashboard"),
    ("studio", "AI Content Studio", "sparkles"),
    ("scheduling", "Scheduling Center", "calendar-clock"),
    ("settings", "Settings", "settings"),
]


def _nav_button(view_id: str, label: str, icon: str) -> rx.Component:
    is_active = AppState.active_view == view_id
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4"),
        rx.el.span(label, class_name="text-sm font-medium"),
        on_click=lambda: AppState.set_view(view_id),
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 w-full px-3 py-2 rounded-lg bg-indigo-50 text-indigo-700 transition-colors",
            "flex items-center gap-3 w-full px-3 py-2 rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors",
        ),
    )


def _sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.button(
                rx.el.div(
                    rx.icon("send", class_name="h-4 w-4 text-white"),
                    class_name="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center",
                ),
                rx.el.span(
                    "PostMeLater", class_name="font-bold text-slate-900"
                ),
                on_click=AppState.exit_app,
                class_name="flex items-center gap-2 px-2 py-2 hover:bg-slate-50 rounded-lg w-full transition-colors",
            ),
            class_name="px-3 py-4 border-b border-slate-200",
        ),
        rx.el.nav(
            rx.el.div(
                rx.el.p(
                    "Workspace",
                    class_name="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2",
                ),
                _nav_button("dashboard", "Dashboard", "layout-dashboard"),
                _nav_button("studio", "AI Content Studio", "sparkles"),
                _nav_button(
                    "scheduling", "Scheduling Center", "calendar-clock"
                ),
                class_name="flex flex-col gap-1",
            ),
            rx.el.div(
                rx.el.p(
                    "Account",
                    class_name="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2 mt-6",
                ),
                rx.el.button(
                    rx.icon("settings", class_name="h-4 w-4"),
                    rx.el.span("Settings", class_name="text-sm font-medium"),
                    on_click=lambda: AppState.set_view("settings"),
                    class_name="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors",
                ),
                class_name="flex flex-col gap-1",
            ),
            class_name="flex-1 px-3 py-4 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.img(
                    src=AppState.user_avatar,
                    class_name="h-9 w-9 rounded-full bg-slate-100",
                ),
                rx.el.div(
                    rx.el.p(
                        AppState.user_name,
                        class_name="text-sm font-semibold text-slate-900 truncate",
                    ),
                    rx.el.p(
                        AppState.user_email,
                        class_name="text-xs text-slate-500 truncate",
                    ),
                    class_name="flex-1 min-w-0",
                ),
                rx.icon("chevron-right", class_name="h-4 w-4 text-slate-400"),
                on_click=lambda: AppState.set_view("settings"),
                class_name="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 cursor-pointer",
            ),
            class_name="border-t border-slate-200 p-3",
        ),
        class_name="hidden lg:flex flex-col w-64 h-screen bg-white border-r border-slate-200 sticky top-0 shrink-0",
    )


def _topbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.button(
                rx.icon("menu", class_name="h-5 w-5"),
                on_click=AppState.toggle_mobile_nav,
                class_name="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100",
            ),
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="h-4 w-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2",
                ),
                rx.el.input(
                    placeholder="Search posts, drafts, accounts...",
                    class_name="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-700",
                ),
                class_name="relative flex-1 max-w-md hidden sm:block",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    rx.el.span("Quick draft", class_name="hidden sm:inline"),
                    on_click=lambda: AppState.set_view("studio"),
                    class_name="flex items-center gap-2 bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
                rx.el.button(
                    rx.icon("bell", class_name="h-5 w-5"),
                    class_name="p-2 rounded-lg text-slate-600 hover:bg-slate-100 relative",
                ),
                class_name="flex items-center gap-2 ml-auto",
            ),
            class_name="flex items-center gap-3 h-16 px-4 sm:px-6 lg:px-8",
        ),
        class_name="bg-white border-b border-slate-200 sticky top-0 z-20",
    )


def _mobile_drawer() -> rx.Component:
    return rx.cond(
        AppState.mobile_nav_open,
        rx.el.div(
            rx.el.div(
                on_click=AppState.toggle_mobile_nav,
                class_name="fixed inset-0 bg-slate-900/50 z-40 lg:hidden",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("send", class_name="h-4 w-4 text-white"),
                            class_name="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center",
                        ),
                        rx.el.span(
                            "PostMeLater", class_name="font-bold text-slate-900"
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=AppState.toggle_mobile_nav,
                        class_name="p-2 rounded-lg text-slate-600 hover:bg-slate-100",
                    ),
                    class_name="flex items-center justify-between px-4 h-16 border-b border-slate-200",
                ),
                rx.el.nav(
                    _nav_button("dashboard", "Dashboard", "layout-dashboard"),
                    _nav_button("studio", "AI Content Studio", "sparkles"),
                    _nav_button(
                        "scheduling", "Scheduling Center", "calendar-clock"
                    ),
                    _nav_button("settings", "Settings", "settings"),
                    rx.el.div(class_name="h-px bg-slate-200 my-3"),
                    rx.el.button(
                        rx.icon("log-out", class_name="h-4 w-4"),
                        rx.el.span(
                            "Back to landing", class_name="text-sm font-medium"
                        ),
                        on_click=AppState.exit_app,
                        class_name="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors",
                    ),
                    class_name="flex flex-col gap-1 p-3",
                ),
                class_name="fixed top-0 left-0 bottom-0 w-72 bg-white z-50 lg:hidden",
            ),
        ),
        rx.fragment(),
    )


def app_shell() -> rx.Component:
    return rx.el.div(
        _sidebar(),
        rx.el.div(
            _topbar(),
            rx.el.main(
                rx.el.div(
                    rx.match(
                        AppState.active_view,
                        ("dashboard", dashboard_view()),
                        ("studio", studio_view()),
                        ("scheduling", scheduling_view()),
                        ("settings", settings_view()),
                        dashboard_view(),
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
                ),
                class_name="flex-1",
            ),
            class_name="flex-1 flex flex-col min-w-0",
        ),
        _mobile_drawer(),
        class_name="flex min-h-screen bg-slate-50",
    )
