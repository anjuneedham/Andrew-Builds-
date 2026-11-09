"""CP1: idea backlog + promote, calendar (America/Jamaica), through the real HTTP handler + owner auth. Needs TEST_DATABASE_URL (throwaway)."""

import json
import unittest
from datetime import datetime, timezone

from core.content import schedule
from dashboard import app as dash
from tests import authutil
from tests.dbutil import make_conn


class Base(unittest.TestCase):
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

    def actions(self, like):
        return [r["action"] for r in self.conn.execute("SELECT action FROM audit_events WHERE action LIKE ? ORDER BY id", (like,))]

    def idea(self, **kw):
        code, out = self.call("POST", "/ideas", {"title": "SAMPLE idea", **kw})
        self.assertEqual(code, 201, out)
        return out

    def episode(self, **kw):
        type(self).n += 1
        code, out = self.call("POST", "/episodes", {"series_id": self.series, "code": f"CAL{self.n:03}", "title": "SAMPLE ep", **kw})
        self.assertEqual(code, 201, out)
        return out


class IdeasApi(Base):
    def test_every_route_is_401_without_a_session(self):
        for method, path in [("GET", "/ideas"), ("POST", "/ideas"), ("GET", "/ideas/1"), ("PATCH", "/ideas/1"), ("DELETE", "/ideas/1"),
                             ("POST", "/ideas/1/status"), ("POST", "/ideas/1/promote")]:
            with self.subTest(route=f"{method} {path}"):
                self.assertEqual(self.call(method, path, token=None)[0], 401)
                self.assertEqual(self.call(method, path, token="bad")[0], 401)

    def test_create_read_list_and_defaults(self):
        i = self.idea(notes="SAMPLE notes", series_id=self.series)
        self.assertEqual((i["status"], i["notes"], i["series_id"], i["episode_id"]), ("BACKLOG", "SAMPLE notes", self.series, None))
        self.assertEqual(self.call("GET", f"/ideas/{i['id']}")[1]["title"], "SAMPLE idea")
        self.assertIn(i["id"], [x["id"] for x in self.call("GET", "/ideas")[1]])
        self.assertEqual(self.idea()["notes"], "")

    def test_validation_is_400_and_unknown_ids_are_404(self):
        for body in ({}, {"title": ""}, {"title": "  "}, {"title": 5}, {"title": "t" * 201}, {"title": "t", "notes": 5}, {"title": "t", "notes": "n" * 5001},
                     {"title": "t", "series_id": "1"}, {"title": "t", "series_id": True}, {"title": "t", "status": "DROPPED"}, {"title": "t", "episode_id": 1}):
            with self.subTest(body=str(body)[:50]):
                self.assertEqual(self.call("POST", "/ideas", body)[0], 400)
        for raw in (b"nope", b"[]", b"\xff"):
            self.assertEqual(self.call("POST", "/ideas", raw)[0], 400)
        self.assertEqual(self.call("POST", "/ideas", {"title": "t", "series_id": 999999})[0], 404)
        for method in ("GET", "PATCH", "DELETE"):
            self.assertEqual(self.call(method, "/ideas/999999", {"title": "x"})[0], 404)
        self.assertEqual(self.call("POST", "/ideas/999999/status", {"to": "DROPPED"})[0], 404)
        self.assertEqual(self.call("POST", "/ideas/999999/promote", {"code": "X1"})[0], 404)

    def test_patch_edits_allowed_fields_only(self):
        i = self.idea()
        code, out = self.call("PATCH", f"/ideas/{i['id']}", {"title": "SAMPLE new", "notes": "", "series_id": self.series})
        self.assertEqual((code, out["title"], out["notes"], out["series_id"]), (200, "SAMPLE new", "", self.series))
        self.assertIsNone(self.call("PATCH", f"/ideas/{i['id']}", {"series_id": None})[1]["series_id"])
        for body in ({}, {"status": "DROPPED"}, {"episode_id": 1}, {"title": ""}, {"notes": None}, {"series_id": "x"}):
            with self.subTest(body=body):
                self.assertEqual(self.call("PATCH", f"/ideas/{i['id']}", body)[0], 400)
        self.assertEqual(self.call("PATCH", f"/ideas/{i['id']}", {"series_id": 999999})[0], 404)

    def test_drop_and_restore(self):
        i = self.idea()["id"]
        self.assertEqual(self.call("POST", f"/ideas/{i}/status", {"to": "DROPPED"})[1]["status"], "DROPPED")
        self.assertEqual(self.call("POST", f"/ideas/{i}/status", {"to": "DROPPED"})[0], 409)
        self.assertEqual(self.call("POST", f"/ideas/{i}/status", {"to": "BACKLOG"})[1]["status"], "BACKLOG")
        for to in ("SCHEDULED", "NOPE", None):
            self.assertEqual(self.call("POST", f"/ideas/{i}/status", {"to": to})[0], 400)
        self.assertEqual(self.call("POST", f"/ideas/{i}/status", {})[0], 400)

    def test_promote_creates_an_idea_status_episode_and_links_both_ways(self):
        i = self.idea(series_id=self.series)
        code, out = self.call("POST", f"/ideas/{i['id']}/promote", {"code": "PRO-1", "planned_date": "2026-12-03", "target_duration_s": 480})
        self.assertEqual(code, 201, out)
        ep, idea = out["episode"], out["idea"]
        self.assertEqual((ep["title"], ep["status"], ep["series_id"], ep["planned_date"], ep["target_duration_s"]),
                         ("SAMPLE idea", "IDEA", self.series, "2026-12-03", 480))
        self.assertEqual((idea["status"], idea["episode_id"]), ("SCHEDULED", ep["id"]))
        self.assertEqual(self.call("GET", f"/ideas/{i['id']}")[1]["episode_id"], ep["id"])
        self.assertEqual(self.call("GET", f"/episodes/{ep['id']}")[0], 200)

    def test_promote_rules(self):
        i = self.idea()
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/promote", {"code": "NOS-1"})[0], 400)           # no series anywhere
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/promote", {"series_id": self.series})[0], 400)  # no code
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/promote", {"series_id": self.series, "code": "x y"})[0], 400)
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/promote", {"series_id": 999999, "code": "NOS-2"})[0], 404)
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/promote", {"series_id": self.series, "code": "NOS-3", "title": "other"})[0], 400)
        self.assertEqual(self.call("GET", f"/ideas/{i['id']}")[1]["status"], "BACKLOG")                      # nothing changed
        ok = self.call("POST", f"/ideas/{i['id']}/promote", {"series_id": self.series, "code": "NOS-4"})
        self.assertEqual(ok[0], 201)
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/promote", {"series_id": self.series, "code": "NOS-5"})[0], 409)  # already promoted
        d = self.idea()["id"]
        self.call("POST", f"/ideas/{d}/status", {"to": "DROPPED"})
        self.assertEqual(self.call("POST", f"/ideas/{d}/promote", {"series_id": self.series, "code": "NOS-6"})[0], 409)       # dropped

    def test_duplicate_code_on_promote_is_409_and_rolls_everything_back(self):
        ep = self.episode()
        i = self.idea(series_id=self.series)
        before = self.actions("content.%")
        code, out = self.call("POST", f"/ideas/{i['id']}/promote", {"code": ep["code"]})
        self.assertEqual(code, 409)
        self.assertNotIn("constraint", out["error"].lower())
        self.assertEqual(self.call("GET", f"/ideas/{i['id']}")[1]["status"], "BACKLOG")
        self.assertEqual(self.actions("content.%"), before)                                                  # no audit row either

    def test_edit_and_delete_of_a_promoted_idea(self):
        i = self.idea(series_id=self.series)
        ep = self.call("POST", f"/ideas/{i['id']}/promote", {"code": "PRO-D1"})[1]["episode"]
        self.assertEqual(self.call("DELETE", f"/ideas/{i['id']}")[0], 409)
        self.assertEqual(self.call("POST", f"/ideas/{i['id']}/status", {"to": "DROPPED"})[0], 409)
        self.assertEqual(self.call("PATCH", f"/ideas/{i['id']}", {"notes": "still editable"})[0], 200)
        # deleting the episode sends the idea back to the backlog instead of leaving it pointing at nothing
        self.assertEqual(self.call("DELETE", f"/episodes/{ep['id']}")[0], 200)
        back = self.call("GET", f"/ideas/{i['id']}")[1]
        self.assertEqual((back["status"], back["episode_id"]), ("BACKLOG", None))

    def test_delete_is_audited_and_hard(self):
        i = self.idea()
        self.assertEqual(self.call("DELETE", f"/ideas/{i['id']}")[1], {"deleted": i["id"]})
        self.assertEqual(self.call("GET", f"/ideas/{i['id']}")[0], 404)
        row = self.conn.execute("SELECT target, detail FROM audit_events WHERE action = 'content.idea.delete' ORDER BY id DESC").fetchone()
        self.assertEqual((row["target"], row["detail"]), (f"idea:{i['id']}", "SAMPLE idea"))

    def test_every_write_is_audited_and_a_failed_write_is_not(self):
        before = len(self.actions("content.idea.%"))
        i = self.idea()
        self.call("PATCH", f"/ideas/{i['id']}", {"title": "SAMPLE b"})
        self.call("POST", f"/ideas/{i['id']}/status", {"to": "DROPPED"})
        self.call("POST", "/ideas", {"title": ""})
        self.call("POST", f"/ideas/{i['id']}/status", {"to": "DROPPED"})   # 409
        self.assertEqual(self.actions("content.idea.%")[before:], ["content.idea.create", "content.idea.update", "content.idea.status"])


