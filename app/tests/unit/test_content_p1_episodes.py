"""P1 slice 1: series + episodes API, status state machine, delete rules, audit. Through the real HTTP handler + owner auth.
Needs TEST_DATABASE_URL (a THROWAWAY Postgres). All sample data is labelled SAMPLE and lives in a per-test schema."""

import json
import unittest

from core.content import episodes
from core.content.meta import ENUMS
from dashboard import app as dash
from tests import authutil
from tests.dbutil import make_conn


class EpisodesApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = make_conn()
        cls.token, _, _ = authutil.session(cls.conn)
        cls.series = cls.conn.execute("SELECT id FROM series ORDER BY id LIMIT 1").fetchone()["id"]
        cls.n = 0

    def call(self, method, path, body=None, token="default"):
        tok = self.token if token == "default" else token
        raw = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else b""
        code, _, out = dash.handle(method, "/api/content" + path, ("Bearer " + tok) if tok else None, self.conn, raw)
        return code, json.loads(out)

    def make(self, **kw):
        type(self).n += 1
        body = {"series_id": self.series, "code": f"S{self.n:03}", "title": "SAMPLE episode"}
        body.update(kw)
        code, out = self.call("POST", "/episodes", body)
        self.assertEqual(code, 201, out)
        return out

    def ready_script(self, eid):
        """A script that passes the claim gate: one non-factual line, then READY_TO_RECORD."""
        sid = self.conn.execute("INSERT INTO scripts(episode_id, version) VALUES (?, 1) RETURNING id", (eid,)).fetchone()["id"]
        self.conn.execute("INSERT INTO script_lines(script_id, position, kind, text) VALUES (?, 1, 'OPINION', 'SAMPLE opinion line')", (sid,))
        self.conn.execute("UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (sid,))

    def audit_actions(self):
        return [r["action"] for r in self.conn.execute("SELECT action FROM audit_events WHERE action LIKE 'content.episode.%' ORDER BY id")]

    # --- authentication ---
    def test_every_route_is_401_without_a_session(self):
        for method, path in [("GET", "/series"), ("GET", "/episodes"), ("POST", "/episodes"), ("GET", "/episodes/1"),
                             ("PATCH", "/episodes/1"), ("DELETE", "/episodes/1"), ("POST", "/episodes/1/status")]:
            with self.subTest(route=f"{method} {path}"):
                self.assertEqual(self.call(method, path, token=None)[0], 401)
                self.assertEqual(self.call(method, path, token="bad")[0], 401)

    # --- series ---
    def test_series_lists_the_seeded_series_with_counts(self):
        code, out = self.call("GET", "/series")
        self.assertEqual(code, 200)
        self.assertEqual(len(out), 4)
        self.assertTrue(all({"id", "slug", "title", "episodes"} <= set(s) for s in out))

    # --- create / read ---
    def test_create_defaults_to_idea_and_is_readable(self):
        ep = self.make(planned_date="2026-12-01", target_duration_s=540, production_path="production/episode-003")
        self.assertEqual((ep["status"], ep["planned_date"], ep["target_duration_s"]), ("IDEA", "2026-12-01", 540))
        self.assertEqual(ep["allowed_next"], ["SCRIPTING", "ARCHIVED"])
        self.assertEqual(self.call("GET", f"/episodes/{ep['id']}")[1]["code"], ep["code"])
        self.assertIn(ep["id"], [e["id"] for e in self.call("GET", "/episodes")[1]])

    def test_create_validation_is_400(self):
        bad = [{}, {"series_id": self.series}, {"series_id": self.series, "code": "x"}, {"series_id": "1", "code": "A1", "title": "t"},
               {"series_id": self.series, "code": "has space", "title": "t"}, {"series_id": self.series, "code": "A1", "title": "   "},
               {"series_id": self.series, "code": "A1", "title": "t", "planned_date": "2026-13-45"},
               {"series_id": self.series, "code": "A1", "title": "t", "planned_date": 20261201},
               {"series_id": self.series, "code": "A1", "title": "t", "target_duration_s": 0},
               {"series_id": self.series, "code": "A1", "title": "t", "target_duration_s": True},
               {"series_id": self.series, "code": "A1", "title": "t", "production_path": "../etc/passwd"},
               {"series_id": self.series, "code": "A1", "title": "t", "production_path": "elsewhere/x"},
               {"series_id": self.series, "code": "A1", "title": "t" * 300}]
        for body in bad:
            with self.subTest(body=str(body)[:60]):
                self.assertEqual(self.call("POST", "/episodes", body)[0], 400)
        for raw in (b"not json", b"[1,2]", b"\xff\xfe"):
            self.assertEqual(self.call("POST", "/episodes", raw)[0], 400)
        self.assertEqual(self.call("POST", "/episodes", b"{" + b" " * 70_000 + b"}")[0], 400)

    def test_unknown_ids_are_404_and_duplicate_code_is_409(self):
        self.assertEqual(self.call("POST", "/episodes", {"series_id": 999999, "code": "Z1", "title": "t"})[0], 404)
        self.assertEqual(self.call("POST", "/episodes", {"series_id": self.series, "code": "Z1", "title": "t", "parent_episode_id": 999999})[0], 400)
        for method in ("GET", "PATCH", "DELETE"):
            self.assertEqual(self.call(method, "/episodes/999999", {"title": "x"})[0], 404)
        self.assertEqual(self.call("POST", "/episodes/999999/status", {"to": "SCRIPTING"})[0], 404)
        self.assertEqual(self.call("GET", "/episodes/abc")[0], 404)
        ep = self.make()
        code, out = self.call("POST", "/episodes", {"series_id": self.series, "code": ep["code"], "title": "again"})
        self.assertEqual(code, 409)
        self.assertNotIn("constraint", out["error"].lower())
        self.assertNotIn("psycopg", out["error"].lower())

    # --- edit ---
    def test_patch_edits_allowed_fields_only(self):
        ep = self.make()
        code, out = self.call("PATCH", f"/episodes/{ep['id']}", {"title": "SAMPLE renamed", "planned_date": "2026-12-05"})
        self.assertEqual((code, out["title"], out["planned_date"]), (200, "SAMPLE renamed", "2026-12-05"))
        self.assertEqual(self.call("PATCH", f"/episodes/{ep['id']}", {"planned_date": None})[1]["planned_date"], None)
        for body in ({}, {"status": "QA"}, {"code": "NEW"}, {"series_id": 2}, {"title": ""}, {"title": "ok", "id": 5}):
            with self.subTest(body=body):
                self.assertEqual(self.call("PATCH", f"/episodes/{ep['id']}", body)[0], 400)
        self.assertEqual(self.call("GET", f"/episodes/{ep['id']}")[1]["status"], "IDEA")

    # --- state machine ---
    def test_transition_table_covers_every_status_and_only_known_ones(self):
        statuses = set(ENUMS[("episodes", "status")])
        self.assertEqual(set(episodes.TRANSITIONS), statuses)
        for src, targets in episodes.TRANSITIONS.items():
            self.assertTrue(set(targets) <= statuses and src not in targets, src)

    def test_status_moves_follow_the_machine(self):
        ep = self.make()
        i = ep["id"]
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "QA"})[0], 409)       # skipping ahead
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "IDEA"})[0], 409)     # same status
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "NOPE"})[0], 400)
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {})[0], 400)
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "SCRIPTING"})[1]["status"], "SCRIPTING")
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "IDEA"})[1]["status"], "IDEA")  # one step back
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "ARCHIVED"})[1]["status"], "ARCHIVED")
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "IDEA"})[1]["status"], "IDEA")  # restore

    def test_ready_to_record_needs_a_ready_script_enforced_by_the_database(self):
        ep = self.make()
        i = ep["id"]
        self.call("POST", f"/episodes/{i}/status", {"to": "SCRIPTING"})
        code, out = self.call("POST", f"/episodes/{i}/status", {"to": "READY_TO_RECORD"})
        self.assertEqual(code, 409)
        self.assertIn("READY_TO_RECORD script", out["error"])
        self.assertEqual(self.call("GET", f"/episodes/{i}")[1]["status"], "SCRIPTING")  # rolled back
        self.conn.execute("INSERT INTO scripts(episode_id, version, status) VALUES (?, 1, 'DRAFT')", (i,))
        self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": "READY_TO_RECORD"})[0], 409)  # a draft is not enough

    def test_full_forward_path_with_a_ready_script(self):
        ep = self.make()
        i = ep["id"]
        self.ready_script(i)
        for to in ("SCRIPTING", "READY_TO_RECORD", "RECORDED", "EDITING", "QA", "READY_TO_PUBLISH", "PUBLISHED", "ARCHIVED"):
            with self.subTest(to=to):
                self.assertEqual(self.call("POST", f"/episodes/{i}/status", {"to": to})[1]["status"], to)

    # --- delete ---
    def test_delete_only_idea_or_archived_and_is_audited(self):
        ep = self.make(code="DEL-1")
        i = ep["id"]
        self.call("POST", f"/episodes/{i}/status", {"to": "SCRIPTING"})
        code, out = self.call("DELETE", f"/episodes/{i}")
        self.assertEqual(code, 409)
        self.assertIn("archive", out["error"])
        self.call("POST", f"/episodes/{i}/status", {"to": "ARCHIVED"})
        self.assertEqual(self.call("DELETE", f"/episodes/{i}")[1], {"deleted": i})
        self.assertEqual(self.call("GET", f"/episodes/{i}")[0], 404)
        row = self.conn.execute("SELECT target, detail FROM audit_events WHERE action = 'content.episode.delete' ORDER BY id DESC").fetchone()
        self.assertEqual((row["target"], row["detail"]), (f"episode:{i}", "DEL-1"))

    def test_delete_blocked_when_other_records_depend_on_it(self):
        ep = self.make()
        self.conn.execute("INSERT INTO scripts(episode_id, version) VALUES (?, 1)", (ep["id"],))
        code, out = self.call("DELETE", f"/episodes/{ep['id']}")
        self.assertEqual(code, 409)
        self.assertEqual(self.call("GET", f"/episodes/{ep['id']}")[0], 200)

    # --- audit / role ---
    def test_every_write_is_audited(self):
        before = len(self.audit_actions())
        ep = self.make()
        self.call("PATCH", f"/episodes/{ep['id']}", {"title": "SAMPLE b"})
        self.call("POST", f"/episodes/{ep['id']}/status", {"to": "SCRIPTING"})
        self.assertEqual(self.audit_actions()[before:], ["content.episode.create", "content.episode.update", "content.episode.status"])

    def test_failed_write_leaves_no_audit_row(self):
        before = len(self.audit_actions())
        self.call("POST", "/episodes", {"series_id": self.series, "code": "NOAUDIT", "title": "t", "planned_date": "bad"})
        self.assertEqual(len(self.audit_actions()), before)

    def test_requests_do_not_leak_the_content_role_to_the_connection(self):
        self.make()
        self.assertNotEqual(self.conn.execute("SELECT current_user AS u").fetchone()["u"], "content_app")


if __name__ == "__main__":
    unittest.main()
