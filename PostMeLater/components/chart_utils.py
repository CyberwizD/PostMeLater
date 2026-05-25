import reflex as rx


TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "borderColor": "#E2E8F0",
        "borderRadius": "0.75rem",
        "boxShadow": "0px 8px 24px rgba(15, 23, 42, 0.08)",
        "fontFamily": "Inter, sans-serif",
        "fontSize": "0.8125rem",
        "lineHeight": "1.25rem",
        "fontWeight": "500",
        "minWidth": "9rem",
        "padding": "0.5rem 0.75rem",
        "position": "relative",
    },
    "item_style": {
        "display": "flex",
        "paddingBottom": "2px",
        "paddingTop": "2px",
        "color": "#0f172a",
    },
    "label_style": {
        "color": "#64748b",
        "fontWeight": "600",
        "fontSize": "0.75rem",
        "marginBottom": "0.25rem",
    },
    "separator": "",
    "cursor": {"strokeWidth": 1, "fill": "#F1F5F9"},
}


CHART_TOOLTIP_CLASS = (
    "[&_.recharts-tooltip-item-unit]:text-slate-500 "
    "[&_.recharts-tooltip-item-value]:!text-slate-900 "
    "[&_.recharts-tooltip-item-value]:!font-semibold "
    "[&_.recharts-tooltip-item-value]:mr-[0.2rem] "
    "[&_.recharts-tooltip-item]:flex "
    "[&_.recharts-tooltip-item]:items-center "
    "[&_.recharts-tooltip-item]:before:content-[''] "
    "[&_.recharts-tooltip-item]:before:size-2.5 "
    "[&_.recharts-tooltip-item]:before:rounded-[3px] "
    "[&_.recharts-tooltip-item]:before:shrink-0 "
    "[&_.recharts-tooltip-item]:before:!bg-[currentColor] "
    "[&_.recharts-tooltip-item]:before:mr-2 "
    "[&_.recharts-tooltip-item-name]:text-slate-600 "
    "[&_.recharts-tooltip-item-list]:flex "
    "[&_.recharts-tooltip-item-list]:flex-col "
    "[&_.recharts-tooltip-wrapper]:z-[2]"
)