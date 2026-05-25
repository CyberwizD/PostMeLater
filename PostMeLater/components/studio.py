import reflex as rx
from PostMeLater.states.content_state import (
    ContentState,
    PLATFORM_OPTIONS,
    TONE_OPTIONS,
)


PLATFORM_ICONS = {
    "Twitter / X": "twitter",
    "LinkedIn": "linkedin",
    "Instagram": "instagram",
    "Facebook": "facebook",
    "Threads": "at-sign",
}


def _platform_chip(platform: str) -> rx.Component:
    icon = PLATFORM_ICONS.get(platform, "globe")
    is_selected = ContentState.selected_platforms.contains(platform)
    return rx.el.button(
        rx.icon(icon, class_name="h-3.5 w-3.5"),
        rx.el.span(platform, class_name="text-xs font-medium"),
        on_click=lambda: ContentState.toggle_platform(platform),
        class_name=rx.cond(
            is_selected,
            "flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-600 text-white border border-indigo-600 transition-colors",
            "flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white text-slate-700 border border-slate-200 hover:border-indigo-300 hover:text-indigo-700 transition-colors",
        ),
        type="button",
    )


def _tone_chip(tone: str) -> rx.Component:
    is_selected = ContentState.tone == tone
    return rx.el.button(
        tone,
        on_click=lambda: ContentState.set_tone(tone),
        class_name=rx.cond(
            is_selected,
            "px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs font-semibold transition-colors",
            "px-3 py-1.5 rounded-lg bg-white text-slate-600 border border-slate-200 hover:border-slate-300 text-xs font-medium transition-colors",
        ),
        type="button",
    )


def _quality_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                "Quality score",
                class_name="text-xs font-semibold text-slate-500 uppercase tracking-wider",
            ),
            rx.el.div(
                rx.el.span(
                    ContentState.quality_score.to_string() + "/100",
                    class_name="text-sm font-bold text-slate-900",
                ),
                rx.el.span(
                    ContentState.quality_label,
                    class_name=rx.cond(
                        ContentState.quality_score >= 80,
                        "text-xs font-semibold text-emerald-600 ml-2",
                        rx.cond(
                            ContentState.quality_score >= 55,
                            "text-xs font-semibold text-indigo-600 ml-2",
                            "text-xs font-semibold text-amber-600 ml-2",
                        ),
                    ),
                ),
                class_name="flex items-baseline",
            ),
            class_name="flex items-center justify-between mb-2",
        ),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    ContentState.quality_score >= 80,
                    "h-2 rounded-full bg-emerald-500 transition-all",
                    rx.cond(
                        ContentState.quality_score >= 55,
                        "h-2 rounded-full bg-indigo-500 transition-all",
                        "h-2 rounded-full bg-amber-500 transition-all",
                    ),
                ),
                style={"width": ContentState.quality_score.to_string() + "%"},
            ),
            class_name="h-2 rounded-full bg-slate-100 overflow-hidden",
        ),
        rx.el.div(
            _check_item(
                "Length 80–280 chars",
                (ContentState.char_count >= 80)
                & (ContentState.char_count <= 280),
            ),
            _check_item("Includes hashtags", ContentState.has_hashtags),
            _check_item("Has emoji polish", ContentState.has_emoji),
            _check_item("Has call-to-action", ContentState.has_cta),
            class_name="grid grid-cols-2 gap-2 mt-4",
        ),
        class_name="bg-slate-50 border border-slate-200 rounded-xl p-4",
    )


def _check_item(label: str, ok) -> rx.Component:
    return rx.el.div(
        rx.cond(
            ok,
            rx.icon("circle-check", class_name="h-3.5 w-3.5 text-emerald-600"),
            rx.icon("circle", class_name="h-3.5 w-3.5 text-slate-300"),
        ),
        rx.el.span(
            label,
            class_name=rx.cond(
                ok,
                "text-xs font-medium text-slate-700",
                "text-xs font-medium text-slate-400",
            ),
        ),
        class_name="flex items-center gap-1.5",
    )


def _draft_row(draft) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    draft["tone"],
                    class_name="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md",
                ),
                rx.el.span(
                    draft["created_at"],
                    class_name="text-xs text-slate-400 ml-2",
                ),
                class_name="flex items-center",
            ),
            rx.el.p(
                draft["body"],
                class_name="text-sm text-slate-700 mt-2 line-clamp-2",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("pencil", class_name="h-3.5 w-3.5"),
                "Load",
                on_click=lambda: ContentState.load_draft(draft["id"]),
                class_name="flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 rounded-md hover:bg-indigo-100 transition-colors",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                on_click=lambda: ContentState.delete_draft(draft["id"]),
                class_name="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors",
            ),
            class_name="flex items-center gap-1 shrink-0",
        ),
        class_name="flex items-start gap-3 p-3 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition-colors",
    )


