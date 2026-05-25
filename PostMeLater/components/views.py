import reflex as rx
from PostMeLater.states.content_state import ContentState, ActivityEvent, AccountHealth
from PostMeLater.states.app_state import AppState
from PostMeLater.components.studio import studio_view as _studio
from PostMeLater.components.scheduling import scheduling_view as _scheduling
from PostMeLater.components.chart_utils import TOOLTIP_PROPS, CHART_TOOLTIP_CLASS


def studio_view() -> rx.Component:
    return _studio()


def scheduling_view() -> rx.Component:
    return _scheduling()


def _upcoming_mini(post) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                post["scheduled_date"] + " · " + post["scheduled_time"],
                class_name="text-xs font-semibold text-indigo-700",
            ),
            rx.el.span(
                post["account"],
                class_name="text-xs font-medium text-slate-500",
            ),
            class_name="flex items-center justify-between mb-1.5",
        ),
        rx.el.p(
            post["body"],
            class_name="text-sm text-slate-700 line-clamp-2 leading-relaxed",
        ),
        class_name="p-3 bg-white border border-slate-200 rounded-xl hover:border-indigo-200 transition-colors",
    )


def _dash_stat(
    icon: str, label: str, value, hint: str, accent: str = "indigo"
) -> rx.Component:
    accents = {
        "indigo": "h-9 w-9 rounded-lg bg-indigo-50 flex items-center justify-center mb-3 text-indigo-600",
        "emerald": "h-9 w-9 rounded-lg bg-emerald-50 flex items-center justify-center mb-3 text-emerald-600",
        "amber": "h-9 w-9 rounded-lg bg-amber-50 flex items-center justify-center mb-3 text-amber-600",
        "red": "h-9 w-9 rounded-lg bg-red-50 flex items-center justify-center mb-3 text-red-600",
        "slate": "h-9 w-9 rounded-lg bg-slate-100 flex items-center justify-center mb-3 text-slate-600",
    }
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4"),
            class_name=accents.get(accent, accents["indigo"]),
        ),
        rx.el.p(label, class_name="text-xs font-medium text-slate-500"),
        rx.el.p(
            value.to_string(),
            class_name="text-2xl font-bold text-slate-900 mt-1",
        ),
        rx.el.p(hint, class_name="text-xs text-slate-500 mt-1"),
        class_name="bg-white border border-slate-200 rounded-xl p-4",
    )


def _chart_legend() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                class_name="w-3 h-3 inline-block mr-2 rounded-sm bg-indigo-500",
            ),
            rx.el.span(
                "Engagement",
                class_name="text-xs font-medium text-slate-600",
            ),
            class_name="flex items-center mr-4",
        ),
        rx.el.div(
            rx.el.span(
                class_name="w-3 h-3 inline-block mr-2 rounded-sm bg-emerald-400",
            ),
            rx.el.span(
                "Posts", class_name="text-xs font-medium text-slate-600"
            ),
            class_name="flex items-center",
        ),
        class_name="flex items-center",
    )


def _engagement_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Engagement this week",
                    class_name="font-semibold text-slate-900",
                ),
                rx.el.p(
                    "Daily engagement and posting cadence.",
                    class_name="text-sm text-slate-500 mt-0.5",
                ),
            ),
            _chart_legend(),
            class_name="flex items-start justify-between mb-4 flex-wrap gap-3",
        ),
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-40"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.area(
                data_key="engagement",
                name="Engagement",
                stroke="#6366F1",
                fill="#6366F1",
                fill_opacity=0.15,
                stroke_width=2,
                type_="natural",
            ),
            rx.recharts.area(
                data_key="posts",
                name="Posts",
                stroke="#10B981",
                fill="#10B981",
                fill_opacity=0.1,
                stroke_width=2,
                type_="natural",
            ),
            rx.recharts.x_axis(
                data_key="day",
                axis_line=False,
                tick_line=False,
                tick_size=10,
                custom_attrs={"fontSize": "12px", "fill": "#64748b"},
            ),
            rx.recharts.y_axis(
                axis_line=False,
                tick_line=False,
                tick_size=10,
                custom_attrs={"fontSize": "12px", "fill": "#64748b"},
            ),
            data=ContentState.weekly_chart,
            width="100%",
            height=260,
            margin={"left": 0, "right": 12, "top": 10, "bottom": 0},
            class_name=CHART_TOOLTIP_CLASS,
        ),
        class_name="bg-white border border-slate-200 rounded-xl p-5",
    )


