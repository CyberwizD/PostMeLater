import reflex as rx
from PostMeLater.states.content_state import ContentState, ScheduledPost


PLATFORM_ICONS = {
    "Twitter / X": "twitter",
    "LinkedIn": "linkedin",
    "Instagram": "instagram",
    "Facebook": "facebook",
    "Threads": "at-sign",
}


def _status_badge(status) -> rx.Component:
    return rx.match(
        status,
        (
            "scheduled",
            rx.el.span(
                rx.icon("clock", class_name="h-3 w-3"),
                "Scheduled",
                class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-indigo-50 text-indigo-700 w-fit",
            ),
        ),
        (
            "posted",
            rx.el.span(
                rx.icon("check", class_name="h-3 w-3"),
                "Posted",
                class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 w-fit",
            ),
        ),
        (
            "failed",
            rx.el.span(
                rx.icon("triangle-alert", class_name="h-3 w-3"),
                "Failed",
                class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-red-50 text-red-700 w-fit",
            ),
        ),
        rx.el.span("—", class_name="text-xs text-slate-400"),
    )


def _platform_pill(p: str) -> rx.Component:
    return rx.el.span(
        rx.icon("send", class_name="h-3 w-3"),
        p,
        class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700",
    )


def _filter_pill(label: str, value: str, count) -> rx.Component:
    is_active = ContentState.queue_filter == value
    return rx.el.button(
        rx.el.span(label, class_name="text-sm font-medium"),
        rx.el.span(
            count.to_string(),
            class_name=rx.cond(
                is_active,
                "px-1.5 py-0.5 rounded text-xs font-bold bg-white/20",
                "px-1.5 py-0.5 rounded text-xs font-bold bg-slate-200 text-slate-600",
            ),
        ),
        on_click=lambda: ContentState.set_queue_filter(value),
        class_name=rx.cond(
            is_active,
            "flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-600 text-white transition-colors",
            "flex items-center gap-2 px-3 py-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors",
        ),
    )


def _post_row(post: ScheduledPost) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                _status_badge(post["status"]),
                rx.el.span(
                    post["scheduled_date"] + " · " + post["scheduled_time"],
                    class_name="text-xs font-medium text-slate-500",
                ),
                rx.el.span(
                    post["account"],
                    class_name="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md",
                ),
                rx.cond(
                    post["cadence"] != "One-time",
                    rx.el.span(
                        rx.icon("repeat", class_name="h-3 w-3"),
                        post["cadence"],
                        class_name="inline-flex items-center gap-1 text-xs font-medium text-slate-600 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    post["engagement"] > 0,
                    rx.el.span(
                        rx.icon("heart", class_name="h-3 w-3"),
                        post["engagement"].to_string(),
                        class_name="inline-flex items-center gap-1 text-xs font-semibold text-pink-700 bg-pink-50 px-2 py-0.5 rounded-md",
                    ),
                    rx.fragment(),
                ),
                class_name="flex items-center gap-2 flex-wrap",
            ),
            rx.el.p(
                post["body"],
                class_name="text-sm text-slate-700 mt-2 line-clamp-3 leading-relaxed whitespace-pre-line",
            ),
            rx.el.div(
                rx.foreach(post["platforms"], _platform_pill),
                class_name="flex items-center gap-1.5 mt-3 flex-wrap",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.div(
            rx.cond(
                post["status"] == "failed",
                rx.el.button(
                    rx.icon("rotate-cw", class_name="h-3.5 w-3.5"),
                    "Retry",
                    on_click=lambda: ContentState.retry_post(post["id"]),
                    class_name="flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 rounded-md hover:bg-indigo-100 transition-colors",
                ),
                rx.cond(
                    post["status"] == "scheduled",
                    rx.el.button(
                        rx.icon("check", class_name="h-3.5 w-3.5"),
                        "Mark posted",
                        on_click=lambda: ContentState.mark_posted(post["id"]),
                        class_name="flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 rounded-md hover:bg-emerald-100 transition-colors",
                    ),
                    rx.fragment(),
                ),
            ),
            rx.cond(
                post["status"] != "posted",
                rx.el.button(
                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                    on_click=lambda: ContentState.open_edit(post["id"]),
                    class_name="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors",
                ),
                rx.fragment(),
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                on_click=lambda: ContentState.cancel_post(post["id"]),
                class_name="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors",
            ),
            class_name="flex items-center gap-1 shrink-0",
        ),
        class_name="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition-colors",
    )


