"""PostgreSQL connection + forward-only migrations.

Production: Neon via Vercel (DATABASE_URL, pooled -> no server-side prepared
statements). Rows support both row["name"] and row[0]. Statements use `?`
placeholders, translated to the driver's `%s`.
"""

import os
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import psycopg

MIGRATIONS = Path(__file__).resolve().parents[1] / "database" / "migrations"
MIGRATION_LOCK = 7_262_025  # arbitrary app-wide advisory-lock key


# Variables, in order of preference. DATABASE_URL is the explicit choice. POSTGRES_URL / POSTGRES_URL_NON_POOLING are what
# Vercel's Supabase integration creates (pooled first: it is IPv4 and works from serverless functions).
URL_VARS = ("DATABASE_URL", "POSTGRES_URL", "POSTGRES_URL_NON_POOLING")
_DROP_PARAMS = {"supa", "pgbouncer"}  # added by Supabase/Vercel; libpq/psycopg reject them as unknown options


def clean_url(url: str) -> str:
    """Remove query options psycopg cannot parse. Never logs or returns anything but the URL itself."""
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k.lower() not in _DROP_PARAMS]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))


def database_url(environ=None) -> str:
    """First usable postgres URL from URL_VARS, cleaned; "" if none."""
    env = os.environ if environ is None else environ
    for name in URL_VARS:
        v = (env.get(name) or "").strip()
        if v.startswith(("postgres://", "postgresql://")):
            return clean_url(v)
    return ""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Row(dict):
    """Dict row that also allows positional access."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def _row_factory(cursor):
    names = [c.name for c in cursor.description or []]
    return lambda values: Row(zip(names, values))


class Connection:
    """Thin wrapper: autocommit, `?` placeholders, name/index rows."""

    def __init__(self, raw):
        self.raw = raw

    def execute(self, sql, params=()):
        return self.raw.execute(_translate(sql), params or None)

    def transaction(self):
        return self.raw.transaction()

    def close(self):
        self.raw.close()


def _translate(sql: str) -> str:
    if "?" not in sql:
        return sql
    return re.sub(r"\?", "%s", sql)


def connect(url: str | None = None, schema: str | None = None) -> Connection:
    url = url or database_url()
    if not url.startswith(("postgres://", "postgresql://")):
        raise RuntimeError("no postgres:// URL: set DATABASE_URL (or connect the Vercel Supabase integration)")
    raw = psycopg.connect(url, autocommit=True, row_factory=_row_factory, prepare_threshold=None)
    if schema:
        raw.execute(f'SET search_path TO "{schema}"')
    return Connection(raw)


def money(value) -> float:
    return float(value) if isinstance(value, Decimal) else float(value or 0)


def migrate(conn: Connection) -> list[str]:
    """Apply pending migrations; safe under concurrent cold starts (advisory lock)."""
    applied = []
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(%s)" % MIGRATION_LOCK)
        conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
        done = {r["name"] for r in conn.execute("SELECT name FROM schema_migrations")}
        for f in sorted(MIGRATIONS.glob("*.sql")):
            if f.name in done:
                continue
            conn.raw.execute(f.read_text())  # no params: multi-statement allowed
            conn.execute("INSERT INTO schema_migrations(name, applied_at) VALUES (?, ?)", (f.name, now()))
            applied.append(f.name)
    return applied
