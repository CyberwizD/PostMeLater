import reflex as rx

from PostMeLater.states.content_state import ContentState


def _field(label: str, placeholder: str, value, on_change) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="text-xs font-semibold text-slate-600 mb-1.5 block"),
        rx.el.input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            class_name="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100",
        ),
    )


def _template_row(template) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(template["name"], class_name="text-sm font-semibold text-slate-900"),
            rx.el.p(template["prompt"], class_name="text-xs text-slate-500 mt-1 line-clamp-2"),
            class_name="min-w-0 flex-1",
        ),
        rx.el.button(
            rx.icon("send", class_name="h-4 w-4"),
            on_click=lambda: ContentState.use_template(template["id"]),
            class_name="p-2 rounded-lg text-indigo-600 hover:bg-indigo-50",
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="h-4 w-4"),
            on_click=lambda: ContentState.delete_template(template["id"]),
            class_name="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50",
        ),
        class_name="flex items-start gap-2 p-3 bg-white border border-slate-200 rounded-xl",
    )


def _campaign_row(campaign) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(campaign["name"], class_name="text-sm font-semibold text-slate-900"),
            rx.el.p(campaign["goal"], class_name="text-xs text-slate-500 mt-1 line-clamp-2"),
            class_name="min-w-0 flex-1",
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="h-4 w-4"),
            on_click=lambda: ContentState.delete_campaign(campaign["id"]),
            class_name="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50",
        ),
        class_name="flex items-start gap-2 p-3 bg-white border border-slate-200 rounded-xl",
    )


def _section(title: str, icon: str, *children: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-indigo-600"),
            rx.el.h2(title, class_name="font-semibold text-slate-900"),
            class_name="flex items-center gap-2 mb-4",
        ),
        *children,
        class_name="bg-white border border-slate-200 rounded-2xl p-5",
    )


def content_lab_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Content Lab", class_name="text-2xl font-bold text-slate-900"),
            rx.el.p(
                "Shape your brand voice, templates, campaigns, and long-form repurposing workflow.",
                class_name="text-sm text-slate-500 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            _section(
                "Brand voice",
                "audio-lines",
                rx.el.div(
                    _field("Voice", "e.g. clear, practical, founder-led", ContentState.brand_voice, ContentState.set_brand_voice),
                    _field("Audience", "e.g. creators, founders, operators", ContentState.brand_audience, ContentState.set_brand_audience),
                    _field("Keywords", "e.g. AI, consistency, content systems", ContentState.brand_keywords, ContentState.set_brand_keywords),
                    class_name="grid grid-cols-1 gap-3",
                ),
                rx.el.button(
                    rx.icon("save", class_name="h-4 w-4"),
                    "Save brand profile",
                    on_click=ContentState.save_brand_profile,
                    class_name="mt-4 flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                ),
            ),
            _section(
                "Content campaigns",
                "target",
                rx.el.div(
                    _field("Campaign name", "Launch week, weekly insights, build in public", ContentState.campaign_name, ContentState.set_campaign_name),
                    _field("Goal", "What should this campaign accomplish?", ContentState.campaign_goal, ContentState.set_campaign_goal),
                    rx.el.button(
                        rx.icon("plus", class_name="h-4 w-4"),
                        "Save campaign",
                        on_click=ContentState.save_campaign,
                        class_name="w-fit flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                    ),
                    class_name="grid grid-cols-1 gap-3 mb-4",
                ),
                rx.cond(
                    ContentState.campaigns.length() > 0,
                    rx.el.div(rx.foreach(ContentState.campaigns, _campaign_row), class_name="space-y-2"),
                    rx.el.p("No campaigns saved yet.", class_name="text-sm text-slate-500"),
                ),
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5",
        ),
        rx.el.div(
            _section(
                "Saved templates",
                "bookmark",
                rx.el.div(
                    _field("Template name", "e.g. Product lesson, weekly recap", ContentState.template_name, ContentState.set_template_name),
                    rx.el.textarea(
                        placeholder="Template prompt or reusable structure",
                        value=ContentState.template_prompt,
                        on_change=ContentState.set_template_prompt,
                        class_name="w-full min-h-28 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400",
                    ),
                    rx.el.button(
                        rx.icon("save", class_name="h-4 w-4"),
                        "Save template",
                        on_click=ContentState.save_template,
                        class_name="w-fit flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                    ),
                    class_name="grid grid-cols-1 gap-3 mb-4",
                ),
                rx.cond(
                    ContentState.templates.length() > 0,
                    rx.el.div(rx.foreach(ContentState.templates, _template_row), class_name="space-y-2"),
                    rx.el.p("No templates saved yet.", class_name="text-sm text-slate-500"),
                ),
            ),
            _section(
                "Repurpose long text",
                "scan-text",
                rx.el.textarea(
                    placeholder="Paste a blog post, transcript, newsletter, or raw notes",
                    value=ContentState.repurpose_source,
                    on_change=ContentState.set_repurpose_source,
                    class_name="w-full min-h-40 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("sparkles", class_name="h-4 w-4"),
                        rx.cond(ContentState.is_repurposing, "Repurposing...", "Generate posts"),
                        on_click=ContentState.repurpose_long_text,
                        class_name="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("send", class_name="h-4 w-4"),
                        "Use in Studio",
                        on_click=ContentState.use_repurpose_in_studio,
                        class_name="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 transition-colors",
                    ),
                    class_name="flex items-center gap-2 mt-3 flex-wrap",
                ),
                rx.cond(
                    ContentState.repurpose_result != "",
                    rx.el.div(
                        rx.el.p("Generated posts", class_name="text-xs font-semibold text-slate-500 mb-2"),
                        rx.el.pre(
                            ContentState.repurpose_result,
                            class_name="whitespace-pre-wrap text-sm text-slate-800 leading-relaxed bg-slate-50 border border-slate-200 rounded-xl p-4",
                        ),
                        class_name="mt-4",
                    ),
                    rx.fragment(),
                ),
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-5",
        ),
    )
