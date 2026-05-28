# PostMeLater

PostMeLater is a Reflex-based personal AI content operating system. It helps a user generate social media posts with AI, save ideas and templates, schedule posts through Zernio, track publishing status, and review analytics in one workspace.

The app is designed for personal or small shared use. Each signed-in user can save their own Zernio API key and optional AI provider key, so users do not have to share one publishing workspace.

## What The App Does

- Google sign-in through Supabase Auth.
- Per-user Zernio API key storage.
- Social account connection through Zernio hosted OAuth links.
- AI content generation, shortening, CTA rewriting, and long-form repurposing.
- Draft saving and scheduling.
- Queue management for scheduled, posted, failed, and draft items.
- Automatic Zernio status sync using background polling.
- Content Lab for ideas, templates, campaigns, and brand voice.
- Analytics view powered by Zernio analytics where available.
- Supabase-backed persistence in deployment, with SQLite fallback for local development.

## Tech Stack

- Python
- Reflex `0.9.2`
- Tailwind via Reflex Tailwind plugin
- Supabase Auth for Google OAuth
- Supabase REST tables for persistent app data
- Zernio API for account connection, scheduling, post status, and analytics
- Gemini by default for AI generation, with support for OpenAI, Claude, OpenRouter, and custom OpenAI-compatible providers

## Project Structure

```text
PostMeLater/
  PostMeLater.py                 App entrypoint and route registration
  components/
    landing.py                   Public landing page
    docs.py                      Public docs page
    shell.py                     Authenticated app shell and navigation
    views.py                     Dashboard view
    studio.py                    AI Content Studio
    scheduling.py                Scheduling Center and queue
    accounts.py                  Social account connection UI
    analytics.py                 Zernio analytics UI
    planner.py                   Ideas and calendar planning UI
    content_lab.py               Brand voice, ideas, templates, campaigns
    settings.py                  Profile, integrations, Zernio, AI settings
    auth_callback.py             Auth callback page
  states/
    app_state.py                 Auth/session/app navigation state
    content_state.py             Main workspace, scheduling, AI, analytics state
  services/
    config.py                    Environment loading helpers
    supabase_auth.py             Supabase Google OAuth and app sessions
    store.py                     Supabase/SQLite persistence layer
    zernio.py                    Zernio REST client
    gemini.py                    AI provider clients and prompts
  database/
    migrations/
      supabase_postmelater.sql   Supabase table migration
```

## Runtime Architecture

The app has three main layers.

### 1. UI Components

Files in `PostMeLater/components` define Reflex components. They mostly render state from `AppState` and `ContentState`, and call event handlers on user actions.

Important screens:

- `landing.py`: public marketing/entry screen.
- `docs.py`: public setup guide.
- `shell.py`: authenticated layout, sidebar, top bar, and view switching.
- `views.py`: dashboard cards, upcoming posts, charts, recent activity.
- `studio.py`: AI post generation, drafting, and scheduling form.
- `scheduling.py`: calendar, queue, status badges, retry/edit/cancel actions.
- `accounts.py`: connect social accounts through Zernio.
- `settings.py`: profile, Zernio API key, AI provider settings.
- `analytics.py`: Zernio performance and analytics.
- `content_lab.py` and `planner.py`: ideas, templates, campaigns, brand workflow.

### 2. State Layer

`AppState` handles:

- Auth session cookie.
- OAuth verifier cookie.
- Current authenticated user.
- Active app view.
- Sign-in and sign-out flow.
- View switching.

`ContentState` handles:

- Drafts, posts, connected accounts, ideas, templates, campaigns, brand settings.
- Zernio account sync and post status sync.
- AI generation and rewrite events.
- Scheduling, retrying, editing, cancelling, and marking posts.
- Analytics loading.
- Computed dashboard values and chart data.

### 3. Service Layer

`services/config.py`

- Loads `.env` into `os.environ`.
- Exposes `get_setting()` and `app_timezone()`.

`services/supabase_auth.py`

- Builds Supabase Google OAuth URLs using PKCE.
- Exchanges callback codes for Supabase sessions.
- Stores app sessions in `.states/supabase_oauth.sqlite3`.
- Refreshes Supabase sessions when they are close to expiry.

`services/store.py`

