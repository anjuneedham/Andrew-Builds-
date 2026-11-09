"""CP1 / P2a: scripts and script lines through the real HTTP handler + owner auth. Needs TEST_DATABASE_URL (throwaway).
The claim gate itself is tested at database level in test_content_p0; here we prove the API surfaces it and adds the step order."""

import json
import unittest

from core.content import scripts
from core.content.meta import ENUMS
from dashboard import app as dash
from tests import authutil
from tests.dbutil import make_conn


class ScriptsApi(unittest.TestCase):
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

    def episode(self):
        type(self).n += 1
        code, out = self.call("POST", "/episodes", {"series_id": self.series, "code": f"SC{self.n:03}", "title": "SAMPLE ep"})
        self.assertEqual(code, 201)
        return out["id"]

    def script(self, eid=None, **kw):
        code, out = self.call("POST", f"/episodes/{eid or self.episode()}/scripts", kw)
        self.assertEqual(code, 201, out)
        return out

    def line(self, sid, text="SAMPLE line", kind="OPINION", **kw):
        code, out = self.call("POST", f"/scripts/{sid}/lines", {"text": text, "kind": kind, **kw})
        self.assertEqual(code, 201, out)
        return out

    def texts(self, sid):
        return [l["text"] for l in self.call("GET", f"/scripts/{sid}")[1]["lines"]]

    def actions(self, like="content.script.%"):
        return [r["action"] for r in self.conn.execute("SELECT action FROM audit_events WHERE action LIKE ? ORDER BY id", (like,))]

    # --- auth ---
    def test_every_route_is_401_without_a_session(self):
        routes = [("GET", "/episodes/1/scripts"), ("POST", "/episodes/1/scripts"), ("GET", "/scripts/1"), ("PATCH", "/scripts/1"), ("DELETE", "/scripts/1"),
                  ("POST", "/scripts/1/status"), ("POST", "/scripts/1/lines"), ("PATCH", "/lines/1"), ("DELETE", "/lines/1"), ("POST", "/lines/1/move")]
        for method, path in routes:
            with self.subTest(route=f"{method} {path}"):
                self.assertEqual(self.call(method, path, token=None)[0], 401)
                self.assertEqual(self.call(method, path, token="bad")[0], 401)

    # --- scripts ---
    def test_create_numbers_versions_per_episode_and_lists_them(self):
        e = self.episode()
        a, b = self.script(e), self.script(e, body="SAMPLE notes")
        self.assertEqual((a["version"], b["version"], a["status"], b["body"]), (1, 2, "DRAFT", "SAMPLE notes"))
        self.assertEqual(self.script()["version"], 1)                                   # another episode starts at 1
        rows = self.call("GET", f"/episodes/{e}/scripts")[1]
        self.assertEqual([r["version"] for r in rows], [2, 1])
        self.assertTrue(all({"id", "status", "lines"} <= set(r) for r in rows))

    def test_create_validation_and_404(self):
        e = self.episode()
        for body in ({"body": 5}, {"body": "x" * 20_001}, {"status": "LOCKED"}, {"version": 9}, {"copy_from": "1"}, {"copy_from": True}):
            with self.subTest(body=str(body)[:40]):
                self.assertEqual(self.call("POST", f"/episodes/{e}/scripts", body)[0], 400)
        other = self.script()["id"]                                                      # a script of a different episode
        self.assertEqual(self.call("POST", f"/episodes/{e}/scripts", {"copy_from": other})[0], 400)
        self.assertEqual(self.call("POST", f"/episodes/{e}/scripts", {"copy_from": 999999})[0], 400)
        self.assertEqual(self.call("POST", "/episodes/999999/scripts", {})[0], 404)
        self.assertEqual(self.call("GET", "/episodes/999999/scripts")[0], 404)
        self.assertEqual(self.call("POST", f"/episodes/{e}/scripts", b"nope")[0], 400)

    def test_cannot_add_a_script_to_an_archived_episode(self):
        e = self.episode()
        self.call("POST", f"/episodes/{e}/status", {"to": "ARCHIVED"})
        code, out = self.call("POST", f"/episodes/{e}/scripts", {})
        self.assertEqual(code, 409)
        self.assertIn("restore", out["error"])

    def test_get_patch_body_and_unknown_ids(self):
        s = self.script()
        self.assertEqual(self.call("PATCH", f"/scripts/{s['id']}", {"body": "SAMPLE new body"})[1]["body"], "SAMPLE new body")
        self.assertEqual(self.call("PATCH", f"/scripts/{s['id']}", {"body": ""})[1]["body"], "")
        for body in ({}, {"body": None}, {"body": 5}, {"status": "READY_TO_RECORD"}, {"version": 3}, {"body": "x" * 20_001}):
            with self.subTest(body=str(body)[:40]):
                self.assertEqual(self.call("PATCH", f"/scripts/{s['id']}", body)[0], 400)
        for method in ("GET", "PATCH", "DELETE"):
            self.assertEqual(self.call(method, "/scripts/999999", {"body": "x"})[0], 404)
        self.assertEqual(self.call("POST", "/scripts/999999/status", {"to": "IN_REVIEW"})[0], 404)
        self.assertEqual(self.call("GET", "/scripts/abc")[0], 404)

    # --- lines ---
    def test_lines_default_to_fact_and_are_appended_in_order(self):
        s = self.script()["id"]
        out = self.call("POST", f"/scripts/{s}/lines", {"text": "  SAMPLE first  "})[1]
        self.assertEqual([(l["position"], l["text"], l["kind"]) for l in out["lines"]], [(1, "SAMPLE first", "FACT")])
        self.line(s, "SAMPLE second", "QUESTION")
        out = self.line(s, "SAMPLE third", "CTA")
        self.assertEqual([l["position"] for l in out["lines"]], [1, 2, 3])
        self.assertEqual(out["counts"], {"FACT": 1, "QUESTION": 1, "CTA": 1})

    def test_insert_at_a_position_shifts_the_rest(self):
        s = self.script()["id"]
        for t in ("a", "b", "c"):
            self.line(s, t)
        out = self.line(s, "NEW", position=2)
        self.assertEqual([l["text"] for l in out["lines"]], ["a", "NEW", "b", "c"])
        self.assertEqual([l["position"] for l in out["lines"]], [1, 2, 3, 4])
        self.assertEqual([l["text"] for l in self.line(s, "FIRST", position=1)["lines"]][:2], ["FIRST", "a"])
        self.assertEqual(self.line(s, "LAST", position=6)["lines"][-1]["text"], "LAST")

    def test_line_validation(self):
        s = self.script()["id"]
        self.line(s, "one")
        for body in ({}, {"text": ""}, {"text": "  "}, {"text": 5}, {"text": "t" * 2001}, {"text": "t", "kind": "NOPE"}, {"text": "t", "kind": None},
                     {"text": "t", "kind": "fact"}, {"text": "t", "position": 0}, {"text": "t", "position": 3}, {"text": "t", "position": "1"},
                     {"text": "t", "position": True}, {"text": "t", "script_id": 2}):
            with self.subTest(body=str(body)[:50]):
                self.assertEqual(self.call("POST", f"/scripts/{s}/lines", body)[0], 400)
        self.assertEqual(self.call("POST", "/scripts/999999/lines", {"text": "t"})[0], 404)
        self.assertEqual(self.texts(s), ["one"])

    def test_every_kind_in_the_enum_is_accepted(self):
        s = self.script()["id"]
        for k in ENUMS[("script_lines", "kind")]:
            self.assertEqual(self.call("POST", f"/scripts/{s}/lines", {"text": f"SAMPLE {k}", "kind": k})[0], 201)
        self.assertEqual(set(scripts.KINDS), set(ENUMS[("script_lines", "kind")]))

    def test_edit_a_line(self):
        s = self.script()["id"]
        lid = self.line(s, "old", "OPINION")["lines"][0]["id"]
        out = self.call("PATCH", f"/lines/{lid}", {"text": "new", "kind": "REFLECTION"})[1]
        self.assertEqual((out["lines"][0]["text"], out["lines"][0]["kind"]), ("new", "REFLECTION"))
        self.assertEqual(self.call("PATCH", f"/lines/{lid}", {"kind": "FACT"})[1]["lines"][0]["kind"], "FACT")
        for body in ({}, {"text": ""}, {"kind": "NOPE"}, {"position": 2}, {"script_id": 9}, {"text": 7}):
            with self.subTest(body=body):
                self.assertEqual(self.call("PATCH", f"/lines/{lid}", body)[0], 400)
        self.assertEqual(self.call("PATCH", "/lines/999999", {"text": "x"})[0], 404)

    def test_delete_a_line_closes_the_gap(self):
        s = self.script()["id"]
        ids = [self.line(s, t)["lines"][-1]["id"] for t in ("a", "b", "c")]
        out = self.call("DELETE", f"/lines/{ids[1]}")[1]
        self.assertEqual([(l["position"], l["text"]) for l in out["lines"]], [(1, "a"), (2, "c")])
        self.assertEqual(self.call("DELETE", f"/lines/{ids[1]}")[0], 404)
        self.assertEqual(self.call("DELETE", "/lines/999999")[0], 404)

    def test_move_a_line_up_and_down(self):
        s = self.script()["id"]
        ids = {t: self.line(s, t)["lines"][-1]["id"] for t in ("a", "b", "c", "d")}
        self.assertEqual([l["text"] for l in self.call("POST", f"/lines/{ids['d']}/move", {"to": 1})[1]["lines"]], ["d", "a", "b", "c"])
        self.assertEqual([l["text"] for l in self.call("POST", f"/lines/{ids['d']}/move", {"to": 4})[1]["lines"]], ["a", "b", "c", "d"])
        self.assertEqual([l["text"] for l in self.call("POST", f"/lines/{ids['a']}/move", {"to": 3})[1]["lines"]], ["b", "c", "a", "d"])
        self.assertEqual([l["text"] for l in self.call("POST", f"/lines/{ids['a']}/move", {"to": 3})[1]["lines"]], ["b", "c", "a", "d"])  # no-op
        self.assertEqual([l["position"] for l in self.call("GET", f"/scripts/{s}")[1]["lines"]], [1, 2, 3, 4])
        for body in ({}, {"to": 0}, {"to": 5}, {"to": "1"}, {"to": True}, {"to": 1, "x": 2}):
            with self.subTest(body=body):
                self.assertEqual(self.call("POST", f"/lines/{ids['a']}/move", body)[0], 400)
        self.assertEqual(self.call("POST", "/lines/999999/move", {"to": 1})[0], 404)

    # --- status machine ---
    def test_transition_table_covers_every_status_and_only_known_ones(self):
        statuses = set(ENUMS[("scripts", "status")])
        self.assertEqual(set(scripts.TRANSITIONS), statuses)
        for src, targets in scripts.TRANSITIONS.items():
            self.assertTrue(set(targets) <= statuses and src not in targets, src)
        self.assertEqual(scripts.TRANSITIONS["LOCKED"], ())

    def test_status_steps_follow_the_machine(self):
        s = self.script()["id"]
        self.line(s, "SAMPLE opinion", "OPINION")
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "READY_TO_RECORD"})[0], 409)   # DRAFT cannot skip review
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "DRAFT"})[0], 409)             # same status
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "LOCKED"})[0], 409)
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "NOPE"})[0], 400)
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {})[0], 400)
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "IN_REVIEW"})[1]["status"], "IN_REVIEW")
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "DRAFT"})[1]["status"], "DRAFT")      # one step back
        self.call("POST", f"/scripts/{s}/status", {"to": "IN_REVIEW"})
        out = self.call("POST", f"/scripts/{s}/status", {"to": "READY_TO_RECORD"})[1]                          # only non-FACT lines: gate passes
        self.assertEqual((out["status"], out["editable"], out["allowed_next"]), ("READY_TO_RECORD", False, ["DRAFT", "LOCKED"]))
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "LOCKED"})[1]["status"], "LOCKED")
        for to in ("DRAFT", "IN_REVIEW", "READY_TO_RECORD"):
            code, out = self.call("POST", f"/scripts/{s}/status", {"to": to})
            self.assertEqual(code, 409)
            self.assertIn("final", out["error"])

    def test_a_fact_line_blocks_ready_to_record_even_through_the_api(self):
        s = self.script()["id"]
        self.line(s, "SAMPLE a factual claim", "FACT")
        self.call("POST", f"/scripts/{s}/status", {"to": "IN_REVIEW"})
        code, out = self.call("POST", f"/scripts/{s}/status", {"to": "READY_TO_RECORD"})
        self.assertEqual(code, 409)
        self.assertIn("claim check", out["error"])
        self.assertNotIn("CONTENT_RULE", out["error"])
        self.assertEqual(self.call("GET", f"/scripts/{s}")[1]["status"], "IN_REVIEW")
        self.call("PATCH", f"/lines/{self.call('GET', f'/scripts/{s}')[1]['lines'][0]['id']}", {"kind": "OPINION"})   # re-tag: now it passes
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "READY_TO_RECORD"})[0], 200)

    def test_an_empty_script_cannot_become_ready(self):
        s = self.script()["id"]
        self.call("POST", f"/scripts/{s}/status", {"to": "IN_REVIEW"})
        self.assertEqual(self.call("POST", f"/scripts/{s}/status", {"to": "READY_TO_RECORD"})[0], 409)

    def test_a_ready_script_is_frozen_and_returning_to_draft_unfreezes_it_and_pulls_the_episode_back(self):
        e = self.episode()
        s = self.script(e)["id"]
        lid = self.line(s, "SAMPLE", "OPINION")["lines"][0]["id"]
        self.call("POST", f"/scripts/{s}/status", {"to": "IN_REVIEW"})
        self.call("POST", f"/scripts/{s}/status", {"to": "READY_TO_RECORD"})
        self.call("POST", f"/episodes/{e}/status", {"to": "SCRIPTING"})
        self.assertEqual(self.call("POST", f"/episodes/{e}/status", {"to": "READY_TO_RECORD"})[0], 200)     # episode gate now satisfied
        frozen = [("PATCH", f"/scripts/{s}", {"body": "changed"}), ("POST", f"/scripts/{s}/lines", {"text": "new"}),
                  ("PATCH", f"/lines/{lid}", {"text": "changed"}), ("DELETE", f"/lines/{lid}", None), ("DELETE", f"/scripts/{s}", None)]
        for method, path, body in frozen:
            with self.subTest(route=f"{method} {path}"):
                self.assertEqual(self.call(method, path, body)[0], 409)
        self.assertEqual(self.texts(s), ["SAMPLE"])
        self.call("POST", f"/scripts/{s}/status", {"to": "DRAFT"})
        self.assertEqual(self.call("GET", f"/episodes/{e}")[1]["status"], "SCRIPTING")                       # pulled back by the database
        self.assertEqual(self.call("PATCH", f"/lines/{lid}", {"text": "now editable"})[0], 200)

    def test_a_locked_script_never_changes(self):
        s = self.script()["id"]
        lid = self.line(s, "SAMPLE", "OPINION")["lines"][0]["id"]
        self.line(s, "SAMPLE 2", "OPINION")
        for to in ("IN_REVIEW", "READY_TO_RECORD", "LOCKED"):
            self.call("POST", f"/scripts/{s}/status", {"to": to})
        for method, path, body in (("PATCH", f"/scripts/{s}", {"body": "x"}), ("POST", f"/scripts/{s}/lines", {"text": "x"}),
                                   ("PATCH", f"/lines/{lid}", {"text": "x"}), ("POST", f"/lines/{lid}/move", {"to": 2}), ("DELETE", f"/scripts/{s}", None)):
            self.assertEqual(self.call(method, path, body)[0], 409, (method, path))

    # --- delete ---
    def test_delete_draft_script_removes_its_lines_and_is_audited(self):
        e = self.episode()
        s = self.script(e)
        self.line(s["id"], "SAMPLE")
        self.assertEqual(self.call("DELETE", f"/scripts/{s['id']}")[1], {"deleted": s["id"]})
        self.assertEqual(self.call("GET", f"/scripts/{s['id']}")[0], 404)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM script_lines WHERE script_id = ?", (s["id"],)).fetchone()[0], 0)
        row = self.conn.execute("SELECT target, detail FROM audit_events WHERE action = 'content.script.delete' ORDER BY id DESC").fetchone()
        self.assertEqual((row["target"], row["detail"]), (f"script:{s['id']}", f"episode:{e} v1"))

    # --- new version from an old one ---
    def test_copy_from_copies_body_lines_kinds_and_claim_links(self):
        e = self.episode()
        s1 = self.script(e, body="SAMPLE body")["id"]
        self.line(s1, "SAMPLE fact", "FACT")
        self.line(s1, "SAMPLE opinion", "OPINION")
        fid = self.call("GET", f"/scripts/{s1}")[1]["lines"][0]["id"]
        src = self.conn.execute("INSERT INTO sources(kind, reference) VALUES ('document', 'SAMPLE') RETURNING id").fetchone()["id"]
        cl = self.conn.execute("INSERT INTO claims(statement, project) VALUES ('SAMPLE claim', 'andrew-builds') RETURNING id").fetchone()["id"]
        self.conn.execute("INSERT INTO claim_sources VALUES (?, ?)", (cl, src))
        self.conn.execute("INSERT INTO line_claims VALUES (?, ?)", (fid, cl))
        s2 = self.script(e, copy_from=s1)
        self.assertEqual((s2["version"], s2["body"], s2["status"]), (2, "SAMPLE body", "DRAFT"))
        self.assertEqual([(l["text"], l["kind"], len(l["claims"])) for l in s2["lines"]], [("SAMPLE fact", "FACT", 1), ("SAMPLE opinion", "OPINION", 0)])
        self.assertNotEqual(s2["lines"][0]["id"], fid)
        self.assertEqual(self.script(e, copy_from=s1, body="override")["body"], "override")
        self.assertEqual(self.texts(s1), ["SAMPLE fact", "SAMPLE opinion"])                                  # source untouched

    def test_a_locked_script_can_be_copied_into_a_new_draft(self):
        e = self.episode()
        s1 = self.script(e)["id"]
        self.line(s1, "SAMPLE", "OPINION")
        for to in ("IN_REVIEW", "READY_TO_RECORD", "LOCKED"):
            self.call("POST", f"/scripts/{s1}/status", {"to": to})
        s2 = self.script(e, copy_from=s1)
        self.assertEqual((s2["status"], s2["editable"], len(s2["lines"])), ("DRAFT", True, 1))

    # --- audit / role ---
    def test_every_write_is_audited_and_a_failed_write_is_not(self):
        before = len(self.actions("content.%"))
        s = self.script()["id"]
        lid = self.line(s, "SAMPLE", "OPINION")["lines"][0]["id"]
        self.line(s, "SAMPLE 2", "OPINION")
        self.call("PATCH", f"/scripts/{s}", {"body": "b"})
        self.call("PATCH", f"/lines/{lid}", {"text": "t"})
        self.call("POST", f"/lines/{lid}/move", {"to": 2})
        self.call("POST", f"/scripts/{s}/status", {"to": "IN_REVIEW"})
        self.call("DELETE", f"/lines/{lid}")
        good = self.actions("content.%")[before:]
        self.assertEqual([a for a in good if a != "content.episode.create"],
                         ["content.script.create", "content.line.add", "content.line.add", "content.script.update", "content.line.update",
                          "content.line.move", "content.script.status", "content.line.delete"])
        n = len(self.actions("content.%"))
        self.call("POST", f"/scripts/{s}/lines", {"text": "bad", "kind": "NOPE"})                        # 400
        self.call("POST", f"/scripts/{s}/status", {"to": "LOCKED"})                                      # 409
        self.call("PATCH", "/lines/999999", {"text": "x"})                                               # 404
        self.assertEqual(len(self.actions("content.%")), n)

    def test_rule_violation_rolls_back_partial_position_shifts(self):
        s = self.script()["id"]
        for t in ("a", "b"):
            self.line(s, t, "OPINION")
        for to in ("IN_REVIEW", "READY_TO_RECORD"):
            self.call("POST", f"/scripts/{s}/status", {"to": to})
        self.assertEqual(self.call("POST", f"/scripts/{s}/lines", {"text": "new", "position": 1})[0], 409)
        self.assertEqual(self.texts(s), ["a", "b"])
        self.assertEqual([l["position"] for l in self.call("GET", f"/scripts/{s}")[1]["lines"]], [1, 2])

    def test_requests_do_not_leak_the_content_role_to_the_connection(self):
        self.script()
        self.assertNotEqual(self.conn.execute("SELECT current_user AS u").fetchone()["u"], "content_app")


if __name__ == "__main__":
    unittest.main()
