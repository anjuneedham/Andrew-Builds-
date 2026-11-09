"""P1 slice 1: series and episodes. Pure functions over a connection that is ALREADY inside content_session().
Validation errors raise Invalid (400); unknown ids raise NotFound (404); rule/uniqueness/dependency conflicts raise Conflict (409).
Messages are written here and are safe to show; driver text never leaves this module."""

import re
from datetime import date

import psycopg

from core.audit import audit
from core.content import access
from core.content.meta import ENUMS

ACTOR = "owner"
STATUSES = ENUMS[("episodes", "status")]
CODE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$")
PATH_RE = re.compile(r"^production/[A-Za-z0-9._/-]+$")

# Moving forward one stage, back one stage, or to ARCHIVED from anywhere; ARCHIVED can only be restored to IDEA.
# READY_TO_RECORD is additionally gated by the database (needs a READY_TO_RECORD script). Nothing here publishes anything:
# PUBLISHED is only a record that Andrew posted it himself.
TRANSITIONS = {
    "IDEA": ("SCRIPTING", "ARCHIVED"),
    "SCRIPTING": ("IDEA", "READY_TO_RECORD", "ARCHIVED"),
    "READY_TO_RECORD": ("SCRIPTING", "RECORDED", "ARCHIVED"),
    "RECORDED": ("READY_TO_RECORD", "EDITING", "ARCHIVED"),
    "EDITING": ("RECORDED", "QA", "ARCHIVED"),
    "QA": ("EDITING", "READY_TO_PUBLISH", "ARCHIVED"),
    "READY_TO_PUBLISH": ("QA", "PUBLISHED", "ARCHIVED"),
    "PUBLISHED": ("ARCHIVED",),
    "ARCHIVED": ("IDEA",),
}


class Invalid(Exception):
    pass


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


def _row(r):
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(r).items()}


def _text(body, key, required=False, maxlen=200):
    v = body.get(key)
    if v is None:
        if required:
            raise Invalid(f"{key} is required")
        return None
    if not isinstance(v, str) or not v.strip():
        raise Invalid(f"{key} must be non-empty text")
    v = v.strip()
    if len(v) > maxlen:
        raise Invalid(f"{key} is too long (max {maxlen})")
    return v


def _date(body):
    v = body.get("planned_date")
    if v is None:
        return None
    try:
        return date.fromisoformat(v).isoformat()
    except (TypeError, ValueError):
        raise Invalid("planned_date must be YYYY-MM-DD") from None


def _duration(body):
    v = body.get("target_duration_s")
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, int) or not 0 < v <= 86_400:
        raise Invalid("target_duration_s must be a whole number of seconds between 1 and 86400")
    return v


def _path(body):
    v = body.get("production_path")
    if v is None:
        return None
    if not isinstance(v, str) or not PATH_RE.match(v) or ".." in v:
        raise Invalid("production_path must be a safe path starting with production/")
    return v


def _guard(fn):
    """Run a write; translate the database's own rule errors into safe messages."""
    try:
        return fn()
    except psycopg.errors.CheckViolation as e:
        msg = access.rule_message(e)
        raise Conflict(msg or "that change is not allowed") from None
    except psycopg.errors.UniqueViolation:
        raise Conflict("that code is already used in this series") from None
    except psycopg.errors.ForeignKeyViolation:
        raise Conflict("this episode is still referenced by other records") from None


def list_series(conn):
    rows = conn.execute("SELECT s.id, s.slug, s.title, count(e.id) AS episodes FROM series s LEFT JOIN episodes e ON e.series_id = s.id "
                        "GROUP BY s.id ORDER BY s.id").fetchall()
    return [_row(r) for r in rows]


_COLS = "id, series_id, code, title, status, planned_date, target_duration_s, production_path, parent_episode_id, created_at, updated_at"


