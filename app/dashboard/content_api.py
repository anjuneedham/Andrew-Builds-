"""HTTP layer for the content platform (/api/content/*). The caller (dashboard.app.handle) has already authenticated the
owner, so an unauthenticated request never reaches this module. Returns (status, content_type, bytes).
Errors we raise on purpose carry safe messages; anything unexpected propagates and the server answers a generic 503,
never driver text."""

import json
import re

from core.content import access, episodes, meta, status

CONTENT_MAX_BODY = 65_536


def _out(code, obj):
    return code, "application/json", json.dumps(obj, default=str).encode()


def _meta():
    return {
        "role": meta.ROLE,
        "enums": {f"{t}.{c}": list(v) for (t, c), v in meta.ENUMS.items()},
        "factual_kinds": list(meta.FACTUAL_KINDS),
        "non_factual_kinds": list(meta.NON_FACTUAL_KINDS),
        "course_total_seconds": meta.COURSE_TOTAL_SECONDS,
        "rules": list(meta.RULES),
        "not_built": [{"phase": p, "what": w} for p, w in meta.NOT_BUILT],
    }


_ID = re.compile(r"^episodes/(\d{1,18})(?:/(status))?$")


def _json_body(body: bytes) -> dict:
    if len(body) > CONTENT_MAX_BODY:
        raise episodes.Invalid("request body too large")
    try:
        data = json.loads(body or b"{}")
    except (ValueError, UnicodeDecodeError):
        raise episodes.Invalid("body must be JSON") from None
    if not isinstance(data, dict):
        raise episodes.Invalid("body must be a JSON object")
    return data


def _episodes_route(method, p, conn, body):
    if p == "episodes":
        if method == "GET":
            return 200, episodes.list_episodes(conn)
        if method == "POST":
            return 201, episodes.create_episode(conn, _json_body(body))
        return None
    m = _ID.match(p)
    if not m:
        return None
    eid, sub = int(m.group(1)), m.group(2)
    if sub == "status":
        return (200, episodes.change_status(conn, eid, _json_body(body))) if method == "POST" else None
    if method == "GET":
        return 200, episodes.get_episode(conn, eid)
    if method == "PATCH":
        return 200, episodes.update_episode(conn, eid, _json_body(body))
    if method == "DELETE":
        return 200, episodes.delete_episode(conn, eid)
    return None


def handle(method, path, conn, body: bytes):
    p = path[len("/api/content/"):].strip("/")
    if method == "GET":
        if p == "meta":
            return _out(200, _meta())
        if p == "health":
            return _out(200, status.foundation(conn))
    try:
        # every write runs as content_app inside one transaction; a raised error rolls the whole request back
        with access.content_session(conn):
            if p == "series" and method == "GET":
                return _out(200, episodes.list_series(conn))
            res = _episodes_route(method, p, conn, body)
            if res is not None:
                return _out(*res)
    except episodes.Invalid as e:
        return _out(400, {"error": str(e)})
    except episodes.NotFound as e:
        return _out(404, {"error": str(e)})
    except episodes.Conflict as e:
        return _out(409, {"error": str(e)})
    return _out(404, {"error": "not found"})
