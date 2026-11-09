"""P2a: scripts and script lines. One sentence per line, each tagged with a kind (default FACT, so nothing slips through unmarked).
Runs inside content_session(). The database owns the hard rules: READY_TO_RECORD needs every FACT line to cite CONFIRMED claims,
READY_TO_RECORD and LOCKED scripts cannot change, LOCKED is final. Here we add the step order and friendly messages.
Claims, sources and the claim checker screen arrive in P2b; until then any FACT line blocks READY_TO_RECORD (by design)."""

import psycopg

from core.audit import audit
from core.content import access
from core.content.common import ACTOR, Conflict, Invalid, NotFound, only_keys, text, whole
from core.content.meta import ENUMS

STATUSES = ENUMS[("scripts", "status")]
KINDS = ENUMS[("script_lines", "kind")]
BODY_MAX, LINE_MAX = 20_000, 2_000
FROZEN = ("READY_TO_RECORD", "LOCKED")

# DRAFT -> IN_REVIEW -> READY_TO_RECORD -> LOCKED, with one step back at each stage (LOCKED is final).
# DRAFT cannot jump straight to READY_TO_RECORD: a script is always reviewed first. The claim gate is the database's.
TRANSITIONS = {
    "DRAFT": ("IN_REVIEW",),
    "IN_REVIEW": ("DRAFT", "READY_TO_RECORD"),
    "READY_TO_RECORD": ("DRAFT", "LOCKED"),
    "LOCKED": (),
}


def _guard(fn):
    try:
        return fn()
    except psycopg.errors.CheckViolation as e:
        raise Conflict(access.rule_message(e) or "that change is not allowed") from None
    except psycopg.errors.UniqueViolation:
        raise Conflict("someone changed this at the same time; reload and try again") from None
    except psycopg.errors.ForeignKeyViolation:
        raise Conflict("this script is still referenced by other records") from None


def _iso(r):
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(r).items()}


def _episode(conn, eid: int):
    r = conn.execute("SELECT id, status FROM episodes WHERE id = ?", (eid,)).fetchone()
    if not r:
        raise NotFound("episode not found")
    return r


def list_scripts(conn, eid: int):
    _episode(conn, eid)
    rows = conn.execute("SELECT s.id, s.episode_id, s.version, s.status, s.created_at, s.updated_at, count(l.id) AS lines "
                        "FROM scripts s LEFT JOIN script_lines l ON l.script_id = s.id WHERE s.episode_id = ? "
                        "GROUP BY s.id ORDER BY s.version DESC", (eid,)).fetchall()
    return [_iso(r) for r in rows]


def get_script(conn, sid: int):
    s = conn.execute("SELECT id, episode_id, version, status, body, created_at, updated_at FROM scripts WHERE id = ?", (sid,)).fetchone()
    if not s:
        raise NotFound("script not found")
    out = _iso(s)
    lines = conn.execute("SELECT id, position, text, kind FROM script_lines WHERE script_id = ? ORDER BY position", (sid,)).fetchall()
    claims = {}
    for r in conn.execute("SELECT lc.line_id, c.id, c.code, c.status FROM line_claims lc JOIN claims c ON c.id = lc.claim_id "
                          "JOIN script_lines l ON l.id = lc.line_id WHERE l.script_id = ? ORDER BY c.code", (sid,)):
        claims.setdefault(r["line_id"], []).append({"id": r["id"], "code": r["code"], "status": r["status"]})
    out["lines"] = [{**dict(r), "claims": claims.get(r["id"], [])} for r in lines]
    out["editable"] = out["status"] not in FROZEN
    out["allowed_next"] = list(TRANSITIONS[out["status"]])
    out["counts"] = {k: sum(1 for r in lines if r["kind"] == k) for k in KINDS if any(r["kind"] == k for r in lines)}
    return out


def create_script(conn, eid: int, body: dict):
    ep = _episode(conn, eid)
    only_keys(body, ("body", "copy_from"))
    if ep["status"] in ("ARCHIVED", "PUBLISHED"):
        raise Conflict(f"episode is {ep['status']}; restore it before adding a script")
    new_body = text(body, "body", maxlen=BODY_MAX, allow_empty=True)
    src = body.get("copy_from")
    if src is not None:
        whole(src, "copy_from")
        row = conn.execute("SELECT body FROM scripts WHERE id = ? AND episode_id = ?", (src, eid)).fetchone()
        if not row:
            raise Invalid("copy_from must be a script of this episode")
        if new_body is None:
            new_body = row["body"]
    version = conn.execute("SELECT coalesce(max(version), 0) + 1 AS v FROM scripts WHERE episode_id = ?", (eid,)).fetchone()["v"]
    sid = _guard(lambda: conn.execute("INSERT INTO scripts(episode_id, version, body) VALUES (?,?,?) RETURNING id",
                                      (eid, version, new_body or "")).fetchone()["id"])
    if src is not None:       # the new draft starts as a copy of the old lines and their claim links
        conn.execute("INSERT INTO script_lines(script_id, position, text, kind) SELECT ?, position, text, kind FROM script_lines WHERE script_id = ?", (sid, src))
        conn.execute("INSERT INTO line_claims(line_id, claim_id) SELECT n.id, lc.claim_id FROM script_lines o "
                     "JOIN line_claims lc ON lc.line_id = o.id JOIN script_lines n ON n.script_id = ? AND n.position = o.position "
                     "WHERE o.script_id = ?", (sid, src))
    audit(conn, ACTOR, "content.script.create", f"script:{sid}", f"episode:{eid} v{version}" + (f" copy of script:{src}" if src else ""))
    return get_script(conn, sid)