def _platform_chart() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Platform mix",
                class_name="font-semibold text-slate-900",
            ),
            rx.el.p(
                "Posts queued or delivered per channel.",
                class_name="text-sm text-slate-500 mt-0.5",
            ),
            class_name="mb-4",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-40"
            ),
            rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
            rx.recharts.bar(
                data_key="posts",
                name="Posts",
                fill="#6366F1",
                radius=[6, 6, 0, 0],
            ),
            rx.recharts.x_axis(
                data_key="platform",
                axis_line=False,
                tick_line=False,
                tick_size=10,
                custom_attrs={"fontSize": "12px", "fill": "#64748b"},
            ),
            rx.recharts.y_axis(
                axis_line=False,
                tick_line=False,
                tick_size=10,
                custom_attrs={"fontSize": "12px", "fill": "#64748b"},
            ),
            data=ContentState.platform_chart,
            width="100%",
            height=260,
            bar_size=32,
            margin={"left": 0, "right": 12, "top": 10, "bottom": 0},
            class_name=CHART_TOOLTIP_CLASS,
        ),
        class_name="bg-white border border-slate-200 rounded-xl p-5",
    )


def _activity_row(ev: ActivityEvent) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(ev["icon"], class_name="h-4 w-4"),
            class_name=rx.match(
                ev["accent"],
                (
                    "emerald",
                    "h-8 w-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0",
                ),
                (
                    "red",
                    "h-8 w-8 rounded-lg bg-red-50 text-red-600 flex items-center justify-center shrink-0",
                ),
                (
                    "indigo",
                    "h-8 w-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0",
                ),
                "h-8 w-8 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center shrink-0",
            ),
        ),
        rx.el.div(
            rx.el.p(
                ev["title"],
                class_name="text-sm font-semibold text-slate-900 truncate",
            ),
            rx.el.p(
                ev["detail"],
                class_name="text-xs text-slate-500 truncate mt-0.5",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.span(
            ev["time"],
            class_name="text-xs font-medium text-slate-400 shrink-0",
        ),
        class_name="flex items-center gap-3 py-2.5",
    )


def _account_health_row(a: AccountHealth) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(a["icon"], class_name="h-4 w-4 text-slate-700"),
            class_name="h-9 w-9 rounded-lg bg-slate-100 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                a["handle"],
                class_name="text-sm font-semibold text-slate-900 truncate",
            ),
            rx.el.p(
                a["platform"],
                class_name="text-xs text-slate-500 truncate",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.div(
            rx.el.p(
                a["posts_week"].to_string() + " posts",
                class_name="text-xs font-semibold text-slate-700 text-right",
            ),
            rx.el.p(
                "avg " + a["engagement"].to_string(),
                class_name="text-xs text-slate-500 text-right",
            ),
            class_name="hidden sm:block",
        ),
        rx.el.span(
            a["status"],
            class_name=rx.match(
                a["accent"],
                (
                    "emerald",
                    "text-xs font-semibold px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 w-fit",
                ),
                (
                    "red",
                    "text-xs font-semibold px-2 py-1 rounded-md bg-red-50 text-red-700 w-fit",
                ),
                (
                    "indigo",
                    "text-xs font-semibold px-2 py-1 rounded-md bg-indigo-50 text-indigo-700 w-fit",
                ),
                "text-xs font-semibold px-2 py-1 rounded-md bg-slate-100 text-slate-700 w-fit",
            ),
        ),
        class_name="flex items-center gap-3 py-3 border-b border-slate-100 last:border-b-0",
    )


