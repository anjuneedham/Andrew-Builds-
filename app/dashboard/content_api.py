"""HTTP layer for the content platform (/api/content/*). The caller (dashboard.app.handle) has already authenticated the
owner, so an unauthenticated request never reaches this module. Returns (status, content_type, bytes).
Errors we raise on purpose carry safe messages; anything unexpected propagates and the server answers a generic 503,
never driver text."""

import json

from core.content import meta, status

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


def handle(method, path, conn, body: bytes):
    p = path[len("/api/content/"):].strip("/")
    if method == "GET":
        if p == "meta":
            return _out(200, _meta())
        if p == "health":
            return _out(200, status.foundation(conn))
    return _out(404, {"error": "not found"})
