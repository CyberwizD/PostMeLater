import reflex as rx


def _info_row(label: str, value: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-indigo-600"),
            class_name="h-9 w-9 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(label, class_name="text-xs font-semibold text-slate-500"),
            rx.el.p(value, class_name="text-sm font-semibold text-slate-900 mt-0.5"),
            class_name="min-w-0",
        ),
        class_name="flex items-center gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl",
    )


def _section(title: str, icon: str, *children: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-indigo-600"),
            rx.el.h3(title, class_name="font-semibold text-slate-900 text-sm"),
            class_name="flex items-center gap-2 mb-4",
        ),
        *children,
        class_name="bg-white border border-slate-200 rounded-2xl p-5",
    )


def settings_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Settings", class_name="text-2xl font-bold text-slate-900"),
            rx.el.p(
                "Manage your profile, workspace defaults, and integrations.",
                class_name="text-sm text-slate-500 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            _section(
                "Profile",
                "user",
                rx.el.div(
                    rx.el.img(
                        src="https://api.dicebear.com/9.x/notionists/svg?seed=alex",
                        class_name="h-16 w-16 rounded-2xl bg-slate-100 border border-slate-200",
                    ),
                    rx.el.div(
                        rx.el.h2(
                            "Alex Morgan",
                            class_name="text-lg font-bold text-slate-900",
                        ),
                        rx.el.p(
                            "alex@studio.com",
                            class_name="text-sm text-slate-500 mt-0.5",
                        ),
                        rx.el.span(
                            "Personal workspace",
                            class_name="inline-flex items-center px-2 py-1 rounded-md bg-indigo-50 text-indigo-700 text-xs font-semibold mt-3",
                        ),
                        class_name="min-w-0",
                    ),
                    class_name="flex items-center gap-4 mb-5",
                ),
                rx.el.div(
                    _info_row("Access", "Magic Link sign-in", "mail-check"),
                    _info_row("Account mode", "Private / invited use", "user-check"),
                    class_name="grid grid-cols-1 sm:grid-cols-2 gap-3",
                ),
            ),
            _section(
                "Workspace",
                "sliders-horizontal",
                rx.el.div(
                    _info_row("Default timezone", "Africa/Lagos", "clock"),
                    _info_row("Default tone", "Professional", "sparkles"),
                    _info_row("Data storage", "PostMeLater database", "database"),
                    class_name="grid grid-cols-1 gap-3",
                ),
            ),
            _section(
                "Integrations",
                "plug",
                rx.el.div(
                    _info_row("Publishing", "Zernio", "send"),
                    _info_row("AI engine", "Gemini", "sparkles"),
                    _info_row("Auth", "Supabase Magic Link", "key-round"),
                    class_name="grid grid-cols-1 gap-3",
                ),
            ),
            class_name="grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-5",
        ),
    )
