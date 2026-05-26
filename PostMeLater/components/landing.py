import reflex as rx
from PostMeLater.states.app_state import AppState


def _nav_link(label: str) -> rx.Component:
    return rx.el.a(
        label,
        href="#",
        class_name="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors",
    )


def _feature_card(icon: str, title: str, desc: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-indigo-600"),
            class_name="flex items-center justify-center h-12 w-12 rounded-xl bg-indigo-50 mb-5",
        ),
        rx.el.h3(title, class_name="text-lg font-semibold text-slate-900 mb-2"),
        rx.el.p(desc, class_name="text-sm text-slate-600 leading-relaxed"),
        class_name="bg-white border border-slate-200 rounded-2xl p-6 hover:border-indigo-200 hover:shadow-sm transition-all",
    )


def _stat(value: str, label: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(value, class_name="text-3xl font-bold text-slate-900"),
        rx.el.p(label, class_name="text-sm text-slate-500 mt-1"),
        class_name="text-center",
    )


def landing_page() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("send", class_name="h-5 w-5 text-white"),
                        class_name="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center",
                    ),
                    rx.el.span(
                        "PostMeLater",
                        class_name="text-lg font-bold text-slate-900",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.nav(
                    _nav_link("Features"),
                    _nav_link("Docs"),
                    class_name="hidden md:flex items-center gap-8",
                ),
                rx.el.div(
                    rx.el.button(
                        "Sign in",
                        on_click=AppState.enter_app,
                        class_name="text-sm font-medium text-slate-600 hover:text-slate-900 hidden sm:block",
                    ),
                    rx.el.button(
                        "Open workspace",
                        rx.icon("arrow-right", class_name="h-4 w-4"),
                        on_click=AppState.enter_app,
                        class_name="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                    ),
                    class_name="flex items-center gap-3",
                ),
                class_name="max-w-7xl mx-auto px-6 lg:px-8 h-16 flex items-center justify-between",
            ),
            class_name="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-30",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "sparkles", class_name="h-3.5 w-3.5 text-indigo-600"
                    ),
                    rx.el.span(
                        "AI-first content workspace.",
                        class_name="text-xs font-semibold text-indigo-700",
                    ),
                    class_name="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 mb-6",
                ),
                rx.el.h1(
                    "Your personal content ",
                    rx.el.span(
                        "operating system.", class_name="text-indigo-600"
                    ),
                    class_name="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight leading-tight max-w-4xl mx-auto",
                ),
                rx.el.p(
                    "Draft with AI, shape ideas into posts, schedule across your own channels, and keep your content workflow in one focused workspace.",
                    class_name="mt-6 text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed",
                ),
                rx.el.div(
                    rx.el.button(
                        "Sign in",
                        rx.icon("arrow-right", class_name="h-4 w-4"),
                        on_click=AppState.enter_app,
                        class_name="flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md",
                    ),
                    rx.el.button(
                        rx.icon("play", class_name="h-4 w-4"),
                        "Preview workflow",
                        class_name="flex items-center gap-2 bg-white text-slate-700 border border-slate-200 px-6 py-3 rounded-xl font-semibold hover:border-slate-300 transition-all",
                    ),
                    class_name="mt-8 flex flex-col sm:flex-row gap-3 justify-center",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("check", class_name="h-4 w-4 text-emerald-500"),
                        rx.el.span(
                            "Private workspace",
                            class_name="text-sm text-slate-600",
                        ),
                        class_name="flex items-center gap-1.5",
                    ),
                    rx.el.div(
                        rx.icon("check", class_name="h-4 w-4 text-emerald-500"),
                        rx.el.span(
                            "Bring your Zernio account", class_name="text-sm text-slate-600"
                        ),
                        class_name="flex items-center gap-1.5",
                    ),
                    rx.el.div(
                        rx.icon("check", class_name="h-4 w-4 text-emerald-500"),
                        rx.el.span(
                            "AI-assisted drafting",
                            class_name="text-sm text-slate-600",
                        ),
                        class_name="flex items-center gap-1.5",
                    ),
                    class_name="mt-8 flex flex-wrap items-center justify-center gap-6",
                ),
                class_name="text-center",
            ),
            class_name="max-w-7xl mx-auto px-6 lg:px-8 pt-20 pb-16",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                class_name="h-2.5 w-2.5 rounded-full bg-red-400"
                            ),
                            rx.el.div(
                                class_name="h-2.5 w-2.5 rounded-full bg-yellow-400"
                            ),
                            rx.el.div(
                                class_name="h-2.5 w-2.5 rounded-full bg-green-400"
                            ),
                            class_name="flex items-center gap-1.5",
                        ),
                        rx.el.div(
                            "postmelater.app/dashboard",
                            class_name="text-xs text-slate-400 font-mono",
                        ),
                        rx.el.div(class_name="w-12"),
                        class_name="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-slate-50",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    "Scheduled this week",
                                    class_name="text-xs font-medium text-slate-500",
                                ),
                                rx.el.p(
                                    "47 posts",
                                    class_name="text-2xl font-bold text-slate-900 mt-1",
                                ),
                                rx.el.p(
                                    "+12% vs last week",
                                    class_name="text-xs text-emerald-600 mt-1 font-medium",
                                ),
                                class_name="bg-white border border-slate-200 rounded-xl p-4",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Engagement rate",
                                    class_name="text-xs font-medium text-slate-500",
                                ),
                                rx.el.p(
                                    "8.4%",
                                    class_name="text-2xl font-bold text-slate-900 mt-1",
                                ),
                                rx.el.p(
                                    "+2.1% vs last week",
                                    class_name="text-xs text-emerald-600 mt-1 font-medium",
                                ),
                                class_name="bg-white border border-slate-200 rounded-xl p-4",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Drafts ready",
                                    class_name="text-xs font-medium text-slate-500",
                                ),
                                rx.el.p(
                                    "12",
                                    class_name="text-2xl font-bold text-slate-900 mt-1",
                                ),
                                rx.el.p(
                                    "3 awaiting review",
                                    class_name="text-xs text-slate-500 mt-1 font-medium",
                                ),
                                class_name="bg-white border border-slate-200 rounded-xl p-4",
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-3 gap-3",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "wifi",
                                        class_name="h-4 w-4 text-sky-500",
                                    ),
                                    class_name="h-8 w-8 rounded-lg bg-sky-50 flex items-center justify-center",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Launching our new feature today! 🚀",
                                        class_name="text-sm font-medium text-slate-900",
                                    ),
                                    rx.el.p(
                                        "Tomorrow • 9:00 AM",
                                        class_name="text-xs text-slate-500 mt-0.5",
                                    ),
                                ),
                                rx.el.span(
                                    "Scheduled",
                                    class_name="ml-auto text-xs px-2 py-1 rounded-md bg-indigo-50 text-indigo-700 font-semibold w-fit",
                                ),
                                class_name="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "link",
                                        class_name="h-4 w-4 text-blue-600",
                                    ),
                                    class_name="h-8 w-8 rounded-lg bg-blue-50 flex items-center justify-center",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "5 lessons from scaling our team to 50.",
                                        class_name="text-sm font-medium text-slate-900",
                                    ),
                                    rx.el.p(
                                        "Posted • 2h ago",
                                        class_name="text-xs text-slate-500 mt-0.5",
                                    ),
                                ),
                                rx.el.span(
                                    "Posted",
                                    class_name="ml-auto text-xs px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 font-semibold w-fit",
                                ),
                                class_name="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl",
                            ),
                            class_name="mt-3 space-y-2",
                        ),
                        class_name="p-5 bg-slate-50",
                    ),
                    class_name="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-xl shadow-slate-200/40",
                ),
                class_name="max-w-5xl mx-auto",
            ),
            class_name="max-w-7xl mx-auto px-6 lg:px-8 pb-24",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Everything you need to ship great content",
                        class_name="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight",
                    ),
                    rx.el.p(
                        "From drafting to delivery, PostMeLater keeps your content workflow focused and personal.",
                        class_name="mt-4 text-lg text-slate-600 max-w-2xl mx-auto",
                    ),
                    class_name="text-center mb-12",
                ),
                rx.el.div(
                    _feature_card(
                        "sparkles",
                        "AI Content Studio",
                        "Generate on-brand drafts in seconds. Pick a tone, target a platform, and let AI do the heavy lifting.",
                    ),
                    _feature_card(
                        "calendar-clock",
                        "Smart Scheduling",
                        "Pick optimal time windows or queue posts on autopilot. Built-in cadence controls keep you consistent.",
                    ),
                    _feature_card(
                        "layout-dashboard",
                        "Unified Dashboard",
                        "See engagement, lifecycle status, and account health in one place. No more switching tabs.",
                    ),
                    _feature_card(
                        "git-branch",
                        "Lifecycle Tracking",
                        "Track every post from draft to posted to failed. Retry, edit, or cancel with one click.",
                    ),
                    _feature_card(
                        "users",
                        "Your Accounts",
                        "Connect the social accounts you actually use and manage them from one queue.",
                    ),
                    _feature_card(
                        "shield-check",
                        "Reliable Delivery",
                        "Track failures, retry delivery, and keep your publishing workflow visible.",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5",
                ),
                class_name="max-w-7xl mx-auto px-6 lg:px-8",
            ),
            class_name="py-20 bg-white border-y border-slate-200",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    _stat("1", "Focused workspace"),
                    _stat("24/7", "Content queue"),
                    _stat("AI", "Draft assistant"),
                    _stat("2+", "Connected accounts"),
                    class_name="grid grid-cols-2 md:grid-cols-4 gap-8",
                ),
                class_name="max-w-5xl mx-auto px-6 lg:px-8",
            ),
            class_name="py-16",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Ready to open your workspace?",
                        class_name="text-3xl sm:text-4xl font-bold text-white tracking-tight",
                    ),
                    rx.el.p(
                        "Sign in and keep building your personal content system.",
                        class_name="mt-4 text-lg text-indigo-100 max-w-2xl mx-auto",
                    ),
                    rx.el.button(
                        "Sign in",
                        rx.icon("arrow-right", class_name="h-4 w-4"),
                        on_click=AppState.enter_app,
                        class_name="mt-8 flex items-center gap-2 bg-white text-indigo-700 px-6 py-3 rounded-xl font-semibold hover:bg-indigo-50 transition-all mx-auto",
                    ),
                    class_name="text-center",
                ),
                class_name="max-w-7xl mx-auto px-6 lg:px-8",
            ),
            class_name="py-20 bg-gradient-to-br from-indigo-600 to-indigo-700",
        ),
        rx.el.footer(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("send", class_name="h-4 w-4 text-white"),
                        class_name="h-7 w-7 rounded-lg bg-indigo-600 flex items-center justify-center",
                    ),
                    rx.el.span(
                        "PostMeLater", class_name="font-bold text-slate-900"
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.p(
                    "© 2026 PostMeLater. All rights reserved.",
                    class_name="text-sm text-slate-500",
                ),
                class_name="max-w-7xl mx-auto px-6 lg:px-8 h-16 flex items-center justify-between",
            ),
            class_name="border-t border-slate-200 bg-white",
        ),
        class_name="min-h-screen bg-slate-50",
    )
