import reflex as rx

from PostMeLater.states.content_state import CONNECT_PLATFORM_OPTIONS, ContentState


def _connect_platform_option(platform: str) -> rx.Component:
    return rx.el.option(platform, value=platform)


def _account_row(account) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("send", class_name="h-4 w-4 text-indigo-600"),
            class_name="h-10 w-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                account["display_name"],
                class_name="text-sm font-semibold text-slate-900 truncate",
            ),
            rx.el.p(
                account["username"],
                class_name="text-xs text-slate-500 truncate mt-0.5",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.span(
            account["platform"],
            class_name="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-1 rounded-md",
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="h-3.5 w-3.5"),
            "Disconnect",
            title="Disconnect this account from Zernio",
            on_click=lambda: ContentState.open_disconnect_account(account["id"]),
            class_name="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors",
        ),
        class_name="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl",
    )


def _disconnect_modal() -> rx.Component:
    return rx.cond(
        ContentState.disconnect_modal_open,
        rx.el.div(
            rx.el.div(
                on_click=ContentState.close_disconnect_account,
                class_name="fixed inset-0 bg-slate-900/45 z-40",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("triangle-alert", class_name="h-5 w-5 text-red-600"),
                        rx.el.h3(
                            "Disconnect account",
                            class_name="font-semibold text-slate-900",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=ContentState.close_disconnect_account,
                        class_name="p-1.5 rounded-md text-slate-400 hover:bg-slate-100",
                    ),
                    class_name="flex items-center justify-between p-5 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.el.p(
                        "You are about to disconnect this social account:",
                        class_name="text-sm text-slate-600",
                    ),
                    rx.el.p(
                        ContentState.disconnect_account_label,
                        class_name="mt-2 text-sm font-semibold text-slate-900 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2",
                    ),
                    rx.el.div(
                        rx.icon("info", class_name="h-4 w-4 text-amber-600 mt-0.5"),
                        rx.el.p(
                            "PostMeLater will keep your drafts, history, ideas, and templates, but this account will no longer be available for new scheduled posts. Any upcoming posts targeting it may fail if they have not already published.",
                            class_name="text-sm text-amber-800 leading-relaxed",
                        ),
                        class_name="flex items-start gap-2 mt-4 p-3 rounded-xl bg-amber-50 border border-amber-100",
                    ),
                    class_name="p-5",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=ContentState.close_disconnect_account,
                        class_name="px-4 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="h-4 w-4"),
                        "Disconnect",
                        on_click=ContentState.confirm_disconnect_account,
                        class_name="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors",
                    ),
                    class_name="flex items-center justify-end gap-2 p-5 border-t border-slate-200 bg-slate-50 rounded-b-2xl",
                ),
                class_name="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden",
            ),
        ),
        rx.fragment(),
    )


def accounts_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Social Accounts",
                class_name="text-2xl font-bold text-slate-900",
            ),
            rx.el.p(
                "Connect and refresh the social channels PostMeLater can schedule to.",
                class_name="text-sm text-slate-500 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("plug", class_name="h-4 w-4 text-indigo-600"),
                    rx.el.h3(
                        "Connect a channel",
                        class_name="font-semibold text-slate-900 text-sm",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="h-4 w-4"),
                    "Refresh",
                    on_click=ContentState.refresh_accounts,
                    class_name="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 transition-colors",
                ),
                class_name="flex items-center justify-between mb-4 gap-3 flex-wrap",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Platform",
                        class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.foreach(
                                CONNECT_PLATFORM_OPTIONS,
                                _connect_platform_option,
                            ),
                            value=ContentState.connect_platform,
                            on_change=ContentState.set_connect_platform,
                            class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer text-slate-900",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                        ),
                        class_name="relative",
                    ),
                    class_name="min-w-0 flex-1",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "Connect account",
                    on_click=ContentState.connect_account,
                    class_name="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors self-end",
                ),
                class_name="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-3 mb-5",
            ),
            rx.cond(
                ContentState.api_notice != "",
                rx.el.div(
                    rx.icon("info", class_name="h-4 w-4 text-amber-600"),
                    rx.el.p(
                        ContentState.api_notice,
                        class_name="text-sm font-medium text-amber-800",
                    ),
                    class_name="flex items-center gap-2 p-3 bg-amber-50 border border-amber-100 rounded-xl",
                ),
                rx.fragment(),
            ),
            class_name="bg-white border border-slate-200 rounded-2xl p-5 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("users", class_name="h-4 w-4 text-indigo-600"),
                rx.el.h3(
                    "Connected accounts",
                    class_name="font-semibold text-slate-900 text-sm",
                ),
                class_name="flex items-center gap-2 mb-4",
            ),
            rx.cond(
                ContentState.accounts.length() > 0,
                rx.el.div(
                    rx.foreach(ContentState.accounts, _account_row),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-3",
                ),
                rx.el.div(
                    rx.icon(
                        "users",
                        class_name="h-10 w-10 text-slate-300 mx-auto",
                    ),
                    rx.el.p(
                        "No social accounts connected",
                        class_name="text-sm font-semibold text-slate-800 mt-3",
                    ),
                    rx.el.p(
                        "Choose a platform above and connect it through Zernio's hosted OAuth flow.",
                        class_name="text-xs text-slate-500 mt-1",
                    ),
                    class_name="text-center py-12 bg-slate-50 border border-slate-200 rounded-2xl",
                ),
            ),
            class_name="bg-white border border-slate-200 rounded-2xl p-5",
        ),
        _disconnect_modal(),
    )
