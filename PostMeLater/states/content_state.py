import reflex as rx
import uuid
import random
import json
from datetime import datetime, timedelta
from typing import Any, TypedDict
import logging

from PostMeLater.services import gemini, store, zernio
from PostMeLater.services.config import get_setting


class Draft(TypedDict):
    id: str
    body: str
    topic: str
    audience: str
    keywords: str
    tone: str
    platforms: list[str]
    created_at: str


class ScheduledPost(TypedDict):
    id: str
    zernio_post_id: str
    body: str
    platforms: list[str]
    account: str
    account_id: str
    scheduled_at: str
    scheduled_date: str
    scheduled_time: str
    cadence: str
    status: str
    tone: str
    engagement: int
    error: str


class ConnectedAccount(TypedDict):
    id: str
    platform: str
    username: str
    display_name: str
    profile_id: str


class AccountOption(TypedDict):
    value: str
    label: str


class ActivityEvent(TypedDict):
    id: str
    icon: str
    title: str
    detail: str
    time: str
    accent: str


class AccountHealth(TypedDict):
    handle: str
    platform: str
    icon: str
    posts_week: int
    engagement: float
    status: str
    accent: str


class DayColumn(TypedDict):
    label: str
    weekday: str
    date_iso: str
    is_today: bool
    posts: list[ScheduledPost]


class ChartPoint(TypedDict):
    day: str
    posts: int
    engagement: int


class PlatformPoint(TypedDict):
    platform: str
    posts: int


PLATFORM_OPTIONS = [
    "Twitter / X",
    "LinkedIn",
    "Instagram",
    "Facebook",
    "Threads",
]
CONNECT_PLATFORM_OPTIONS = [
    "Twitter / X",
    "LinkedIn",
    "Instagram",
    "Facebook",
    "Threads",
    "TikTok",
    "YouTube",
    "Pinterest",
    "Reddit",
]
API_PLATFORM_LABELS = {
    "twitter": "Twitter / X",
    "x": "Twitter / X",
    "linkedin": "LinkedIn",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "threads": "Threads",
    "tiktok": "TikTok",
    "youtube": "YouTube",
    "pinterest": "Pinterest",
    "reddit": "Reddit",
}
TONE_OPTIONS = [
    "Professional",
    "Casual",
    "Witty",
    "Inspirational",
    "Urgent",
    "Friendly",
    "Bold",
    "Educational",
]
ACCOUNT_OPTIONS = [
    "Default account",
]
CADENCE_OPTIONS = ["One-time", "Daily", "Weekly", "Bi-weekly", "Monthly"]
WINDOW_OPTIONS = [
    "Morning (8–11am)",
    "Midday (11am–1pm)",
    "Afternoon (1–5pm)",
    "Evening (5–9pm)",
]


def _platform_label(platform: str) -> str:
    if platform in CONNECT_PLATFORM_OPTIONS:
        return platform
    normalized = platform.strip().lower().replace("_", "").replace("-", "")
    normalized = normalized.replace(" ", "").replace("/", "")
    return API_PLATFORM_LABELS.get(normalized, platform.strip().title())


def _hook(tone: str, topic: str) -> str:
    topic = topic.strip() or "what we're building"
    hooks = {
        "Professional": f"A quick note on {topic}:",
        "Casual": f"Real talk — {topic} 👇",
        "Witty": f"Plot twist: {topic}.",
        "Inspirational": f"Here's what {topic} taught me 💡",
        "Urgent": f"Important update on {topic} 🚨",
        "Friendly": f"Hey friends! Quick thought on {topic} ✨",
        "Bold": f"Stop scrolling. {topic.capitalize()} matters.",
        "Educational": f"Today's lesson: {topic} 🧠",
    }
    return hooks.get(tone, f"On {topic}:")


def _body(tone: str, audience: str, keywords: str) -> str:
    aud = audience.strip() or "creators and operators"
    kw = [k.strip() for k in keywords.split(",") if k.strip()]
    kw_line = ""
    if kw:
        kw_line = f" Built for {aud}, with a focus on {', '.join(kw[:3])}."
    bodies = {
        "Professional": f"After working with {aud} this quarter, three patterns stood out — clarity beats cleverness, cadence compounds, and feedback loops are everything.{kw_line}",
        "Casual": f"Spent the week chatting with {aud} and honestly? The consistent ones win. Show up, ship small, repeat.{kw_line}",
        "Witty": f"Most {aud} optimize for output. The smart ones optimize for consistency. Outputs come and go — habits compound.{kw_line}",
        "Inspirational": f"Every {aud} I admire shares one trait: they kept going when it stopped being exciting. That's the moment most people quit.{kw_line}",
        "Urgent": f"If you're a {aud}, the window for compounding is now. Three months of consistency beats a year of bursts.{kw_line}",
        "Friendly": f"Talking to {aud} this week reminded me — the small reps matter way more than the big launches. Tiny wins, daily.{kw_line}",
        "Bold": f"{aud.capitalize()} who win don't have more time. They have ruthless priorities and zero tolerance for noise.{kw_line}",
        "Educational": f"Three things every {aud} should know: 1) Cadence > intensity, 2) Distribution > content, 3) Feedback > opinions.{kw_line}",
    }
    return bodies.get(
        tone, f"Here's what we learned working with {aud}.{kw_line}"
    )


