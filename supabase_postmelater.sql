-- PostMeLater persistent workspace tables.
-- Run this once in Supabase SQL Editor.
-- These tables are accessed by the deployed Reflex backend with
-- SUPABASE_SERVICE_ROLE_KEY, so keep that key server-side only.

create table if not exists public.pml_drafts (
    user_id text not null,
    id text not null,
    body text not null,
    topic text not null default '',
    audience text not null default '',
    keywords text not null default '',
    tone text not null default 'Professional',
    platforms_json text not null default '[]',
    created_at text not null,
    primary key (user_id, id)
);

create table if not exists public.pml_posts (
    user_id text not null,
    id text not null,
    zernio_post_id text not null default '',
    body text not null,
    platforms_json text not null default '[]',
    account text not null default '',
    account_id text not null default '',
    scheduled_at text not null default '',
    scheduled_date text not null default '',
    scheduled_time text not null default '',
    cadence text not null default 'One-time',
    status text not null default 'scheduled',
    tone text not null default 'Professional',
    engagement integer not null default 0,
    error text not null default '',
    created_at text not null,
    updated_at text not null,
    primary key (user_id, id)
);

create table if not exists public.pml_accounts (
    user_id text not null,
    id text not null,
    platform text not null,
    username text not null default '',
    display_name text not null default '',
    profile_id text not null default '',
    raw_json text not null default '{}',
    updated_at text not null,
    primary key (user_id, id)
);

create table if not exists public.pml_zernio_settings (
    user_id text primary key,
    api_key text not null default '',
    profile_id text not null default '',
    updated_at text not null
);

create table if not exists public.pml_ai_settings (
    user_id text primary key,
    provider text not null default 'gemini',
    api_key text not null default '',
    model text not null default '',
    base_url text not null default '',
    updated_at text not null
);

create table if not exists public.pml_ideas (
    user_id text not null,
    id text not null,
    title text not null default '',
    notes text not null default '',
    status text not null default 'inbox',
    source text not null default '',
    created_at text not null,
    updated_at text not null,
    primary key (user_id, id)
);

create table if not exists public.pml_content_templates (
    user_id text not null,
    id text not null,
    name text not null default '',
    prompt text not null default '',
    created_at text not null,
    updated_at text not null,
    primary key (user_id, id)
);

create table if not exists public.pml_campaigns (
    user_id text not null,
    id text not null,
    name text not null default '',
    goal text not null default '',
    created_at text not null,
    updated_at text not null,
    primary key (user_id, id)
);

create table if not exists public.pml_brand_settings (
    user_id text primary key,
    voice text not null default '',
    audience text not null default '',
    keywords text not null default '',
    updated_at text not null
);

alter table public.pml_drafts enable row level security;
alter table public.pml_posts enable row level security;
alter table public.pml_accounts enable row level security;
alter table public.pml_zernio_settings enable row level security;
alter table public.pml_ai_settings enable row level security;
alter table public.pml_ideas enable row level security;
alter table public.pml_content_templates enable row level security;
alter table public.pml_campaigns enable row level security;
alter table public.pml_brand_settings enable row level security;
