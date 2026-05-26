import reflex as rx

from PostMeLater.states.app_state import AppState


def _nav_link(label: str, href: str) -> rx.Component:
    return rx.el.a(
        label,
        href=href,
        class_name="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors",
    )


def _doc_card(title: str, desc: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-indigo-600"),
            class_name="h-9 w-9 rounded-lg bg-indigo-50 flex items-center justify-center mb-4",
        ),
        rx.el.h3(title, class_name="text-base font-semibold text-slate-900"),
        rx.el.p(desc, class_name="text-sm text-slate-600 leading-relaxed mt-2"),
        class_name="bg-white border border-slate-200 rounded-2xl p-5",
    )


def _doc_section(
    title: str, body: str, section_id: str, *items: rx.Component
) -> rx.Component:
    return rx.el.section(
        rx.el.h2(title, class_name="text-xl font-bold text-slate-900"),
        rx.el.p(body, class_name="text-sm text-slate-600 leading-relaxed mt-2"),
        rx.el.div(*items, class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5"),
        id=section_id,
        class_name="py-8 border-b border-slate-200 last:border-b-0",
    )


def docs_page() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.a(
                    rx.el.div(
                        rx.icon("send", class_name="h-5 w-5 text-white"),
                        class_name="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center",
                    ),
                    rx.el.span(
                        "PostMeLater",
                        class_name="text-lg font-bold text-slate-900",
                    ),
                    href="/",
                    class_name="flex items-center gap-2",
                ),
                rx.el.nav(
                    _nav_link("Features", "/#features"),
                    _nav_link("Documentation", "/docs"),
                    class_name="hidden md:flex items-center gap-8",
                ),
                rx.el.button(
                    "Sign in",
                    on_click=AppState.open_signin,
                    class_name="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
                class_name="max-w-7xl mx-auto px-6 lg:px-8 h-16 flex items-center justify-between",
            ),
            class_name="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-30",
        ),
        rx.el.div(
            rx.el.aside(
                rx.el.div(
                    rx.el.p(
                        "Documentation",
                        class_name="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3",
                    ),
                    rx.el.a(
                        "Setup",
                        href="#setup",
                        class_name="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-1.5",
                    ),
                    rx.el.a(
                        "Zernio",
                        href="#zernio",
                        class_name="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-1.5",
                    ),
                    rx.el.a(
                        "Scheduling",
                        href="#scheduling",
                        class_name="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-1.5",
                    ),
                    rx.el.a(
                        "Limits",
                        href="#limits",
                        class_name="block text-sm font-medium text-slate-700 hover:text-indigo-600 py-1.5",
                    ),
                    class_name="sticky top-24",
                ),
                class_name="hidden lg:block w-56 shrink-0",
            ),
            rx.el.article(
                rx.el.div(
                    rx.el.span(
                        "PostMeLater Docs",
                        class_name="inline-flex items-center px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 text-xs font-semibold",
                    ),
                    rx.el.h1(
                        "Set up your personal content workspace",
                        class_name="text-4xl font-bold text-slate-900 tracking-tight mt-4",
                    ),
                    rx.el.p(
                        "Use this guide to connect Zernio, generate posts with AI, and schedule content from PostMeLater.",
                        class_name="text-lg text-slate-600 leading-relaxed mt-4 max-w-3xl",
                    ),
                    class_name="pb-8 border-b border-slate-200",
                ),
                rx.el.div(
                    _doc_section(
                        "Setup",
                        "Start with the core accounts PostMeLater needs for sign-in, AI generation, and publishing.",
                        "setup",
                        _doc_card(
                            "Supabase Google OAuth",
                            "Enable Google as a Supabase Auth provider so users sign in with their Google account.",
                            "key-round",
                        ),
                        _doc_card(
                            "Gemini",
                            "Add your Gemini API key for content generation, rewriting, and CTA polish.",
                            "sparkles",
                        ),
                    ),
                    _doc_section(
                        "Zernio",
                        "Zernio handles publishing. PostMeLater stores the account IDs and sends schedule requests.",
                        "zernio",
                        _doc_card(
                            "Create a Zernio API key",
                            "Generate a read-write API key in Zernio and add it in Settings or your environment.",
                            "key-round",
                        ),
                        _doc_card(
                            "Connect social accounts",
                            "Open Social Accounts and connect each social profile through Zernio's hosted OAuth flow.",
                            "plug",
                        ),
                    ),
                    _doc_section(
                        "Scheduling",
                        "Draft in the AI Content Studio, choose platforms, then send the schedule to Zernio.",
                        "scheduling",
                        _doc_card(
                            "Choose account and cadence",
                            "Pick a date, time, account, and cadence before adding the post to the queue.",
                            "calendar-clock",
                        ),
                        _doc_card(
                            "Track delivery state",
                            "Scheduled, posted, and failed states are visible in the queue and dashboard.",
                            "layout-dashboard",
                        ),
                    ),
                    _doc_section(
                        "Limits",
                        "The Zernio free allowance belongs to the Zernio account that owns the connected social accounts.",
                        "limits",
                        _doc_card(
                            "Two free accounts",
                            "If someone brings their own Zernio account, their connected accounts count against their own Zernio allowance.",
                            "users",
                        ),
                        _doc_card(
                            "Your private workspace",
                            "For personal use, your own Zernio key and accounts are enough. For invited users, store their own Zernio credentials separately.",
                            "shield-check",
                        ),
                    ),
                ),
                class_name="flex-1 min-w-0 max-w-4xl",
            ),
            class_name="max-w-7xl mx-auto px-6 lg:px-8 py-12 flex gap-10",
        ),
        class_name="font-['Inter'] antialiased text-slate-900 min-h-screen bg-slate-50",
    )
