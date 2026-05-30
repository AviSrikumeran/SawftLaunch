"""Identity storage.

Uses Supabase (Postgres) when SUPABASE_URL + SUPABASE_KEY are set — this is the
production path: short, permanent /u/<slug> links that survive restarts.
Falls back to local JSON files when those env vars are absent, so local dev and
first-run work with zero setup.

Supabase table (run once in the SQL editor):

    create table if not exists identities (
        slug text primary key,
        data jsonb not null,
        created_at timestamptz default now()
    );

Use the service_role key (server-side secret) so the server can read/write
without row-level-security policies.
"""

import json
import os
import re
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TABLE = "identities"

_supabase = None  # lazily created client


def _cfg():
    # Read at call time (not import time) so a .env loaded later is respected.
    return os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")


def _use_supabase():
    url, key = _cfg()
    return bool(url and key)


def _client():
    global _supabase
    if _supabase is None:
        from supabase import create_client
        url, key = _cfg()
        _supabase = create_client(url, key)
    return _supabase


def _slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "launch"


def save_identity(identity):
    """Persist a render-ready identity and return its unique slug."""
    slug = f"{_slugify(identity['name'])}-{secrets.token_hex(3)}"
    if _use_supabase():
        _client().table(TABLE).insert({"slug": slug, "data": identity}).execute()
    else:
        DATA_DIR.mkdir(exist_ok=True)
        (DATA_DIR / f"{slug}.json").write_text(json.dumps(identity))
    return slug


def load_identity(slug):
    """Return the stored identity dict for a slug, or None if not found."""
    if _use_supabase():
        res = _client().table(TABLE).select("data").eq("slug", slug).limit(1).execute()
        rows = res.data or []
        return rows[0]["data"] if rows else None
    path = DATA_DIR / f"{slug}.json"
    return json.loads(path.read_text()) if path.exists() else None
