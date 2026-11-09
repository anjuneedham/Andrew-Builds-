"""HTTP layer for the content platform (/api/content/*). The caller (dashboard.app.handle) has already authenticated the
owner, so an unauthenticated request never reaches this module. Returns (status, content_type, bytes).
Errors we raise on purpose carry safe messages; anything unexpected propagates and the server answers a generic 503,
never driver text."""

import json
import re

from core.content import access, episodes, ideas, meta, schedule, scripts, status
from core.content.common import Conflict, Invalid, NotFound

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


def _json_body(body: bytes) -> dict:
    if len(body) > CONTENT_MAX_BODY:
        raise Invalid("request body too large")
    try:
        data = json.loads(body or b"{}")
    except (ValueError, UnicodeDecodeError):
        raise Invalid("body must be JSON") from None
    if not isinstance(data, dict):
        raise Invalid("body must be a JSON object")
    return data


# (pattern, {METHOD: handler(conn, raw_body, *path_ids) -> (status, object)}). A known path with another method is a 404.
# The serverless entry hands us the URL path only (no query string), so every filter lives in the path.
def _routes():
    j = _json_body
    return [
        (r"series", {"GET": lambda c, b: (200, episodes.list_series(c))}),
        (r"episodes", {"GET": lambda c, b: (200, episodes.list_episodes(c)), "POST": lambda c, b: (201, episodes.create_episode(c, j(b)))}),
        (r"episodes/(\d{1,18})", {"GET": lambda c, b, i: (200, episodes.get_episode(c, i)),
                                  "PATCH": lambda c, b, i: (200, episodes.update_episode(c, i, j(b))),
                                  "DELETE": lambda c, b, i: (200, episodes.delete_episode(c, i))}),
        (r"episodes/(\d{1,18})/status", {"POST": lambda c, b, i: (200, episodes.change_status(c, i, j(b)))}),
        (r"episodes/(\d{1,18})/scripts", {"GET": lambda c, b, i: (200, scripts.list_scripts(c, i)),
                                          "POST": lambda c, b, i: (201, scripts.create_script(c, i, j(b)))}),
        (r"ideas", {"GET": lambda c, b: (200, ideas.list_ideas(c)), "POST": lambda c, b: (201, ideas.create_idea(c, j(b)))}),
        (r"ideas/(\d{1,18})", {"GET": lambda c, b, i: (200, ideas.get_idea(c, i)),
                               "PATCH": lambda c, b, i: (200, ideas.update_idea(c, i, j(b))),
                               "DELETE": lambda c, b, i: (200, ideas.delete_idea(c, i))}),
        (r"ideas/(\d{1,18})/status", {"POST": lambda c, b, i: (200, ideas.change_status(c, i, j(b)))}),
        (r"ideas/(\d{1,18})/promote", {"POST": lambda c, b, i: (201, ideas.promote(c, i, j(b)))}),
        (r"calendar/today", {"GET": lambda c, b: (200, schedule.current())}),
        (r"calendar/month/([^/]{1,12})", {"GET": lambda c, b, m: (200, schedule.month(c, str(m)))}),
        (r"calendar/week/([^/]{1,12})", {"GET": lambda c, b, d: (200, schedule.week(c, str(d)))}),
        (r"scripts/(\d{1,18})", {"GET": lambda c, b, i: (200, scripts.get_script(c, i)),
                                 "PATCH": lambda c, b, i: (200, scripts.update_script(c, i, j(b))),
                                 "DELETE": lambda c, b, i: (200, scripts.delete_script(c, i))}),
        (r"scripts/(\d{1,18})/status", {"POST": lambda c, b, i: (200, scripts.change_status(c, i, j(b)))}),
        (r"scripts/(\d{1,18})/lines", {"POST": lambda c, b, i: (201, scripts.add_line(c, i, j(b)))}),
        (r"lines/(\d{1,18})", {"PATCH": lambda c, b, i: (200, scripts.update_line(c, i, j(b))),
                               "DELETE": lambda c, b, i: (200, scripts.delete_line(c, i))}),
        (r"lines/(\d{1,18})/move", {"POST": lambda c, b, i: (200, scripts.move_line(c, i, j(b)))}),
    ]


ROUTES = [(re.compile("^" + pat + "$"), fns) for pat, fns in _routes()]


def _dispatch(method, p, conn, body):
    for rx, fns in ROUTES:
        m = rx.match(p)
        if m and method in fns:
            args = [int(g) if g.isdigit() else g for g in m.groups()]   # ids are digits; calendar parts are strings
            return fns[method](conn, body, *args)
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
            res = _dispatch(method, p, conn, body)
            if res is not None:
                return _out(*res)
    except Invalid as e:
        return _out(400, {"error": str(e)})
    except NotFound as e:
        return _out(404, {"error": str(e)})
    except Conflict as e:
        return _out(409, {"error": str(e)})
    return _out(404, {"error": "not found"})