def list_episodes(conn):
    return [_row(r) for r in conn.execute(f"SELECT {_COLS} FROM episodes ORDER BY planned_date NULLS LAST, id").fetchall()]


def get_episode(conn, eid: int):
    r = conn.execute(f"SELECT {_COLS} FROM episodes WHERE id = ?", (eid,)).fetchone()
    if not r:
        raise NotFound("episode not found")
    out = _row(r)
    out["allowed_next"] = list(TRANSITIONS[out["status"]])
    return out


def create_episode(conn, body: dict):
    series_id = body.get("series_id")
    if isinstance(series_id, bool) or not isinstance(series_id, int):
        raise Invalid("series_id is required")
    code, title = _text(body, "code", True, 40), _text(body, "title", True)
    if not CODE_RE.match(code):
        raise Invalid("code may use letters, numbers, dot, dash and underscore (max 40)")
    if not conn.execute("SELECT 1 FROM series WHERE id = ?", (series_id,)).fetchone():
        raise NotFound("series not found")
    parent = body.get("parent_episode_id")
    if parent is not None and (isinstance(parent, bool) or not isinstance(parent, int)
                               or not conn.execute("SELECT 1 FROM episodes WHERE id = ?", (parent,)).fetchone()):
        raise Invalid("parent_episode_id must be an existing episode")
    args = (series_id, code, title, _date(body), _duration(body), _path(body), parent)

    def run():
        return conn.execute("INSERT INTO episodes(series_id, code, title, planned_date, target_duration_s, production_path, parent_episode_id) "
                            "VALUES (?,?,?,?,?,?,?) RETURNING id", args).fetchone()["id"]
    eid = _guard(run)
    audit(conn, ACTOR, "content.episode.create", f"episode:{eid}", code)
    return get_episode(conn, eid)


EDITABLE = ("title", "planned_date", "target_duration_s", "production_path")


def update_episode(conn, eid: int, body: dict):
    get_episode(conn, eid)
    sets, args = [], []
    for key in EDITABLE:
        if key in body:
            val = {"title": lambda: _text(body, "title", True), "planned_date": lambda: _date(body),
                   "target_duration_s": lambda: _duration(body), "production_path": lambda: _path(body)}[key]()
            sets.append(f"{key} = ?")
            args.append(val)
    unknown = set(body) - set(EDITABLE)
    if unknown:
        raise Invalid("cannot change: " + ", ".join(sorted(unknown)))
    if not sets:
        raise Invalid("nothing to change")
    _guard(lambda: conn.execute(f"UPDATE episodes SET {', '.join(sets)}, updated_at = now() WHERE id = ?", (*args, eid)))
    audit(conn, ACTOR, "content.episode.update", f"episode:{eid}", ",".join(k for k in EDITABLE if k in body))
    return get_episode(conn, eid)


def change_status(conn, eid: int, body: dict):
    to = body.get("to")
    if to not in STATUSES:
        raise Invalid("to must be one of: " + ", ".join(STATUSES))
    cur = get_episode(conn, eid)["status"]
    if to not in TRANSITIONS[cur]:
        raise Conflict(f"cannot move from {cur} to {to}; allowed: " + ", ".join(TRANSITIONS[cur]))
    _guard(lambda: conn.execute("UPDATE episodes SET status = ?, updated_at = now() WHERE id = ?", (to, eid)))
    audit(conn, ACTOR, "content.episode.status", f"episode:{eid}", f"{cur}->{to}")
    return get_episode(conn, eid)


def delete_episode(conn, eid: int):
    ep = get_episode(conn, eid)
    if ep["status"] not in ("IDEA", "ARCHIVED"):
        raise Conflict("only IDEA or ARCHIVED episodes can be deleted; archive it first")
    _guard(lambda: conn.execute("DELETE FROM episodes WHERE id = ?", (eid,)))
    audit(conn, ACTOR, "content.episode.delete", f"episode:{eid}", ep["code"])
    return {"deleted": eid}