def _cta(tone: str) -> str:
    ctas = {
        "Professional": "Curious how others approach this — what's worked for you?",
        "Casual": "What's been working for you lately? Drop it below 👇",
        "Witty": "Convince me I'm wrong in the replies.",
        "Inspirational": "Tag someone who needs this today. 💛",
        "Urgent": "Don't sleep on this. Save the post for later.",
        "Friendly": "Would love to hear your take! 💬",
        "Bold": "Disagree? I'd love to hear why.",
        "Educational": "Save this for later — and follow for more breakdowns.",
    }
    return ctas.get(tone, "What do you think?")


def _hashtags(keywords: str, platforms: list[str]) -> str:
    if not platforms:
        return ""
    needs_tags = any(
        p in ("Twitter / X", "Instagram", "Threads") for p in platforms
    )
    if not needs_tags:
        return ""
    base = ["#creators", "#building", "#growth"]
    extra = [
        f"#{k.strip().lower().replace(' ', '')}"
        for k in keywords.split(",")
        if k.strip()
    ][:3]
    return " ".join(extra + base[: 3 - len(extra)])


SEED_BODIES = [
    "Launching our new analytics dashboard today 🚀\n\nReal-time metrics, smart filters, and one-click exports — built for teams that move fast.\n\nWho wants early access?",
    "5 lessons from scaling our team from 5 to 50:\n\n1. Hire slow, fire fast\n2. Document everything\n3. Async > sync\n4. Trust > control\n5. Customers > opinions\n\nWhat would you add? 💬",
    "The hardest part of building isn't shipping. It's deciding what NOT to ship. 🧠\n\nFocus is the unfair advantage.",
    "Quiet reminder: cadence beats intensity. ✨\n\nShow up small, every day. The compounding is real.",
    "We just hit $1M ARR 🎉\n\nThree years. Zero funding. A lot of replies, late nights, and ruthless prioritization.\n\nThank you for being part of it 💛",
    "If you're a SaaS founder feeling stuck on growth, run this audit:\n\n→ Onboarding (first 5 minutes)\n→ Activation (first key action)\n→ Retention (week 2 return)\n\nFix in that order.",
    "Hot take: most 'productivity tools' are just procrastination dressed up.\n\nThe best tool is the one you actually open. 🔥",
    "Three underrated skills for indie hackers:\n\n• Writing clearly\n• Asking better questions\n• Cutting features\n\nBoring? Yes. Compounding? Absolutely.",
    "We rewrote our onboarding flow. Activation jumped from 34% → 58% in two weeks.\n\nThe lever? Removing steps, not adding.",
    "What's working for our content this quarter:\n\n→ Replies > impressions\n→ Threads > one-liners\n→ Stories > stats\n\nDouble down on what gets DMs.",
    "Friendly reminder for builders:\n\nDistribution is the moat. Build the audience first, the product fits faster.",
    "If your product needs a tutorial, you have a UX problem — not an education problem. 💡",
    "Spent the morning talking to 5 customers. Three said the same thing.\n\nThat's not a coincidence — that's a roadmap. 🧭",
    "Stop optimizing your morning routine. Start optimizing your decision filters. 🚨",
    "Building in public for 18 months taught me one thing:\n\nThe people who follow you for the wins won't stick around for the work. The ones who do — protect them.",
]

SEED_TONES = [
    "Professional",
    "Bold",
    "Inspirational",
    "Educational",
    "Casual",
    "Witty",
    "Friendly",
    "Urgent",
]

SEED_PLATFORM_SETS = [
    ["Twitter / X", "LinkedIn"],
    ["LinkedIn"],
    ["Twitter / X"],
    ["Instagram", "Threads"],
    ["Twitter / X", "LinkedIn", "Threads"],
    ["LinkedIn", "Facebook"],
]


def _seed_scheduled_posts() -> list[ScheduledPost]:
    rng = random.Random(42)
    posts: list[ScheduledPost] = []
    now = datetime.now().replace(second=0, microsecond=0)
    today_9 = now.replace(hour=9, minute=0)
    plan = [
        # (offset_days, hour, minute, status, account, engagement)
        (-12, 9, 30, "posted", "@studio.main", 412),
        (-10, 14, 0, "posted", "@brand.official", 298),
        (-8, 8, 15, "posted", "@studio.creator", 180),
        (-7, 17, 0, "posted", "@founder.alex", 524),
        (-6, 11, 30, "posted", "@studio.main", 376),
        (-5, 9, 0, "posted", "@brand.official", 245),
        (-5, 18, 0, "failed", "@studio.creator", 0),
        (-4, 10, 0, "posted", "@founder.alex", 612),
        (-3, 13, 30, "posted", "@studio.main", 489),
        (-2, 9, 0, "posted", "@brand.official", 333),
        (-2, 16, 0, "posted", "@founder.alex", 421),
        (-1, 11, 0, "posted", "@studio.main", 388),
        (-1, 19, 0, "failed", "@studio.creator", 0),
        (0, 8, 30, "posted", "@founder.alex", 156),
        (0, 14, 0, "scheduled", "@studio.main", 0),
        (0, 18, 30, "scheduled", "@brand.official", 0),
        (1, 9, 0, "scheduled", "@studio.main", 0),
        (1, 13, 30, "scheduled", "@studio.creator", 0),
        (1, 17, 0, "scheduled", "@founder.alex", 0),
        (2, 10, 0, "scheduled", "@brand.official", 0),
        (2, 15, 0, "scheduled", "@studio.main", 0),
        (3, 9, 30, "scheduled", "@founder.alex", 0),
        (3, 14, 0, "scheduled", "@studio.creator", 0),
        (4, 11, 0, "scheduled", "@studio.main", 0),
        (4, 18, 0, "scheduled", "@brand.official", 0),
        (5, 10, 30, "scheduled", "@founder.alex", 0),
        (6, 13, 0, "scheduled", "@studio.main", 0),
        (8, 9, 0, "scheduled", "@brand.official", 0),
        (10, 14, 0, "scheduled", "@founder.alex", 0),
    ]
    for i, (off, h, m, status, account, eng) in enumerate(plan):
        dt = today_9 + timedelta(days=off)
        dt = dt.replace(hour=h, minute=m)
        body = SEED_BODIES[i % len(SEED_BODIES)]
        platforms = SEED_PLATFORM_SETS[i % len(SEED_PLATFORM_SETS)]
        tone = SEED_TONES[i % len(SEED_TONES)]
        posts.append(
            ScheduledPost(
                id=str(uuid.uuid4()),
                zernio_post_id="",
                body=body,
                platforms=list(platforms),
                account=account,
                account_id="",
                scheduled_at=dt.strftime("%Y-%m-%dT%H:%M:00"),
                scheduled_date=dt.strftime("%b %d, %Y"),
                scheduled_time=dt.strftime("%I:%M %p"),
                cadence="One-time" if i % 4 != 0 else "Weekly",
                status=status,
                tone=tone,
                engagement=eng,
                error="",
            )
        )
    return posts


