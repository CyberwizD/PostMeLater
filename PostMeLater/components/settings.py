import reflex as rx
from PostMeLater.states.app_state import AppState
from PostMeLater.states.content_state import AI_PROVIDER_OPTIONS, ContentState


def _provider_option(provider: str) -> rx.Component:
    return rx.el.option(provider, value=provider)


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
        class_name="bg-white border border-slate-200 rounded-2xl p-5 h-fit",
    )


def _integration_input(
    label: str,
    placeholder: str,
    value,
    on_change,
    input_type: str = "text",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
        ),
        rx.el.input(
            type=input_type,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder-slate-400",
        ),
    )


def _zernio_step(number: str, title: str, detail: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            number,
            class_name="h-7 w-7 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center text-xs font-bold shrink-0",
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-semibold text-slate-900"),
            rx.el.p(detail, class_name="text-sm text-slate-600 mt-1 leading-relaxed"),
            class_name="min-w-0",
        ),
        class_name="flex items-start gap-3",
    )


def _zernio_help_modal() -> rx.Component:
    return rx.cond(
        ContentState.zernio_help_open,
        rx.el.div(
            rx.el.div(
                on_click=ContentState.close_zernio_help,
                class_name="fixed inset-0 bg-slate-900/45 z-40",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("key-round", class_name="h-4 w-4 text-indigo-600"),
                        rx.el.h3(
                            "How to connect your Zernio API key",
                            class_name="font-semibold text-slate-900",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=ContentState.close_zernio_help,
                        class_name="p-2 rounded-lg text-slate-500 hover:bg-slate-100",
                    ),
                    class_name="flex items-center justify-between px-5 py-4 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.el.p(
                        "Zernio gives you an API key during onboarding, and you can also create one later from the dashboard.",
                        class_name="text-sm text-slate-600 leading-relaxed mb-5",
                    ),
                    rx.el.div(
                        _zernio_step(
                            "1",
                            "Create or open your Zernio account",
                            "Sign in to Zernio, or create an account if you do not have one yet.",
                        ),
                        _zernio_step(
                            "2",
                            "Open API Keys",
                            "Go to Settings -> API Keys, or use the API keys dashboard link below.",
                        ),
                        _zernio_step(
                            "3",
                            "Create and copy a key",
                            "Create a read-write key for PostMeLater. Copy it immediately because Zernio only shows the full key once.",
                        ),
                        _zernio_step(
                            "4",
                            "Paste it into PostMeLater",
                            "Return here, paste the key, then save. After that, connect your social accounts from Social Accounts.",
                        ),
                        class_name="space-y-4",
                    ),
                    rx.el.div(
                        rx.el.a(
                            rx.icon("external-link", class_name="h-4 w-4"),
                            "Open Zernio",
                            href="https://zernio.com",
                            target="_blank",
                            class_name="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700",
                        ),
                        rx.el.a(
                            rx.icon("key-round", class_name="h-4 w-4"),
                            "API keys dashboard",
                            href="https://zernio.com/dashboard/api-keys",
                            target="_blank",
                            class_name="flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6",
                    ),
                    rx.el.div(
                        rx.icon("shield-check", class_name="h-4 w-4 text-emerald-600"),
                        rx.el.p(
                            "Keep your key private. PostMeLater stores it for your signed-in workspace only.",
                            class_name="text-xs text-emerald-800",
                        ),
                        class_name="flex items-start gap-2 mt-5 p-3 rounded-xl bg-emerald-50 border border-emerald-100",
                    ),
                    class_name="px-5 py-5",
                ),
                class_name="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 -translate-y-1/2 bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden",
            ),
        ),
        rx.fragment(),
    )


