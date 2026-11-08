"""Read-only foundation status: what is migrated, what row-level security is doing, how many rows exist per table."""

from core.content.access import content_session
from core.content.meta import ROLE, TABLES


def foundation(conn) -> dict:
    migrations = [r["name"] for r in conn.execute("SELECT name FROM schema_migrations ORDER BY name")]
    flags = {r["relname"]: (r["relrowsecurity"], r["relforcerowsecurity"]) for r in conn.execute(
        "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class "
        "WHERE relnamespace = current_schema()::regnamespace AND relname = ANY(?)", (list(TABLES),))}
    tables = []
    with content_session(conn):
        who = conn.execute("SELECT current_user AS u").fetchone()["u"]
        for t in TABLES:  # names come from a constant tuple, never from the request
            rows = conn.execute(f"SELECT count(*) AS c FROM {t}").fetchone()["c"]
            on, forced = flags.get(t, (False, False))
            tables.append({"name": t, "rows": rows, "rls_enabled": on, "rls_forced": forced})
    return {"migrations": migrations, "content_migrated": "002_content.sql" in migrations, "queried_as": who, "role": ROLE,
            "rls_ok": all(t["rls_enabled"] and t["rls_forced"] for t in tables), "tables": tables}