def studio_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "AI Content Studio",
                    class_name="text-2xl font-bold text-slate-900",
                ),
                rx.el.p(
                    "Brief the AI, choose a tone, and ship on-brand content in seconds.",
                    class_name="text-sm text-slate-500 mt-1",
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("eraser", class_name="h-4 w-4"),
                    "Clear",
                    on_click=ContentState.clear_studio,
                    class_name="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors",
                ),
                rx.el.button(
                    rx.icon("save", class_name="h-4 w-4"),
                    "Save draft",
                    on_click=ContentState.save_draft,
                    class_name="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-start justify-between mb-6 gap-4 flex-wrap",
        ),
        rx.el.div(
            # LEFT: Brief + tone
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "clipboard-list",
                            class_name="h-4 w-4 text-indigo-600",
                        ),
                        rx.el.h3(
                            "Campaign brief",
                            class_name="font-semibold text-slate-900 text-sm",
                        ),
                        class_name="flex items-center gap-2 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Topic",
                            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                        ),
                        rx.el.input(
                            placeholder="e.g. Launching our new analytics feature",
                            default_value=ContentState.topic,
                            on_change=ContentState.set_topic.debounce(300),
                            class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder-slate-400",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Target audience",
                            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                        ),
                        rx.el.input(
                            placeholder="e.g. SaaS founders, indie hackers",
                            default_value=ContentState.audience,
                            on_change=ContentState.set_audience.debounce(300),
                            class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder-slate-400",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Keywords (comma-separated)",
                            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                        ),
                        rx.el.input(
                            placeholder="growth, automation, productivity",
                            default_value=ContentState.keywords,
                            on_change=ContentState.set_keywords.debounce(300),
                            class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder-slate-400",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Goal",
                            class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                        ),
                        rx.el.div(
                            rx.el.select(
                                rx.el.option("Awareness", value="Awareness"),
                                rx.el.option("Engagement", value="Engagement"),
                                rx.el.option(
                                    "Lead generation", value="Lead generation"
                                ),
                                rx.el.option("Launch", value="Launch"),
                                rx.el.option("Education", value="Education"),
                                value=ContentState.goal,
                                on_change=ContentState.set_goal,
                                class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                            ),
                            class_name="relative",
                        ),
                    ),
                    class_name="bg-white border border-slate-200 rounded-2xl p-5",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "palette", class_name="h-4 w-4 text-indigo-600"
                        ),
                        rx.el.h3(
                            "Tone",
                            class_name="font-semibold text-slate-900 text-sm",
                        ),
                        class_name="flex items-center gap-2 mb-3",
                    ),
                    rx.el.div(
                        rx.foreach(TONE_OPTIONS, _tone_chip),
                        class_name="flex flex-wrap gap-2",
                    ),
                    class_name="bg-white border border-slate-200 rounded-2xl p-5 mt-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("send", class_name="h-4 w-4 text-indigo-600"),
                        rx.el.h3(
                            "Platforms",
                            class_name="font-semibold text-slate-900 text-sm",
                        ),
                        class_name="flex items-center gap-2 mb-3",
                    ),
                    rx.el.div(
                        rx.foreach(PLATFORM_OPTIONS, _platform_chip),
                        class_name="flex flex-wrap gap-2",
                    ),
                    class_name="bg-white border border-slate-200 rounded-2xl p-5 mt-4",
                ),
                class_name="flex flex-col",
            ),
            # RIGHT: Editor
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "sparkles", class_name="h-4 w-4 text-indigo-600"
                            ),
                            rx.el.h3(
                                "Post editor",
                                class_name="font-semibold text-slate-900 text-sm",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.el.span(
                                ContentState.char_count.to_string() + " chars",
                                class_name="text-xs font-medium text-slate-500",
                            ),
                            rx.el.span("•", class_name="text-slate-300"),
                            rx.el.span(
                                ContentState.word_count.to_string() + " words",
                                class_name="text-xs font-medium text-slate-500",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        class_name="flex items-center justify-between mb-3",
                    ),
                    rx.el.textarea(
                        placeholder="Write your post here, or click 'Generate with AI' to draft from your brief...",
                        default_value=ContentState.post_body,
                        on_change=ContentState.set_post_body.debounce(300),
                        rows=10,
                        class_name="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900 placeholder-slate-400 resize-y leading-relaxed",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                ContentState.is_generating,
                                rx.icon(
                                    "loader-circle",
                                    class_name="h-4 w-4 animate-spin",
                                ),
                                rx.icon("sparkles", class_name="h-4 w-4"),
                            ),
                            "Generate with AI",
                            on_click=ContentState.generate_post,
                            disabled=ContentState.is_generating,
                            class_name="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 disabled:opacity-60 transition-colors",
                        ),
                        rx.el.button(
                            rx.icon("scissors", class_name="h-4 w-4"),
                            "Shorten",
                            on_click=ContentState.rewrite_shorter,
                            class_name="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                        ),
                        rx.el.button(
                            rx.icon("smile", class_name="h-4 w-4"),
                            "Polish",
                            on_click=ContentState.add_emoji_polish,
                            class_name="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                        ),
                        rx.el.button(
                            rx.icon("megaphone", class_name="h-4 w-4"),
                            "Add CTA",
                            on_click=ContentState.add_cta,
                            class_name="flex items-center gap-2 px-3 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 rounded-lg transition-colors",
                        ),
                        class_name="flex items-center gap-2 mt-3 flex-wrap",
                    ),
                    class_name="bg-white border border-slate-200 rounded-2xl p-5",
                ),
                rx.el.div(
                    _quality_bar(),
                    class_name="mt-4",
                ),
                _schedule_panel(),
                class_name="flex flex-col",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-5",
        ),
        # Drafts list
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("file-text", class_name="h-4 w-4 text-indigo-600"),
                    rx.el.h3(
                        "Saved drafts",
                        class_name="font-semibold text-slate-900 text-sm",
                    ),
                    rx.el.span(
                        ContentState.queue_count_draft.to_string(),
                        class_name="ml-1 px-2 py-0.5 text-xs font-semibold text-slate-600 bg-slate-100 rounded-md",
                    ),
                    class_name="flex items-center gap-2 mb-4",
                ),
                rx.cond(
                    ContentState.drafts.length() > 0,
                    rx.el.div(
                        rx.foreach(ContentState.drafts, _draft_row),
                        class_name="flex flex-col gap-2",
                    ),
                    rx.el.div(
                        rx.icon(
                            "inbox", class_name="h-8 w-8 text-slate-300 mx-auto"
                        ),
                        rx.el.p(
                            "No drafts yet",
                            class_name="text-sm font-medium text-slate-700 mt-2",
                        ),
                        rx.el.p(
                            "Generate a post and click Save draft to keep it here.",
                            class_name="text-xs text-slate-500 mt-1",
                        ),
                        class_name="text-center py-8",
                    ),
                ),
                class_name="bg-white border border-slate-200 rounded-2xl p-5",
            ),
            class_name="mt-5",
        ),
    )