def settings_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Settings", class_name="text-2xl font-bold text-slate-900"),
            rx.el.p(
                "Manage your profile and connected services.",
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
                        src=AppState.user_avatar,
                        class_name="h-16 w-16 rounded-2xl bg-slate-100 border border-slate-200",
                    ),
                    rx.el.div(
                        rx.el.h2(
                            AppState.user_name,
                            class_name="text-lg font-bold text-slate-900",
                        ),
                        rx.el.p(
                            AppState.user_email,
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
                    _info_row("Default timezone", "Africa/Lagos", "clock"),
                    _info_row("Account mode", "Personal use", "user-check"),
                    _info_row("AI engine", ContentState.ai_engine_label, "sparkles"),
                    _info_row(
                        "Connected channels",
                        ContentState.accounts.length().to_string() + " accounts",
                        "users",
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-2 gap-3",
                ),
            ),
            _section(
                "Integrations",
                "plug",
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                ContentState.zernio_status_label,
                                class_name=rx.cond(
                                    ContentState.zernio_key_saved,
                                    "text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md",
                                    "text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-1 rounded-md",
                                ),
                            ),
                            rx.el.p(
                                ContentState.zernio_status_detail,
                                class_name="text-xs text-slate-500 mt-2",
                            ),
                            class_name="min-w-0",
                        ),
                        rx.el.button(
                            rx.icon("help-circle", class_name="h-4 w-4"),
                            "How to connect",
                            on_click=ContentState.open_zernio_help,
                            class_name="flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700 shrink-0",
                        ),
                        class_name="mb-4 flex items-start justify-between gap-3",
                    ),
                    _integration_input(
                        "Zernio API key",
                        rx.cond(
                            ContentState.zernio_key_saved,
                            "Leave blank to keep saved key",
                            "Paste your Zernio API key",
                        ),
                        ContentState.zernio_api_key_input,
                        ContentState.set_zernio_api_key_input,
                        "password",
                    ),
                    _integration_input(
                        "Zernio profile ID",
                        "Optional",
                        ContentState.zernio_profile_id_input,
                        ContentState.set_zernio_profile_id_input,
                    ),
                    rx.el.button(
                        rx.icon("save", class_name="h-4 w-4"),
                        "Save Zernio settings",
                        on_click=ContentState.save_zernio_settings,
                        class_name="mt-3 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors",
                    ),
                    class_name="mb-5 p-4 bg-slate-50 border border-slate-200 rounded-xl",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            ContentState.ai_status_label,
                            class_name=rx.cond(
                                ContentState.ai_key_saved,
                                "text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md",
                                "text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-1 rounded-md",
                            ),
                        ),
                        rx.el.p(
                            ContentState.ai_status_detail,
                            class_name="text-xs text-slate-500 mt-2",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "AI provider",
                            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                        ),
                        rx.el.div(
                            rx.el.select(
                                rx.foreach(AI_PROVIDER_OPTIONS, _provider_option),
                                value=ContentState.ai_provider_input,
                                on_change=ContentState.set_ai_provider_input,
                                class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer text-slate-900",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                            ),
                            class_name="relative",
                        ),
                        class_name="mb-3",
                    ),
                    _integration_input(
                        "AI API key",
                        rx.cond(
                            ContentState.ai_key_saved,
                            "Leave blank to keep saved key",
                            "Optional: paste your own provider API key",
                        ),
                        ContentState.ai_api_key_input,
                        ContentState.set_ai_api_key_input,
                        "password",
                    ),
                    _integration_input(
                        "AI model",
                        "Model name for the selected provider",
                        ContentState.ai_model_input,
                        ContentState.set_ai_model_input,
                    ),
                    rx.cond(
                        ContentState.ai_base_url_enabled,
                        _integration_input(
                            "Base URL",
                            "https://openrouter.ai/api/v1 or your provider URL",
                            ContentState.ai_base_url_input,
                            ContentState.set_ai_base_url_input,
                        ),
                        rx.fragment(),
                    ),
                    rx.el.button(
                        rx.icon("save", class_name="h-4 w-4"),
                        "Save AI settings",
                        on_click=ContentState.save_ai_settings,
                        class_name="mt-3 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors",
                    ),
                    class_name="mb-5 p-4 bg-slate-50 border border-slate-200 rounded-xl",
                ),
            ),
            class_name="grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-5 items-start",
        ),
        _zernio_help_modal(),
    )