def dashboard_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Dashboard", class_name="text-2xl font-bold text-slate-900"
                ),
                rx.el.p(
                    "Welcome back, Alex. Here's what's happening with your content.",
                    class_name="text-sm text-slate-500 mt-1",
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("calendar-clock", class_name="h-4 w-4"),
                    "View queue",
                    on_click=lambda: AppState.set_view("scheduling"),
                    class_name="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4"),
                    "New post",
                    on_click=lambda: AppState.set_view("studio"),
                    class_name="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-start justify-between mb-8 flex-wrap gap-4",
        ),
        rx.el.div(
            _dash_stat(
                "calendar-clock",
                "Scheduled",
                ContentState.queue_count_scheduled,
                "Across all accounts",
                "indigo",
            ),
            _dash_stat(
                "circle-check",
                "Posted",
                ContentState.queue_count_posted,
                "Lifetime",
                "emerald",
            ),
            _dash_stat(
                "trending-up",
                "Avg engagement",
                ContentState.avg_engagement,
                "Per post (last 14 days)",
                "amber",
            ),
            _dash_stat(
                "triangle-alert",
                "Failed",
                ContentState.queue_count_failed,
                "Need attention",
                "red",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6",
        ),
        rx.el.div(
            _engagement_chart(),
            _platform_chart(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6",
        ),
        rx.el.div(
            # Upcoming posts
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Upcoming posts",
                            class_name="font-semibold text-slate-900",
                        ),
                        rx.el.p(
                            "Your next scheduled deliveries.",
                            class_name="text-sm text-slate-500 mt-0.5",
                        ),
                    ),
                    rx.el.button(
                        "View all",
                        rx.icon("arrow-right", class_name="h-3.5 w-3.5"),
                        on_click=lambda: AppState.set_view("scheduling"),
                        class_name="flex items-center gap-1 text-sm font-semibold text-indigo-600 hover:text-indigo-700",
                    ),
                    class_name="px-5 py-4 border-b border-slate-200 flex items-center justify-between",
                ),
                rx.el.div(
                    rx.cond(
                        ContentState.upcoming_week.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                ContentState.upcoming_week, _upcoming_mini
                            ),
                            class_name="flex flex-col gap-2",
                        ),
                        rx.el.div(
                            rx.icon(
                                "inbox",
                                class_name="h-10 w-10 text-slate-300 mx-auto",
                            ),
                            rx.el.p(
                                "No posts scheduled yet",
                                class_name="text-sm font-medium text-slate-700 mt-3",
                            ),
                            rx.el.p(
                                "Head to the AI Content Studio to draft your first post.",
                                class_name="text-sm text-slate-500 mt-1",
                            ),
                            rx.el.button(
                                rx.icon("sparkles", class_name="h-4 w-4"),
                                "Open Studio",
                                on_click=lambda: AppState.set_view("studio"),
                                class_name="mt-4 inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                            ),
                            class_name="text-center py-10",
                        ),
                    ),
                    class_name="p-5",
                ),
                class_name="bg-white border border-slate-200 rounded-xl",
            ),
            # Account health
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Account health",
                        class_name="font-semibold text-slate-900",
                    ),
                    rx.el.p(
                        "Performance across connected channels.",
                        class_name="text-sm text-slate-500 mt-0.5",
                    ),
                    class_name="px-5 py-4 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.foreach(
                        ContentState.account_health, _account_health_row
                    ),
                    class_name="px-5 py-2",
                ),
                class_name="bg-white border border-slate-200 rounded-xl",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6",
        ),
        # Recent activity
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Recent activity",
                        class_name="font-semibold text-slate-900",
                    ),
                    rx.el.p(
                        "Latest events across your queue.",
                        class_name="text-sm text-slate-500 mt-0.5",
                    ),
                ),
                rx.el.button(
                    "Open scheduling",
                    rx.icon("arrow-right", class_name="h-3.5 w-3.5"),
                    on_click=lambda: AppState.set_view("scheduling"),
                    class_name="flex items-center gap-1 text-sm font-semibold text-indigo-600 hover:text-indigo-700",
                ),
                class_name="px-5 py-4 border-b border-slate-200 flex items-center justify-between",
            ),
            rx.el.div(
                rx.cond(
                    ContentState.recent_activity.length() > 0,
                    rx.el.div(
                        rx.foreach(ContentState.recent_activity, _activity_row),
                        class_name="divide-y divide-slate-100",
                    ),
                    rx.el.div(
                        rx.icon(
                            "history",
                            class_name="h-10 w-10 text-slate-300 mx-auto",
                        ),
                        rx.el.p(
                            "No activity yet",
                            class_name="text-sm font-medium text-slate-700 mt-3",
                        ),
                        rx.el.p(
                            "Schedule a post to see updates here.",
                            class_name="text-sm text-slate-500 mt-1",
                        ),
                        class_name="text-center py-10",
                    ),
                ),
                class_name="px-5",
            ),
            class_name="bg-white border border-slate-200 rounded-xl",
        ),
    )