def _seed_drafts() -> list[Draft]:
    return [
        Draft(
            id=str(uuid.uuid4()),
            body="Three principles for building a brand that lasts:\n\n1. Be useful before you're loud\n2. Show your work, not your wins\n3. Care louder than your competitors\n\nThe rest compounds.",
            topic="brand building",
            audience="founders",
            keywords="brand, growth, longevity",
            tone="Inspirational",
            platforms=["Twitter / X", "LinkedIn"],
            created_at=(datetime.now() - timedelta(hours=3)).strftime(
                "%b %d, %Y · %I:%M %p"
            ),
        ),
        Draft(
            id=str(uuid.uuid4()),
            body="What we shipped this week 📦\n\n→ New keyboard shortcuts\n→ Faster search (3x)\n→ Dark mode polish\n→ A long-requested API endpoint\n\nThanks for the feedback — keep it coming.",
            topic="weekly changelog",
            audience="customers",
            keywords="product, changelog, ship",
            tone="Friendly",
            platforms=["Twitter / X"],
            created_at=(datetime.now() - timedelta(days=1)).strftime(
                "%b %d, %Y · %I:%M %p"
            ),
        ),
        Draft(
            id=str(uuid.uuid4()),
            body="Hiring lesson: the best people don't apply to job posts. They get pulled in by the work you do in public. ✨\n\nShip loud, hire from the audience.",
            topic="hiring",
            audience="founders, operators",
            keywords="hiring, audience, building in public",
            tone="Bold",
            platforms=["LinkedIn", "Twitter / X"],
            created_at=(datetime.now() - timedelta(days=2)).strftime(
                "%b %d, %Y · %I:%M %p"
            ),
        ),
    ]