def update_script(conn, sid: int, body: dict):
    get_script(conn, sid)
    only_keys(body, ("body",))
    if "body" not in body or body["body"] is None:
        raise Invalid("nothing to change")
    new_body = text(body, "body", maxlen=BODY_MAX, allow_empty=True)
    _guard(lambda: conn.execute("UPDATE scripts SET body = ?, updated_at = now() WHERE id = ?", (new_body, sid)))
    audit(conn, ACTOR, "content.script.update", f"script:{sid}", "body")
    return get_script(conn, sid)


def change_status(conn, sid: int, body: dict):
    to = body.get("to")
    if to not in STATUSES:
        raise Invalid("to must be one of: " + ", ".join(STATUSES))
    cur = get_script(conn, sid)["status"]
    if to not in TRANSITIONS[cur]:
        allowed = ", ".join(TRANSITIONS[cur]) or "none (LOCKED is final)"
        raise Conflict(f"cannot move from {cur} to {to}; allowed: {allowed}")
    _guard(lambda: conn.execute("UPDATE scripts SET status = ?, updated_at = now() WHERE id = ?", (to, sid)))
    audit(conn, ACTOR, "content.script.status", f"script:{sid}", f"{cur}->{to}")
    return get_script(conn, sid)


def delete_script(conn, sid: int):
    s = get_script(conn, sid)
    if s["status"] in FROZEN:
        raise Conflict(f"a {s['status']} script cannot be deleted; move a READY_TO_RECORD script back to DRAFT first")
    _guard(lambda: conn.execute("DELETE FROM scripts WHERE id = ?", (sid,)))
    audit(conn, ACTOR, "content.script.delete", f"script:{sid}", f"episode:{s['episode_id']} v{s['version']}")
    return {"deleted": sid}


# ---- lines ----
def _kind(body, default=None):
    k = body.get("kind", default)
    if k not in KINDS:
        raise Invalid("kind must be one of: " + ", ".join(KINDS))
    return k


def _line(conn, lid: int):
    r = conn.execute("SELECT id, script_id, position FROM script_lines WHERE id = ?", (lid,)).fetchone()
    if not r:
        raise NotFound("line not found")
    return r


def _count(conn, sid: int) -> int:
    return conn.execute("SELECT count(*) AS n FROM script_lines WHERE script_id = ?", (sid,)).fetchone()["n"]


def add_line(conn, sid: int, body: dict):
    get_script(conn, sid)
    only_keys(body, ("text", "kind", "position"))
    t, kind = text(body, "text", True, LINE_MAX), _kind(body, "FACT")
    n = _count(conn, sid)
    pos = n + 1 if body.get("position") is None else whole(body["position"], "position", 1, n + 1)
    def run():
        conn.execute("UPDATE script_lines SET position = position + 1 WHERE script_id = ? AND position >= ?", (sid, pos))
        return conn.execute("INSERT INTO script_lines(script_id, position, text, kind) VALUES (?,?,?,?) RETURNING id", (sid, pos, t, kind)).fetchone()["id"]
    lid = _guard(run)
    audit(conn, ACTOR, "content.line.add", f"line:{lid}", f"script:{sid} #{pos} {kind}")
    return get_script(conn, sid)


def update_line(conn, lid: int, body: dict):
    ln = _line(conn, lid)
    only_keys(body, ("text", "kind"))
    sets, args = [], []
    if "text" in body:
        sets.append("text = ?"); args.append(text(body, "text", True, LINE_MAX))
    if "kind" in body:
        sets.append("kind = ?"); args.append(_kind(body))
    if not sets:
        raise Invalid("nothing to change")
    _guard(lambda: conn.execute(f"UPDATE script_lines SET {', '.join(sets)}, updated_at = now() WHERE id = ?", (*args, lid)))
    audit(conn, ACTOR, "content.line.update", f"line:{lid}", f"script:{ln['script_id']} " + ",".join(k for k in ("text", "kind") if k in body))
    return get_script(conn, ln["script_id"])


def delete_line(conn, lid: int):
    ln = _line(conn, lid)
    def run():
        conn.execute("DELETE FROM script_lines WHERE id = ?", (lid,))
        conn.execute("UPDATE script_lines SET position = position - 1 WHERE script_id = ? AND position > ?", (ln["script_id"], ln["position"]))
    _guard(run)
    audit(conn, ACTOR, "content.line.delete", f"line:{lid}", f"script:{ln['script_id']} #{ln['position']}")
    return get_script(conn, ln["script_id"])


def move_line(conn, lid: int, body: dict):
    ln = _line(conn, lid)
    only_keys(body, ("to",))
    sid, cur = ln["script_id"], ln["position"]
    to = whole(body.get("to"), "to", 1, _count(conn, sid))
    if to != cur:
        def run():
            if to > cur:
                conn.execute("UPDATE script_lines SET position = position - 1 WHERE script_id = ? AND position > ? AND position <= ?", (sid, cur, to))
            else:
                conn.execute("UPDATE script_lines SET position = position + 1 WHERE script_id = ? AND position >= ? AND position < ?", (sid, to, cur))
            conn.execute("UPDATE script_lines SET position = ? WHERE id = ?", (to, lid))
        _guard(run)
        audit(conn, ACTOR, "content.line.move", f"line:{lid}", f"script:{sid} {cur}->{to}")
    return get_script(conn, sid)
