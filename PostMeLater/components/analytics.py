import reflex as rx

from PostMeLater.states.content_state import ContentState
from PostMeLater.components.chart_utils import TOOLTIP_PROPS, CHART_TOOLTIP_CLASS


def _metric_card(metric) -> rx.Component:
    accent = rx.match(
        metric["accent"],
        (
            "emerald",
            "h-10 w-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center",
        ),
        (
            "amber",
            "h-10 w-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center",
        ),
        (
            "slate",
            "h-10 w-10 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center",
        ),
        "h-10 w-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center",
    )
    return rx.el.div(
        rx.el.div(rx.icon(metric["icon"], class_name="h-4 w-4"), class_name=accent),
        rx.el.p(metric["label"], class_name="text-xs font-semibold text-slate-500 mt-3"),
        rx.el.p(metric["value"], class_name="text-2xl font-bold text-slate-900 mt-1"),
        rx.el.p(metric["hint"], class_name="text-xs text-slate-500 mt-1"),
        class_name="bg-white border border-slate-200 rounded-xl p-4",
    )


def _top_post(post) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(post["body"], class_name="text-sm font-semibold text-slate-900 line-clamp-2"),
                rx.el.p(
                    post["platform"] + " " + post["published_at"],
                    class_name="text-xs text-slate-500 mt-1 truncate",
                ),
                class_name="min-w-0",
            ),
            rx.el.div(
                rx.el.p(post["engagement"].to_string(), class_name="text-sm font-bold text-slate-900 text-right"),
                rx.el.p("engagement", class_name="text-xs text-slate-500"),
                class_name="shrink-0",
            ),
            class_name="flex items-start justify-between gap-4",
        ),
        rx.el.div(
            rx.el.span("Likes " + post["likes"].to_string(), class_name="text-xs font-medium text-slate-600"),
            rx.el.span("Comments " + post["comments"].to_string(), class_name="text-xs font-medium text-slate-600"),
            rx.el.span("Shares " + post["shares"].to_string(), class_name="text-xs font-medium text-slate-600"),
            class_name="flex items-center gap-3 mt-3 flex-wrap",
        ),
        class_name="p-4 bg-white border border-slate-200 rounded-xl",
    )


def analytics_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Analytics", class_name="text-2xl font-bold text-slate-900"),
                rx.el.p(
                    "Zernio performance metrics for your published content.",
                    class_name="text-sm text-slate-500 mt-1",
                ),
            ),
            rx.el.div(
                rx.el.select(
                    rx.el.option("Last 7 days", value="7"),
                    rx.el.option("Last 30 days", value="30"),
                    rx.el.option("Last 90 days", value="90"),
                    value=ContentState.analytics_window,
                    on_change=ContentState.set_analytics_window,
                    class_name="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700",
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="h-4 w-4"),
                    "Refresh",
                    on_click=ContentState.refresh_analytics,
                    class_name="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-start justify-between gap-4 flex-wrap mb-6",
        ),
        rx.cond(
            ContentState.analytics_notice != "",
            rx.el.div(
                rx.icon("info", class_name="h-4 w-4 text-amber-600"),
                rx.el.p(ContentState.analytics_notice, class_name="text-sm font-medium text-amber-800"),
                class_name="flex items-center gap-2 p-3 bg-amber-50 border border-amber-100 rounded-xl mb-5",
            ),
            rx.fragment(),
        ),
        rx.el.div(
            rx.foreach(ContentState.analytics_metric_cards, _metric_card),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2("Performance trend", class_name="font-semibold text-slate-900"),
                    rx.el.p(
                        "Daily engagement and post volume.",
                        class_name="text-sm text-slate-500 mt-0.5",
                    ),
                    class_name="mb-4",
                ),
                rx.recharts.area_chart(
                    rx.recharts.cartesian_grid(horizontal=True, vertical=False, class_name="opacity-40"),
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
                    rx.recharts.x_axis(data_key="day", axis_line=False, tick_line=False, tick_size=10),
                    rx.recharts.y_axis(axis_line=False, tick_line=False, tick_size=10),
                    data=ContentState.analytics_chart,
                    width="100%",
                    height=280,
                    margin={"left": 0, "right": 12, "top": 10, "bottom": 0},
                    class_name=CHART_TOOLTIP_CLASS,
                ),
                class_name="bg-white border border-slate-200 rounded-xl p-5",
            ),
            rx.el.div(
                rx.el.h2("Best time to post", class_name="font-semibold text-slate-900"),
                rx.el.p(ContentState.best_time_summary, class_name="text-sm text-slate-600 mt-3 leading-relaxed"),
                rx.el.div(
                    rx.icon("clock-3", class_name="h-8 w-8 text-indigo-600"),
                    class_name="h-16 w-16 rounded-2xl bg-indigo-50 flex items-center justify-center mt-6",
                ),
                class_name="bg-white border border-slate-200 rounded-xl p-5",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-5 mb-5",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2("Top performing posts", class_name="font-semibold text-slate-900"),
                rx.el.p(
                    "Sorted by total engagement from Zernio analytics.",
                    class_name="text-sm text-slate-500 mt-0.5",
                ),
                class_name="mb-4",
            ),
            rx.cond(
                ContentState.top_analytics_posts.length() > 0,
                rx.el.div(
                    rx.foreach(ContentState.top_analytics_posts, _top_post),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-3",
                ),
                rx.el.div(
                    rx.icon("trending-up", class_name="h-10 w-10 text-slate-300 mx-auto"),
                    rx.el.p("No analytics posts yet", class_name="text-sm font-semibold text-slate-800 mt-3"),
                    rx.el.p(
                        "Publish through Zernio, then refresh this page after metrics sync.",
                        class_name="text-xs text-slate-500 mt-1",
                    ),
                    class_name="text-center py-12 bg-slate-50 border border-slate-200 rounded-2xl",
                ),
            ),
            class_name="bg-white border border-slate-200 rounded-xl p-5",
        ),
    )
