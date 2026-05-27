import reflex as rx

from PostMeLater.states.app_state import AppState
from PostMeLater.states.content_state import ContentState


def _calendar_post(post) -> rx.Component:
    return rx.el.div(
        rx.el.p(post["scheduled_time"], class_name="text-[11px] font-semibold text-indigo-700"),
        rx.el.p(post["body"], class_name="text-xs text-slate-700 line-clamp-2 mt-1"),
        class_name="p-2 rounded-lg bg-indigo-50 border border-indigo-100",
    )


def _calendar_day(day) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(day["weekday"], class_name="text-[11px] font-semibold uppercase text-slate-500"),
            rx.el.span(
                day["label"],
                class_name=rx.cond(
                    day["is_today"],
                    "text-sm font-bold text-indigo-700",
                    "text-sm font-bold text-slate-900",
                ),
            ),
            class_name=rx.cond(
                day["is_today"],
                "flex items-center justify-between border-b border-indigo-200 pb-2",
                "flex items-center justify-between border-b border-slate-100 pb-2",
            ),
        ),
        rx.cond(
            day["posts"].length() > 0,
            rx.el.div(rx.foreach(day["posts"], _calendar_post), class_name="space-y-2 mt-3"),
            rx.el.div(
                rx.el.span("-", class_name="text-slate-300"),
                class_name="h-20 flex items-center justify-center",
            ),
        ),
        class_name=rx.cond(
            day["is_today"],
            "min-h-44 bg-white border border-indigo-200 rounded-xl p-3",
            "min-h-44 bg-white border border-slate-200 rounded-xl p-3",
        ),
    )


def _idea_card(idea) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(idea["title"], class_name="text-sm font-semibold text-slate-900"),
                rx.el.p(idea["notes"], class_name="text-xs text-slate-500 mt-1 line-clamp-2"),
                rx.cond(
                    idea["source"] != "",
                    rx.el.span(
                        idea["source"],
                        class_name="inline-flex mt-3 px-2 py-1 rounded-md bg-slate-100 text-xs font-semibold text-slate-600",
                    ),
                    rx.fragment(),
                ),
                class_name="min-w-0",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: ContentState.delete_idea(idea["id"]),
                class_name="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50",
            ),
            class_name="flex items-start justify-between gap-3",
        ),
        rx.el.div(
            rx.el.button(
                "Draft",
                on_click=lambda: ContentState.load_idea_to_studio(idea["id"]),
                class_name="px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100",
            ),
            rx.el.button(
                "Plan",
                on_click=lambda: ContentState.update_idea_status(idea["id"], "planned"),
                class_name="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200",
            ),
            rx.el.button(
                "Archive",
                on_click=lambda: ContentState.update_idea_status(idea["id"], "archived"),
                class_name="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-500 hover:bg-slate-100",
            ),
            class_name="flex items-center gap-2 mt-4 flex-wrap",
        ),
        class_name="p-4 bg-white border border-slate-200 rounded-xl",
    )


def _idea_column(title: str, count, items) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="text-sm font-semibold text-slate-900"),
            rx.el.span(
                count.to_string(),
                class_name="text-xs font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded-md",
            ),
            class_name="flex items-center justify-between mb-3",
        ),
        rx.cond(
            items.length() > 0,
            rx.el.div(rx.foreach(items, _idea_card), class_name="space-y-3"),
            rx.el.div(
                rx.icon("inbox", class_name="h-8 w-8 text-slate-300 mx-auto"),
                rx.el.p("Nothing here yet", class_name="text-xs font-semibold text-slate-500 mt-2"),
                class_name="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50",
            ),
        ),
        class_name="min-w-0",
    )


def planner_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Planner", class_name="text-2xl font-bold text-slate-900"),
                rx.el.p(
                    "Capture ideas and see how they fit around your content calendar.",
                    class_name="text-sm text-slate-500 mt-1",
                ),
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4"),
                "New post",
                on_click=lambda: AppState.set_view("studio"),
                class_name="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
            ),
            class_name="flex items-start justify-between gap-4 flex-wrap mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2("Content calendar", class_name="font-semibold text-slate-900"),
                rx.el.p("This week across scheduled, posted, and failed posts.", class_name="text-sm text-slate-500 mt-0.5"),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.foreach(ContentState.week_calendar, _calendar_day),
                class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-7 gap-3",
            ),
            class_name="bg-white border border-slate-200 rounded-2xl p-5 mb-5",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2("Ideas inbox", class_name="font-semibold text-slate-900"),
                rx.el.p(
                    "Save raw ideas before they become drafts, campaigns, or scheduled posts.",
                    class_name="text-sm text-slate-500 mt-0.5",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Idea title",
                    value=ContentState.idea_title,
                    on_change=ContentState.set_idea_title,
                    class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400",
                ),
                rx.el.input(
                    placeholder="Source or keyword",
                    value=ContentState.idea_source,
                    on_change=ContentState.set_idea_source,
                    class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400",
                ),
                rx.el.textarea(
                    placeholder="Notes, hook, link, or angle",
                    value=ContentState.idea_notes,
                    on_change=ContentState.set_idea_notes,
                    class_name="w-full min-h-24 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 md:col-span-2",
                ),
                rx.el.button(
                    rx.icon("save", class_name="h-4 w-4"),
                    "Save idea",
                    on_click=ContentState.save_idea,
                    class_name="md:col-span-2 w-fit flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6 p-4 bg-slate-50 border border-slate-200 rounded-xl",
            ),
            rx.el.div(
                _idea_column("Inbox", ContentState.inbox_ideas.length(), ContentState.inbox_ideas),
                _idea_column("Planned", ContentState.planned_ideas.length(), ContentState.planned_ideas),
                _idea_column("Archived", ContentState.archived_ideas.length(), ContentState.archived_ideas),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-4",
            ),
            class_name="bg-white border border-slate-200 rounded-2xl p-5",
        ),
    )