- Stores app data.
- Uses Supabase REST when `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are configured.
- Falls back to local SQLite at `.states/postmelater.sqlite3` when Supabase persistence is not configured.

`services/zernio.py`

- Wraps Zernio endpoints for accounts, profiles, connection URLs, posts, retries, edits, deletes, and analytics.
- Supports `ZERNIO_API_KEY` and legacy `LATE_API_KEY`.
- Most app calls pass a per-user API key from Settings.

`services/gemini.py`

- Provides AI generation behind a single `generate_text()` function.
- Supports `gemini`, `openai`, `anthropic`, `openrouter`, and `custom`.
- Custom providers must be OpenAI-compatible chat completion APIs.

## Main Workflows

### Authentication Workflow

1. User clicks Sign in.
2. `AppState.open_signin()` creates a PKCE verifier and stores it in a short-lived cookie.
3. User is redirected to Supabase Google OAuth.
4. Supabase redirects back to `/auth/confirm`.
5. `AppState.confirm_auth()` exchanges the code for a Supabase session.
6. `supabase_auth.create_app_session()` creates an app session ID.
7. The app stores that session ID in the `pml_session` cookie.
8. `AppState.load_session()` loads the user profile on future page loads.

The app user ID comes from Supabase. `ContentState.init_seed()` reads that user ID and uses it as the owner ID for all stored data.

### Persistence Workflow

On startup, `ContentState.init_seed()` calls `store.init_db()`.

If Supabase persistence is configured:

- Data is written to tables prefixed with `pml_`.
- The backend uses `SUPABASE_SERVICE_ROLE_KEY`.
- The SQL migration is in `PostMeLater/database/migrations/supabase_postmelater.sql`.

If Supabase persistence is not configured:

- The app uses local SQLite in `.states/postmelater.sqlite3`.
- This is useful for local development.
- It is not reliable for deployed persistence because redeploys can remove local disk state.

### Zernio Integration Workflow

1. User signs in.
2. User opens Settings.
3. User saves their own Zernio API key and optional profile ID.
4. The key is stored per user in `pml_zernio_settings` or local SQLite fallback.
5. User opens Social Accounts and chooses a platform.
6. `ContentState.connect_account()` asks Zernio for a hosted connection URL.
7. User completes the social account OAuth flow on Zernio.
8. PostMeLater refreshes connected accounts using `zernio.list_accounts()`.

Connected accounts are cached locally per user so the UI can show account/platform choices quickly.

### Scheduling Workflow

1. User writes or generates a post in AI Content Studio.
2. User selects connected platforms and an account.
3. User selects schedule date/time.
4. `ContentState.schedule_post()` sends the post to Zernio using `zernio.create_post()`.
5. Zernio returns a remote post ID and status.
6. PostMeLater saves a local post row with:
   - local `id`
   - `zernio_post_id`
   - `scheduled_at`
   - `status`
   - selected platforms and account
7. Dashboard, Scheduling Center, Planner, and Analytics read from the shared local post list.

### Post Status Sync Workflow

Zernio is the source of truth for whether scheduled posts are eventually published or failed.

PostMeLater keeps local rows in sync through several paths:

- On app load, `ContentState.init_seed()` syncs accounts and statuses.
- On app load, `ContentState.poll_zernio_statuses()` starts a background poller.
- The poller checks Zernio every 45 seconds while the user is signed in.
- When opening Dashboard, Analytics, Planner, Scheduling Center, or Studio, `AppState.set_view()` triggers an immediate sync.
- The Scheduling Center still has a manual `Sync Zernio` button as a fallback.

Status mapping:

```text
Zernio published -> PostMeLater posted
Zernio failed    -> PostMeLater failed
Zernio partial   -> PostMeLater failed, with error detail
Zernio draft/scheduled/publishing/queued/pending -> PostMeLater scheduled
```

### AI Generation Workflow

The app default AI provider is Gemini through `GEMINI_API_KEY`.

Users can optionally save their own AI provider settings in Settings:

- Gemini
- OpenAI
- Claude/Anthropic
- OpenRouter
- Custom OpenAI-compatible endpoint

When a user saves their own AI key, `ContentState` passes that key to `gemini.generate_text()`. If no per-user key is saved, the app uses the environment key.

If generation fails, the Studio creates a local fallback draft so the user is not blocked.

### Analytics Workflow

The Analytics page uses Zernio APIs:

- `zernio.get_analytics()`
- `zernio.get_daily_metrics()`

Analytics are only as complete as the connected Zernio account data. New accounts may show empty analytics until Zernio has collected enough data.

## Environment Variables

Create a `.env` file in the repo root for local development. Do not commit real secrets.

```env
APP_BASE_URL=http://localhost:3000
APP_TIMEZONE=Africa/Lagos

SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=

