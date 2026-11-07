"""Outreach Desk: owner-only API + static app. Every /api route except login/setup needs a session bearer token in the
Authorization header (no cookies, so no CSRF surface). One handle() serves both the local runner and Vercel."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from core import db
from core.auth import owner_login as ol
from dashboard import sales_api

PAGE = (Path(__file__).parent / "pages" / "index.html").read_text()
STATIC = Path(__file__).parent / "static"
STATIC_MIME = {".js": "text/javascript", ".css": "text/css", ".woff2": "font/woff2", ".png": "image/png",
               ".json": "application/json", ".webmanifest": "application/manifest+json", ".svg": "image/svg+xml"}
STATIC_ROOT = {"/manifest.webmanifest", "/sw.js", "/icon-192.png", "/icon-512.png"}
STATIC_DIRS = ("/css/", "/js/", "/fonts/")
MAX_BODY = 4096                       # auth routes
READ_CAP = sales_api.SALES_MAX_BODY + 1  # most we ever read; each route enforces its own limit
HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    # No inline scripts and no third-party origins: a tight XSS barrier.
    "Content-Security-Policy": ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                                "img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
                                "base-uri 'none'; form-action 'self'"),
}


def static_file(path: str):
    """(content_type, bytes) for an allowed static file, else None. Path traversal safe."""
    if path not in STATIC_ROOT and not path.startswith(STATIC_DIRS):
        return None
    root = STATIC.resolve()
    f = (root / path.lstrip("/")).resolve()
    if root not in f.parents or not f.is_file() or f.suffix not in STATIC_MIME:
        return None
    return STATIC_MIME[f.suffix], f.read_bytes()


def _json(code, obj):
    return code, "application/json", json.dumps(obj).encode()


def _fields(body: bytes, *names):
    if len(body) > MAX_BODY:
        raise ValueError("body too large")
    data = json.loads(body or b"{}")
    out = []
    for n in names:
        v = data.get(n, "")
        if not isinstance(v, str):
            raise ValueError("bad field")
        out.append(v)
    return out


def handle(method, path, authz, conn, body: bytes = b""):
    """Returns (status, content_type, body_bytes)."""
    if method == "GET" and path == "/":
        return 200, "text/html; charset=utf-8", PAGE.encode()
    if method == "GET":
        f = static_file(path)
        if f:
            return 200, f[0], f[1]
    if not path.startswith("/api/"):
        return _json(404, {"error": "not found"})

    # --- unauthenticated: login and one-time setup (rate limited, audited) ---
    try:
        if method == "GET" and path == "/api/auth/state":
            return _json(200, {"setup_complete": ol.setup_complete(conn), "setup_enabled": ol.setup_enabled(),
                               "mode": "LIVE" if os.environ.get("VERCEL") else "LOCAL"})
        if method == "POST" and path == "/api/auth/login":
            password, code = _fields(body, "password", "code")
            return _json(200, ol.login(conn, password, code))
        if method == "POST" and path == "/api/auth/setup/begin":
            token, password = _fields(body, "setup_token", "password")
            return _json(200, ol.begin_setup(conn, token, password))
        if method == "POST" and path == "/api/auth/setup/confirm":
            token, code = _fields(body, "setup_token", "code")
            return _json(200, {"recovery_codes": ol.confirm_setup(conn, token, code)})
    except ol.LockedOut:
        return _json(429, {"error": "too many attempts; try again later"})
    except ol.SetupDisabled:
        return _json(403, {"error": "setup is not enabled"})
    except ol.SetupClosed:
        return _json(403, {"error": "setup is already complete"})
    except ol.AuthError:
        return _json(401, {"error": "invalid credentials"})
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return _json(400, {"error": str(e) if isinstance(e, ValueError) and "password" in str(e) else "bad request"})

    # --- authenticated ---
    token = authz[7:] if authz and authz.startswith("Bearer ") else ""
    try:
        ol.verify_session(conn, token)
    except ol.AuthError:
        return _json(401, {"error": "unauthorized"})
    if path.startswith("/api/sales/"):
        return sales_api.handle(method, path, conn, body)
    if method == "POST" and path == "/api/auth/logout":
        ol.logout(conn, token)
        return _json(200, {"ok": True})
    if method == "POST" and path == "/api/auth/logout-all":
        ol.logout_everywhere(conn)
        return _json(200, {"ok": True})
    return _json(404, {"error": "not found"})


def serve(host="127.0.0.1", port=8080):
    """Local server. Same code as the live site: a fresh database connection per request (a suspended serverless
    database can never wedge the app)."""
    first = db.connect()  # DATABASE_URL; fails fast and loudly if missing or wrong
    db.migrate(first)
    first.close()

    class H(BaseHTTPRequestHandler):
        def _go(self, method):
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(min(n, READ_CAP)) if n else b""
            path = self.path.split("?")[0]
            conn = None
            try:
                conn = db.connect() if path.startswith("/api/") else None
                code, ctype, out = handle(method, path, self.headers.get("Authorization"), conn, body)
            except Exception:
                code, ctype, out = 503, "application/json", json.dumps({"error": "database unavailable"}).encode()
            finally:
                if conn is not None:
                    conn.close()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(out)))
            for k, v in HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(out)

        do_GET = lambda self: self._go("GET")
        do_POST = lambda self: self._go("POST")

        def log_message(self, *a):
            pass

    ThreadingHTTPServer((host, port), H).serve_forever()


if __name__ == "__main__":
    serve()