class CalendarApi(Base):
    def setUp(self):
        self._clock = schedule.clock
        self.at(2026, 11, 9, 15)            # Monday 9 Nov 2026, 10:00 in Jamaica

    def tearDown(self):
        schedule.clock = self._clock

    @staticmethod
    def at(y, mo, d, h, mi=0):
        schedule.clock = lambda: datetime(y, mo, d, h, mi, tzinfo=timezone.utc)

    def test_every_route_is_401_without_a_session(self):
        for path in ("/calendar/today", "/calendar/month/2026-11", "/calendar/week/2026-11-09"):
            self.assertEqual(self.call("GET", path, token=None)[0], 401)
            self.assertEqual(self.call("GET", path, token="bad")[0], 401)

    def test_today_is_the_jamaica_date_not_the_utc_date(self):
        self.at(2026, 11, 10, 3, 30)        # 03:30 UTC on the 10th is still 22:30 on the 9th in Jamaica
        out = self.call("GET", "/calendar/today")[1]
        self.assertEqual((out["today"], out["timezone"], out["month"], out["week_start"]), ("2026-11-09", "America/Jamaica", "2026-11", "2026-11-09"))
        self.at(2026, 11, 10, 5, 0)         # 05:00 UTC = 00:00 Jamaica: the new day starts exactly here
        self.assertEqual(self.call("GET", "/calendar/today")[1]["today"], "2026-11-10")
        self.at(2026, 12, 1, 4, 59)         # still 30 November in Jamaica
        out = self.call("GET", "/calendar/today")[1]
        self.assertEqual((out["today"], out["month"]), ("2026-11-30", "2026-11"))

    def test_month_grid_starts_on_monday_and_covers_whole_weeks(self):
        out = self.call("GET", "/calendar/month/2026-11")[1]       # 1 Nov 2026 is a Sunday; 30 Nov is a Monday
        days = out["days"]
        self.assertEqual((out["start"], out["end"]), ("2026-10-26", "2026-12-06"))
        self.assertEqual(len(days), 42)
        self.assertEqual(sum(d["in_month"] for d in days), 30)
        self.assertEqual([d["date"] for d in days if d["is_today"]], ["2026-11-09"])
        feb = self.call("GET", "/calendar/month/2027-02")[1]       # 1 Feb 2027 is a Monday, 28 Feb a Sunday: exactly 4 weeks
        self.assertEqual((feb["start"], feb["end"], len(feb["days"])), ("2027-02-01", "2027-02-28", 28))
        dec = self.call("GET", "/calendar/month/2026-12")[1]       # December rolls the year correctly
        self.assertEqual((dec["start"], dec["end"]), ("2026-11-30", "2027-01-03"))

    def test_episodes_appear_on_their_planned_day_and_overdue_is_flagged(self):
        late = self.episode(planned_date="2026-11-03")
        today = self.episode(planned_date="2026-11-09")
        far = self.episode(planned_date="2026-11-20")
        none = self.episode()
        done = self.episode(planned_date="2026-11-02")
        for to in ("ARCHIVED",):
            self.call("POST", f"/episodes/{done['id']}/status", {"to": to})
        out = self.call("GET", "/calendar/month/2026-11")[1]
        by = {d["date"]: d["episodes"] for d in out["days"]}
        self.assertIn(late["id"], [e["id"] for e in by["2026-11-03"]])
        self.assertTrue(next(e for e in by["2026-11-03"] if e["id"] == late["id"])["overdue"])
        self.assertFalse(next(e for e in by["2026-11-09"] if e["id"] == today["id"])["overdue"])   # due today is not overdue
        self.assertFalse(next(e for e in by["2026-11-20"] if e["id"] == far["id"])["overdue"])
        self.assertFalse(next(e for e in by["2026-11-02"] if e["id"] == done["id"])["overdue"])    # archived is never overdue
        self.assertIn(none["id"], [e["id"] for e in out["unscheduled"]])
        self.assertNotIn(done["id"], [e["id"] for e in out["unscheduled"]])
        for d in out["days"]:
            for e in d["episodes"]:
                self.assertEqual(e["planned_date"], d["date"])

    def test_leading_and_trailing_days_show_their_episodes_too(self):
        e = self.episode(planned_date="2026-10-28")                 # shown in the November grid's first week
        out = self.call("GET", "/calendar/month/2026-11")[1]
        day = next(d for d in out["days"] if d["date"] == "2026-10-28")
        self.assertFalse(day["in_month"])
        self.assertIn(e["id"], [x["id"] for x in day["episodes"]])

    def test_week_view_normalises_to_monday(self):
        e = self.episode(planned_date="2026-11-12")
        for any_day in ("2026-11-09", "2026-11-12", "2026-11-15"):
            out = self.call("GET", f"/calendar/week/{any_day}")[1]
            self.assertEqual((out["start"], out["end"], len(out["days"])), ("2026-11-09", "2026-11-15", 7))
            self.assertIn(e["id"], [x["id"] for d in out["days"] for x in d["episodes"]])
        self.assertEqual(self.call("GET", "/calendar/week/2026-11-16")[1]["start"], "2026-11-16")

    def test_bad_calendar_input_is_400_and_unknown_paths_404(self):
        for path in ("/calendar/month/2026-13", "/calendar/month/2026-00", "/calendar/month/1999-01", "/calendar/month/2101-01", "/calendar/month/nov",
                     "/calendar/month/202611", "/calendar/week/2026-13-01", "/calendar/week/20261109", "/calendar/week/1999-01-04", "/calendar/week/x"):
            with self.subTest(path=path):
                self.assertEqual(self.call("GET", path)[0], 400)
        for method, path in (("POST", "/calendar/today"), ("GET", "/calendar"), ("GET", "/calendar/year/2026"), ("GET", "/calendar/month/2026-11/x")):
            with self.subTest(path=path):
                self.assertEqual(self.call(method, path)[0], 404)

    def test_reschedule_is_a_patch_of_planned_date_and_moves_the_episode(self):
        e = self.episode(planned_date="2026-11-10")
        self.assertEqual(self.call("PATCH", f"/episodes/{e['id']}", {"planned_date": "2026-11-17"})[0], 200)
        by = {d["date"]: [x["id"] for x in d["episodes"]] for d in self.call("GET", "/calendar/month/2026-11")[1]["days"]}
        self.assertNotIn(e["id"], by["2026-11-10"])
        self.assertIn(e["id"], by["2026-11-17"])

    def test_strict_date_format_on_episodes(self):
        for bad in ("20261201", "2026-W49-1", "2026-1-5", " 2026-12-01"):
            with self.subTest(bad=bad):
                self.assertEqual(self.call("POST", "/episodes", {"series_id": self.series, "code": "D1", "title": "t", "planned_date": bad})[0], 400)


if __name__ == "__main__":
    unittest.main()