ZERNIO_API_KEY=
ZERNIO_PROFILE_ID=
```

Required for Google sign-in:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `APP_BASE_URL`

Required for persistent deployed app data:

- `SUPABASE_SERVICE_ROLE_KEY`
- Supabase tables created from `PostMeLater/database/migrations/supabase_postmelater.sql`

Required for app-level Gemini fallback:

- `GEMINI_API_KEY`

Optional:

- `ZERNIO_API_KEY`: app-wide fallback only. Normal users should save their own Zernio key in Settings.
- `ZERNIO_PROFILE_ID`: optional fallback profile ID.
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`: app-wide fallback keys for those providers.

## Supabase Setup

1. Create a Supabase project.
2. Enable Google as an auth provider in Supabase Auth.
3. Configure Google OAuth in Google Cloud.
4. In Supabase Auth URL settings, add:

```text
Site URL: https://your-deployed-app-domain
Redirect URL: https://your-deployed-app-domain/auth/confirm
```

For local development, also allow:

```text
http://localhost:3000
http://localhost:3000/auth/confirm
```

5. Run the SQL in:

```text
PostMeLater/database/migrations/supabase_postmelater.sql
```

6. Add these backend environment variables:

```env
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
```

Important: `SUPABASE_SERVICE_ROLE_KEY` must stay server-side only. Do not expose it in frontend code or public repositories.

## Zernio Setup

Each user can bring their own Zernio API key.

User flow:

1. Create or log in to Zernio.
2. Copy the Zernio API key from onboarding or the Zernio API Keys dashboard.
3. Open PostMeLater Settings.
4. Paste the Zernio API key.
5. Save.
6. Open Social Accounts.
7. Connect the desired social accounts.

The current app stores the Zernio API key in the app database per signed-in user. Scheduling and account sync calls use that user's key.

## Local Development

Create and activate a virtual environment:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the app:

```powershell
reflex run
```

Default URLs:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

Compile/import sanity check:

```powershell
.\venv\Scripts\python.exe -m compileall PostMeLater
```

## Deployment Notes

For deployment, configure these as backend environment variables:

- `APP_BASE_URL`
- `APP_TIMEZONE`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GEMINI_API_KEY` or another app-level AI provider key

After deployment:

1. Update Supabase Auth URLs to the deployed domain.
2. Update Google OAuth authorized origins and redirect URLs.
3. Confirm `/auth/confirm` works.
4. Confirm Settings can save a Zernio API key.
5. Confirm Social Accounts can connect through Zernio.
6. Schedule a test post.
7. Confirm it appears in Zernio.
8. Confirm PostMeLater moves it from scheduled to posted after Zernio publishes it.

## Data Ownership

All workspace data is keyed by `user_id`.

Main entities:

- drafts
- posts
- connected accounts
- Zernio settings
- AI settings
- ideas
- content templates
- campaigns
- brand settings

The user ID comes from Supabase Auth. This is why Google sign-in must work before per-user data will behave correctly.

## Security Notes

- Do not commit `.env`.
- Do not expose `SUPABASE_SERVICE_ROLE_KEY` to the browser.
- User Zernio API keys and AI keys are stored server-side in the configured persistence backend.
- Supabase RLS is enabled in the migration, but the backend uses the service role key. Access control is enforced by always querying and writing with the current app `user_id`.
- Consider encrypting user-saved API keys before production use with untrusted users.

## Troubleshooting

### User signs in but sees no saved data after redeploy

The app is probably using local SQLite instead of Supabase persistence. Add `SUPABASE_SERVICE_ROLE_KEY`, run the SQL migration, and redeploy.

### Google OAuth returns a bad OAuth state error

Check that:

- `APP_BASE_URL` matches the deployed domain.
- Supabase Auth redirect URLs include `/auth/confirm`.
- Google Cloud authorized redirect URI is the Supabase callback URL:

```text
https://YOUR_SUPABASE_PROJECT.supabase.co/auth/v1/callback
```

### Zernio says an API key is required

The signed-in user needs to save their own Zernio API key in Settings before connecting accounts or scheduling posts.

### A post published on social media but still says scheduled

PostMeLater syncs Zernio status automatically every 45 seconds while signed in. It also syncs when opening Dashboard, Analytics, Planner, Scheduling Center, or Studio. The manual `Sync Zernio` button is available as a fallback.

### AI generation falls back to a local draft

The configured AI provider key is missing, invalid, rate-limited, or temporarily unavailable. Add a user AI key in Settings or configure an app-level provider key in the environment.

## Development Guidelines

- Keep UI style consistent with the existing Reflex/Tailwind components.
- Put backend integrations in `services/`.
- Put cross-screen workflow state in `ContentState`.
- Keep per-user behavior keyed by Supabase `user_id`.
- Do not add new storage tables without updating the Supabase migration and `store.py`.
- Prefer Zernio as the source of truth for publishing state.
- Keep `Sync Zernio` as a fallback even with background polling.