def _calendar_post(post: ScheduledPost) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.span(
                post["scheduled_time"],
                class_name="text-[10px] font-bold text-indigo-700",
            ),
            rx.match(
                post["status"],
                (
                    "scheduled",
                    rx.el.span(
                        class_name="h-1.5 w-1.5 rounded-full bg-indigo-500"
                    ),
                ),
                (
                    "posted",
                    rx.el.span(
                        class_name="h-1.5 w-1.5 rounded-full bg-emerald-500"
                    ),
                ),
                (
                    "failed",
                    rx.el.span(
                        class_name="h-1.5 w-1.5 rounded-full bg-red-500"
                    ),
                ),
                rx.el.span(class_name="h-1.5 w-1.5 rounded-full bg-slate-400"),
            ),
            class_name="flex items-center justify-between mb-1",
        ),
        rx.el.p(
            post["body"],
            class_name="text-[11px] text-slate-700 line-clamp-2 leading-snug text-left",
        ),
        on_click=lambda: ContentState.open_edit(post["id"]),
        class_name=rx.match(
            post["status"],
            (
                "posted",
                "w-full p-2 bg-emerald-50/50 border border-emerald-100 rounded-lg hover:border-emerald-300 transition-colors text-left",
            ),
            (
                "failed",
                "w-full p-2 bg-red-50/50 border border-red-100 rounded-lg hover:border-red-300 transition-colors text-left",
            ),
            "w-full p-2 bg-indigo-50/50 border border-indigo-100 rounded-lg hover:border-indigo-300 transition-colors text-left",
        ),
    )


def _calendar_column(col) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                col["weekday"],
                class_name="text-[10px] font-semibold text-slate-500 uppercase tracking-wider",
            ),
            rx.el.p(
                col["label"],
                class_name=rx.cond(
                    col["is_today"],
                    "text-sm font-bold text-indigo-600",
                    "text-sm font-bold text-slate-900",
                ),
            ),
            class_name=rx.cond(
                col["is_today"],
                "px-3 py-2 border-b-2 border-indigo-500 bg-indigo-50/30",
                "px-3 py-2 border-b border-slate-200",
            ),
        ),
        rx.el.div(
            rx.cond(
                col["posts"].length() > 0,
                rx.el.div(
                    rx.foreach(col["posts"], _calendar_post),
                    class_name="flex flex-col gap-1.5",
                ),
                rx.el.p(
                    "—",
                    class_name="text-xs text-slate-300 text-center py-3",
                ),
            ),
            class_name="p-2 min-h-[140px]",
        ),
        class_name="bg-white border-r border-slate-200 last:border-r-0 min-w-0 flex flex-col",
    )


def _edit_modal() -> rx.Component:
    return rx.cond(
        ContentState.edit_modal_open,
        rx.el.div(
            rx.el.div(
                on_click=ContentState.close_edit,
                class_name="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "calendar-clock",
                            class_name="h-5 w-5 text-indigo-600",
                        ),
                        rx.el.h3(
                            "Edit timing",
                            class_name="font-semibold text-slate-900",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.button(
                        rx.icon(
                            "x",
                            class_name="h-5 w-5",
                        ),
                        on_click=ContentState.close_edit,
                        class_name="p-1.5 rounded-md text-slate-400 hover:bg-slate-100",
                    ),
                    class_name="flex items-center justify-between p-5 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.el.p(
                        "Update the schedule for this post. It will return to the queue as scheduled.",
                        class_name="text-sm text-slate-600 mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Date",
                                class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                            ),
                            rx.el.input(
                                type="date",
                                default_value=ContentState.edit_date,
                                on_change=ContentState.set_edit_date,
                                class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Time",
                                class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                            ),
                            rx.el.input(
                                type="time",
                                default_value=ContentState.edit_time,
                                on_change=ContentState.set_edit_time,
                                class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900",
                            ),
                        ),
                        class_name="grid grid-cols-2 gap-3 mb-3",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Account",
                            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                        ),
                        rx.el.div(
                            rx.el.select(
                                rx.el.option(
                                    "@studio.main",
                                    value="@studio.main",
                                ),
                                rx.el.option(
                                    "@studio.creator",
                                    value="@studio.creator",
                                ),
                                rx.el.option(
                                    "@brand.official",
                                    value="@brand.official",
                                ),
                                rx.el.option(
                                    "@founder.alex",
                                    value="@founder.alex",
                                ),
                                value=ContentState.edit_account,
                                on_change=ContentState.set_edit_account,
                                class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer text-slate-900",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                            ),
                            class_name="relative",
                        ),
                    ),
                    class_name="p-5",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=ContentState.close_edit,
                        class_name="px-4 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                    ),
                    rx.el.button(
                        rx.icon(
                            "check",
                            class_name="h-4 w-4",
                        ),
                        "Save changes",
                        on_click=ContentState.save_edit,
                        class_name="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors",
                    ),
                    class_name="flex items-center justify-end gap-2 p-5 border-t border-slate-200 bg-slate-50 rounded-b-2xl",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90%] max-w-md bg-white rounded-2xl border border-slate-200 z-50 shadow-2xl",
            ),
        ),
        rx.fragment(),
    )


