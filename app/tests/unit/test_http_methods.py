"""The content API uses PATCH and DELETE. Unit tests call dashboard.handle() directly, which cannot notice that a real HTTP
entry point does not answer those methods (BaseHTTPRequestHandler replies 501). This test talks to the real Vercel handler class
over a socket. No database is involved: with no database configured the handler answers 503 - the point is that it is not 501."""

import http.client
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest import mock

from api import index
from core import db


class HttpMethods(unittest.TestCase):
    def test_every_method_the_api_uses_reaches_the_router(self):
        env = {k: v for k, v in os.environ.items() if k not in db.URL_VARS}
        with mock.patch.dict(os.environ, env, clear=True):
            srv = ThreadingHTTPServer(("127.0.0.1", 0), index.handler)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                for method in ("GET", "POST", "PATCH", "DELETE"):
                    with self.subTest(method=method):
                        c = http.client.HTTPConnection("127.0.0.1", srv.server_port, timeout=5)
                        c.request(method, "/api/content/episodes/1", body=b"{}" if method in ("POST", "PATCH") else None)
                        status = c.getresponse().status
                        c.close()
                        self.assertEqual(status, 503, f"{method} was not routed (got {status}; 501 means the handler lacks do_{method})")
            finally:
                srv.shutdown()
                srv.server_close()


if __name__ == "__main__":
    unittest.main()
