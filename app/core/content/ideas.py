"""P1: the idea backlog and "promote idea to episode". Runs inside content_session(). Errors: see common.py."""

import psycopg

from core.audit import audit
from core.content import episodes
from core.content.common import ACTOR, Conflict, Invalid, NotFound, only_keys, text, whole

_COLS = "id, title, notes, series_id, moment_id, episode_id, status, created_at, updated_at"
EDITABLE = ("title", "notes", "series_id")
SETTABLE = ("BACKLOG", "DROPPED")     # SCHEDULED is only ever reached by promoting the idea


def _row(r):
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(r).items()}


def list_ideas(conn):
    rows = conn.execute(f"SELECT {_COLS} FROM ideas ORDER BY (status = 'DROPPED'), id DESC").fetchall()
    return [_row(r) for r in rows]


def get_idea(conn, iid: int):
    r = conn.execute(f"SELECT {_COLS} FROM ideas WHERE id = ?", (iid,)).fetchone()
    if not r:
        raise NotFound("idea not found")
    return _row(r)


def _series(conn, body, required=False):
    sid = body.get("series_id")
    if sid is None:
        if required:
            raise Invalid("series_id is required")
        return None
    whole(sid, "series_id")
    if not conn.execute("SELECT 1 FROM series WHERE id = ?", (sid,)).fetchone():
        raise NotFound("series not found")
    return sid


def create_idea(conn, body: dict):
    only_keys(body, ("title", "notes", "series_id"))
    title = text(body, "title", True)
    notes = text(body, "notes", maxlen=5000, allow_empty=True) or ""
    series_id = _series(conn, body)
    iid = conn.execute("INSERT INTO ideas(title, notes, series_id) VALUES (?,?,?) RETURNING id", (title, notes, series_id)).fetchone()["id"]
    audit(conn, ACTOR, "content.idea.create", f"idea:{iid}", title)
    return get_idea(conn, iid)


def update_idea(conn, iid: int, body: dict):
    get_idea(conn, iid)
    only_keys(body, EDITABLE)
    sets, args = [], []
    if "title" in body:
        sets.append("title = ?"); args.append(text(body, "title", True))
    if "notes" in body:
        if body["notes"] is None:
            raise Invalid("notes must be text")
        sets.append("notes = ?"); args.append(text(body, "notes", maxlen=5000, allow_empty=True))
    if "series_id" in body:
        sets.append("series_id = ?"); args.append(_series(conn, body))
    if not sets:
        raise Invalid("nothing to change")
    conn.execute(f"UPDATE ideas SET {', '.join(sets)} WHERE id = ?", (*args, iid))
    audit(conn, ACTOR, "content.idea.update", f"idea:{iid}", ",".join(k for k in EDITABLE if k in body))
    return get_idea(conn, iid)


def change_status(conn, iid: int, body: dict):
    to = body.get("to")
    if to not in SETTABLE:
        raise Invalid("to must be one of: " + ", ".join(SETTABLE) + " (an idea becomes SCHEDULED only by promoting it)")
    cur = get_idea(conn, iid)["status"]
    if cur == "SCHEDULED":
        raise Conflict("this idea was promoted to an episode; manage the episode instead")
    if cur == to:
        raise Conflict(f"idea is already {cur}")
    conn.execute("UPDATE ideas SET status = ? WHERE id = ?", (to, iid))
    audit(conn, ACTOR, "content.idea.status", f"idea:{iid}", f"{cur}->{to}")
    return get_idea(conn, iid)


def promote(conn, iid: int, body: dict):
    """Turn a BACKLOG idea into an IDEA-status episode (title copied). Nothing is created unless both steps succeed."""
    idea = get_idea(conn, iid)
    only_keys(body, ("series_id", "code", "planned_date", "target_duration_s"))
    if idea["status"] != "BACKLOG":
        raise Conflict(f"only a BACKLOG idea can be promoted (this one is {idea['status']})")
    args = dict(body)
    if args.get("series_id") is None:
        args["series_id"] = idea["series_id"]
    if args["series_id"] is None:
        raise Invalid("series_id is required (the idea has no series yet)")
    args["title"] = idea["title"]
    episode = episodes.create_episode(conn, args)
    conn.execute("UPDATE ideas SET status = 'SCHEDULED', episode_id = ?, series_id = ? WHERE id = ?", (episode["id"], episode["series_id"], iid))
    audit(conn, ACTOR, "content.idea.promote", f"idea:{iid}", f"episode:{episode['id']} {episode['code']}")
    return {"idea": get_idea(conn, iid), "episode": episode}


def delete_idea(conn, iid: int):
    idea = get_idea(conn, iid)
    if idea["status"] == "SCHEDULED":
        raise Conflict("this idea became an episode; delete or archive the episode instead")
    try:
        conn.execute("DELETE FROM ideas WHERE id = ?", (iid,))
    except psycopg.errors.ForeignKeyViolation:
        raise Conflict("this idea is still referenced by other records") from None
    audit(conn, ACTOR, "content.idea.delete", f"idea:{iid}", idea["title"])
    return {"deleted": iid}