def _schedule_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("calendar-clock", class_name="h-4 w-4 text-indigo-600"),
            rx.el.h3(
                "Schedule this post",
                class_name="font-semibold text-slate-900 text-sm",
            ),
            class_name="flex items-center gap-2 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Date",
                    class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                ),
                rx.el.input(
                    type="date",
                    default_value=ContentState.schedule_date,
                    on_change=ContentState.set_schedule_date,
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
                    default_value=ContentState.schedule_time,
                    on_change=ContentState.set_schedule_time,
                    class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-slate-900",
                ),
            ),
            class_name="grid grid-cols-2 gap-3 mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Account",
                    class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("@studio.main", value="@studio.main"),
                        rx.el.option(
                            "@studio.creator", value="@studio.creator"
                        ),
                        rx.el.option(
                            "@brand.official", value="@brand.official"
                        ),
                        rx.el.option("@founder.alex", value="@founder.alex"),
                        value=ContentState.schedule_account,
                        on_change=ContentState.set_schedule_account,
                        class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer focus:outline-none focus:border-indigo-300 text-slate-900",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Cadence",
                    class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("One-time", value="One-time"),
                        rx.el.option("Daily", value="Daily"),
                        rx.el.option("Weekly", value="Weekly"),
                        rx.el.option("Bi-weekly", value="Bi-weekly"),
                        rx.el.option("Monthly", value="Monthly"),
                        value=ContentState.schedule_cadence,
                        on_change=ContentState.set_schedule_cadence,
                        class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer focus:outline-none focus:border-indigo-300 text-slate-900",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                    ),
                    class_name="relative",
                ),
            ),
            class_name="grid grid-cols-2 gap-3 mb-3",
        ),
        rx.el.div(
            rx.el.label(
                "Preferred window",
                class_name="text-xs font-semibold text-slate-600 mb-1.5 block",
            ),
            rx.el.div(
                rx.el.select(
                    rx.el.option("Morning (8–11am)", value="Morning (8–11am)"),
                    rx.el.option(
                        "Midday (11am–1pm)", value="Midday (11am–1pm)"
                    ),
                    rx.el.option(
                        "Afternoon (1–5pm)", value="Afternoon (1–5pm)"
                    ),
                    rx.el.option("Evening (5–9pm)", value="Evening (5–9pm)"),
                    value=ContentState.schedule_window,
                    on_change=ContentState.set_schedule_window,
                    class_name="w-full px-3 py-2 pr-9 bg-white border border-slate-200 rounded-lg text-sm appearance-none cursor-pointer focus:outline-none focus:border-indigo-300 text-slate-900",
                ),
                rx.icon(
                    "chevron-down",
                    class_name="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none",
                ),
                class_name="relative",
            ),
            class_name="mb-4",
        ),
        rx.el.button(
            rx.icon("send-horizontal", class_name="h-4 w-4"),
            "Schedule post",
            on_click=ContentState.schedule_post,
            class_name="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
        ),
        class_name="bg-white border border-slate-200 rounded-2xl p-5 mt-4",
    )