class ContentState(rx.State):
    user_id: str = "default"
    topic: str = ""
    audience: str = ""
    keywords: str = ""
    goal: str = "Awareness"
    tone: str = "Professional"
    selected_platforms: list[str] = []
    post_body: str = ""
    is_generating: bool = False

    drafts: list[Draft] = []
    scheduled_posts: list[ScheduledPost] = []
    accounts: list[ConnectedAccount] = []
    seeded: bool = False
    api_notice: str = ""
    zernio_api_key_input: str = ""
    zernio_profile_id_input: str = ""
    zernio_key_saved: bool = False

    schedule_date: str = ""
    schedule_time: str = "09:00"
    schedule_account: str = ""
    schedule_window: str = "Morning (8–11am)"
    schedule_cadence: str = "One-time"
    schedule_interval_days: int = 1

    connect_platform: str = "Twitter / X"
    queue_filter: str = "all"
    queue_account_filter: str = "all"

    edit_modal_open: bool = False
    edit_post_id: str = ""
    edit_date: str = ""
    edit_time: str = ""
    edit_account: str = ""

    def _owner_id(self) -> str:
        return self.user_id or "default"

    def _load_zernio_settings(self):
        settings = store.get_zernio_settings(self._owner_id())
        self.zernio_key_saved = bool(settings.get("api_key"))
        self.zernio_profile_id_input = settings.get("profile_id", "")

    def _zernio_settings(self) -> dict[str, str]:
        return store.get_zernio_settings(self._owner_id())

    def _zernio_api_key(self) -> str:
        return self._zernio_settings().get("api_key", "")

    def _zernio_profile_id(self) -> str:
        return self._zernio_settings().get("profile_id", "")

    def _reload_from_store(self):
        self.drafts = store.list_drafts(self._owner_id())
        self.scheduled_posts = store.list_posts(self._owner_id())
        self.accounts = store.list_accounts(self._owner_id())
        self._sync_selected_platforms()
        if not self.schedule_date:
            self.schedule_date = datetime.now().strftime("%Y-%m-%d")
        if not self.schedule_account and self.accounts:
            self.schedule_account = self.accounts[0]["id"]

    def _connected_platform_labels(self) -> list[str]:
        labels: list[str] = []
        for account in self.accounts:
            label = _platform_label(account.get("platform", ""))
            if label and label not in labels:
                labels.append(label)
        ordered = [p for p in CONNECT_PLATFORM_OPTIONS if p in labels]
        ordered.extend([p for p in labels if p not in ordered])
        return ordered

    def _sync_selected_platforms(self):
        available = self._connected_platform_labels()
        self.selected_platforms = [
            platform
            for platform in self.selected_platforms
            if platform in available
        ]
        if not self.selected_platforms and available:
            self.selected_platforms = list(available)

    def _sync_accounts_from_zernio(self):
        api_key = self._zernio_api_key()
        if not api_key:
            self.accounts = []
            store.save_accounts([], self._owner_id())
            self._sync_selected_platforms()
            self.api_notice = "Add your Zernio API key in Settings."
            return
        try:
            accounts = zernio.list_accounts(api_key_override=api_key)
            store.save_accounts(accounts, self._owner_id())
            self.accounts = store.list_accounts(self._owner_id())
            self._sync_selected_platforms()
            if not self.schedule_account and self.accounts:
                self.schedule_account = self.accounts[0]["id"]
            if accounts:
                self.api_notice = ""
            else:
                self.api_notice = "No connected Zernio accounts yet."
        except Exception:
            logging.exception("Could not sync Zernio accounts")
            self.api_notice = "Could not sync Zernio accounts."

    @rx.event
    def set_connect_platform(self, platform: str):
        self.connect_platform = platform

    @rx.event
    def set_zernio_api_key_input(self, value: str):
        self.zernio_api_key_input = value

    @rx.event
    def set_zernio_profile_id_input(self, value: str):
        self.zernio_profile_id_input = value

    @rx.event
    def save_zernio_settings(self):
        existing = self._zernio_settings()
        api_key = self.zernio_api_key_input.strip() or existing.get("api_key", "")
        if not api_key:
            return rx.toast("Paste your Zernio API key first.")
        store.save_zernio_settings(
            self._owner_id(), api_key, self.zernio_profile_id_input
        )
        self.zernio_api_key_input = ""
        self._load_zernio_settings()
        self._sync_accounts_from_zernio()
        return rx.toast("Zernio settings saved")

    @rx.event
    def refresh_accounts(self):
        self._sync_accounts_from_zernio()
        if self.accounts:
            return rx.toast("Connected accounts refreshed")
        return rx.toast("No connected accounts found")

    @rx.event
    def connect_account(self):
        api_key = self._zernio_api_key()
        if not api_key:
            return rx.toast("Add your Zernio API key before connecting accounts.")
        redirect_url = get_setting(
            "APP_BASE_URL",
            "SITE_URL",
            "REFLEX_PUBLIC_URL",
            default="http://localhost:3000",
        ).rstrip("/")
        try:
            auth_url = zernio.get_connect_url(
                self.connect_platform,
                redirect_url,
                api_key_override=api_key,
                profile_id=self._zernio_profile_id(),
            )
        except zernio.ZernioError as exc:
            return rx.toast(str(exc))
        return rx.call_script(f"window.location.assign({json.dumps(auth_url)})")

    def _account_label(self, account_id: str) -> str:
        for account in self.accounts:
            if account["id"] == account_id:
                name = (
                    account.get("username")
                    or account.get("display_name")
                    or account["id"]
                )
                return f"{name} ({account['platform']})"
        return account_id or "Default account"

    def _targets_for_selected_platforms(self) -> tuple[list[dict[str, str]], list[str]]:
        targets: list[dict[str, str]] = []
        missing: list[str] = []
        preferred = next(
            (a for a in self.accounts if a["id"] == self.schedule_account),
            None,
        )
        for platform_label in self.selected_platforms:
            platform = zernio.platform_api_name(platform_label)
            match = None
            if preferred and preferred["platform"] == platform:
                match = preferred
            if match is None:
                match = next(
                    (a for a in self.accounts if a["platform"] == platform),
                    None,
                )
            if match is None:
                missing.append(platform_label)
                continue
            targets.append({"platform": platform, "accountId": match["id"]})
        return targets, missing

    def _save_and_reload_post(self, post: ScheduledPost):
        store.save_post(post, self._owner_id())
        self._reload_from_store()

    @rx.var
    def account_options(self) -> list[AccountOption]:
        if not self.accounts:
            return [AccountOption(value="", label="No connected accounts")]
        return [
            AccountOption(
                value=account["id"],
                label=self._account_label(account["id"]),
            )
            for account in self.accounts
        ]

    @rx.var
    def connected_platform_options(self) -> list[str]:
        return self._connected_platform_labels()

    @rx.var
    def zernio_status_label(self) -> str:
        return "Configured" if self.zernio_key_saved else "Not configured"

    @rx.var
    def zernio_status_detail(self) -> str:
        if self.zernio_key_saved:
            return "Your saved Zernio API key is used for this workspace."
        return "Add your own Zernio API key to connect and schedule accounts."

    @rx.var
    def char_count(self) -> int:
        return len(self.post_body)

    @rx.var
    def word_count(self) -> int:
        return len(self.post_body.split()) if self.post_body.strip() else 0

    @rx.var
    def has_hashtags(self) -> bool:
        return "#" in self.post_body

    @rx.var
    def has_emoji(self) -> bool:
        return any(ord(c) > 8000 for c in self.post_body)

    @rx.var
    def has_cta(self) -> bool:
        triggers = [
            "?",
            "comment",
            "share",
            "follow",
            "save",
            "tag",
            "reply",
            "let me know",
            "what do you",
            "drop",
        ]
        low = self.post_body.lower()
        return any(t in low for t in triggers)

    @rx.var
    def quality_score(self) -> int:
        score = 0
        if 80 <= self.char_count <= 280:
            score += 30
        elif self.char_count > 0:
            score += 15
        if self.has_hashtags:
            score += 15
        if self.has_emoji:
            score += 15
        if self.has_cta:
            score += 25
        if self.word_count >= 12:
            score += 15
        return min(score, 100)

    @rx.var
    def quality_label(self) -> str:
        s = self.quality_score
        if s >= 80:
            return "Excellent"
        if s >= 55:
            return "Good"
        if s >= 25:
            return "Needs work"
        return "Empty"

    @rx.var
    def can_schedule(self) -> bool:
        return (
            len(self.post_body.strip()) > 0
            and len(self.selected_platforms) > 0
            and len(self.schedule_date) > 0
        )

    @rx.var
    def filtered_queue(self) -> list[ScheduledPost]:
        items = self.scheduled_posts
        if self.queue_filter != "all":
            items = [p for p in items if p["status"] == self.queue_filter]
        if self.queue_account_filter != "all":
            items = [
                p
                for p in items
                if p.get("account_id", "") == self.queue_account_filter
                or p["account"] == self.queue_account_filter
            ]
        return sorted(items, key=lambda p: p["scheduled_at"])

    @rx.var
    def queue_count_scheduled(self) -> int:
        return sum(
            1 for p in self.scheduled_posts if p["status"] == "scheduled"
        )

    @rx.var
    def queue_count_posted(self) -> int:
        return sum(1 for p in self.scheduled_posts if p["status"] == "posted")

    @rx.var
    def queue_count_failed(self) -> int:
        return sum(1 for p in self.scheduled_posts if p["status"] == "failed")

    @rx.var
    def queue_count_draft(self) -> int:
        return len(self.drafts)

    @rx.var
    def upcoming_week(self) -> list[ScheduledPost]:
        now = datetime.now()
        cutoff = now + timedelta(days=7)
        result = []
        for p in self.scheduled_posts:
            if p["status"] != "scheduled":
                continue
            try:
                dt = datetime.fromisoformat(p["scheduled_at"])
                if now <= dt <= cutoff:
                    result.append(p)
            except Exception:
                logging.exception("Unexpected error")
                continue
        return sorted(result, key=lambda p: p["scheduled_at"])[:6]

    @rx.event
    def set_topic(self, v: str):
        self.topic = v

    @rx.event
    def set_audience(self, v: str):
        self.audience = v

    @rx.event
    def set_keywords(self, v: str):
        self.keywords = v

    @rx.event
    def set_goal(self, v: str):
        self.goal = v

    @rx.event
    def set_tone(self, v: str):
        self.tone = v

    @rx.event
    def set_post_body(self, v: str):
        self.post_body = v

    @rx.event
    def toggle_platform(self, platform: str):
        if platform not in self._connected_platform_labels():
            return rx.toast("Connect this platform before selecting it.")
        if platform in self.selected_platforms:
            self.selected_platforms = [
                p for p in self.selected_platforms if p != platform
            ]
        else:
            self.selected_platforms = self.selected_platforms + [platform]

    @rx.event
    def generate_post(self):
        self.is_generating = True
        yield
        try:
            prompt = gemini.build_post_prompt(
                topic=self.topic,
                audience=self.audience,
                keywords=self.keywords,
                goal=self.goal,
                tone=self.tone,
                platforms=self.selected_platforms,
            )
            self.post_body = gemini.generate_text(prompt)
        except Exception:
            logging.exception("Gemini generation failed")
            hook = _hook(self.tone, self.topic)
            body = _body(self.tone, self.audience, self.keywords)
            cta = _cta(self.tone)
            tags = _hashtags(self.keywords, self.selected_platforms)
            parts = [hook, "", body, "", cta]
            if tags:
                parts.extend(["", tags])
            self.post_body = "\n".join(parts).strip()
            self.is_generating = False
            return rx.toast("Gemini failed, so I used a local draft fallback.")
        self.is_generating = False

    @rx.event
    def rewrite_shorter(self):
        if not self.post_body.strip():
            return
        self.is_generating = True
        yield
        try:
            prompt = gemini.build_rewrite_prompt(
                self.post_body,
                "Rewrite this social post to be shorter, sharper, and ready to publish. Keep the meaning and preserve useful hashtags.",
            )
            self.post_body = gemini.generate_text(prompt)
        except Exception:
            logging.exception("Gemini shorten failed")
            sentences = [
                s.strip()
                for s in self.post_body.replace("\n", " ").split(".")
                if s.strip()
            ]
            if len(sentences) > 2:
                sentences = sentences[:2]
            self.post_body = ". ".join(sentences) + "."
            self.is_generating = False
            return rx.toast("Gemini failed, so I shortened it locally.")
        self.is_generating = False

    @rx.event
    def add_emoji_polish(self):
        if not self.post_body.strip():
            return
        emojis = ["✨", "🚀", "💡", "🔥", "💛"]
        e = random.choice(emojis)
        if not self.has_emoji:
            self.post_body = f"{self.post_body} {e}"

    @rx.event
    def add_cta(self):
        if self.has_cta:
            return
        if not self.post_body.strip():
            return
        try:
            prompt = gemini.build_rewrite_prompt(
                self.post_body,
                f"Add one natural call to action in a {self.tone.lower()} tone. Return only the finished post.",
            )
            self.post_body = gemini.generate_text(prompt)
        except Exception:
            logging.exception("Gemini CTA failed")
            cta = _cta(self.tone)
            self.post_body = f"{self.post_body}\n\n{cta}".strip()
            return rx.toast("Gemini failed, so I added a local CTA.")

    @rx.event
    def clear_studio(self):
        self.post_body = ""
        self.topic = ""
        self.audience = ""
        self.keywords = ""

    @rx.event
    def save_draft(self):
        if not self.post_body.strip():
            return rx.toast("Write or generate a post first.")
        draft: Draft = {
            "id": str(uuid.uuid4()),
            "body": self.post_body,
            "topic": self.topic,
            "audience": self.audience,
            "keywords": self.keywords,
            "tone": self.tone,
            "platforms": list(self.selected_platforms),
            "created_at": datetime.now().strftime("%b %d, %Y · %I:%M %p"),
        }
        store.save_draft(draft, self._owner_id())
        self._reload_from_store()
        return rx.toast("Draft saved")

    @rx.event
    def load_draft(self, draft_id: str):
        for d in self.drafts:
            if d["id"] == draft_id:
                self.post_body = d["body"]
                self.topic = d["topic"]
                self.audience = d["audience"]
                self.keywords = d["keywords"]
                self.tone = d["tone"]
                self.selected_platforms = list(d["platforms"])
                self._sync_selected_platforms()
                return rx.toast("Draft loaded into editor")
        return None

    @rx.event
    def delete_draft(self, draft_id: str):
        store.delete_draft(draft_id, self._owner_id())
        self._reload_from_store()

    @rx.event
    def set_schedule_date(self, v: str):
        self.schedule_date = v

    @rx.event
    def set_schedule_time(self, v: str):
        self.schedule_time = v

    @rx.event
    def set_schedule_account(self, v: str):
        self.schedule_account = v

    @rx.event
    def set_schedule_window(self, v: str):
        self.schedule_window = v

    @rx.event
    def set_schedule_cadence(self, v: str):
        self.schedule_cadence = v

    @rx.event
    def set_schedule_interval_days(self, v: str):
        try:
            self.schedule_interval_days = max(1, int(v))
        except Exception:
            logging.exception("Unexpected error")
            self.schedule_interval_days = 1

    def _make_post(
        self,
        body: str,
        date_str: str,
        time_str: str,
        zernio_post_id: str = "",
        status: str = "scheduled",
        error: str = "",
    ) -> ScheduledPost:
        scheduled_at = f"{date_str}T{time_str}:00"
        try:
            dt = datetime.fromisoformat(scheduled_at)
            display_date = dt.strftime("%b %d, %Y")
            display_time = dt.strftime("%I:%M %p")
        except Exception:
            logging.exception("Unexpected error")
            display_date = date_str
            display_time = time_str
        account_id = self.schedule_account or (
            self.accounts[0]["id"] if self.accounts else ""
        )
        return ScheduledPost(
            id=str(uuid.uuid4()),
            zernio_post_id=zernio_post_id,
            body=body,
            platforms=list(self.selected_platforms),
            account=self._account_label(account_id),
            account_id=account_id,
            scheduled_at=scheduled_at,
            scheduled_date=display_date,
            scheduled_time=display_time,
            cadence=self.schedule_cadence,
            status=status,
            tone=self.tone,
            engagement=0,
            error=error,
        )

    @rx.event
    def schedule_post(self):
        if not self.post_body.strip():
            return rx.toast("Write or generate a post first.")
        if not self.selected_platforms:
            return rx.toast("Pick at least one platform.")
        if not self.schedule_date:
            return rx.toast("Pick a date to schedule.")
        targets, missing = self._targets_for_selected_platforms()
        if missing:
            return rx.toast(
                f"Connect an account for: {', '.join(missing)}"
            )
        if not targets:
            return rx.toast("Connect a Zernio account before scheduling.")
        body = self.post_body
        new_posts: list[ScheduledPost] = []
        try:
            base_dt = datetime.fromisoformat(
                f"{self.schedule_date}T{self.schedule_time}:00"
            )
        except Exception:
            logging.exception("Unexpected error")
            return rx.toast("Invalid date or time.")
        cadence_map = {
            "One-time": [0],
            "Daily": [0, 1, 2, 3, 4],
            "Weekly": [0, 7, 14, 21],
            "Bi-weekly": [0, 14, 28],
            "Monthly": [0, 30, 60],
        }
        offsets = cadence_map.get(self.schedule_cadence, [0])
        for off in offsets:
            dt = base_dt + timedelta(days=off)
            zernio_post_id = ""
            status = "scheduled"
            error = ""
            try:
                api_key = self._zernio_api_key()
                if api_key:
                    response = zernio.create_post(
                        content=body,
                        scheduled_for=dt.isoformat(),
                        platforms=targets,
                        api_key_override=api_key,
                    )
                    zernio_post_id = str(
                        response.get("_id")
                        or response.get("id")
                        or response.get("postId")
                        or ""
                    )
            except Exception as exc:
                logging.exception("Zernio schedule failed")
                status = "failed"
                error = str(exc)
            post = self._make_post(
                body,
                dt.strftime("%Y-%m-%d"),
                dt.strftime("%H:%M"),
                zernio_post_id=zernio_post_id,
                status=status,
                error=error,
            )
            store.save_post(post, self._owner_id())
            new_posts.append(post)
        self._reload_from_store()
        self.post_body = ""
        failed = sum(1 for post in new_posts if post["status"] == "failed")
        if failed:
            return rx.toast(
                f"{failed} post(s) could not be scheduled in Zernio. Check the queue."
            )
        return rx.toast(
            f"Scheduled {len(new_posts)} post(s) to {self._account_label(self.schedule_account)}"
        )

    @rx.event
    def cancel_post(self, post_id: str):
        post = next((p for p in self.scheduled_posts if p["id"] == post_id), None)
        if post is None:
            return
        zernio_post_id = post.get("zernio_post_id", "")
        if zernio_post_id:
            try:
                zernio.delete_post(
                    zernio_post_id, api_key_override=self._zernio_api_key()
                )
            except Exception:
                logging.exception("Zernio delete failed")
                return rx.toast("Could not delete this post in Zernio.")
        store.delete_post(post_id, self._owner_id())
        self._reload_from_store()
        return rx.toast("Post removed")

    @rx.event
    def retry_post(self, post_id: str):
        updated = False
        for post in self.scheduled_posts:
            if post["id"] != post_id:
                continue
            try:
                if post.get("zernio_post_id", ""):
                    zernio.retry_post(
                        post["zernio_post_id"],
                        api_key_override=self._zernio_api_key(),
                    )
                store.save_post(
                    {
                        **post,
                        "status": "scheduled",
                        "error": "",
                    },
                    self._owner_id(),
                )
                updated = True
            except Exception:
                logging.exception("Zernio retry failed")
                return rx.toast("Could not retry this post in Zernio.")
        if updated:
            self._reload_from_store()
            return rx.toast("Post retry queued")

    @rx.event
    def mark_posted(self, post_id: str):
        for post in self.scheduled_posts:
            if post["id"] == post_id:
                store.save_post(
                    {**post, "status": "posted", "error": ""}, self._owner_id()
                )
                self._reload_from_store()
                return

    @rx.event
    def mark_failed(self, post_id: str):
        for post in self.scheduled_posts:
            if post["id"] == post_id:
                store.save_post({**post, "status": "failed"}, self._owner_id())
                self._reload_from_store()
                return

    @rx.event
    def set_queue_filter(self, v: str):
        self.queue_filter = v

    @rx.event
    def set_queue_account_filter(self, v: str):
        self.queue_account_filter = v

    @rx.event
    async def init_seed(self):
        from PostMeLater.states.app_state import AppState

        app_state = await self.get_state(AppState)
        next_user_id = app_state.user_id or app_state.user_email or "default"
        if self.seeded and self.user_id == next_user_id:
            return
        self.user_id = next_user_id
        store.init_db()
        self._load_zernio_settings()
        self._reload_from_store()
        self._sync_accounts_from_zernio()
        self._reload_from_store()
        self.seeded = True

    @rx.event
    def open_edit(self, post_id: str):
        for p in self.scheduled_posts:
            if p["id"] == post_id:
                try:
                    dt = datetime.fromisoformat(p["scheduled_at"])
                    self.edit_date = dt.strftime("%Y-%m-%d")
                    self.edit_time = dt.strftime("%H:%M")
                except Exception:
                    logging.exception("Edit parse error")
                    self.edit_date = ""
                    self.edit_time = "09:00"
                self.edit_account = p.get("account_id", "") or p["account"]
                self.edit_post_id = post_id
                self.edit_modal_open = True
                return

    @rx.event
    def close_edit(self):
        self.edit_modal_open = False
        self.edit_post_id = ""

    @rx.event
    def set_edit_date(self, v: str):
        self.edit_date = v

    @rx.event
    def set_edit_time(self, v: str):
        self.edit_time = v

    @rx.event
    def set_edit_account(self, v: str):
        self.edit_account = v

    @rx.event
    def save_edit(self):
        if not self.edit_post_id:
            return rx.toast("No post selected.")
        if not self.edit_date or not self.edit_time:
            return rx.toast("Pick a valid date and time.")
        try:
            dt = datetime.fromisoformat(f"{self.edit_date}T{self.edit_time}:00")
        except Exception:
            logging.exception("Bad datetime in edit")
            return rx.toast("Invalid date or time.")
        post = next(
            (p for p in self.scheduled_posts if p["id"] == self.edit_post_id),
            None,
        )
        if post is None:
            return rx.toast("Post not found.")
        if post.get("zernio_post_id", ""):
            try:
                zernio.update_post(
                    post_id=post["zernio_post_id"],
                    scheduled_for=dt.isoformat(),
                    api_key_override=self._zernio_api_key(),
                )
            except Exception:
                logging.exception("Zernio edit failed")
                return rx.toast("Could not update this post in Zernio.")
        store.save_post(
            {
                **post,
                "scheduled_at": dt.strftime("%Y-%m-%dT%H:%M:00"),
                "scheduled_date": dt.strftime("%b %d, %Y"),
                "scheduled_time": dt.strftime("%I:%M %p"),
                "account": self._account_label(self.edit_account),
                "account_id": self.edit_account,
                "status": "scheduled",
                "error": "",
            },
            self._owner_id(),
        )
        self._reload_from_store()
        self.edit_modal_open = False
        self.edit_post_id = ""
        return rx.toast("Schedule updated")

    @rx.var
    def week_calendar(self) -> list[DayColumn]:
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Start on Monday
        start = today - timedelta(days=today.weekday())
        cols: list[DayColumn] = []
        for i in range(7):
            d = start + timedelta(days=i)
            day_posts: list[ScheduledPost] = []
            for p in self.scheduled_posts:
                try:
                    dt = datetime.fromisoformat(p["scheduled_at"])
                    if dt.date() == d.date():
                        day_posts.append(p)
                except Exception:
                    logging.exception("calendar parse error")
                    continue
            day_posts = sorted(day_posts, key=lambda p: p["scheduled_at"])
            cols.append(
                DayColumn(
                    label=d.strftime("%b %d"),
                    weekday=d.strftime("%a"),
                    date_iso=d.strftime("%Y-%m-%d"),
                    is_today=(d.date() == today.date()),
                    posts=day_posts,
                )
            )
        return cols

    @rx.var
    def weekly_chart(self) -> list[ChartPoint]:
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start = today - timedelta(days=6)
        points: list[ChartPoint] = []
        for i in range(7):
            d = start + timedelta(days=i)
            posts = 0
            engagement = 0
            for p in self.scheduled_posts:
                try:
                    dt = datetime.fromisoformat(p["scheduled_at"])
                    if dt.date() == d.date():
                        posts += 1
                        engagement += int(p.get("engagement", 0) or 0)
                except Exception:
                    logging.exception("chart parse error")
                    continue
            points.append(
                ChartPoint(
                    day=d.strftime("%a"), posts=posts, engagement=engagement
                )
            )
        return points

    @rx.var
    def platform_chart(self) -> list[PlatformPoint]:
        counts: dict[str, int] = {p: 0 for p in PLATFORM_OPTIONS}
        for post in self.scheduled_posts:
            for pl in post["platforms"]:
                if pl in counts:
                    counts[pl] += 1
        return [
            PlatformPoint(platform=k.replace(" / X", ""), posts=v)
            for k, v in counts.items()
        ]

    @rx.var
    def total_engagement(self) -> int:
        return sum(
            int(p.get("engagement", 0) or 0) for p in self.scheduled_posts
        )

    @rx.var
    def avg_engagement(self) -> float:
        posted = [p for p in self.scheduled_posts if p["status"] == "posted"]
        if not posted:
            return 0.0
        total = sum(int(p.get("engagement", 0) or 0) for p in posted)
        return round(total / len(posted), 1)

    @rx.var
    def engagement_rate(self) -> float:
        # synthetic rate based on engagement / 5000
        if self.queue_count_posted == 0:
            return 0.0
        return round(min(self.avg_engagement / 50.0, 99.9), 1)

    @rx.var
    def recent_activity(self) -> list[ActivityEvent]:
        events: list[ActivityEvent] = []
        sorted_posts = sorted(
            self.scheduled_posts, key=lambda p: p["scheduled_at"], reverse=True
        )
        for p in sorted_posts[:8]:
            if p["status"] == "posted":
                events.append(
                    ActivityEvent(
                        id=p["id"],
                        icon="circle-check",
                        title=f"Posted to {p['account']}",
                        detail=p["body"].split("\n")[0][:80],
                        time=f"{p['scheduled_date']} · {p['scheduled_time']}",
                        accent="emerald",
                    )
                )
            elif p["status"] == "failed":
                events.append(
                    ActivityEvent(
                        id=p["id"],
                        icon="triangle-alert",
                        title=f"Delivery failed for {p['account']}",
                        detail=p["body"].split("\n")[0][:80],
                        time=f"{p['scheduled_date']} · {p['scheduled_time']}",
                        accent="red",
                    )
                )
            else:
                events.append(
                    ActivityEvent(
                        id=p["id"],
                        icon="clock",
                        title=f"Scheduled to {p['account']}",
                        detail=p["body"].split("\n")[0][:80],
                        time=f"{p['scheduled_date']} · {p['scheduled_time']}",
                        accent="indigo",
                    )
                )
        return events

    @rx.var
    def account_health(self) -> list[AccountHealth]:
        accounts = [
            (
                self._account_label(account["id"]),
                account["platform"].title(),
                {
                    "twitter": "twitter",
                    "linkedin": "linkedin",
                    "instagram": "instagram",
                    "facebook": "facebook",
                    "threads": "at-sign",
                }.get(account["platform"], "at-sign"),
            )
            for account in self.accounts
        ]
        if not accounts:
            accounts = [("No connected accounts", "Zernio", "at-sign")]
        result: list[AccountHealth] = []
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        for handle, platform, icon in accounts:
            posts_week = 0
            eng = 0
            posted_count = 0
            failed_count = 0
            for p in self.scheduled_posts:
                if p["account"] != handle:
                    continue
                try:
                    dt = datetime.fromisoformat(p["scheduled_at"])
                    if week_ago <= dt <= today and p["status"] == "posted":
                        posts_week += 1
                        eng += int(p.get("engagement", 0) or 0)
                        posted_count += 1
                    if p["status"] == "failed":
                        failed_count += 1
                except Exception:
                    logging.exception("acct health parse")
                    continue
            avg = round(eng / posted_count, 1) if posted_count else 0.0
            if failed_count > 0:
                status = "Needs attention"
                accent = "red"
            elif posts_week == 0:
                status = "Idle"
                accent = "slate"
            elif avg >= 350:
                status = "Excellent"
                accent = "emerald"
            else:
                status = "Healthy"
                accent = "indigo"
            result.append(
                AccountHealth(
                    handle=handle,
                    platform=platform,
                    icon=icon,
                    posts_week=posts_week,
                    engagement=avg,
                    status=status,
                    accent=accent,
                )
            )
        return result