def scheduling_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Scheduling Center",
                class_name="text-2xl font-bold text-slate-900",
            ),
            rx.el.p(
                "Manage your queue, track lifecycle status, and adjust delivery.",
                class_name="text-sm text-slate-500 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            _stat_card(
                "calendar-clock",
                "Scheduled",
                ContentState.queue_count_scheduled,
                "indigo",
            ),
            _stat_card(
                "circle-check",
                "Posted",
                ContentState.queue_count_posted,
                "emerald",
            ),
            _stat_card(
                "triangle-alert",
                "Failed",
                ContentState.queue_count_failed,
                "red",
            ),
            _stat_card(
                "file-text", "Drafts", ContentState.queue_count_draft, "slate"
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "calendar-days", class_name="h-4 w-4 text-indigo-600"
                    ),
                    rx.el.h3(
                        "This week",
                        class_name="font-semibold text-slate-900 text-sm",
                    ),
                    rx.el.div(
                        rx.el.span(
                            class_name="h-2 w-2 rounded-full bg-indigo-500"
                        ),
                        rx.el.span(
                            "Scheduled",
                            class_name="text-xs font-medium text-slate-600",
                        ),
                        rx.el.span(
                            class_name="h-2 w-2 rounded-full bg-emerald-500 ml-3"
                        ),
                        rx.el.span(
                            "Posted",
                            class_name="text-xs font-medium text-slate-600",
                        ),
                        rx.el.span(
                            class_name="h-2 w-2 rounded-full bg-red-500 ml-3"
                        ),
                        rx.el.span(
                            "Failed",
                            class_name="text-xs font-medium text-slate-600",
                        ),
                        class_name="flex items-center gap-1.5 ml-auto",
                    ),
                    class_name="flex items-center gap-2 mb-4 flex-wrap",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.foreach(
                            ContentState.week_calendar, _calendar_column
                        ),
                        class_name="grid grid-cols-7 min-w-[700px]",
                    ),
                    class_name="overflow-x-auto border border-slate-200 rounded-xl",
                ),
                class_name="bg-white border border-slate-200 rounded-2xl p-5 mb-6",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Queue", class_name="font-semibold text-slate-900"
                    ),
                    rx.el.p(
                        "All posts across your connected accounts.",
                        class_name="text-xs text-slate-500 mt-0.5",
                    ),
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.select(
                            rx.el.option("All accounts", value="all"),
                            rx.el.option("@studio.main", value="@studio.main"),
                            rx.el.option(
                                "@studio.creator", value="@studio.creator"
                            ),
                            rx.el.option(
                                "@brand.official", value="@brand.official"
                            ),
                            rx.el.option(
                                "@founder.alex", value="@founder.alex"
                            ),
                            value=ContentState.queue_account_filter,
                            on_change=ContentState.set_queue_account_filter,
                            class_name="px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer text-slate-700",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                        ),
                        class_name="relative",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center justify-between mb-4 flex-wrap gap-3",
            ),
            rx.el.div(
                _filter_pill(
                    "All", "all", ContentState.scheduled_posts.length()
                ),
                _filter_pill(
                    "Scheduled", "scheduled", ContentState.queue_count_scheduled
                ),
                _filter_pill(
                    "Posted", "posted", ContentState.queue_count_posted
                ),
                _filter_pill(
                    "Failed", "failed", ContentState.queue_count_failed
                ),
                class_name="flex items-center gap-1 mb-4 flex-wrap p-1 bg-slate-50 border border-slate-200 rounded-xl w-fit",
            ),
            rx.cond(
                ContentState.filtered_queue.length() > 0,
                rx.el.div(
                    rx.foreach(ContentState.filtered_queue, _post_row),
                    class_name="flex flex-col gap-2",
                ),
                rx.el.div(
                    rx.icon(
                        "inbox", class_name="h-10 w-10 text-slate-300 mx-auto"
                    ),
                    rx.el.p(
                        "No posts match this filter",
                        class_name="text-sm font-medium text-slate-700 mt-3",
                    ),
                    rx.el.p(
                        "Try a different status or schedule a new post from the Studio.",
                        class_name="text-xs text-slate-500 mt-1",
                    ),
                    class_name="text-center py-12 bg-white border border-slate-200 rounded-2xl",
                ),
            ),
        ),
        _edit_modal(),
    )


def _stat_card(icon: str, label: str, value, accent: str) -> rx.Component:
    accent_classes = {
        "indigo": "h-9 w-9 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600",
        "emerald": "h-9 w-9 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600",
        "red": "h-9 w-9 rounded-lg bg-red-50 flex items-center justify-center text-red-600",
        "slate": "h-9 w-9 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600",
    }
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4"),
            class_name=accent_classes.get(accent, accent_classes["slate"]),
        ),
        rx.el.div(
            rx.el.p(label, class_name="text-xs font-medium text-slate-500"),
            rx.el.p(
                value.to_string(),
                class_name="text-xl font-bold text-slate-900 mt-0.5",
            ),
        ),
        class_name="flex items-center gap-3 bg-white border border-slate-200 rounded-xl p-4",
    )